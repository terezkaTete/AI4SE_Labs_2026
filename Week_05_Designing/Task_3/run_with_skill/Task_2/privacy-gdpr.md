# RecipeCove: privacy and GDPR details

Companion to [ADR-001](ADR-001-recipecove-architecture.md). The architecture makes these measures easy to implement, but compliance also depends on process (policies, contracts, incident handling), which this file only lists.

## Data inventory

| Data | Where | Notes |
|---|---|---|
| Google `sub`, email, name, avatar URL | `user` table | Comes from OIDC. Needed for login and the profile page (stories 1, 6, 8). |
| Favourites | `favourite` | Links users to recipes. |
| Calendars and events | `calendar`, `calendar_event` | Recipe + date + optional note. Deleted with the calendar (story 10) through `ON DELETE CASCADE`. |
| Chat messages | `chat_message` | May contain special-category data (health, religion). Deleted after 30 days. |
| Session data | Django session store | Deleted on logout (story 7) or when the session expires. |
| Request logs | PaaS logs | IP addresses. Kept for 14 days. No chat content. |
| Backups | Managed Postgres | 7-day retention, so deleted data disappears from backups within 7 days. |

## Requirement → measure

| GDPR requirement | Measure |
|---|---|
| Art. 5 (minimization, storage limitation) | Only the Google fields above. Retention periods per the inventory. |
| Art. 6 (lawful basis) | Contract for the account features. Consent for the optional email reminders (if added later). |
| Art. 9 (special categories) | Chat text isn't linked to the profile, has short retention, and a notice in the chat UI explains this. |
| Art. 15 / 20 (access, portability) | New story 16: a JSON export of every table with a `user_id` (covered by the export test). |
| Art. 16 (rectification) | Name and email are synced from Google at each login. |
| Art. 17 (erasure) | New story 15: delete the account in one transaction (cascade). Backups expire within 7 days. Logs contain no user content. |
| Art. 25 (privacy by design) | The LLM sees no identifiers. Server-side sessions. Least-privilege DB role for the chatbot tool (read-only on catalogue tables). |
| Art. 28 (processors) | DPAs with the PaaS, the DB host and the LLM provider. |
| Art. 32 (security) | TLS, a secrets manager, dependency scanning in CI, and the module boundary rules. |
| Art. 44+ (transfers) | EU regions for the app and DB. Check the LLM provider's region or Standard Contractual Clauses. |
| Art. 33 (breach notification) | Incident runbook: notify the authority within 72 h. |

## Residual risks
- The LLM provider may log prompts. Mitigate with a no-training/zero-retention option, if the provider offers one.
- Users may paste personal data into the chat anyway. The UI warns them, but it can't prevent it.
- This analysis is an engineering view, not legal advice.
