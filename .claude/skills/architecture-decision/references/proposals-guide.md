# Phase 1 guide: from requirements to a decision

## 1. Requirements summary
- What the system is, in 2–3 sentences. What is its central feature?
- Actors.
- A table: functional area | story numbers | notes (ambiguities, implied needs).
- Open questions that change the architecture:
  - data source (own DB vs third-party API, imported vs live),
  - special components (AI/LLM, real-time, payments, offline),
  - external integrations (e.g. "app calendar" vs Google Calendar),
  - missing stories (admin? account deletion?),
  - missing non-functional requirements (scale, availability, privacy),
  - oddly worded stories, with how you interpret them.

## 2. Assumptions
Ask with **one** `AskUserQuestion` call (up to 4 questions). Recommended ones first:
1. **Team size and skills** (solo / 2–5 / many teams; backend vs frontend experience). *This flips the decision most often.*
2. **Data source** for the core domain data.
3. **Scale and traffic shape** (steady vs spiky; users and concurrency).
4. **The riskiest special component** (e.g. "LLM chatbot grounded in our data?") and **compliance** (EU → GDPR).

If the user says "assume": write a numbered table (A1…A8) with topic | assumption | short reason. Then add a line: **"The recommendation is most sensitive to A_x (team size) and A_y; if those change, revisit."**

## 3. Three architectures

Default set (they differ along the axes that matter to students):
- **A. Modular monolith:** one deployable, strict internal modules, one DB.
- **B. Microservices:** a service per domain, an API gateway, a broker, a DB per service.
- **C. Serverless / BaaS:** a static SPA, managed auth/DB/search, functions for secrets and logic.

Swap one in when the requirements call for it (event-driven / CQRS, offline-first sync, real-time pub/sub, hexagonal as an internal style).

**Per architecture, always include:**
- **Idea** (1–2 sentences).
- **ASCII diagram**: components, data stores, external systems, protocols.
- **Mapping of modules/services to stories.**
- **Data model sketch** (at least for the first architecture).
- **Pros / cons.**
- **Deployment** (e.g. "one container + managed Postgres on a PaaS", "Kubernetes or docker-compose/ECS, CI/CD per service, OpenTelemetry", "CDN + managed services + functions").
- **Painful low-level parts, each with a one-sentence *why*.** Examples of the expected depth:
  - *Search sync in microservices:* "write to DB, then publish event" is two operations, and only one is transactional. A crash in between loses the event → transactional outbox + idempotent consumers.
  - *Showing a list of X with data owned by another service:* N+1 calls vs batch endpoint vs local copy; each has a cost.
  - *JWT logout isn't instant:* services trust signature + expiry without a central check → short-lived tokens + refresh revocation, or a deny-list.
  - *BaaS security rules are the backend:* show a concrete dangerous rule (`allow read, write: if request.auth != null;`) and the correct one (`request.auth.uid == uid`).
  - *Serverless LLM streaming:* gateway timeouts (e.g. AWS API Gateway ~29 s) and response buffering.
  - *Monolith + slow external calls:* thread-per-request workers get held for seconds → async/SSE or a bounded pool.
  - *OIDC done right:* state (CSRF), PKCE, nonce, ID token validation, key on `sub` not email.
  - *Imported free-text data:* normalization ("2 cloves garlic, minced"), idempotent upserts.
  - *Dates:* store local dates for "day" events, not UTC timestamps.

## 4. Comparison and recommendation
- Table: criteria (fit for scope/team, time to MVP, ops effort, independent scaling, fault isolation, consistency/joins, search, lock-in, cost, hardest part) × A/B/C.
- Recommendation + **evolution path** (which component would be extracted first, and the triggers for doing it).

## 5. Follow-ups to cover proactively
- **"Simple but seamless":** define seamless (fast pages, immediate consistency, no random failures, smooth special component, zero-downtime deploys), then explain which option has the fewest moving parts and why. List concrete measures that make it seamless.
- **"When is the recommendation wrong?":**
  - Conditions per alternative.
  - **Concrete example systems** in a table, e.g. B for a grocery platform with ~10 teams, video streaming, ride-hailing or bank core systems; C for a 4-week MVP, a seasonal campaign site, a conference app, an offline mobile app or event-driven jobs.
  - **Why this system is neither.**
  - Rule of thumb: start with A unless nobody can run a backend (→ C) or there are many teams or extreme, uneven scale (→ B). Extract only on concrete pain.
- **Team size sensitivity:** a table of options × (small team vs solo). For a solo developer, a "hybrid" with a separate service usually isn't worth it. If the reason for a separate service is a language/ecosystem (e.g. Python for AI), **write the whole monolith in that language** instead. Suggest batteries-included frameworks (e.g. Django + django-allauth + HTMX + admin) to cut work.
- **Deep dive into the riskiest component**, e.g. LLM grounding:
  - The problem (invented items, wrong constraints).
  - Three levels: prompt-only, retrieve-then-generate, tool calling.
  - Flow diagram.
  - Rules: hard constraints in SQL, return IDs not data, validate output, narrow read-only tool, enum parameters, honest empty results.
  - Tool schema sketch.
  - Painful parts: tag quality, synonyms, latency, conversation state, cost and abuse, property-based evaluation set, fallback.

## 6. Decision
Record:
- the chosen architecture, with a diagram;
- key design decisions (module boundaries and how they are enforced, frontend approach, isolation of the risky component, data, auth, deployment);
- trade-offs accepted vs the runner-up (table);
- remaining painful parts;
- **future extraction path** (triggers + how the module interface becomes an HTTP contract).
