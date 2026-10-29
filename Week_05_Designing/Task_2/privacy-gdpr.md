# RecipeCove — Privacy and GDPR details

Companion to `ADR-001-recipecove-architecture.md`. The ADR keeps only the GDPR points that follow from the architecture decision. This file holds the full analysis.

The architecture does not make RecipeCove GDPR-compliant by itself. Compliance also needs organizational measures (privacy policy, records of processing, contracts), which are out of scope for this ADR. What the architecture provides is the technical ability to comply, and it keeps that cheap.

**Personal data the system holds:**

| Data | Where | Notes |
|---|---|---|
| Google `sub`, email, name, avatar | `accounts` | The minimum needed for login and the profile page (story 8). No passwords are stored. |
| Favorites | `favorites` | Linked to the user. |
| Calendars and events | `calendars` | Linked to the user. |
| Chat messages | `suggestions` | Can reveal **special-category data** (Art. 9). A "diabetic" diet reveals health; "halal" or "kosher" can reveal religion. |
| Session cookie, server logs, error reports | platform, Sentry | Technical data, including IP addresses. |

**How the design meets the main GDPR requirements:**

| GDPR requirement | How it is met |
|---|---|
| **Data minimization** (Art. 5(1)(c)) | Only the four Google fields above are stored. Visitors stay anonymous. Chat conversations are kept per session only and are **not linked to the user account or stored after the session**, which keeps special-category data out of the database. |
| **Lawful basis** (Art. 6) | Account, favorites and calendar are processed to provide the service the user signed up for (contract). Security logs rely on legitimate interest. No analytics or ad tracking, so the only cookie is the strictly necessary session cookie and no consent banner is needed. |
| **Right of access and portability** (Art. 15, 20) | Each module exposes `export_user_data(user)` in its `services.py`. An "Export my data" action combines them into one JSON download. Because all modules share one database, nothing is spread across services. |
| **Right to erasure** (Art. 17) | Deleting a calendar (story 10) deletes it and its events in one transaction. A "Delete my account" action, which the user stories don't include and **must be added**, deletes the user and cascades to all their rows in one transaction. With one database there's no cross-service saga, unlike option 3. |
| **Erasure in backups and logs** | Deleted data stays in DB backups until they expire. Backup retention is set to a fixed period (e.g. 14 days) and stated in the privacy policy. Logs and Sentry events are kept for 30 days at most. |
| **Rectification** (Art. 16) | Profile fields are refreshed from Google on each login, so corrections made in the Google account flow through. |
| **Privacy by design** (Art. 25) | The chatbot's tool reads only the public recipe catalogue and never sees user data. Recipe IDs are validated and cards are rendered from our DB, so no user data can leak through LLM output. |
| **Security of processing** (Art. 32) | HTTPS only. The session cookie is HttpOnly, Secure and SameSite. The managed DB is encrypted at rest. Secrets live in environment variables. Sentry is configured to scrub personal data (`send_default_pii=False`). |
| **Processors** (Art. 28) | Hosting/DB provider, LLM provider and Sentry each need a data processing agreement (DPA). Hosting and DB run in an **EU region**. Chat text is sent to the LLM **without user identifiers**, with a provider configuration that doesn't use the data for training. |
| **International transfers** (Art. 44+) | US-based processors (likely the LLM provider and Sentry) need a transfer mechanism: the EU–US Data Privacy Framework or Standard Contractual Clauses. |
| **Breach notification** (Art. 33) | Sentry and uptime alerts give the developer early detection to meet the 72-hour reporting deadline. |

**Residual risks:**
- Users may type personal data into the chat (names, medical details). It is still sent to the LLM provider, which is mitigated only by the DPA, no-training settings and not storing it.
- One developer handles access, erasure and breach duties without a dedicated privacy role, so these actions must be self-service and automated.
