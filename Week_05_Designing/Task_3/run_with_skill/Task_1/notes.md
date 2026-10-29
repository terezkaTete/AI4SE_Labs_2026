# Week 05 – Task 1 (rerun with skill): Architecture discussion for RecipeCove

These are running notes from the Task 3 rerun of Task 1, done with the `architecture-decision` skill. They record key points, decisions, trade-offs and open questions, not a verbatim transcript.

Source requirements: `Week_05_Designing/Tasks/data/RecipeCove.txt`

## Contents
1. Requirements summary
2. Assumptions
3. Candidate architectures (A: modular monolith, B: microservices, C: serverless/BaaS)
4. Comparison table and recommendation
5. "Simple but seamless"
6. When the recommendation is wrong, with example systems
7. Team-size sensitivity
8. Final decision
9. Deep dive: grounding the LLM chatbot
10. Discussion log

---

## 1. Requirements summary

RecipeCove is a web app for finding recipes, saving them and reading about recipes and ingredients. **Its central feature is discovery**, through a search bar (story 2) and a chatbot that suggests recipes for a chosen diet (story 5). Registered users also get a profile, a favourites list and a calendar of recipe reminders that lives inside the app.

**Actors:** Visitor (anonymous), Registered user (signed in with Google). No admin or content editor is mentioned.

| Functional area | Stories | Notes / ambiguities |
|---|---|---|
| Identity | 1, 6, 7 | Google sign-in only (OIDC). Story 7 says "so that I can *leave* my information within the website". We read it as "my data stays saved after logout". |
| Discovery: search | 2 | Search by name only. Typo tolerance would be good to have. |
| Discovery: chatbot | 5 | "Suggested recipes for a specific diet". Could be a rule-based filter or an LLM. This is the riskiest component. |
| Catalogue pages | 3, 4 | Recipe and ingredient detail pages. This implies a structured ingredient entity, not free text. |
| Profile | 8 | Read-only view of basic info (taken from Google). |
| Favourites | 12–14 | Simple many-to-many between users and recipes. |
| Calendar | 9–11 | The calendar is "application-created", so it lives in the app, not in Google Calendar. Unclear whether a user can have more than one. Story 10 ("remove the data gathered") hints at a right to delete data. |

**Open questions that change the architecture:**
- **Data source:** our own catalogue (imported or curated) or a live third-party API (Spoonacular, TheMealDB)?
- **Chatbot:** a rule-based diet filter or an LLM? If it's an LLM, it must only suggest recipes that exist in the catalogue.
- **Reminders:** the calendar only shows them, or does the app actively notify users (email/push)? Notifying needs a scheduler.
- **Missing stories:** admin/content management, account deletion, editing the profile.
- **Missing non-functional requirements:** team, scale, availability, privacy (EU means GDPR).

## 2. Assumptions

A1–A4 were answered by the user in one question set at the start. A5–A9 were assumed by the assistant.

| # | Topic | Assumption | Source / reason |
|---|---|---|---|
| A1 | Team | **1 developer** builds and operates the whole system. | User |
| A2 | Data source | Recipes and ingredients are **imported once into our own DB** from an open dataset (e.g. TheMealDB dump), with re-imports as needed. | User. We control the schema, search and the chatbot's grounding. |
| A3 | Chatbot | **A real LLM, grounded in the catalogue**: it may only suggest recipes that exist in our DB. | User |
| A4 | Scale and compliance | Hundreds to a few thousand users, steady traffic, **EU users, so GDPR applies**. | User |
| A5 | Calendar | In-app only. Several calendars per user are allowed (stories 9/10 say "a Calendar"). An event is a recipe on a **local date**. Reminders are shown in the app; email notification is optional and comes later. | Spec says "application-created". |
| A6 | Auth | Google OIDC is the only login. No passwords are stored. | Story 1 |
| A7 | Admin | The developer manages the catalogue through an admin UI and import scripts. Users don't create content. | No story mentions it. |
| A8 | Availability | Best effort (~99%). A few minutes of downtime per deploy is acceptable, but should be avoided. | Student project |
| A9 | LLM provider | A hosted LLM API with tool calling. Costs are capped per user. | Self-hosting is not realistic for one developer. |

**The recommendation is most sensitive to A1 (team size) and A3 (LLM chatbot).** With a larger team, extracting the chatbot as a separate service becomes reasonable. With a rule-based chatbot, the hardest component disappears and option C becomes more attractive. If either changes, revisit section 4.

## 3. Candidate architectures

### A. Modular monolith

**Idea:** one deployable Python application (chosen because of A3: the LLM ecosystem is strongest in Python) with strict internal modules and one PostgreSQL database. Pages are server-rendered, with HTMX for small dynamic parts.

```
 Browser ──HTTPS──►  ┌──────────── RecipeCove app (Django) ────────────┐
   (HTML + HTMX,     │  identity │ catalogue │ search │ chatbot │      │
    SSE for chat)    │  profile  │ favourites│ calendar│ admin  │      │
                     └──────┬───────────────────┬──────────┬─────────┘
                            │ SQL               │ HTTPS    │ OIDC
                     ┌──────▼──────┐     ┌──────▼─────┐ ┌──▼─────┐
                     │ PostgreSQL  │     │ LLM API    │ │ Google │
                     │ (+ pg_trgm) │     │(tool calls)│ │  OIDC  │
                     └─────────────┘     └────────────┘ └────────┘
        import job (management command) ──► PostgreSQL  ◄── open recipe dataset
```

| Module | Stories |
|---|---|
| identity | 1, 6, 7 |
| profile | 8 |
| catalogue | 3, 4 (plus import) |
| search | 2 |
| chatbot | 5 |
| favourites | 12, 13, 14 |
| calendar | 9, 10, 11 |

**Data model sketch:**
```
user(id, google_sub UNIQUE, email, name, avatar_url, created_at)
recipe(id, source_id UNIQUE, title, instructions, image_url, prep_minutes, ...)
ingredient(id, name UNIQUE, description, nutrition_json)
recipe_ingredient(recipe_id, ingredient_id, quantity_text, quantity_num, unit)
diet(id, code UNIQUE)            -- vegan, vegetarian, gluten_free, keto, ...
recipe_diet(recipe_id, diet_id)
favourite(user_id, recipe_id, created_at, PK(user_id, recipe_id))
calendar(id, user_id, name, created_at)
calendar_event(id, calendar_id ON DELETE CASCADE, recipe_id, event_date DATE, note)
chat_session / chat_message(...)  -- short retention (see A4/GDPR)
```

**Pros:** fewest moving parts, so the most realistic option for one developer. Real joins and transactions (favourites + recipe titles in one query). One deploy, one log stream, one place to debug. Django gives auth integration (django-allauth), an admin UI (A7) and migrations for free.

**Cons:** everything scales together. A bug or a memory leak can take down the whole app. Module boundaries hold only if they're enforced (otherwise you get a "big ball of mud").

**Deployment:** one container on a PaaS (Fly.io, Render or Railway, in an EU region) + managed PostgreSQL in the EU. GitHub Actions: tests → build image → deploy with a health check. Rolling deploys avoid downtime.

**Painful low-level parts:**
- **Slow LLM calls hold workers.** A tool-calling round trip takes 3–15 s. With classic sync workers (gunicorn, 4 workers), four chatting users block the whole site. *Why:* thread-per-request means each waiting call holds a worker. → Run the chatbot view under ASGI (async) and stream with SSE, or give it a separate, bounded worker pool.
- **Module boundaries erode.** *Why:* in one codebase nothing stops `calendar` from importing `catalogue.models` directly, and in six months every module depends on every other. → Each module exposes a small `services.py` API. An import-linter rule in CI forbids imports of other modules' internals.
- **Importing free-text ingredients.** *Why:* datasets store "2 cloves garlic, minced" as one string, but story 4 needs a real `ingredient` entity. → Parse into quantity/unit/name, normalize names (garlic vs garlic cloves), keep the raw text, and use idempotent upserts keyed on `source_id` so re-imports don't create duplicates.
- **Diet tags are missing or wrong.** *Why:* datasets rarely tag "gluten-free" reliably, and both the chatbot (section 9) and suggestions depend on these tags. → Derive tags from the ingredients with rules (meat → not vegetarian), and review them manually in the admin UI.
- **OIDC done right.** *Why:* the details are easy to get wrong and hard to notice. → Use a library (allauth) that handles state (CSRF), PKCE, nonce and ID-token validation. Key users on `sub`, not email, because emails can change.
- **Calendar dates.** *Why:* "cook risotto on 3 March" is a day, not an instant. Storing it as UTC midnight shifts it to the previous day for users west of UTC. → Use a `DATE` column. Only an optional reminder time needs a timezone.

### B. Microservices

**Idea:** one service per domain, each with its own DB, behind an API gateway. Events flow over a message broker.

```
 SPA (React) ──► API Gateway (JWT check, routing, rate limit)
                   │        │          │           │            │
              identity   catalogue   search     chatbot    user-data
              svc+DB     svc+DB      svc+       svc        svc+DB
                          │          OpenSearch   │       (profile, favs,
                          │ events      ▲         │ HTTP   calendar)
                          └──► broker ──┘         └──► catalogue svc + LLM API
                               (RabbitMQ/Kafka)
```

| Service | Stories |
|---|---|
| identity | 1, 6, 7 |
| catalogue | 3, 4 |
| search | 2 |
| chatbot | 5 |
| user-data | 8–14 |

**Pros:** independent deploys and scaling (e.g. scale only the chatbot). A crashing chatbot doesn't take down search. Each service can use its own language.

**Cons:** for one developer it's 5 services, a gateway, a broker, 4 databases, distributed tracing and N CI pipelines to keep running. Most of the work goes into infrastructure, not features.

**Deployment:** Kubernetes (or docker-compose/ECS for a small setup), CI/CD per service, a managed broker, OpenTelemetry for tracing, centralised logs.

**Painful low-level parts:**
- **Keeping the search index in sync.** *Why:* "write to the catalogue DB, then publish an event" is two operations, and only the first is transactional. A crash in between loses the event, and search stays stale forever. → Transactional outbox + idempotent consumers.
- **Favourites list with recipe titles (story 14).** *Why:* user-data owns the favourites and catalogue owns the titles, so there's no join. → N+1 HTTP calls (slow), a batch endpoint (coupling), or a local copy of titles (needs syncing). Each option has a cost.
- **Logout isn't instant (story 7).** *Why:* services trust the JWT's signature and expiry without asking a central server, so a stolen token works until it expires. → Short-lived access tokens + revocable refresh tokens, or a deny-list.
- **Deleting a calendar or account across services (story 10, GDPR erasure).** *Why:* the data is spread over several DBs with no shared transaction. → A saga or event that every service handles idempotently, plus a check that it finished.
- **Chatbot depends on catalogue at runtime.** *Why:* every tool call is a network hop, so latency and failures add up. → Timeouts, retries and a circuit breaker.

### C. Serverless / BaaS

**Idea:** a static SPA on a CDN. Managed services do the heavy lifting (Supabase or Firebase for auth + DB, a managed search service), and a few functions hold secrets and logic (the chatbot).

```
 SPA (CDN) ──► Supabase Auth (Google)      ┐
     │    ──► Supabase Postgres (RLS)      ├── managed
     │    ──► Algolia/Typesense (search)   ┘
     └──► Edge/Lambda function "chat" ──► LLM API
                       └──► DB (read-only role)
 import script (run locally/CI) ──► Postgres + search index
```

| Component | Stories |
|---|---|
| Auth service | 1, 6, 7 |
| DB + row-level security | 3, 4, 8–14 |
| Search service | 2 |
| `chat` function | 5 |

**Pros:** almost no servers to operate, and it scales to zero. Fastest MVP if you're comfortable with the frontend. Auth comes ready-made.

**Cons:** vendor lock-in. Business logic is split between frontend, security rules and functions. Harder to test locally. Costs are less predictable when traffic spikes.

**Deployment:** CDN (Netlify/Vercel/Cloudflare Pages) + Supabase project (EU region) + functions deployed from CI + migrations through the Supabase CLI.

**Painful low-level parts:**
- **Security rules are the backend.** *Why:* the browser talks to the DB directly, so one loose rule exposes all data. A dangerous rule looks like `using (auth.uid() is not null)` (any signed-in user can read every calendar). The correct one is `using (auth.uid() = user_id)`. Every table needs its own reviewed rule plus tests.
- **LLM streaming through functions.** *Why:* gateways have hard timeouts (AWS API Gateway ~29 s) and some buffer the whole response, so streamed tokens arrive in one block at the end, or the request gets cut off. → Use a platform with streaming support (edge functions, Lambda response streaming) and keep tool loops short.
- **Two copies of the catalogue (DB + search index).** *Why:* there's no transaction across the two vendors, so the import must update both and recover from partial failures.
- **Cold starts.** *Why:* the first request after a quiet period starts a new runtime and adds 0.5–2 s to the already slow chatbot.

## 4. Comparison table and recommendation

| Criterion | A. Modular monolith | B. Microservices | C. Serverless/BaaS |
|---|---|---|---|
| Fit for 1 developer (A1) | ✅ best | ❌ ops work dominates | ✅ good if frontend-strong |
| Time to MVP | ✅ fast (Django batteries) | ❌ slow | ✅ fastest for CRUD |
| Ops effort | ✅ one container + DB | ❌ high | ✅ lowest |
| Independent scaling | ⚠️ whole app | ✅ per service | ✅ per function |
| Fault isolation | ⚠️ shared process | ✅ | ✅ |
| Consistency / joins (stories 12–14, 10) | ✅ ACID, joins | ❌ sagas, no joins | ✅ one Postgres |
| Search (story 2) | ✅ pg_trgm/full-text, no sync | ⚠️ separate index + sync | ⚠️ second vendor + sync |
| LLM chatbot (A3) | ✅ Python ecosystem, async needed | ✅ isolated service | ⚠️ timeouts, cold starts |
| Security model | ✅ server-side checks | ⚠️ distributed auth | ⚠️ RLS rules are the backend |
| GDPR erasure (A4, story 10) | ✅ one transaction | ❌ cross-service saga | ✅ one DB (+ index) |
| Vendor lock-in | ✅ low | ✅ low | ❌ high |
| Cost at small scale | ✅ low, predictable | ❌ highest | ✅ free tier, spiky risk |
| Hardest part | async LLM, module discipline | everything distributed | security rules, LLM streaming |

**Recommendation: A, a modular monolith in Python (Django).** It's the only option with ✅ on all four criteria that matter most here: fit for one developer (A1), the LLM chatbot (A3), consistency/joins and GDPR erasure (A4). C is the runner-up: it has comparable ops effort, but it puts the chatbot on its weakest spot (function timeouts and cold starts) and moves security into DB rules.

**Evolution path:** the **chatbot module is extracted first**, if (a) its load or costs need separate scaling, (b) it needs its own deploy cadence (prompt/model changes), or (c) a second developer joins and owns it. Its module interface `suggest_recipes(diet, message, history) -> [recipe_id]` is already shaped like an HTTP contract. Search moves to a dedicated engine only if pg_trgm becomes too slow or too weak (relevance, synonyms).

## 5. "Simple but seamless"

**What "seamless" means here:** pages load in under 300 ms, a saved favourite is visible immediately (no eventual consistency), there are no random partial failures, the chatbot streams its answer instead of freezing, and deploys don't cause visible downtime.

**Option A has the fewest moving parts**, so the fewest things can fail between the user and the data: one process, one DB, no network hops between modules, and no sync between stores. Concrete measures to make it seamless:
- ASGI + SSE for the chatbot, so its latency doesn't block other pages.
- HTMX for favourites and calendar actions (no full page reloads, no SPA to build).
- Postgres trigram indexes for search (typo tolerance with no extra service).
- Rolling deploys with health checks. Migrations backwards-compatible (expand → migrate → contract).
- A timeout and a friendly fallback for the LLM ("Here are popular vegan recipes" from a plain SQL query).

## 6. When the recommendation is wrong, with example systems

**Choose B (microservices) when** many teams need to deploy independently, parts have very different scale or reliability needs, or the domains are large. **Choose C (serverless/BaaS) when** nobody can or wants to run a backend, the time-to-market is weeks, or traffic is highly spiky or seasonal.

| Example system | Clear choice | Why |
|---|---|---|
| Grocery delivery platform with ~10 teams (catalogue, cart, payments, logistics) | B | Teams need independent deploys. Logistics and payments need separate scaling and fault isolation. |
| Video streaming service | B | Transcoding, recommendations and playback have very different scale profiles. |
| Ride-hailing (matching, pricing, payments) | B | Real-time matching must keep running even when other parts fail. Heavy uneven load. |
| 4-week MVP to test a startup idea | C | Speed matters more than control. Auth, DB and hosting come ready-made. |
| Seasonal campaign site (Black Friday, a music festival) | C | Traffic spikes ×100 for days, then drops to zero. Pay-per-use fits. |
| Conference app, offline-capable mobile app | C | Mostly read-only content + managed sync (Firestore offline). |

**Why RecipeCove is neither:** one developer, one small domain, steady modest traffic, and data that needs joins (favourites, calendar → recipes). Nothing calls for independent deploys or extreme scale (B). The LLM chatbot is the one part that fits serverless poorly (C).

**Rule of thumb:** start with A unless nobody can run a backend (→ C) or there are many teams or extreme, uneven scale (→ B). Extract a part only when it causes concrete pain.

## 7. Team-size sensitivity

| Option | Small team (3–5) | Solo developer (A1) |
|---|---|---|
| A. Monolith | ✅ good. Module ownership per person. | ✅ **best** |
| A + separate chatbot service ("hybrid") | ✅ reasonable if one person owns the AI part and wants Python next to a JS/Java main app | ❌ two deploys, two CI pipelines and an HTTP contract, just to use Python. Write the whole monolith in Python instead. |
| B. Microservices | ⚠️ still heavy | ❌ |
| C. Serverless/BaaS | ✅ if the team is frontend-heavy | ⚠️ OK, but the chatbot sits on its weakest spot |

**Solo-developer advice:** use batteries-included tools to cut work: **Django + django-allauth (Google OIDC) + Django admin (A7) + HTMX + PostgreSQL**, with the LLM SDK called from an async view.

*(In the original Task 1 session, the team size changed from 3–5 to 1 after the decision, which overturned a hybrid decision. Here it was asked up front, A1.)*

## 8. Final decision

**Chosen: A, a modular monolith in Python (Django)** (diagram in section 3A). The user accepted the recommendation from section 4.

**Key design decisions:**
- **Modules:** identity, profile, catalogue, search, chatbot, favourites, calendar (stories mapped in section 3A). Each module exposes a `services.py` API. Other modules may only import that API, and an import-linter contract in CI enforces it.
- **Frontend:** server-rendered Django templates + HTMX. No SPA.
- **Chatbot:** an async (ASGI) view that streams with SSE. Tool calling against a read-only `search_recipes` tool, with grounding rules from section 9. Module interface: `suggest_recipes(diet, message, history) -> [recipe_id]`. Falls back to plain SQL suggestions.
- **Data:** one PostgreSQL in an EU region. pg_trgm for search. The catalogue is imported with idempotent upserts. Calendar events use a `DATE` column.
- **Auth:** Google OIDC via django-allauth, keyed on `sub`. Server-side sessions, so logout (story 7) takes effect immediately.
- **Deployment:** one container on an EU PaaS + managed Postgres. GitHub Actions: tests → build → rolling deploy with a health check.

**Trade-offs accepted vs the runner-up (C, serverless/BaaS):**

| We give up | We get |
|---|---|
| Scale-to-zero and near-zero ops | No function timeouts or cold starts for the chatbot, the central feature |
| Ready-made auth/DB | Security checks in server code instead of per-table RLS rules |
| Per-function scaling and fault isolation | One process to debug, ACID joins, one-transaction erasure |

**Remaining painful parts:** LLM latency (async + SSE), module discipline (linter), ingredient normalization and diet-tag quality on import (section 3A), LLM cost and abuse (section 9).

**Future extraction path:** the chatbot module goes first. Triggers: separate scaling or cost control, its own deploy cadence, or a second developer who owns it. `suggest_recipes(...)` becomes `POST /suggest` with the same input/output (recipe IDs). Search moves to a dedicated engine only if pg_trgm relevance or speed falls short.

## 9. Deep dive: grounding the LLM chatbot

**The problem:** a plain LLM invents recipes that don't exist in the catalogue, or suggests "vegan" dishes with honey or eggs. Story 5 is only useful if every suggestion links to a real recipe page (story 3) that really fits the diet.

**Three levels:**
1. **Prompt only** ("only suggest vegan recipes"): the model still invents and still ignores constraints. ❌
2. **Retrieve, then generate:** SQL selects candidate recipes for the diet, and the LLM picks and explains among them. Safe, but less conversational.
3. **Tool calling:** the LLM calls a narrow, read-only `search_recipes` tool with structured parameters. SQL enforces the hard constraints, and the LLM writes the reply around the returned IDs. ✅ Recommended.

```
user msg ─► chatbot module ─► LLM (with tool schema)
                 ▲                 │ tool_call: search_recipes(diet=vegan, include=[...])
                 │                 ▼
                 │        catalogue.services.search(...)  ── SQL with WHERE diet = 'vegan'
                 │                 │ returns [{id, title, diets}]  (IDs, not free text)
                 │                 ▼
                 └── validate: every recipe_id in the reply exists AND matches the diet
                        │ OK → render cards from DB data (title/image come from DB, not LLM)
                        └ fail → drop item / fallback list
```

**Rules:**
- Hard constraints (diet, excluded ingredients) are enforced in **SQL**, never trusted to the model.
- The tool returns **IDs + minimal fields**. Recipe cards are rendered from the DB, so the LLM can't change a title or an ingredient list.
- **Validate the output:** any ID the model mentions that the tool didn't return gets removed.
- The tool is **narrow and read-only**, with **enum parameters** (`diet ∈ {vegan, vegetarian, gluten_free, keto, ...}`). It can't reach user data.
- **Honest empty results:** if SQL finds nothing, the model says so instead of making something up.

**Tool schema sketch:**
```json
{
  "name": "search_recipes",
  "description": "Find recipes in the RecipeCove catalogue. Only these recipes may be suggested.",
  "input_schema": {
    "type": "object",
    "properties": {
      "diet": {"type": "string", "enum": ["vegan", "vegetarian", "gluten_free", "keto", "dairy_free"]},
      "include_ingredients": {"type": "array", "items": {"type": "string"}},
      "exclude_ingredients": {"type": "array", "items": {"type": "string"}},
      "max_prep_minutes": {"type": "integer"},
      "limit": {"type": "integer", "maximum": 10}
    },
    "required": ["diet"]
  }
}
```

**Painful parts:**
- **Tag quality:** grounding is only as good as the `recipe_diet` tags (see the diet-tags item in section 3A). A wrong tag produces a confidently wrong answer.
- **Synonyms:** "aubergine" vs "eggplant", "plant-based" vs vegan. Map them in the tool, not in the prompt.
- **Latency:** each tool loop is another LLM round trip. Cap it at 2 tool calls and stream the final text.
- **Conversation state:** keep the last N messages server-side with a short retention period (GDPR, A4). Don't send the user's profile to the LLM.
- **Cost and abuse:** rate limits per user/IP, a max token count, and visitors (story 5 is for visitors) get a lower quota.
- **Evaluation:** a fixed set of prompts with *property* checks (every returned recipe exists and matches the diet), not exact-text checks, run in CI.
- **Fallback:** if the LLM is down or times out, show SQL results for the selected diet. Story 5 still works, just without the chat.

## 10. Discussion log
1. User started the rerun with the skill. Assistant read the spec and summarized it (section 1), then asked the deciding assumptions in one question set: team, data source, chatbot, scale (section 2, A1–A4).
2. User answered: solo developer, imported catalogue, LLM grounded in the catalogue, small EU scale with GDPR. Assistant added A5–A9 and presented the three architectures (section 3), the comparison and recommendation (section 4), and covered the usual follow-ups proactively: "simple but seamless" (section 5), when the choice is wrong (section 6), team size (section 7) and the chatbot deep dive (section 9). The decision is waiting for the user (section 8).
3. User asked what comes next. Assistant explained the remaining steps (decision → ADR → transcript → comparison report). No content changes.
4. User chose A ("go with A and write the ADR"). Assistant recorded the decision (section 8) and wrote the ADR (see `../Task_2/notes.md`).
5. User asked to check the whole of Task 3 for mistakes. Assistant reworded one overclaiming sentence in section 4 (the reason A is recommended), so that it states only what the comparison table shows.
