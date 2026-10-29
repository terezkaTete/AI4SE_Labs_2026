# Week 05 – Task 1: Architecture discussion for RecipeCove

Notes from a discussion with a coding assistant about possible architectures for the RecipeCove system. They are organized by topic, not as a verbatim transcript. Section 10 lists the questions in the order they were actually asked.

**Source requirements:** `Week_05_Designing/Tasks/data/RecipeCove.txt`

**Contents**
1. Requirements summary
2. Assumptions
3. Three candidate architectures (A, B, C)
4. Comparison
5. Which one for a "simple but seamless" app?
6. When A is not the right choice (with examples for B and C)
7. Team size: what changes with only one developer
8. Final decision: a single Python (Django) modular monolith
9. Deep dive: grounding the chatbot
10. Discussion log

---

## 1. Requirements summary

**What it is:** a web app for discovering, inspecting and bookmarking recipes, plus information about ingredients. The central feature is *discovery*, through a search bar and a diet-aware chatbot that suggests recipes.

**Actors:** Visitor (anonymous), Registered user.

| Area | User stories | Notes |
|---|---|---|
| Auth | 1 register with Google, 6 login, 7 logout | Only an external identity provider (Google). No local passwords. |
| Recipe discovery | 2 search by name, 5 suggestions for a diet | Story 5 is the chatbot. Visitors can use it too. |
| Recipe / ingredient info | 3 recipe detail, 4 ingredient detail | "Exhaustive information" means we need a rich data source. |
| Profile | 8 view profile | Basic info, mostly from the Google account. |
| Favorites | 12 add, 13 remove, 14 list | Simple many-to-many link between users and recipes. |
| Calendar | 9 create, 10 delete, 11 add event | "Application-created calendar": an internal calendar or Google Calendar? |

**Open questions found in the requirements**
- Where do recipe and ingredient data come from (own DB or a third-party API)?
- Is the chatbot rule-based or LLM-based? If LLM, how do we stop it from inventing recipes?
- Is the calendar internal, or synchronized with Google Calendar?
- There are no admin / content-management stories. Who maintains the recipes?
- There are no non-functional requirements (scale, availability, privacy).
- Story 7's rationale is oddly worded. We read it as "end my session so my data stays safe".

---

## 2. Assumptions

The user asked the assistant to make reasonable assumptions instead of answering the open questions. A5 was later changed by the user (see section 7).

| # | Topic | Assumption |
|---|---|---|
| A1 | Recipe data | A scheduled job **imports** recipes and ingredients from a third-party API (e.g. Spoonacular / TheMealDB) into **our own database**. The app does not call the API on every page view (rate limits, licensing, latency, and we need to search our own data). |
| A2 | Chatbot | **LLM-based, grounded in our catalogue**: it may only suggest recipes that exist in our DB (section 9). Visitors can use it, so it needs rate limiting. |
| A3 | Calendar | An **internal** calendar, one per user, with events "cook recipe X on date Y". No Google Calendar sync; an iCal export could come later. |
| A4 | Scale | About 10k registered users, at most a few hundred at once, mostly reading. |
| A5 | Team / time | Originally 3–5 developers. **Revised: 1 developer**, about one semester. |
| A6 | Privacy | EU users, so GDPR applies. Deleting a calendar is a hard delete. |
| A7 | Recipe management | No admin stories. Content comes from the import job (plus an admin UI if the framework provides one). |
| A8 | Auth | Google sign-in via OpenID Connect. Users are identified by Google's stable `sub` claim, not by email. |

---

## 3. Three candidate architectures

### A — Modular monolith

**Idea:** one backend application split into strictly separated internal modules. It runs as one process, uses one database, and is deployed as one unit. Modules talk to each other only through their public interfaces.

```
 Browser
    │ HTTPS (pages / JSON, SSE for chat streaming)
 ┌──▼───────────────────────────────────────────────┐
 │ Backend app                                       │
 │  Identity · Catalog · Search · Suggestion(chat) ──┼──► LLM API
 │  Profile · Favorites · Calendar                   │
 │  Import job (scheduled) ──────────────────────────┼──► External recipe API
 └──┬───────────────────────────────────────────────┘
    ▼
 PostgreSQL (relational data + full-text search)
```

- **Modules and user stories:** Identity (1, 6, 7), Search (2), Catalog (3, 4), Suggestion (5), Profile (8), Calendar (9–11), Favorites (12–14).
- **Data model sketch:** `user(google_sub, email, name)`, `recipe`, `ingredient`, `recipe_ingredient(qty, unit)`, `diet_tag`, `favorite(user, recipe)`, `calendar(user)`, `calendar_event(calendar, recipe, date, note)`.
- **Pros:**
  - The simplest option: one codebase, one deploy, easy to debug.
  - ACID transactions. Deleting a calendar and its events happens in one transaction.
  - The favorites list with recipe titles is a single SQL join.
  - Cheap to run.
  - Modules can be extracted into services later.
- **Cons:**
  - Everything scales together.
  - It is one failure domain.
  - Module boundaries only hold if they are enforced (with tooling or discipline).
  - The whole app uses one tech stack.
- **Deployment:** one container + managed Postgres on a PaaS (or a single VM), with a CDN for static assets.
- **Painful parts:**
  - **Google OIDC done correctly.** The login redirect needs a `state` value (against CSRF) and PKCE (against stolen authorization codes). The ID token's signature must be validated against Google's published keys, with a nonce checked to prevent replay. Users must be keyed on Google's stable `sub`, because a user's email address can change.
  - **Search quality in Postgres.** Plain `ILIKE '%term%'` can't rank results or use an index. You need a `tsvector` column with a GIN index for ranked full-text search, plus `pg_trgm` for typo tolerance ("spagetti"), and the relevance still needs tuning.
  - **LLM calls take seconds.** In a thread-per-request server, every waiting chat request holds a worker. A handful of chat users could make normal recipe pages queue up. The chat has to stream (SSE) from async code or a separate, bounded worker pool.
  - Grounding the chatbot (section 9).
  - **Normalizing imported ingredients.** The external API gives free text like "2 cloves garlic, minced". That has to become quantity + unit + a canonical ingredient, or ingredient pages and diet filters won't match. Re-imports must upsert by external ID so they don't create duplicates.
  - **Calendar dates.** Store them as local dates, not UTC timestamps. Otherwise "cook on Friday" can shift to Thursday for a user in another time zone.

### B — Microservices

**Idea:** independently deployable services, each with its own data store. They sit behind an API gateway, call each other over REST/gRPC for queries, and use a message broker to propagate changes.

```
 Browser ─► API Gateway (JWT validation, routing, rate limiting)
              │
   ┌──────────┼───────────┬────────────┬────────────┬───────────┐
 Identity  Catalog      Search      Suggestion    UserData    Calendar
           (Postgres)   (Elastic/   (Python,      (profile,   (Postgres)
                        OpenSearch)  LLM)          favorites)
   └──────────┴───────────┴────────────┴────────────┴───────────┘
          Message broker: RecipeUpdated, UserDeleted, ...
```

- **Pros:**
  - Search and the chatbot can scale independently.
  - Fault isolation: if the chatbot is down, favorites and the calendar still work.
  - Each service can use its own stack: Python for the AI, a real search engine for search.
  - Teams can deploy independently.
- **Cons:**
  - Far too much for 14 user stories and a small team.
  - Data is distributed. The favorites list needs recipe titles from Catalog, which means extra network calls or duplicated data.
  - Eventual consistency.
  - Every network hop is a new place where things can fail.
  - Testing needs contract tests and heavy end-to-end environments.
- **Deployment:** Kubernetes (or at least docker-compose / ECS), a CI/CD pipeline per service, centralized logging and distributed tracing (OpenTelemetry).
- **Painful parts:**
  - **Keeping search in sync.** The naive "write to the DB, then publish an event" is two separate operations, and only the DB write is transactional. If the service crashes between them, the recipe is saved but the event is lost, and the search index never learns about it. The fix is the **transactional outbox**: write the event into an outbox table in the *same* DB transaction, and have a relay publish it. Because the relay can publish an event twice, consumers must be idempotent.
  - **Showing favorites with recipe titles.** UserData owns favorites, but Catalog owns titles and images. There are three options, all with a cost:
    - (a) one call per favorite to Catalog: the N+1 problem, slow;
    - (b) a batch "get recipes by IDs" endpoint: one extra hop, and the page breaks if Catalog is down;
    - (c) UserData keeps a copy of title and image, updated from Catalog events: fast, but the copy can be stale and needs more sync code.
  - **GDPR deletion becomes a saga.** A `UserDeleted` event must be handled by UserData, Calendar, Identity and Suggestion. There is no cross-service transaction, so you need to track that each service actually completed it and retry those that didn't.
  - **Logout with stateless JWTs isn't instant.** Services validate a JWT by its signature and expiry alone, without asking a central server. A token stolen or still held after logout stays valid until it expires. You either keep access tokens very short (minutes) and revoke the refresh token, or maintain a deny-list, which reintroduces central state.
  - Local development means running about 6 services, several databases, Elasticsearch and a broker.
  - Debugging needs distributed tracing, and APIs must be versioned so one service can change without breaking the others.

### C — Serverless / Backend-as-a-Service

**Idea:** write almost no server code. A static frontend on a CDN talks directly to managed services. Small cloud functions handle the parts that need secrets or server logic.

```
 Static SPA on CDN
   ├─► Firebase Auth / Cognito (Google login)
   ├─► Firestore (users, favorites, calendars, recipes) guarded by security rules
   ├─► Algolia / Typesense (search, synced by a trigger function)
   └─► Cloud Function: chatbot ──► LLM API
 Scheduled Function: import job ──► External recipe API
```

- **Pros:**
  - Almost no operations work.
  - Pay-per-use, so it is nearly free at small scale.
  - The fastest way to an MVP; Google login is almost free.
  - Scales automatically.
- **Cons:**
  - Vendor lock-in.
  - NoSQL means no joins. Recipe data copied into favorites goes stale, and filters are limited.
  - Logic is scattered across the client, security rules and functions.
  - Costs are hard to predict.
  - Cold starts.
- **Deployment:** static hosting/CDN (Firebase Hosting / Vercel / S3 + CloudFront) + managed services + functions. There are no servers, but configuration (rules, indexes, function settings) is spread across the vendor's console and config files.
- **Painful parts:**
  - **Security rules effectively *are* the backend.** The browser talks to the DB directly, so rules are the only thing stopping one user from reading another's data. A rule like `allow read, write: if request.auth != null;` on `users/{uid}` looks harmless, but it lets *any* logged-in user read and change *every* user's favorites and calendar. The correct rule checks `request.auth.uid == uid`. Rules need their own tests in the emulator.
  - **Function timeouts make LLM streaming difficult.** An LLM answer can take 10–30+ seconds. AWS API Gateway, for example, cuts requests off at about 29 s, and some setups buffer the whole response before sending it, which kills streaming. You need native response streaming (Lambda function URLs, Cloud Functions v2, Vercel streaming). Cold starts add delay to the first message.
  - **Protecting the anonymous chatbot from abuse.** There's no gateway of your own for per-IP rate limiting. You rely on App Check / reCAPTCHA plus counters in the DB, while every LLM call costs money.
  - **Keeping the search index in sync.** Firestore has no full-text search, so trigger functions copy recipes into Algolia. Triggers are "at least once", so indexing must be idempotent, and the initial bulk import must be batched to stay within rate limits.
  - Deleting a calendar doesn't delete its `events` sub-collection, so a function or recursive delete is needed (and that matters for GDPR, story 10).
  - Local development depends on emulators, which don't behave exactly like production.

---

## 4. Comparison

| Criterion | A: Modular monolith | B: Microservices | C: Serverless/BaaS |
|---|---|---|---|
| Fit for 14 stories / small team | ★★★ | ★ | ★★★ |
| Time to MVP | ★★ | ★ | ★★★ |
| Operational effort | Low–medium | Very high | Very low |
| Independent scaling | ✗ | ✓✓ | ✓ (automatic) |
| Fault isolation (chatbot down) | Weak (mitigated by fallbacks) | Strong | Medium |
| Data consistency / joins | Strong (ACID, SQL) | Eventual, distributed | Weak (NoSQL, copied data) |
| Search quality | OK (Postgres FTS) | Best (Elasticsearch) | Good (Algolia/Typesense) |
| Vendor lock-in | Low | Low–medium | High |
| Cost at small scale | Low, fixed | High | Very low, variable |
| Hardest part | Search tuning, LLM streaming | Data sync, sagas, ops | Security rules, NoSQL modelling |

---

## 5. Which one for a "simple but seamless" app?

**Question:** the app should not be very complicated, but it should work seamlessly. Which architecture?

**Answer: A.** "Seamless" here means:
- pages load fast,
- actions show up immediately,
- there are no random failures,
- the chatbot responds smoothly,
- deploys cause no downtime.

**Why A fits that best:**
- **Fewest moving parts:** one app and one DB, so the fewest places where things can fail.
- **Immediate consistency:** a new favorite appears at once, with the correct title (one transaction and a SQL join). In B and C, data is synced in the background.
- **Predictable latency:** no cold starts (C) and no chains of network calls (B).
- **Easy to debug:** one log and one stack trace, so problems get fixed faster.

C is simple to *start* with, but its rough edges are the kind users notice: cold starts, stale copies of data, and surprise cost or quota errors.

**What makes A actually run smoothly:**
- Managed hosting + managed Postgres with backups.
- Zero-downtime deploys.
- A CDN and HTTP caching for recipe pages and images.
- A streaming chatbot with a fallback.
- Optimistic UI updates for favorites and calendar events.
- Search-as-you-type on Postgres FTS.
- Error tracking (Sentry) + an uptime check.

---

## 6. When A is not the right choice

A is the best choice *under assumptions A1–A8*. If those change, so can the answer.

### B (microservices) is the clear choice when there are many teams, clearly separable business domains, and very different load or compliance needs per domain
| Example | Why B |
|---|---|
| RecipeCove grown into a grocery / meal-kit platform (recipes + ingredient shopping + inventory + payments + delivery + ML recommendations, ~10 teams) | Separate domains with separate teams that release independently. Payments must be isolated (PCI-DSS). Real-time inventory and delivery load is very different from recipe browsing. |
| Video streaming platform | Catalogue, playback, billing and recommendations scale very differently, and playback must survive a billing outage. |
| Ride-hailing / food delivery | Location tracking, matching, pricing and payments each have extreme, different loads and their own teams. |
| Bank core system | Regulators require strict separation and auditing of sensitive data. |

### C (serverless) is the clear choice when the team is small or frontend-only, the data is simple, and traffic is spiky or very low
| Example | Why C |
|---|---|
| RecipeCove as a 4-week MVP / investor demo built by frontend developers | Speed matters more than maintainability; login, hosting and data are mostly configuration. |
| Holiday recipe campaign site for a food brand | A huge spike at Christmas and nothing the rest of the year. It scales automatically and costs nothing when idle. |
| Conference or wedding app | Used a few days a year, with simple data. |
| Offline meal planner / shopping-list mobile app | Firestore's offline sync solves a hard problem out of the box. |
| Event-driven background jobs (resizing uploaded photos, nightly imports) | "Run a function when X happens" is exactly what functions are for. |

### Other changes that would weaken A
- Global users with strict latency requirements (multi-region writes are hard with one Postgres).
- Offline-first mobile apps.
- A team without the discipline to keep module boundaries.

### Why RecipeCove as specified is neither B nor C
- **Not B:** one small team and closely related features, so B's benefits never pay off.
- **Not C:** steady usage and relational data (favorites ↔ recipes ↔ ingredients ↔ diets). The "seamless" goal also rules out cold starts and stale copies of data.

### The likely evolution: A plus one extracted service
If any single part outgrows the monolith, it will be the chatbot: it is slow, external, costly, and has different technology needs. A well-modularized A lets us extract only that module later.

**Rule of thumb:** start with A, unless nobody can run a backend (→ C), or there are many teams or extreme, uneven scale (→ B). Extract services only when there is concrete pain.

---

## 7. Team size: what changes with only one developer

The user first considered extracting the chatbot into a separate Python service, then challenged assumption A5: **what if there is only 1 developer?**

| Option | 3–5 developers | 1 developer |
|---|---|---|
| A — modular monolith | Recommended | **Still recommended**: one codebase, one deploy, one DB fits in one head. |
| A + separate Python chatbot service | Good | **Not worth it (yet)**: two codebases, two CI pipelines, a streaming proxy chain and contract tests for one person. |
| B — microservices | Overkill | Absurd: all operations, no features. |
| C — serverless | Alternative | **Strong alternative**: the least operations work, but the same drawbacks as before. |

**The key idea:** the only reason for a separate service was to use Python for the AI part. A solo developer gets that **without a second service** by writing the *whole monolith* in Python and making the chatbot one of its modules.

**What gets harder with one developer, whatever the architecture:**
- The bus factor is 1, so documentation, tests and boring, standard technology matter.
- The chatbot is the biggest piece of work, so build it last.
- Managed hosting is a must.

**When a solo developer should choose C instead:** they have no backend experience, the project is a short-lived demo, or traffic is tiny and spiky.

---

## 8. Final decision: a single Python (Django) modular monolith

**Decided by the user:** 1 developer, so **Architecture A as one Django application**, with the chatbot as an internal module. This replaces the user's earlier choice of a separate chatbot service, which is kept in 8.4 as the future extraction path.

### 8.1 Architecture
```
 Browser
   │  HTTPS: server-rendered HTML + HTMX, SSE for chat streaming
 ┌─▼──────────────────────────────────────────────────────────────┐
 │ Django app (ASGI, e.g. uvicorn): one codebase, one deploy      │
 │  accounts     Google login (django-allauth), profile  [1,6,7,8]│
 │  catalog      recipes, ingredients, diet tags, search   [2,3,4]│
 │               → public service: search_recipes(filters)        │
 │  suggestions  chatbot: prompt, tool loop, grounding,     [5]   │
 │               rate limit, fallback ────────────────────────────┼──► LLM API
 │  favorites    add / remove / list                    [12,13,14]│
 │  calendars    calendar + events                       [9,10,11]│
 │  importer     management command (platform cron) ──────────────┼──► External recipe API
 │  Django admin (fixing recipes / ingredients)                   │
 └─┬──────────────────────────────────────────────────────────────┘
   ▼
 Managed PostgreSQL (full-text search + pg_trgm; pgvector optional later)
```

### 8.2 Key design decisions
1. **One Django project, with one Django app per module.**
2. **Enforced module boundaries:**
   - Modules call each other only through each module's `services.py`. For example, `suggestions` calls `catalog.services.search_recipes()` and never touches `catalog.models` directly.
   - `import-linter` checks this rule in CI.
3. **Chatbot interface:** `suggest(messages, user_diet=None)` returns a stream of text followed by the `recipe_ids`. Today it is a Python function; if the chatbot is extracted, it becomes the HTTP contract (8.4).
4. **Grounding:** the LLM's search tool calls `catalog.services.search_recipes` in-process. Returned IDs are validated, and recipe cards are rendered from the DB (section 9).
5. **Frontend:** Django templates + HTMX (favorite toggle, search-as-you-type, forms, streamed chat). No separate SPA or JS build.
6. **Async where it matters:** the app runs under ASGI, and the chat view is an `async` streaming view. A slow LLM call therefore doesn't block workers serving recipe pages; the other views stay sync.
7. **Isolation inside the process:** LLM calls have a timeout and a circuit breaker, with a fallback to plain DB suggestions for the chosen diet. There are per-session/IP rate limits and a daily cost cap. An LLM outage affects only story 5.
8. **Data:** one Postgres. Deleting a calendar deletes its events in the same transaction (`on_delete=CASCADE`).
9. **Login:** `django-allauth` handles the Google OIDC details (state, nonce, token validation).
10. **Deployment:** one container on a managed PaaS (Render / Railway / Fly.io) + managed Postgres with backups. One instance with zero-downtime deploys. The import runs as a cron job. Sentry + an uptime check.

### 8.3 Trade-offs accepted
| Given up (vs. a separate chatbot service) | Why it's acceptable for 1 developer |
|---|---|
| Process-level fault isolation | Timeouts, the circuit breaker and the fallback cover the realistic failure (a slow or unavailable LLM). |
| Independent chatbot deploys | Deploys are one command and cause no downtime. |
| Independent scaling | One instance handles ~10k users, and the LLM provider does the heavy compute. |

**Gained:** one language, one codebase, one CI pipeline, no proxy chain for streaming, no contract drift, no service-to-service auth, and simple local development.

**Remaining painful parts:**
- ASGI configuration, and making sure the platform doesn't buffer SSE.
- Cancelling the LLM call when the user disconnects.
- Tuning search relevance.
- Normalizing imported data.
- Maintaining the chatbot evaluation set.

### 8.4 Future extraction path
Extract `suggestions` into its own Python service (e.g. FastAPI) **only when a concrete need appears**: the team grows, the chatbot needs its own scaling or heavy ML, or chatbot crashes and deploys start hurting the main site.

How it would work:
- **Entry point:** the browser still talks only to the main app. Its chat view becomes a thin streaming proxy that handles the session, rate limit, cost cap and re-validation of IDs.
- **Contracts:** `suggest(...)` becomes `POST /v1/chat` (SSE), and `catalog.services.search_recipes` becomes `GET /v1/internal/recipes/search`.
- **Security:** private network + a service token. The chatbot service stays stateless and has no access to the DB.
- **New costs:** streaming through two hops (no buffering; cancel on disconnect), two CI pipelines, correlation IDs in the logs, and contract tests against a shared OpenAPI schema.

---

## 9. Deep dive: grounding the chatbot (story 5)

### The problem
An LLM knows recipes "in general", not *our* catalogue. Without grounding it will:
- **invent recipes** that we don't have, so there is no detail page, no ingredient page, and nothing to add to favorites or the calendar;
- **get diets wrong**, e.g. a "vegan" dish with honey;
- **make up details** such as cooking times or links.

**Grounding** means every suggestion comes from our data and can be checked against it.

### Three levels of grounding
1. **Prompt only** ("only suggest our recipes"): doesn't work, because the model can't see the catalogue.
2. **Retrieve, then generate:** the backend searches first and puts the candidates in the prompt. Robust, but the backend has to guess the filters from the raw message.
3. **Tool calling (chosen):** the LLM interprets the conversation and calls `search_recipes` with structured parameters. A normal SQL query runs, and the LLM answers using only the returned rows. *The LLM understands the user; the database decides what exists.*

### Flow in the final design
```
User: "Something vegan, quick, no mushrooms – I have chickpeas"
 → suggestions module sends history + tool definition to the LLM
 → LLM calls search_recipes(diet="vegan", include=["chickpea"], exclude=["mushroom"], max_time_min=30)
 → catalog.services.search_recipes(...) runs SQL in-process → [{id: 412, "Chickpea curry", 25 min}, ...]
 → LLM returns { message: "...", recipe_ids: [412, 977] }
 → IDs validated → HTMX streams the text, then renders recipe cards from OUR DB
```

### Rules
- **Hard constraints are enforced in SQL, not by the LLM.** "Vegan" becomes a SQL filter.
- **The LLM returns IDs, not recipe data.** Cards come from the DB, so a hallucinated recipe can never appear as a card.
- **Output is validated:** IDs that weren't in the tool result are dropped. If nothing is left, retry once or fall back.
- **The tool is narrow and read-only:** it only reads the public catalogue. No user data, no writes, no free-form SQL. This limits the damage a prompt injection can do.
- **The diet parameter is an enum** of our supported tags, so the model cannot invent a diet.
- **Empty results are reported honestly**, with a suggestion to relax a constraint, never filled with invented recipes.

### Tool definition (sketch)
```json
{
  "name": "search_recipes",
  "description": "Search the RecipeCove catalogue. Only these results may be suggested.",
  "input_schema": {
    "type": "object",
    "properties": {
      "diet":         { "type": "string", "enum": ["vegan","vegetarian","gluten_free","keto","paleo","dairy_free"] },
      "include":      { "type": "array", "items": { "type": "string" } },
      "exclude":      { "type": "array", "items": { "type": "string" } },
      "max_time_min": { "type": "integer" },
      "text":         { "type": "string", "description": "free text / mood, e.g. 'warm comfort food'" },
      "limit":        { "type": "integer", "maximum": 10 }
    }
  }
}
```
Vague requests ("cozy rainy-day food") can later use embeddings with pgvector in the same Postgres, combined with the hard SQL filters.

### Painful parts
- **Tag quality:** grounding guarantees "tagged vegan", not "is vegan". Tags from the import must be checked against ingredients, diet definitions must be fixed, and allergies need a disclaimer.
- **Ingredient synonyms:** "chickpeas" / "garbanzo beans" need normalization or fuzzy matching.
- **Latency:** two LLM round-trips + a query take about 2–5 s. Stream the text, show "searching recipes…" during the tool call, and use a fast model.
- **Conversation state:** keep the last N turns per session to limit token cost.
- **Cost and abuse:** rate limits per visitor, a max-tokens cap, a daily budget cap, and possibly requiring login after a few messages.
- **Testing:** an evaluation set of ~50 prompts (including tricky and injection prompts). Assert properties, not exact text: every ID exists and matches the filters, and no recipe name appears in the reply unless it was in the results. Run it in CI whenever the prompt or model changes.
- **Fallback:** if the LLM fails, show DB results for the diet selected in a dropdown, so story 5 still works.

---

## 10. Discussion log (chronological)

1. The assistant read the requirements, summarized them, and listed the open questions. → sections 1, 2
2. The user asked for reasonable assumptions and three proposals. The assistant proposed A (modular monolith), B (microservices) and C (serverless) with pros, cons and painful parts, and recommended A. → sections 2–4
3. "Not complicated, but seamless — which one?" → A. → section 5
4. The user asked for more detail on chatbot grounding. → section 9
5. "Is there any case where A is not right?" → yes, with the conditions listed. → section 6
6. The user decided to keep A and move the Python chatbot into its own service. *(Later replaced, see item 9.)* → section 8.4
7. The user asked for concrete examples where B or C is the clear choice. → section 6
8. The user challenged A5: "What if there is only 1 developer?" → A still wins, but the separate service isn't worth it; use one Python monolith. → section 7
9. **Final decision:** a single Python (Django) modular monolith with the chatbot as an internal module. → section 8
10. The user asked to reorganize the notes so they read as one coherent document (this version).
