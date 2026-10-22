# Software Requirements Specification

*Generated 2026-10-22 by the requirements-refinement agentic network from 20 input documents: 555 extracted candidate requirements → 138 requirements and 11 blacklisted items after 4 integration/review round(s). Reviewer approved: no (see section 8).*

## 1. Priority Scale (MoSCoW)

| Priority | Meaning | Count |
|---|---|---|
| **Must** | Essential for the system to be usable/acceptable; explicitly demanded by stakeholders, marked critical, or required by law/policy. | 92 |
| **Should** | Important and expected, but the system can go live without it (a workaround exists). | 38 |
| **Could** | Desirable nice-to-have that improves convenience; implemented if time allows. | 8 |
| **Won't** | Acknowledged but explicitly out of scope for the current release. | 0 |

## 2. Glossary

- **Bibliographic Record**: The bibliographic record that describes a work and to which Item records attach; used for cataloging, import/export, and many data-quality checks. Bibliographic Records are the canonical descriptive entities for discovery and metadata exchange and may have multiple attached Items representing physical or logical holdings.
- **Hold**: A patron-originated request to reserve an Item for pickup; in some sources the same concept is called a 'request'. Holds represent the reservation/fulfillment workflow and include placement method and status metadata used by circulation and reporting processes.
- **Item**: The library-held physical or logical unit represented by an Item record, including attributes such as status (checked out, missing), location/home branch, purchase price, and dimensions. Items are the canonical units used in circulation, transfers, inventory, and reporting; variants such as Items currently in transit are described as Item states in this definition. An Item that has departed one location and has no recorded arrival is considered in-transit for reporting and workflow purposes, identified by departure and (missing) arrival event semantics and by a configurable threshold for in-transit reporting. Item-level attributes support queries, counts, and shelf-space estimation and are referenced by report selection and aggregation logic.
- **Last Copy**: An Item that represents the final remaining copy of a Bibliographic Record within a defined scope (library or system). Last Copy detection is used to prevent unintentional removal of the sole remaining instance within the selected scope.
- **Purge Candidate**: An Item or record identified by configurable criteria (status, time in status, inactivity, last circulation) as eligible for purging. Purge Candidates are presented read-only until an explicit deletion operation is confirmed.
- **Report Template**: A saved definition of report selection criteria, display fields, and permissions. Report Templates include subtypes such as canned reports (predefined, non-editable outputs), on‑demand reports (preconfigured runs that may be edited at selection/display level), and open templates (full-attribute templates enabling arbitrary selections) — these subtypes are described within this definition rather than as separate glossary terms. Report Templates govern repeatability, governance, and permitted parameter edits for reporting workflows.
- **Reporting Warehouse**: A historical reporting data store used to serve reporting workloads separately from the live OLTP system to support historical, aggregated, and point-in-time queries without impacting production. The Reporting Warehouse provides read-only access characteristics, supports long-running and aggregated queries, and is allowed to be updated asynchronously; reports may rely on its historical snapshots while the system avoids assuming perfect, instantaneous synchronization with the live database.
- **Role-based Access Control (RBAC)**: A system-level access control model where permissions are granted to roles and users inherit permissions via role assignment. RBAC governs access to reporting features, data transfer utilities, deletion/purge operations, and administrative functions.
- **Shelf-space**: A measure of physical shelving occupied by Items; shelf-space can be estimated from Item dimensions or proxied by Item count when dimensions are missing. Shelf-space is used in reports comparing collection percentage, circulation percentage, and shelf-space percentage by genre or format.
- **Transaction Archive**: An archived store of transaction-level events (checkouts, checkins, holds, payments) retained with privacy protections and aggregation applied as required by law. The Transaction Archive supports historical statistics while protecting personally identifiable information and can expose aggregated monthly and annual statistics retained indefinitely per policy.

## 3. Requirements Overview

| ID | Name | Area | Type | Priority |
|---|---|---|---|---|
| [REQ-001](#req-001) | Activity And Transactions Reporting | Reporting Platform & Templates | Functional | Must |
| [REQ-002](#req-002) | Automated Delivery And Address Book | Reporting Platform & Templates | Functional | Must |
| [REQ-003](#req-003) | Board And Executive Reports | Reporting Platform & Templates | Functional | Must |
| [REQ-004](#req-004) | Canned Report Execution and Consolidation | Reporting Platform & Templates | Functional | Must |
| [REQ-005](#req-005) | Canned Report Templates | Reporting Platform & Templates | Functional | Must |
| [REQ-006](#req-006) | Consolidated Reporting Interface | Reporting Platform & Templates | Functional | Must |
| [REQ-007](#req-007) | Display Query Selections With Results | Reporting Platform & Templates | Functional | Must |
| [REQ-008](#req-008) | Include Null And Blank Fields | Reporting Platform & Templates | Functional | Must |
| [REQ-009](#req-009) | Last Edit And Last Circulation Fields | Reporting Platform & Templates | Functional | Must |
| [REQ-010](#req-010) | Monthly Reporting Support | Reporting Platform & Templates | Functional | Must |
| [REQ-011](#req-011) | Open Template Reporting | Reporting Platform & Templates | Functional | Must |
| [REQ-012](#req-012) | Periodic Reports Support | Reporting Platform & Templates | Functional | Must |
| [REQ-013](#req-013) | Query Design Interface | Reporting Platform & Templates | Functional | Must |
| [REQ-014](#req-014) | Report Export Formats | Reporting Platform & Templates | Functional | Must |
| [REQ-015](#req-015) | Report Queue and Status | Reporting Platform & Templates | Functional | Must |
| [REQ-016](#req-016) | Report Role-Based Access Control | Reporting Platform & Templates | Functional | Must |
| [REQ-017](#req-017) | Report Template Management | Reporting Platform & Templates | Functional | Must |
| [REQ-018](#req-018) | Reporting Interfaces | Reporting Platform & Templates | Functional | Must |
| [REQ-019](#req-019) | Scheduling (Daily, Weekly, Monthly, Yearly) | Reporting Platform & Templates | Functional | Must |
| [REQ-020](#req-020) | Separate Checkin And Renewal Timestamps | Reporting Platform & Templates | Functional | Must |
| [REQ-021](#req-021) | Template Integrity And Restrictions | Reporting Platform & Templates | Functional | Must |
| [REQ-022](#req-022) | Transactional Grouping And Counts | Reporting Platform & Templates | Functional | Must |
| [REQ-023](#req-023) | Cancel Scheduled And Running Reports | Reporting Platform & Templates | Functional | Should |
| [REQ-024](#req-024) | Clone Report Templates | Reporting Platform & Templates | Functional | Should |
| [REQ-025](#req-025) | Custom And Management Reporting | Reporting Platform & Templates | Functional | Should |
| [REQ-026](#req-026) | Historical Point-in-Time Reporting | Reporting Platform & Templates | Functional | Should |
| [REQ-027](#req-027) | On-Demand Reporting | Reporting Platform & Templates | Functional | Should |
| [REQ-028](#req-028) | Quick Access Interface | Reporting Platform & Templates | Functional | Should |
| [REQ-029](#req-029) | Real-Time Reporting Support | Reporting Platform & Templates | Functional | Should |
| [REQ-030](#req-030) | Report Usage Metrics | Reporting Platform & Templates | Functional | Should |
| [REQ-031](#req-031) | Reports UI Discoverability And Help | Reporting Platform & Templates | Functional | Should |
| [REQ-032](#req-032) | Web-Based Report Writer | Reporting Platform & Templates | Functional | Should |
| [REQ-033](#req-033) | Hourly Scheduling | Reporting Platform & Templates | Functional | Could |
| [REQ-034](#req-034) | Upload Filtering Support | Reporting Platform & Templates | Functional | Could |
| [REQ-035](#req-035) | Acquisition Date Tracking For Items | Material Volume & Collection Reporting | Functional | Must |
| [REQ-036](#req-036) | Location Filter For Item Reports | Material Volume & Collection Reporting | Functional | Must |
| [REQ-037](#req-037) | Material Item Report | Material Volume & Collection Reporting | Functional | Must |
| [REQ-038](#req-038) | Customizable Category Definitions | Material Volume & Collection Reporting | Functional | Should |
| [REQ-039](#req-039) | Point-In-Time Item Reporting | Material Volume & Collection Reporting | Functional | Should |
| [REQ-040](#req-040) | Automated Shelf-space and Capacity Reports | Capacity & Shelf-space Analysis | Functional | Must |
| [REQ-041](#req-041) | Branch Drill-Down | Capacity & Shelf-space Analysis | Functional | Must |
| [REQ-042](#req-042) | Capacity View Grouping and Filtering | Capacity & Shelf-space Analysis | Functional | Must |
| [REQ-043](#req-043) | Centralized Data Aggregation | Capacity & Shelf-space Analysis | Functional | Must |
| [REQ-044](#req-044) | Define Capacity Metrics | Capacity & Shelf-space Analysis | Functional | Must |
| [REQ-045](#req-045) | Global Capacity Overview | Capacity & Shelf-space Analysis | Functional | Must |
| [REQ-046](#req-046) | Per-Library and System Reporting | Capacity & Shelf-space Analysis | Functional | Must |
| [REQ-047](#req-047) | Shelf-space Estimation | Capacity & Shelf-space Analysis | Functional | Must |
| [REQ-048](#req-048) | Shelf-space Metrics Report | Capacity & Shelf-space Analysis | Functional | Must |
| [REQ-049](#req-049) | Analyze Capacity and Recommend Distribution | Capacity & Shelf-space Analysis | Functional | Should |
| [REQ-050](#req-050) | Color-Coded Capacity Status | Capacity & Shelf-space Analysis | Functional | Should |
| [REQ-051](#req-051) | Trend and Time-Range Analysis | Capacity & Shelf-space Analysis | Functional | Should |
| [REQ-052](#req-052) | Export Capacity Data | Capacity & Shelf-space Analysis | Functional | Could |
| [REQ-053](#req-053) | Auto Revert And Event-Based Revert | Item Transfer & Relocation Utility | Functional | Must |
| [REQ-054](#req-054) | Batch Processing Efficiency | Item Transfer & Relocation Utility | Non-functional | Must |
| [REQ-055](#req-055) | Batch Transfer Utility | Item Transfer & Relocation Utility | Functional | Must |
| [REQ-056](#req-056) | Change Item Location | Item Transfer & Relocation Utility | Functional | Must |
| [REQ-057](#req-057) | Manual Selection From Results | Item Transfer & Relocation Utility | Functional | Must |
| [REQ-058](#req-058) | Query Candidate Items | Item Transfer & Relocation Utility | Functional | Must |
| [REQ-059](#req-059) | Role-Based Transfer Permissions | Item Transfer & Relocation Utility | Functional | Must |
| [REQ-060](#req-060) | Save And Schedule Queries | Item Transfer & Relocation Utility | Functional | Must |
| [REQ-061](#req-061) | Transfer Audit Logging | Item Transfer & Relocation Utility | Functional | Must |
| [REQ-062](#req-062) | Preview Transfer Changes | Item Transfer & Relocation Utility | Functional | Should |
| [REQ-063](#req-063) | Pull List Generation | Item Transfer & Relocation Utility | Functional | Should |
| [REQ-064](#req-064) | Transfer History Per Item | Item Transfer & Relocation Utility | Functional | Should |
| [REQ-065](#req-065) | Undo Transfer Operation | Item Transfer & Relocation Utility | Functional | Should |
| [REQ-066](#req-066) | Transfer Delay Alerts | Item Transfer & Relocation Utility | Functional | Could |
| [REQ-067](#req-067) | Transit Labels Generation | Item Transfer & Relocation Utility | Functional | Could |
| [REQ-068](#req-068) | Items Currently In Transit Report | Missing/Damaged & In-Transit Reporting | Functional | Must |
| [REQ-069](#req-069) | Missing, Damaged And Lost Items Report | Missing/Damaged & In-Transit Reporting | Functional | Must |
| [REQ-070](#req-070) | Date Range Filtering For Missing/Damaged Reports | Missing/Damaged & In-Transit Reporting | Functional | Should |
| [REQ-071](#req-071) | Separate Missing/Damaged And Items Currently In Transit Reports | Missing/Damaged & In-Transit Reporting | Functional | Should |
| [REQ-072](#req-072) | Sort Items Currently In Transit By Due Date | Missing/Damaged & In-Transit Reporting | Functional | Should |
| [REQ-073](#req-073) | Analytics For Missing Item Patterns | Missing/Damaged & In-Transit Reporting | Functional | Could |
| [REQ-074](#req-074) | Include Item Condition Notes | Missing/Damaged & In-Transit Reporting | Functional | Could |
| [REQ-075](#req-075) | Deletion Audit Logging | Purging, Deletion & Audit Trail | Functional | Must |
| [REQ-076](#req-076) | Deletion Confirmation Step | Purging, Deletion & Audit Trail | Functional | Must |
| [REQ-077](#req-077) | Item Purging Utility | Purging, Deletion & Audit Trail | Functional | Must |
| [REQ-078](#req-078) | Last Copy Detection And Reports | Purging, Deletion & Audit Trail | Functional | Must |
| [REQ-079](#req-079) | Purge Candidate Read-Only Display | Purging, Deletion & Audit Trail | Functional | Must |
| [REQ-080](#req-080) | Purge Criteria: Status/Time/Activity | Purging, Deletion & Audit Trail | Functional | Must |
| [REQ-081](#req-081) | Record Deletion Utilities | Purging, Deletion & Audit Trail | Functional | Must |
| [REQ-082](#req-082) | Audit Reporting And Aggregation | Purging, Deletion & Audit Trail | Functional | Should |
| [REQ-083](#req-083) | Batch Status Conversion | Purging, Deletion & Audit Trail | Functional | Should |
| [REQ-084](#req-084) | Combine Purge Criteria | Purging, Deletion & Audit Trail | Functional | Should |
| [REQ-085](#req-085) | Purge Scheduling | Purging, Deletion & Audit Trail | Functional | Should |
| [REQ-086](#req-086) | Anonymized Demographic Statistics | Patron Demographics & Inactivity Reporting | Functional | Must |
| [REQ-087](#req-087) | Combine Filters With Boolean Logic | Patron Demographics & Inactivity Reporting | Functional | Must |
| [REQ-088](#req-088) | Configurable Age Ranges | Patron Demographics & Inactivity Reporting | Functional | Must |
| [REQ-089](#req-089) | Configure Inactivity Window | Patron Demographics & Inactivity Reporting | Functional | Must |
| [REQ-090](#req-090) | Filter By Patron Characteristics | Patron Demographics & Inactivity Reporting | Functional | Must |
| [REQ-091](#req-091) | Generate Inactive Patrons List | Patron Demographics & Inactivity Reporting | Functional | Must |
| [REQ-092](#req-092) | Group By Patron Characteristics | Patron Demographics & Inactivity Reporting | Functional | Must |
| [REQ-093](#req-093) | Include Null Values In Reports | Patron Demographics & Inactivity Reporting | Functional | Must |
| [REQ-094](#req-094) | Background Processing And Performance | Patron Demographics & Inactivity Reporting | Functional | Should |
| [REQ-095](#req-095) | Configure Inactive Report Scope | Patron Demographics & Inactivity Reporting | Functional | Should |
| [REQ-096](#req-096) | Export Inactive Report | Patron Demographics & Inactivity Reporting | Functional | Should |
| [REQ-097](#req-097) | Include Contact Fields And Exclusions | Patron Demographics & Inactivity Reporting | Functional | Should |
| [REQ-098](#req-098) | Patron Behavior And Predictive Analytics | Patron Demographics & Inactivity Reporting | Functional | Should |
| [REQ-099](#req-099) | Assign Cleanup Tasks To Home Branches | Patron Demographics & Inactivity Reporting | Functional | Could |
| [REQ-100](#req-100) | Attach Financial Data To Records | Financial Reporting & Transactions | Functional | Must |
| [REQ-101](#req-101) | Compliance, Archiving And Retention | Financial Reporting & Transactions | Non-functional | Must |
| [REQ-102](#req-102) | Financial Audit Trail And Ledger | Financial Reporting & Transactions | Functional | Must |
| [REQ-103](#req-103) | Financial Reports | Financial Reporting & Transactions | Functional | Must |
| [REQ-104](#req-104) | Real-Time Payment Updates | Financial Reporting & Transactions | Functional | Must |
| [REQ-105](#req-105) | Role-Based Access To Financial Reports | Financial Reporting & Transactions | Non-functional | Must |
| [REQ-106](#req-106) | Historical Snapshot Of Bills | Financial Reporting & Transactions | Functional | Should |
| [REQ-107](#req-107) | Value Of Items Report | Financial Reporting & Transactions | Functional | Should |
| [REQ-108](#req-108) | Accessibility and Assistive Technology Compliance | System Architecture, Performance & Operations | Non-functional | Must |
| [REQ-109](#req-109) | Accessible HTML Online Help | System Architecture, Performance & Operations | Non-functional | Must |
| [REQ-110](#req-110) | Background Processing and Queuing | System Architecture, Performance & Operations | Non-functional | Must |
| [REQ-111](#req-111) | Consortium Scale Support | System Architecture, Performance & Operations | Non-functional | Must |
| [REQ-112](#req-112) | Enterprise-Grade Centralized Service | System Architecture, Performance & Operations | Non-functional | Must |
| [REQ-113](#req-113) | Environment Separation And Configuration Migration | System Architecture, Performance & Operations | Non-functional | Must |
| [REQ-114](#req-114) | Error Reporting and Diagnostic Feedback | System Architecture, Performance & Operations | Non-functional | Must |
| [REQ-115](#req-115) | OPAC Independence and Performance Protection | System Architecture, Performance & Operations | Non-functional | Must |
| [REQ-116](#req-116) | Operational Performance During Open Hours | System Architecture, Performance & Operations | Non-functional | Must |
| [REQ-117](#req-117) | Platform And Database Support | System Architecture, Performance & Operations | Non-functional | Must |
| [REQ-118](#req-118) | Predefined Administrative Roles | System Architecture, Performance & Operations | Non-functional | Must |
| [REQ-119](#req-119) | Process Documentation | System Architecture, Performance & Operations | Non-functional | Must |
| [REQ-120](#req-120) | Relational Database Back-End And Design | System Architecture, Performance & Operations | Non-functional | Must |
| [REQ-121](#req-121) | Reporting Warehouse | System Architecture, Performance & Operations | Functional | Must |
| [REQ-122](#req-122) | Role-Based Access Control | System Architecture, Performance & Operations | Non-functional | Must |
| [REQ-123](#req-123) | Staff Authentication and Audit | System Architecture, Performance & Operations | Non-functional | Must |
| [REQ-124](#req-124) | Standards-Compliant HTML and Semantic Markup | System Architecture, Performance & Operations | Non-functional | Must |
| [REQ-125](#req-125) | Transaction Archive, Retention, and Privacy | System Architecture, Performance & Operations | Non-functional | Must |
| [REQ-126](#req-126) | Web Client Browser Support | System Architecture, Performance & Operations | Non-functional | Should |
| [REQ-127](#req-127) | Bibliographic Import And Export | Cataloging & Data Quality | Functional | Must |
| [REQ-128](#req-128) | Complete Data Specifications | Cataloging & Data Quality | Non-functional | Must |
| [REQ-129](#req-129) | Data Quality Reporting | Cataloging & Data Quality | Functional | Must |
| [REQ-130](#req-130) | Integration With Acquisitions And Cataloging Modules | Cataloging & Data Quality | Functional | Must |
| [REQ-131](#req-131) | Patron Fields For Reporting | Cataloging & Data Quality | Functional | Must |
| [REQ-132](#req-132) | Vendor Data Interfaces | Cataloging & Data Quality | Functional | Must |
| [REQ-133](#req-133) | WorldCat Integration | Cataloging & Data Quality | Functional | Must |
| [REQ-134](#req-134) | Authority Validation Process | Cataloging & Data Quality | Functional | Should |
| [REQ-135](#req-135) | Data Dictionaries For Staff | Cataloging & Data Quality | Non-functional | Should |
| [REQ-136](#req-136) | MARC Field Extraction Across Rows | Cataloging & Data Quality | Functional | Should |
| [REQ-137](#req-137) | Uncataloged Item Inventory Tracking | Cataloging & Data Quality | Functional | Should |
| [REQ-138](#req-138) | Patron Access Via OPAC Displays | General | Functional | Must |

## 4. Requirements

### Reporting Platform & Templates

#### REQ-001

**Activity And Transactions Reporting** · *Functional · Priority: Must*

The system shall produce activity and transaction reports that indicate traffic and transaction counts (check-outs, check-ins, Holds placed, Holds filled, fines charged, and patron registrations) and shall preserve per-patron counts and support cross-tabulation and grouping by terminal, branch, system, hour, patron age range, patron type, patron location (including county), and groups of libraries; reports shall also include Hold status breakdowns where applicable. Circulation managers and analysts will use these reports for operational monitoring and cross-jurisdictional comparisons; the outputs must expose per-patron transaction tallies so analysts can compute cohort-level metrics and must support grouping by both county and arbitrary groups of libraries for aggregated jurisdictional views. Verification includes running activity and transaction reports that return per-patron counts, exercising grouping by county and by configured groups of libraries, and confirming the renewal percentage calculation and component counts reconcile to transaction records.

*Priority rationale:* Per-patron counts and grouping by county and library groups are explicitly required for operational and cross-jurisdictional analysis.

*Sources:* `early_draft_srs_galecia.txt`, `email_report_features.eml`

#### REQ-002

**Automated Delivery And Address Book** · *Functional · Priority: Must*

The system shall support automated delivery of report outputs, including scheduled delivery by email and a configurable address-book of recipients so administrators can distribute recurring reports to stakeholders. Staff and managers will use automated delivery to share reports without manual distribution; scheduled deliveries shall include metadata about the run and the ability for authorized users to manage recipient lists via an address-book. Verification includes scheduling an email delivery, selecting address-book recipients, and confirming delivery receipt along with attached or linked report output.

*Priority rationale:* Automated delivery is required for routine distribution of governance and operational reports and must be testable independently of export-format behavior.

*Sources:* `meeting_tech_subcommittee_2009-06-30.txt`, `survey_results_2009.txt`

#### REQ-003

**Board And Executive Reports** · *Functional · Priority: Must*

The system shall provide pre-defined board and executive reports (including statistics required by applicable annual reporting and state aid applications) suitable for external consumption and governance. Administrators will use these reports to produce externally facing summary statistics and to meet reporting obligations. Verification includes generating the pre-defined board report set and confirming required statistics and aggregates are present and formatted for external use. Providing these prepared outputs reduces the work required to satisfy oversight and reporting requirements.

*Priority rationale:* Pre-defined board and executive reports are explicitly requested and are required for external reporting and compliance.

*Sources:* `early_draft_srs_galecia.txt`, `email_report_features.eml`

#### REQ-004

**Canned Report Execution and Consolidation** · *Functional · Priority: Must*

The system shall support running canned reports immediately or on a recurring schedule, allow selection of multiple canned reports to run together, and present combined outputs as a single consolidated document when requested. Operational staff and managers will use execution and consolidation capabilities to produce packaged operational packets and recurring summaries efficiently. Verification includes scheduling and running multiple canned reports together and confirming the combined-document behavior and scheduling mechanics function as expected.

*Priority rationale:* Running and consolidating canned reports is essential for routine operational workflows and board reporting cadence.

*Sources:* `evergreen_reference_2009.txt`

#### REQ-005

**Canned Report Templates** · *Functional · Priority: Must*

The system shall include a set of canned Report Templates delivered with the product that cover standard operational and governance metrics (circulation, items, bibliographic, patron, and fines reports). Administrators will rely on the delivered canned templates as vetted starting points for routine reporting and to reduce duplicate template creation. Verification includes locating the provided canned templates and running them to confirm outputs match expected standard metrics.

*Priority rationale:* Stakeholders require an out-of-the-box set of canned reports for basic operations and board reporting without custom template creation.

*Sources:* `early_draft_srs_galecia.txt`, `evergreen_reference_2009.txt`

#### REQ-006

**Consolidated Reporting Interface** · *Functional · Priority: Must*

The system shall provide a single consolidated reporting interface that presents Item counts and summary metrics from across report types so staff do not need to gather data from multiple screens. Staff and managers will use this single view to build, run, and retrieve common operational and governance reports; it reduces manual aggregation work and supports consistent results. The interface shall permit navigation to underlying Report Templates and exported outputs for audit and for drilling into Item-level sources. Verification includes running representative Item-count reports, confirming data previously requiring multiple screens appears together and matches source records, and navigating from consolidated results to underlying templates.

*Priority rationale:* A single consolidated interface is essential to reduce manual effort and ensure consistent reporting.

*Sources:* `conversations/conv_pines014_material_volume.eml`

#### REQ-007

**Display Query Selections With Results** · *Functional · Priority: Must*

The system shall display the query selection criteria used to generate a report alongside the report results so users can see and verify the filter and selection logic. Staff and auditors will use the displayed criteria to validate that outputs were produced from the intended inputs and to reproduce runs. Verification includes running reports and confirming the selection criteria are presented with the results export and on-screen result view. This transparency reduces user error and facilitates auditability.

*Priority rationale:* Stakeholders explicitly requested selection-criteria visibility to verify results and reduce support calls; it is straightforward to verify and critical for trust.

*Sources:* `early_draft_srs_galecia.txt`, `email_report_features.eml`, `evergreen_reference_2009.txt`

#### REQ-008

**Include Null And Blank Fields** · *Functional · Priority: Must*

The system shall include null and blank fields explicitly in report results when those fields are part of the selected output columns so downstream analysis and counts are accurate and predictable. Including nulls prevents silent data loss and ensures users can distinguish empty values from missing rows. Verification includes running queries that target columns with nulls and confirming the exported and displayed results include explicit null/blank entries rather than omitting rows.

*Priority rationale:* Multiple stakeholders emphasized correct null handling; omitting nulls causes inaccurate counts and analyses.

*Sources:* `evergreen_reference_2009.txt`, `meeting_tech_subcommittee_2009-06-30.txt`, `survey_results_2009.txt`

#### REQ-009

**Last Edit And Last Circulation Fields** · *Functional · Priority: Must*

The system shall provide separate fields for an item's last edit date and last circulation date so cataloging and circulation functions can be reported independently and without conflation. Catalogers and circulation staff need to know when an item record was last edited versus when the item last circulated to support collection decisions and metadata hygiene. Verification includes generating item reports that show both fields separately and validating that updates to one field do not alter the other.

*Priority rationale:* Multiple stakeholder sources consistently requested separate last-edit and last-circulation data for accurate reporting and collection management.

*Sources:* `evergreen_reference_2009.txt`, `survey_results_2009.txt`

#### REQ-010

**Monthly Reporting Support** · *Functional · Priority: Must*

The system shall support generating Item-count and summary reports suitable for monthly board reporting, including common roll-ups and date-range presets for month-end reporting. Managers and administrators will use these reports to produce the monthly board packet and to verify compliance with oversight requirements. The capability shall allow scheduling or one‑time generation as needed and shall report Item-level counts and category breakdowns consistent with Report Templates. Verification includes producing a monthly Item-count report using the month preset and confirming the output matches the metrics required for board review.

*Priority rationale:* Monthly reporting is required for governance and oversight.

*Sources:* `conversations/conv_pines014_material_volume.eml`

#### REQ-011

**Open Template Reporting** · *Functional · Priority: Must*

The system shall offer open-template Report Templates (a subtype of Report Template) that expose all attributes associated with circulation, patrons, Items, bills, and Bibliographic Records so advanced staff can build custom filters and displays. Collection analysts and advanced staff will use open templates to select arbitrary attributes for filtering and reporting when other template subtypes are insufficient. Verification includes creating and running an open-template Report Template that selects attributes from the indicated record types and confirming the output contains the requested fields. This capability enables deep analysis and supports novel reporting needs.

*Priority rationale:* Open-template capability is required for advanced analytical workflows and ad-hoc investigations.

*Sources:* `early_draft_srs_galecia.txt`

#### REQ-012

**Periodic Reports Support** · *Functional · Priority: Must*

The system shall support a defined set of periodic report types and fine-grained reporting constructs delivered in the project appendices and shall explicitly include periodic outputs such as: items not checked out in configurable X days, Bibliographic Records with Holds, Item-level Holds (Holds aggregated at the Item level), Items in Transit with outstanding Holds, Patrons with invalid or missing home-branch assignments, Missing Items, Last Copy detection, and new acquisitions by acquisition date range. Administrators and report authors will rely on these predefined periodic reports for recurring quality, compliance, and governance tasks; each periodic report shall be selectable as a canned Report Template and be schedulable. Verification includes producing each listed periodic report type and confirming their outputs match the documented definitions and the appendix sample outputs.

*Priority rationale:* Stakeholders require a known set of periodic checks for compliance and quality; explicitly enumerating them ensures verifiable delivery.

*Sources:* `early_draft_srs_galecia.txt`

#### REQ-013

**Query Design Interface** · *Functional · Priority: Must*

The system shall provide a user-friendly query design interface that supports selecting fields, choosing values from picklists, applying regular expressions, combining expressions with Boolean operators, and applying selection filters using named surveys (resolving survey names to their underlying survey identifiers) against Bibliographic Records, Items, patrons, transactions, and financial records. Report authors and staff will use the interface to construct both ad-hoc and saved queries that include survey-based filters in addition to other attributes so reports and exports can be filtered consistently whether the filter is by name or by identifier. The interface shall document how survey-name resolution operates and shall be verifiable by constructing a query that filters on a survey name, inspecting the resolved identifier in the run metadata, and confirming returned results match the intended survey-scoped data.

*Priority rationale:* Survey-based filtering is required by reporting use cases and must be verifiable in ad-hoc queries as well as scheduled runs.

*Sources:* `early_draft_srs_galecia.txt`, `email_report_features.eml`, `meeting_tech_subcommittee_2009-06-30.txt`, `survey_results_2009.txt`

#### REQ-014

**Report Export Formats** · *Functional · Priority: Must*

The system shall export report outputs in multiple formats (at minimum CSV, Excel, and HTML) and provide export-quality behaviors such as reliable CSV encoding and Excel-friendly formatting, and options to remove duplicate rows so downstream analysis and ingestion are predictable. The system shall also support pivot-table output (for example, Excel pivot workbooks or equivalent pivotable exports) so analysts can begin multi-dimensional analysis immediately without manual pivot construction. Staff and analysts will use these export formats to integrate reports into spreadsheets, downstream tools, and archival records; exports must preserve selected columns, nulls, and ordering where applicable. Verification includes exporting the same report in each supported format (including a pivotable Excel workbook), validating correct formatting and null handling, and confirming options (for example duplicate-row suppression) produce expected output.

*Priority rationale:* 

*Sources:* `evergreen_reference_2009.txt`, `survey_results_2009.txt`

#### REQ-015

**Report Queue and Status** · *Functional · Priority: Must*

The system shall provide a visible report queue showing the position and status (waiting, running, completed, failed) of submitted reports, including submission time, ETA indicators, and prioritization controls so important reports can move ahead. Staff will use queue visibility to understand expected wait time and to diagnose delays; administrators will use priority controls for urgent runs. Verification includes submitting concurrent reports, observing queue positions and statuses, and confirming priority changes affect execution order.

*Priority rationale:* Queue visibility and status are repeatedly requested and directly reduce support load and user confusion; they are essential for acceptable operational experience.

*Sources:* `early_draft_srs_galecia.txt`, `email_report_features.eml`, `evergreen_reference_2009.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `survey_results_2009.txt`

#### REQ-016

**Report Role-Based Access Control** · *Functional · Priority: Must*

The system shall enforce fine‑grained Role-based Access Control for reporting actions and provide shared folder mechanisms so administrators can control who can create, clone, edit, schedule, run, and manage Report Templates and outputs. Administrators will use RBAC and folder-level permissions to protect sensitive reports, permit controlled template editing, and manage visibility of report libraries. Verification includes assigning roles and folder permissions, placing Report Templates in folders, and confirming users’ capabilities align with assigned permissions and folder access.

*Priority rationale:* Multiple stakeholders repeatedly requested fine-grained permissions; RBAC is essential for data governance and safe operation.

*Sources:* `early_draft_srs_galecia.txt`, `email_report_features.eml`, `evergreen_reference_2009.txt`, `survey_results_2009.txt`

#### REQ-017

**Report Template Management** · *Functional · Priority: Must*

The system shall allow administrators to create, publish, manage, and control Report Templates so staff can run templates as-is or use them as controlled starting points for permitted edits. Administrators will use template management to maintain consistent reporting definitions, restrict editable fields where needed, and publish vetted templates to staff. Verification includes creating a Report Template as an administrator, publishing it, and confirming staff can run it and, where permitted, modify allowed parameters without altering template-defined constraints.

*Priority rationale:* Administrators must manage templates to ensure consistent, auditable report definitions across the organization.

*Sources:* `early_draft_srs_galecia.txt`, `email_report_features.eml`, `evergreen_reference_2009.txt`, `survey_results_2009.txt`

#### REQ-018

**Reporting Interfaces** · *Functional · Priority: Must*

The system shall provide Report Template-based reporting interfaces that include subtypes such as canned reports, on‑demand reports, and open templates so different user roles can access reports at the appropriate level of flexibility. Staff and administrators will use canned Report Templates for routine outputs, on‑demand report subtype for editable preconfigured runs, and the open-template subtype for ad‑hoc queries selecting from full attribute sets. Verification includes listing and running reports from each Report Template subtype and confirming behavior matches the subtype definitions in the Report Template documentation. This structure supports governance, repeatability, and advanced analysis workflows while keeping terminology aligned with the glossary.

*Priority rationale:* Aligning interface concepts with the canonical Report Template term preserves consistency and governance.

*Sources:* `early_draft_srs_galecia.txt`, `evergreen_reference_2009.txt`

#### REQ-019

**Scheduling (Daily, Weekly, Monthly, Yearly)** · *Functional · Priority: Must*

The system shall support scheduling report execution at daily, weekly, monthly, and yearly intervals and provide configurable delivery options for recurring and one‑off runs, including the ability to filter scheduled runs by attributes such as survey name where applicable. Administrators and staff will use scheduled runs to automate routine operational and governance reporting and to deliver outputs to recipients without manual intervention. Verification includes scheduling reports on supported cadences including yearly runs, editing schedules, filtering schedules by survey name, and confirming successful runs and deliveries at the configured times.

*Priority rationale:* Comprehensive scheduling cadences (including yearly) and basic filtering are required to meet governance and periodic reporting needs.

*Sources:* `evergreen_reference_2009.txt`, `survey_results_2009.txt`

#### REQ-020

**Separate Checkin And Renewal Timestamps** · *Functional · Priority: Must*

The system shall store and expose check-in timestamp and renewal timestamp as distinct fields so reports can reliably distinguish true check-ins from renewals. This ensures circulation reports and transaction counts correctly represent physical returns versus renewal events and supports accurate operational metrics. Verification includes inspecting records and report outputs for items that were renewed and confirming separate timestamp values are present and used correctly in aggregations.

*Priority rationale:* Accurate circulation metrics require this separation; stakeholders explicitly requested it to avoid miscounting.

*Sources:* `evergreen_reference_2009.txt`, `survey_results_2009.txt`

#### REQ-021

**Template Integrity And Restrictions** · *Functional · Priority: Must*

The system shall ensure changes to report templates preserve result accuracy and allow administrators to restrict which filters and display fields staff may alter so dependable outputs are certified. Administrators will use these controls to prevent template edits that would expose inappropriate data (for example, deleted items) or produce misleading results, while allowing frontline parameterization (such as call number ranges). Verification includes attempting restricted edits as a staff user, confirming the system prevents restricted changes, and validating that permitted parameter changes produce expected results without altering template-defined constraints. This preserves trust in shared templates and supports auditability.

*Priority rationale:* Stakeholders emphasized the need to prevent template changes that could compromise results and to allow limited frontline parameterization; this is essential for dependable reporting.

*Sources:* `early_draft_srs_galecia.txt`, `email_report_features.eml`

#### REQ-022

**Transactional Grouping And Counts** · *Functional · Priority: Must*

The system shall support fine-grained grouping and counting in transaction reports, including grouping by hour, terminal, branch, and system, counting check-in and check-out types both individually and cumulatively, reporting Holds by placement method and Hold status, and exposing per-patron transaction counts at the chosen scope; the system shall support grouping by county and by groups of libraries for aggregated jurisdictional summaries. Analysts and operations staff will use these transactional outputs to evaluate circulation patterns, Holds fulfillment, and staffing impact across organizational boundaries; the outputs must include per-patron counts so renewal and usage metrics can be validated at the patron level and aggregated across configured groups. Verification includes producing transaction reports that exercise each grouping level, demonstrating per-patron counts appear in the output, and validating the renewal-percentage calculation against known transaction data.

*Priority rationale:* Detailed grouping and per-patron counts are required by operational stakeholders and testable against transaction archives.

*Sources:* `early_draft_srs_galecia.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `survey_results_2009.txt`

#### REQ-023

**Cancel Scheduled And Running Reports** · *Functional · Priority: Should*

The system shall allow authorized users to cancel scheduled reports and stop in-progress report processing, with the report processing engine checking for cancellation signals at safe interruption points. Cancellation prevents wasted compute for obsolete jobs and allows administrators to stop runaway or erroneous queries. Verification includes starting long-running jobs and scheduled runs, issuing cancel requests, and confirming processing stops and resources are released, with appropriate status recorded in the queue.

*Priority rationale:* Cancellation is important for operational control and resource management; it is expected but does not block basic reporting.

*Sources:* `meeting_tech_subcommittee_2009-06-30.txt`, `survey_results_2009.txt`

#### REQ-024

**Clone Report Templates** · *Functional · Priority: Should*

The system shall support cloning of existing report templates so users can create a new template variant without modifying the original template. Staff and administrators will use cloning to iterate on templates or create local variants while preserving the canonical template. Verification includes cloning a template, modifying the clone, and confirming the original template remains unchanged while the clone reflects the edits. This prevents accidental modification of shared templates and accelerates template creation.

*Priority rationale:* Cloning simplifies template creation and reduces errors; it is high‑value but not strictly required for initial operation because templates can be recreated manually.

*Sources:* `email_report_features.eml`

#### REQ-025

**Custom And Management Reporting** · *Functional · Priority: Should*

The system shall support custom and management-focused reports and templates (including collection development, program attendance tracking, and staff productivity) and provide mechanisms for producing executive and standard reports used by managers and boards for planning and oversight. This capability supports management processes and allows local/customized reporting to meet diverse operational and oversight needs across branches and consortia. Verification includes creating the listed custom report types, running management-oriented aggregates, and confirming pre-defined executive reports produce the expected fields and summaries.

*Priority rationale:* Custom and management reporting is important for oversight and strategic decision-making; many stakeholders requested it though some needs can be met with templates or ad-hoc queries initially.

*Sources:* `evergreen_reference_2009.txt`, `meeting_minutes/meeting_2009-03-15_minutes.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`, `survey_results_2009.txt`

#### REQ-026

**Historical Point-in-Time Reporting** · *Functional · Priority: Should*

The system shall support point-in-time historical reporting so users can produce reports that reflect the dataset as of a specified past date (for example shelving location at that date), enabling audits and historical analysis. This typically requires access to historical snapshots or a reporting store built for time-based queries and protects analytical correctness when records change over time. Verification includes producing reports for prior dates and confirming returned values match stored snapshots or archived transaction-derived reconstructions for the requested date.

*Priority rationale:* Historical reporting is valuable for audits and analysis; many users requested it though it may require additional infrastructure and can be delivered after baseline reporting.

*Sources:* `survey_results_2009.txt`

#### REQ-027

**On-Demand Reporting** · *Functional · Priority: Should*

The system shall provide on‑demand Report Templates (a subtype of Report Template) that are preconfigured but editable at the selection-criteria and display-option level so staff can run maintenance and collections reports when needed. Front-line staff and managers will use on‑demand Report Templates for occasional or ad hoc analysis without creating new templates. Verification includes editing a preconfigured on‑demand Report Template’s selection criteria or display options and running it successfully against current data sets. This supports responsiveness while preserving a standard starting definition.

*Priority rationale:* On‑demand variability is important for staff productivity but can be delivered after core canned templates.

*Sources:* `early_draft_srs_galecia.txt`, `email_report_features.eml`

#### REQ-028

**Quick Access Interface** · *Functional · Priority: Should*

The system shall provide a quick‑access interface that gives users fast access to common canned Report Templates and templates with descriptive hover text, multi-criteria selection, run options (ASAP and common recurrence presets including yearly), and basic prioritization and cancellation controls. Staff will use the quick‑access UI to launch frequent reports efficiently and to understand each report’s purpose before running; the quick-access view shall surface usage indicators to help users select commonly used reports. Verification includes using the quick access UI to select a canned Report Template, viewing its hover description, choosing run options (including yearly where offered), and canceling a running or scheduled job.

*Priority rationale:* Quick access improves day‑to‑day usability and should include common recurrence presets to match user workflows.

*Sources:* `early_draft_srs_galecia.txt`

#### REQ-029

**Real-Time Reporting Support** · *Functional · Priority: Should*

The system shall support real-time reporting capabilities that return up-to-date operational data during busy periods with acceptable performance characteristics for interactive use. Real-time access enables immediate operational decisions and monitoring without depending solely on batch or delayed extracts. Verification includes running representative queries under load and confirming response times meet defined interactive thresholds and that results reflect the current system state.

*Priority rationale:* Real-time reporting is desirable for operational monitoring and was requested by stakeholders, but can be staged after initial reporting capabilities or supported via a performance-tier strategy.

*Sources:* `evergreen_reference_2009.txt`, `survey_results_2009.txt`

#### REQ-030

**Report Usage Metrics** · *Functional · Priority: Should*

The system shall provide report usage metrics that show total run counts and run counts within a specified date range per Report Template and canned report so administrators can understand report popularity and operational load. Administrators and managers will use usage metrics to optimize the quick-access UI, manage scheduled runs, and identify seldom-used templates for cleanup. Verification includes generating usage reports for a chosen period and confirming returned counts match recorded execution logs for each Report Template.

*Priority rationale:* Usage metrics aid operational decisions but are not strictly required for core reporting functionality.

*Sources:* `early_draft_srs_galecia.txt`

#### REQ-031

**Reports UI Discoverability And Help** · *Functional · Priority: Should*

The system shall provide an intuitive, discoverable reports interface with contextual online help, quick-access controls, and hover tooltips for report titles and controls so users can find and understand reporting features without extensive training. Improving discoverability reduces support load and accelerates user productivity across staff roles. Verification includes usability checks for discoverability, presence and usefulness of online help, and demonstration of contextual tooltips and quick-access elements.

*Priority rationale:* Usability issues were frequently reported; integrated help and tooltips greatly improve adoption though they are not strictly blocking for basic functionality.

*Sources:* `evergreen_reference_2009.txt`, `survey_results_2009.txt`

#### REQ-032

**Web-Based Report Writer** · *Functional · Priority: Should*

The system shall provide a web-based report writer enabling staff to create custom reports using an interactive interface with drag-and-drop field selection, basic filtering, and sorting, and the ability to save and reuse report definitions. Staff will use the writer to produce ad-hoc and recurring custom outputs without developer intervention. Verification includes creating a custom report via the web writer, applying filters and sorts, saving the definition, and re-running it successfully. The writer improves productivity and reduces reliance on back-end report development.

*Priority rationale:* A web-based writer greatly improves productivity and is expected by users, but initial operations could proceed with a more limited writer or template editing tools if necessary.

*Sources:* `evergreen_reference_2009.txt`

#### REQ-033

**Hourly Scheduling** · *Functional · Priority: Could*

The system shall optionally support hourly scheduling for reports that require near‑real‑time or high-frequency automation. Operational staff will use hourly scheduling for short-interval monitoring or operational dashboards where frequent updates are needed. Verification includes scheduling a report with an hourly cadence and confirming repeated execution at the hourly interval. Hourly scheduling is an advanced capability useful for some operational scenarios but is not required for typical governance reporting.

*Priority rationale:* Hourly scheduling is useful for some monitoring scenarios but is not broadly required and can be deferred if necessary.

*Sources:* `evergreen_reference_2009.txt`

#### REQ-034

**Upload Filtering Support** · *Functional · Priority: Could*

The system shall allow users to upload text files (for example, lists of barcodes or transaction control numbers) to use as filter input when running reports. Staff performing targeted analyses (batch lookups, pull lists, or reconciliation) will use this to restrict report results to the uploaded identifiers. Verification includes uploading a text file of identifiers, running a report using the uploaded list as a filter, and confirming the results include only matching Items or transactions. This capability streamlines list-based reporting and eliminates manual entry.

*Priority rationale:* Upload-based filtering is a valuable convenience that saves time for list-based tasks but is not essential for general reporting.

*Sources:* `evergreen_reference_2009.txt`

### Material Volume & Collection Reporting

#### REQ-035

**Acquisition Date Tracking For Items** · *Functional · Priority: Must*

The system shall record and maintain an acquisition date attribute for each Item to enable counting new acquisitions and supporting historical Item queries. Cataloging staff or import processes shall set this attribute at Item creation or via batch updates so that Item reports and date-filtered queries can reliably identify Items added in a given period. This attribute underpins point-in-time reporting and new-acquisitions counts and must be verifiable by inspecting Item records for a populated acquisition date and by running queries that return Items within a specified acquisition date range. Verification is by inspecting Item records and running acquisition-date filtered Item reports.

*Priority rationale:* Acquisition date is required to produce accurate new-acquisition Item counts and historical reports.

*Sources:* `conversations/conv_pines014_material_volume.eml`

#### REQ-036

**Location Filter For Item Reports** · *Functional · Priority: Must*

The system shall allow users running Material Item Reports to restrict Item counts and breakdowns to one or more library locations by filtering on Item location. Branch staff and system administrators use this capability to produce per-branch statistics and verify inventory and holdings at the chosen scope. The filter shall apply consistently to totals and all category subtotals so location-specific Item reports reconcile with Item records. Verification is by running the same Item report with different location filters and confirming counts match Item records with the corresponding location attribute.

*Priority rationale:* Location scoping is fundamental to accurate per-branch reporting.

*Sources:* `conversations/conv_pines014_material_volume.eml`

#### REQ-037

**Material Item Report** · *Functional · Priority: Must*

The system shall provide a Material Item Report that shows current Item counts in the selected scope and a set of consistent subtotals and breakdowns including total unique-Item count, total Hold counts, and per-category Hold counts; the report must also present Item status subtotals such as Checked In, Checked Out, Missing, Damaged, and Lost and support both overlapping and mutually-exclusive bucket views. Administrators and collection staff will use the report to reconcile holdings, understand demand signaled by Holds, and prioritize collection and fulfillment actions; the report shall define the total as the count of unique Items in scope, present clearly-labelled subtotals that may overlap the total, and provide an alternative mutually-exclusive bucketing mode where every Item (and its Hold associations) appears in exactly one bucket. Verification includes running the Material Item Report for a library, reconciling the unique-Item total against Item records, validating that the Hold total equals the sum of all per-category Hold counts, and demonstrating that the overlapping and exclusive-bucket presentations reconcile to the underlying Item attributes and Hold linkage.

*Priority rationale:* Material holdings and Hold counts are core operational metrics required by collection management and fulfillment workflows.

*Sources:* `conversations/conv_pines014_material_volume.eml`, `early_draft_srs_galecia.txt`, `interview_cataloging_2009-05-08.txt`

#### REQ-038

**Customizable Category Definitions** · *Functional · Priority: Should*

The system shall allow administrators to define and manage the categories used for breakdowns in Material Item Reports, including creating, editing, and deleting category definitions and mapping Item attributes to those categories. Administrators use this capability to reflect local taxonomies and ensure reports present meaningful groupings across different libraries. The feature shall allow category changes to be applied to subsequent reports while preserving the ability to compare historical outputs where applicable. Verification is by configuring categories, running Item reports, and confirming Items are aggregated into the configured categories as expected.

*Priority rationale:* Configurable categories allow local relevance of Item breakdowns without changing the underlying reporting engine.

*Sources:* `conversations/conv_pines014_material_volume.eml`

#### REQ-039

**Point-In-Time Item Reporting** · *Functional · Priority: Should*

The system shall allow users to view Item counts as of a specified date/time or over a date range so staff and administrators can perform historical comparisons and trend analysis. This feature supports monthly and annual comparisons and lets users understand how Item counts changed between snapshots. The implementation shall produce results traceable to acquisition dates and transaction records and may leverage a Reporting Warehouse or archived snapshots to avoid impacting live operations. Verification is by running date-filtered Item-count queries and comparing outputs to archived acquisition and transaction data or reporting snapshots.

*Priority rationale:* Historical Item views are valuable for audits and trend analysis but can be implemented after core real-time reporting.

*Sources:* `conversations/conv_pines014_material_volume.eml`

### Capacity & Shelf-space Analysis

#### REQ-040

**Automated Shelf-space and Capacity Reports** · *Functional · Priority: Must*

The system shall automate generation and scheduled delivery of shelf-space, inventory, and capacity reports (including daily runs where needed) to reduce manual spreadsheet work and provide timely data for operations. Automation shall support running reports per-library or per-system, produce the configured outputs, and optionally deliver results to authorized users or allow download. This reduces manual effort, supports daily operational workflows, and ensures consistent, reproducible reports. Verification is by scheduling a report and confirming it runs on schedule, produces the expected output, and is available for download or delivery.

*Priority rationale:* Stakeholders currently run daily manual reports; automation is necessary to remove tedious manual work and meet daily operational needs.

*Sources:* `conversations/conv_pines016_shelf_space.eml`, `meeting_minutes/meeting_2009-07-20_minutes.txt`

#### REQ-041

**Branch Drill-Down** · *Functional · Priority: Must*

The system shall allow users to drill down from the high-level overview into individual branch details so branch managers and planners can inspect local capacity and underlying contributors. Drill-downs shall expose the metrics and records that explain a branch's status (counts, recent changes, and related metrics). This enables targeted operational follow-up and troubleshooting without leaving the capacity interface. Verification is by selecting a branch from the overview and confirming the detailed branch page displays expected metrics and supporting data.

*Priority rationale:* Users need per-branch details to act on overview findings; drill-down is required for usefulness.

*Sources:* `conversations/conv_pines015_capacity_interface.eml`

#### REQ-042

**Capacity View Grouping and Filtering** · *Functional · Priority: Must*

The system shall support grouping, sorting, and filtering of capacity views by attributes such as system/region, library type, and current load so users can focus on relevant subsets of locations. Users (planners and directors) shall be able to combine grouping and filters and choose sort orders to manage large lists of branches. This capability improves readability and usability when the system contains many locations. Verification is by applying groupings, filters, and sorts and confirming the displayed branch list reflects the selected criteria and order.

*Priority rationale:* Needed for usability at scale (hundreds of locations) and explicitly requested in multiple candidates.

*Sources:* `conversations/conv_pines015_capacity_interface.eml`

#### REQ-043

**Centralized Data Aggregation** · *Functional · Priority: Must*

The system shall aggregate capacity and shelf-space related data from the centralized data store to produce system-level and branch-level metrics for reporting and display. Aggregation will ensure consistent metrics across views and reduce load on operational transaction services by using the canonical central data source for queries. This supports accurate cross-branch comparisons and historic calculations. Verification is by running aggregation queries against the central store and confirming report and overview numbers match the aggregated source data.

*Priority rationale:* Aggregation from the central data store is necessary to produce accurate system-wide and per-branch metrics.

*Sources:* `conversations/conv_pines015_capacity_interface.eml`

#### REQ-044

**Define Capacity Metrics** · *Functional · Priority: Must*

The system shall provide a formal definition and configuration mechanism for the metrics used to measure capacity so stakeholders have a shared understanding before building and using the interface. This includes defining what counts toward capacity, thresholds, and the derivation rules so displays and reports are consistent and auditable. Clear metric definitions reduce disputes and guide verification of data quality. Verification is by reviewing the metric definitions configuration and confirming calculated metrics match the documented definitions on sample data.

*Priority rationale:* Stakeholders identified metric definition as a prerequisite for building the interface and for consistent reporting.

*Sources:* `conversations/conv_pines015_capacity_interface.eml`

#### REQ-045

**Global Capacity Overview** · *Functional · Priority: Must*

The system shall present a high-level overview of capacity for all branches so system administrators and planners can assess overall utilization at a glance. The overview shall summarize each branch's capacity and current load to support rapid triage and planning. This capability is intended to give a single-pane view that helps prioritize follow-up actions and identify hotspots across the network. Verification is by viewing the overview and confirming all branches and summary metrics are present and updated from the system data store.

*Priority rationale:* Stakeholders explicitly requested a single overview of all branches and it is a basic operational need for capacity management.

*Sources:* `conversations/conv_pines015_capacity_interface.eml`, `early_draft_srs_galecia.txt`

#### REQ-046

**Per-Library and System Reporting** · *Functional · Priority: Must*

The system shall run shelf-space and capacity reports at both the library (branch) level and the system level and shall provide comparison views (side-by-side breakdowns and system-average comparisons) so branch managers and directors can assess local performance versus peers and the system average. Reporting shall support grouping by library and by system as selectable options and shall offer a comparison display that aligns metrics across selected libraries. This aids quarterly reviews and decision-making by providing consistent per-branch and aggregate perspectives. Verification is by running the same report at branch and system scopes and confirming the comparison view correctly aligns and highlights differences and averages.

*Priority rationale:* Directors and branch managers requested both per-library and per-system views and comparisons for regular reviews.

*Sources:* `conversations/conv_pines016_shelf_space.eml`

#### REQ-047

**Shelf-space Estimation** · *Functional · Priority: Must*

The system shall estimate shelf-space from item dimensions when those dimensions are available and use item count as a configurable proxy when dimensions are missing so shelf-space percentages can be produced even though shelf position is not tracked. Estimation logic shall be configurable and documented so administrators can choose the preferred proxy method for their collections. This enables calculation of shelf-space percentages required by reports while accommodating incomplete item metadata. Verification is by comparing calculated shelf-space values against sample items with known dimensions and verifying the proxy produces expected totals when dimensions are absent.

*Priority rationale:* Shelf-space percentages are a core report output; an estimation approach is necessary because actual shelf-space is not tracked.

*Sources:* `conversations/conv_pines016_shelf_space.eml`

#### REQ-048

**Shelf-space Metrics Report** · *Functional · Priority: Must*

The system shall generate a shelf-space metrics report by genre and format that shows, for each genre/format, the percentage of total circulations, the percentage of the collection, and the percentage of total shelf-space so librarians can evaluate allocation and demand. The report shall compute collection percentages by counting items per genre/format and compute circulation percentages by summing checkouts per genre/format. Shelf-space percentages shall reflect the shelf-space estimation method configured for the system. Verification is by running the report and confirming the three percentage columns reproduce expected values on a test dataset.

*Priority rationale:* Stakeholders explicitly requested these three comparative percentages and use them for collection planning; without them the feature would not meet requirements.

*Sources:* `conversations/conv_pines016_shelf_space.eml`, `early_draft_srs_galecia.txt`, `interview_cataloging_2009-05-08.txt`

#### REQ-049

**Analyze Capacity and Recommend Distribution** · *Functional · Priority: Should*

The system shall provide analysis tools that help evaluate branch capacity and suggest optimal distribution adjustments for the collection so planners can consider reallocation opportunities. Analysis may include identifying over- and under-served branches and modeling the effect of redistributing items or adjusting allocation rules. Recommendations shall be presented as scenarios that staff can review rather than as automated deletions or transfers. Verification is by running the analysis on sample data and confirming the tool identifies imbalances and presents plausible redistribution scenarios.

*Priority rationale:* Analysis and recommendation aid planning and were requested historically, but represent advanced functionality that can follow core reporting and visibility features.

*Sources:* `meeting_minutes/meeting_2009-03-15_minutes.txt`

#### REQ-050

**Color-Coded Capacity Status** · *Functional · Priority: Should*

The system shall display capacity status using color-coding (for example, green for under capacity, yellow for nearing capacity, and red for at/over capacity) so staff can rapidly identify branches that require attention. Color assignments shall be driven by configurable thresholds so different systems or regions can tune the meaning of each color. This visual encoding supports faster triage and communication across operational teams. Verification is by configuring thresholds and confirming branches render with the expected colors as metrics cross thresholds.

*Priority rationale:* Requested by stakeholders for quick triage; valuable but not strictly required for initial functionality.

*Sources:* `conversations/conv_pines015_capacity_interface.eml`

#### REQ-051

**Trend and Time-Range Analysis** · *Functional · Priority: Should*

The system shall provide trend analysis and time-range filtering for capacity and shelf-space metrics so planners can observe growth, shrinkage, seasonal effects, and period-to-period comparisons. Users shall be able to select date ranges and common seasonal groupings (quarters, seasons) to view trends and compare intervals. This supports planning, reporting, and seasonal adjustments in the collection. Verification is by selecting time ranges and seasonal groupings and confirming trend charts and aggregates reflect the selected intervals.

*Priority rationale:* Trend and seasonal analysis are important for planning but the system can operate without advanced time-series features at launch.

*Sources:* `conversations/conv_pines015_capacity_interface.eml`, `conversations/conv_pines016_shelf_space.eml`

#### REQ-052

**Export Capacity Data** · *Functional · Priority: Could*

The system shall allow users to export capacity and shelf-space data to CSV so analysts can perform offline analysis or include figures in external reports. Exported files shall contain the selected fields and respect applied filters, groupings, and date ranges. This provides a simple interoperability mechanism for teams that prefer spreadsheets or downstream systems. Verification is by exporting a CSV and validating the file structure, contents, and filter adherence.

*Priority rationale:* Export is a common convenience feature; useful but not strictly required for core functionality.

*Sources:* `conversations/conv_pines015_capacity_interface.eml`

### Item Transfer & Relocation Utility

#### REQ-053

**Auto Revert And Event-Based Revert** · *Functional · Priority: Must*

The system shall support automatic and event-based reversion of transferred Items to their original location according to configurable rules, including time-based (revert after N days), event-based (revert when an Item is returned or when checked out at destination), and program/event duration semantics for temporary transfers. This supports use cases such as mobile/outreach collections and temporary relocations and prevents permanent misplacement of Items moved for short-term purposes. Verification is by configuring revert rules, performing transfers and triggering the scheduled task or event to observe Items returning to their original location as configured. Typical users are transfer coordinators and collection managers.

*Priority rationale:* Stakeholders flagged automatic and event-driven revert behavior as high priority to support temporary transfers and prevent long-term data drift; the ability to revert is central to temporary relocation workflows.

*Sources:* `conversations/conv_pines018_item_transfer.eml`, `interview_cataloging_2009-05-08.txt`, `survey_results_2009.txt`

#### REQ-054

**Batch Processing Efficiency** · *Non-functional · Priority: Must*

The system shall execute large batch updates using a controlled batching strategy (for example, chunked updates or background jobs) to avoid long locks on the OLTP database and to allow progress reporting and restart after transient failures. This preserves system responsiveness and protects concurrent operations while enabling large transfers. Verification is by running a large transfer job and observing that work is split into smaller update batches with logging, progress metrics and no prolonged database locks. Typical implementers are system administrators and developers responsible for operations.

*Priority rationale:* Avoiding database locking and ensuring reliable completion of large batch jobs is essential for system stability and was specifically requested by operational stakeholders.

*Sources:* `conversations/conv_pines018_item_transfer.eml`

#### REQ-055

**Batch Transfer Utility** · *Functional · Priority: Must*

The system shall provide a batch transfer utility that lets authorized staff create, run and monitor transfer jobs that move sets of Items between locations, coordinating query selection, manual selection, preview, and execution steps. The utility centralizes the batch workflow for common scenarios (mobile libraries, outreach programs, temporary moves) and provides a single place to manage job status and basic error reporting. Verification is by creating a transfer job in the utility and observing expected lifecycle states (queued, running, completed, failed) and results applied to Items. Typical users include transfer coordinators and administrators.

*Priority rationale:* An explicit transfer utility is the orchestrator for the other required capabilities and was requested in multiple sources; without it operations would be ad hoc and error-prone.

*Sources:* `conversations/conv_pines018_item_transfer.eml`, `early_draft_srs_galecia.txt`

#### REQ-056

**Change Item Location** · *Functional · Priority: Must*

The system shall change the location field on selected Item records to implement a transfer from one location to another, updating any related metadata required to reflect the move. This enables staff to effect the transfer of Items between locations and ensures downstream services (holds, circulation) see the new location. Verification is by performing a batch location change and confirming Item records show the new location and related indices reflect the change. Typical users are transfer coordinators and administrators executing moves.

*Priority rationale:* Applying the new location to Item records is the essential operation that implements a transfer and is requested across interviews and surveys.

*Sources:* `conversations/conv_pines018_item_transfer.eml`, `interview_cataloging_2009-05-08.txt`, `survey_results_2009.txt`

#### REQ-057

**Manual Selection From Results** · *Functional · Priority: Must*

The system shall allow staff to manually select or deselect Items from query results (for example via checkboxes) so that the final set included in a transfer operation can be curated before any changes are applied. This capability permits targeted exceptions and manual refinement of automated selections. Verification is by running a query, selecting and deselecting Items in the UI, and confirming only chosen Items are included in the subsequent operation. Typical users are cataloging and branch staff preparing pull lists or transfers.

*Priority rationale:* Manual review and selection is routinely required to avoid unwanted moves and was requested by multiple stakeholders; transfers without this would risk erroneous changes.

*Sources:* `conversations/conv_pines018_item_transfer.eml`, `interview_cataloging_2009-05-08.txt`

#### REQ-058

**Query Candidate Items** · *Functional · Priority: Must*

The system shall provide a query capability and interactive query builder that staff can use to locate candidate Items for transfer by arbitrary selection criteria (status, circulation history, genre, location, dimensions, etc.). This enables staff to define precise selection sets for batch operations and reduces manual lookup effort. Verification is by creating queries with the builder, running them and confirming the returned Item set matches the criteria. Typical users include cataloging and collection management staff performing selection for transfers or purges.

*Priority rationale:* Selecting candidate Items is foundational for any batch transfer workflow and was requested by multiple stakeholders and surveys.

*Sources:* `conversations/conv_pines018_item_transfer.eml`, `interview_cataloging_2009-05-08.txt`, `survey_results_2009.txt`

#### REQ-059

**Role-Based Transfer Permissions** · *Functional · Priority: Must*

The system shall enforce Role-based Access Control for transfer utilities so only users assigned appropriate roles can create, approve, run, undo or schedule transfer jobs and access associated audit data. This prevents unauthorized bulk changes and aligns transfer privileges with institutional policies. Verification is by attempting transfer operations with users in different roles and confirming permissions are enforced according to role assignments. Typical roles include transfer coordinators, managers and administrators.

*Priority rationale:* Stakeholders explicitly marked transfer permission limits as critical; RBAC is essential to prevent misuse and enforce governance.

*Sources:* `conversations/conv_pines018_item_transfer.eml`

#### REQ-060

**Save And Schedule Queries** · *Functional · Priority: Must*

The system shall allow staff to save query definitions as reusable Report Templates and to schedule saved queries to run automatically on a recurring cadence (for example, monthly) producing candidate Item lists or jobs. This supports recurring collection management tasks (e.g., monthly moves based on circulation inactivity) without reauthoring selection criteria each time. Verification is by saving a Report Template, executing it on demand, and configuring a recurring schedule that produces expected results. Administrators and designated staff will create, manage and subscribe to these saved and scheduled queries.

*Priority rationale:* Saved and recurring queries were marked critical by stakeholders and are required to support routine, scheduled transfer workflows with low manual overhead.

*Sources:* `conversations/conv_pines018_item_transfer.eml`, `interview_cataloging_2009-05-08.txt`

#### REQ-061

**Transfer Audit Logging** · *Functional · Priority: Must*

The system shall record audit logs for all transfer operations including who initiated the transfer, timestamp, Items affected, source and destination locations and any automated revert actions so transfers can be reviewed and investigated. Audit logging provides accountability and supports troubleshooting, compliance and operational reporting. Verification is by performing transfer operations and reviewing audit records that capture the required fields and are immutable to regular staff. Typical users include managers and auditors.

*Priority rationale:* Auditability is required for operational accountability and was repeatedly requested; it is essential for safe bulk changes and compliance.

*Sources:* `conversations/conv_pines018_item_transfer.eml`

#### REQ-062

**Preview Transfer Changes** · *Functional · Priority: Should*

The system shall present a preview of the exact Item-level changes that will occur before applying a batch transfer, including counts, source and destination locations and a sample of affected Items, and require explicit confirmation to proceed. This reduces risk of accidental bulk changes and supports staff verification and sign-off. Verification is by initiating a transfer job and observing the preview screen that lists proposed changes and requires confirmation before committing. Typical users include transfer coordinators and managers.

*Priority rationale:* A preview significantly reduces operator error and is expected, but a transfer could be performed with manual verification as a workaround if preview is unavailable at launch.

*Sources:* `conversations/conv_pines018_item_transfer.eml`

#### REQ-063

**Pull List Generation** · *Functional · Priority: Should*

The system shall generate printable pull lists for selected Items intended to be physically moved, showing identifiers, locations and any handling notes to assist staff in locating and packing Items. Pull lists support the physical workflow of retrieving Items that will be transferred and reduce handling errors. Verification is by producing a pull list from a selected Item set and confirming required fields (Item id, title, current location) appear and the list is printable. Typical users are circulation assistants and branch staff performing item pulls.

*Priority rationale:* Pull lists are widely used to support physical workflows and expected by staff, but the system can operate without them if staff use exported reports as a workaround.

*Sources:* `conversations/conv_pines018_item_transfer.eml`

#### REQ-064

**Transfer History Per Item** · *Functional · Priority: Should*

The system shall maintain and expose a transfer history for each Item so staff can see a chronological record of past transfers, including dates, source/destination locations and the initiating user or job. This helps staff understand movement patterns and diagnose item-location anomalies. Verification is by viewing an Item record and confirming the transfer history entries match past transfer events. Typical users are branch staff and collection managers reviewing Item provenance.

*Priority rationale:* Per-Item history is valuable for local investigation and collection analysis; audit logs provide the underlying data, but a dedicated per-Item view improves usability and can be delivered after core auditing.

*Sources:* `conversations/conv_pines018_item_transfer.eml`

#### REQ-065

**Undo Transfer Operation** · *Functional · Priority: Should*

The system shall provide an undo capability that allows authorized staff to revert a recently-executed transfer operation as a single logical action, restoring Item locations and associated metadata to the prior state when safe to do so. This reduces remediation effort after operator error and should be restricted to recent operations to prevent complex conflict scenarios. Verification is by executing a transfer and then performing the undo action to confirm Items and related state are reverted correctly. Typical users are transfer coordinators and managers.

*Priority rationale:* An immediate undo greatly reduces recovery time after mistakes and was requested by staff, but it can be implemented after core transfer and revert automation if necessary.

*Sources:* `conversations/conv_pines018_item_transfer.eml`

#### REQ-066

**Transfer Delay Alerts** · *Functional · Priority: Could*

The system shall provide alerts or notifications to designated staff when transfer jobs are delayed, fail, or otherwise encounter issues (for example long-running jobs, failed batches, or Items flagged as problematic) so staff can take corrective action. Alerts help maintain operational SLAs and reduce lost Items due to unresolved issues. Verification is by simulating a transfer failure or delay and confirming configured recipients receive notifications with useful diagnostics. Typical recipients are transfer coordinators and administrators.

*Priority rationale:* Alerts are useful for operational responsiveness but are not strictly required for basic transfer functionality and can be added after core features.

*Sources:* `conversations/conv_pines018_item_transfer.eml`

#### REQ-067

**Transit Labels Generation** · *Functional · Priority: Could*

The system shall generate transit labels (including printable barcodes and destination information) for Items being transferred so that Items can be tracked while in transit between locations. Labels improve handling accuracy and enable scanning during departure and arrival events. Verification is by generating and printing transit labels for a transfer job and scanning them during departure/arrival to confirm matched Item and destination. Typical users are staff preparing shipments and couriers handling Items.

*Priority rationale:* Transit labels are a useful convenience for handling and tracking but are not strictly required to complete transfers; smaller organizations may use manual labels initially.

*Sources:* `conversations/conv_pines018_item_transfer.eml`

### Missing/Damaged & In-Transit Reporting

#### REQ-068

**Items Currently In Transit Report** · *Functional · Priority: Must*

The system shall generate a unified report that lists Item records currently in transit per branch and per system, identifying Items that meet the in-transit definition (no recorded arrival date and a departure date older than a configurable threshold) and allowing configurable thresholds and sorting; the report shall present departed-from and pending-arrival records in a single view and permit sorting and filtering to prioritize recovery of delayed Items. Delivery and circulation staff will use this report to identify delayed transfers and take recovery action; the system shall treat Item in-transit state consistently with the Item definition in the glossary and allow the threshold to be configured (defaulting to seven days). Verification is by running the report with test data that includes departure and arrival dates and confirming Items meeting the configured definition are returned at branch and system scopes.

*Priority rationale:* In-transit tracking is operationally essential for transfer coordination and must align with the Item in-transit definition.

*Sources:* `conversations/conv_pines019_020_missing_intransit.eml`, `early_draft_srs_galecia.txt`, `interview_cataloging_2009-05-08.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`

#### REQ-069

**Missing, Damaged And Lost Items Report** · *Functional · Priority: Must*

The system shall generate a report that lists Item records whose status is Missing, Damaged, or Lost and group the results by branch while allowing separate selection or combined views for each status; the report shall treat Lost as a distinct status from Missing and shall return Lost counts as a separate metric. Front-line and management staff will use this report for accountability, collection monitoring, and operational follow-up; distinguishing Lost from Missing enables appropriate recovery, billing, and purge decisions. Verification is by running the report for a branch and confirming Items with each status (Missing, Damaged, Lost) are returned, that Lost counts appear as distinct metrics, and that grouping by branch reflects the Item records' location attributes.

*Priority rationale:* Stakeholders require Lost as a separate status for billing and purge workflows; the report must be verifiable and actionable.

*Sources:* `conversations/conv_pines019_020_missing_intransit.eml`, `early_draft_srs_galecia.txt`, `interview_cataloging_2009-05-08.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`

#### REQ-070

**Date Range Filtering For Missing/Damaged Reports** · *Functional · Priority: Should*

The system shall allow users to specify date-range criteria when generating missing and damaged items reports (for example: last 30 days, last quarter) so staff can produce time-bounded views for trending and period comparisons. Staff and managers will use the filter to analyze trends and operational impact over configurable intervals. The feature supports trending analysis and decision-making about collection actions. Verification is by running the missing/damaged report with different date-range selections and confirming results reflect only items that meet the selected intervals.

*Priority rationale:* Date-range trending was requested by stakeholders and is important for analysis, but core per-branch reporting can operate without it at initial release.

*Sources:* `conversations/conv_pines019_020_missing_intransit.eml`

#### REQ-071

**Separate Missing/Damaged And Items Currently In Transit Reports** · *Functional · Priority: Should*

The system shall present Missing/Damaged and Items currently in transit as distinct report types so staff can run each report without mixing different operational workflows. Circulation and collection staff benefit from separate outputs because missing/damaged Items and Items currently in transit require different follow-up processes. Keeping the reports separate reduces confusion and supports clearer operational procedures. Verification is by confirming that both report types are available independently in the reporting interface and produce separate result sets.

*Priority rationale:* 

*Sources:* `conversations/conv_pines019_020_missing_intransit.eml`

#### REQ-072

**Sort Items Currently In Transit By Due Date** · *Functional · Priority: Should*

The system shall provide an option to sort the Items currently in transit report by due date so staff can prioritize chasing the oldest expected arrivals first. Delivery and circulation staff will use this sort to sequence follow-up actions efficiently. Sorting supports reducing transfer delays and improving customer service. Verification is by running the Items currently in transit report and applying the due-date sort, confirming the returned rows are ordered from oldest to newest due date.

*Priority rationale:* 

*Sources:* `conversations/conv_pines019_020_missing_intransit.eml`

#### REQ-073

**Analytics For Missing Item Patterns** · *Functional · Priority: Could*

The system shall provide analytics that identify patterns in missing items (for example by shelf, location, time period, or branch) to support collection health assessment and targeted interventions. Collection development, cataloging, and branch management staff will use these analytics to detect recurring loss points, inform relocations, and prioritize preservation or security measures. Pattern analytics improve long-term collection stewardship and reduce repeat losses. Verification is by running the analytics on test data and confirming the output highlights recurring attributes (shelf/location, time windows, or branch clusters) associated with missing items.

*Priority rationale:* Pattern analysis was requested but is an advanced capability that improves long-term planning; it is not essential for initial reporting and delivery coordination.

*Sources:* `interview_cataloging_2009-05-08.txt`

#### REQ-074

**Include Item Condition Notes** · *Functional · Priority: Could*

The system shall include item condition notes as a display field in missing and damaged items reports so staff see qualitative details (for example: 'water damage', 'vandalism') alongside the item record. Collection and circulation staff will use condition notes to triage repairs, replacements, or further investigation. Providing condition notes improves triage speed and auditability of reported damage. Verification is by running the report and confirming the condition notes field is present and populated per item when notes exist.

*Priority rationale:* Stakeholders requested condition notes for context; useful but not essential to run basic missing/damaged workflows at launch.

*Sources:* `conversations/conv_pines019_020_missing_intransit.eml`

### Purging, Deletion & Audit Trail

#### REQ-075

**Deletion Audit Logging** · *Functional · Priority: Must*

The system shall record every deletion-related event in an audit log that persists the record identifier, record type, timestamp, user identity, user location, whether the attempt was denied, and the stated reason for deletion where provided. Administrators and auditors shall be able to rely on the audit log to establish accountability, to troubleshoot why a record disappeared, and to detect unauthorized deletion attempts. The audit log shall be stored in a queryable audit store so events are retained for review according to policy and so reports can aggregate deletion reasons across time and locations. Verification is by performing deletions and denied-deletion attempts and then querying the audit log to show records with the required fields, timestamps, and deletion-reason values.

*Priority rationale:* 

*Sources:* `conversations/conv_pines021_item_purging.eml`, `conversations/conv_pines022_deletions.eml`, `interview_cataloging_2009-05-08.txt`

#### REQ-076

**Deletion Confirmation Step** · *Functional · Priority: Must*

The system shall require an explicit, separate confirmation step before performing any deletions that permanently remove records or Item records, and shall reference Purge Candidate lists and Last Copy protections as part of the confirmation flow so staff see relevant safeguards before committing. Staff initiating deletions shall be required to confirm the operation and any selected options to prevent accidental data loss; the confirmation UI shall surface Last Copy flags, related Hold counts where relevant, and a clear summary of records to be removed. Verification is by initiating a deletion and showing that the system halts to request explicit confirmation, displays Last Copy and Hold-related safeguards, and only proceeds after a separate confirmed action.

*Priority rationale:* Explicit confirmation is essential to prevent accidental destructive actions and to surface safeguards required by policy.

*Sources:* `conversations/conv_pines021_item_purging.eml`

#### REQ-077

**Item Purging Utility** · *Functional · Priority: Must*

The system shall provide a purging utility and associated reports that identify Purge Candidates using saved or ad-hoc selection criteria and present those results in read-only form for staff review prior to any deletion action. Collection management staff shall use the utility to review and export lists of purge-eligible Item records and other record types before destructive actions are taken, enabling consistent identification and human review of Purge Candidates. Verification is by running the utility to produce lists of Purge Candidates that match configured criteria and by demonstrating saved Report Templates that reproduce those lists.

*Priority rationale:* Purging requires careful, verifiable review of Item-level candidates and must be presented read-only prior to deletion to prevent accidental data loss.

*Sources:* `conversations/conv_pines021_item_purging.eml`, `early_draft_srs_galecia.txt`, `interview_cataloging_2009-05-08.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`

#### REQ-078

**Last Copy Detection And Reports** · *Functional · Priority: Must*

The system shall detect and flag Items that are the Last Copy within a defined scope and provide Last Copy reports scoped to either a library or the entire system so catalogers and managers can avoid removing sole remaining copies. Cataloging and collection staff shall use the Last Copy flags and reports to prevent accidental deletion of the final instance of a Bibliographic Record. This supports preservation of access and assists tasks such as safe WorldCat editing. Verification is by running Last Copy reports for both library and system scopes and by showing Items flagged as Last Copy matching the expected counts.

*Priority rationale:* Last Copy protections are necessary to preserve access and prevent accidental loss of all copies.

*Sources:* `conversations/conv_pines021_item_purging.eml`, `interview_cataloging_2009-05-08.txt`

#### REQ-079

**Purge Candidate Read-Only Display** · *Functional · Priority: Must*

The system shall present purge-candidate lists in read-only form so staff may review and export candidate lists without risk of inadvertent modification. Frontline staff and managers shall use the read-only view to verify candidates before any destructive operation. This preserves data integrity and provides a clear review step for purging workflows. Verification is by opening a purge-candidate list and demonstrating that list rows cannot be edited from the candidate view.

*Priority rationale:* A non-editable review stage is critical to prevent accidental deletions and is explicitly requested by stakeholders.

*Sources:* `conversations/conv_pines021_item_purging.eml`

#### REQ-080

**Purge Criteria: Status/Time/Activity** · *Functional · Priority: Must*

The system shall support purge criteria based on item status, time-in-status, and recent activity so staff can select items such as those missing for a configurable interval or not circulated within a defined period. Circulation and item-management staff shall be able to configure and apply these criteria when running purge reports or templates. This enables targeting of stale or inactive items while preserving items that remain in active use. Verification is by configuring each criterion type and demonstrating that purge-candidate results include only items matching the configured values.

*Priority rationale:* Status, time, and activity criteria are repeatedly requested by stakeholders and are necessary to identify appropriate purge candidates.

*Sources:* `conversations/conv_pines021_item_purging.eml`, `interview_cataloging_2009-05-08.txt`

#### REQ-081

**Record Deletion Utilities** · *Functional · Priority: Must*

The system shall provide deletion utilities that allow authorized staff to remove bibliographic records together with their attached item records and to delete bibliographic records that have no attached items. Cataloging and technical-services staff shall use these utilities to clean orphaned records and to remove records plus their associated items where a bulk removal is required. This capability reduces manual cleanup time and helps maintain catalog quality. Verification is by executing deletion utilities on test records and confirming that targeted bibliographic records and their associated items are removed as specified.

*Priority rationale:* Efficient removal of orphaned records and coordinated deletion of records with their items is repeatedly requested and necessary for catalog maintenance.

*Sources:* `conversations/conv_pines021_item_purging.eml`, `interview_cataloging_2009-05-08.txt`

#### REQ-082

**Audit Reporting And Aggregation** · *Functional · Priority: Should*

The system shall provide a report interface and aggregation functions for deletion audit data so managers can view deletions by location, by system, by record type, by user, and by date range, and can produce totals for reporting periods. Managers and auditors shall be able to run canned or ad-hoc reports and save report templates for recurring needs. These reports support oversight, compliance, and operational analysis such as identifying top deleting users or monthly deletion totals. Verification is by running the audit reports to produce aggregated views and templates that include the requested dimensions and period totals.

*Priority rationale:* Audit reporting is important for oversight and was widely requested; however, basic audit logging is prioritized for initial release and more advanced aggregation can follow.

*Sources:* `conversations/conv_pines022_deletions.eml`, `early_draft_srs_galecia.txt`, `interview_cataloging_2009-05-08.txt`, `survey_results_2009.txt`

#### REQ-083

**Batch Status Conversion** · *Functional · Priority: Should*

The system shall provide a batch status-conversion capability that updates the status of multiple Items in a single operation based on a selection or report output. Circulation and cataloging staff shall use batch conversion to implement policy-driven status changes (for example, marking many Items as Purge Candidate after review). This reduces repetitive manual work and ensures consistent application of status values. Verification is by selecting a set of Items, performing a batch status change, and confirming that all selected Items have the new status.

*Priority rationale:* Batch status changes streamline operational workflows such as identifying Purge Candidates, but immediate deletion is controlled elsewhere.

*Sources:* `conversations/conv_pines021_item_purging.eml`, `interview_cataloging_2009-05-08.txt`

#### REQ-084

**Combine Purge Criteria** · *Functional · Priority: Should*

The system shall allow staff to combine multiple purge criteria with logical operators (e.g., AND) so that purge-candidate sets can be narrowed to meet precise policies. Collection management staff use boolean combinations to express compound policies such as items in a given status for an interval AND lacking recent circulation. Combining criteria reduces false positives and improves the accuracy of purge lists. Verification is by constructing a compound query and showing that only items satisfying all combined conditions appear as purge candidates.

*Priority rationale:* Combining criteria is important and expected for precise selection but a manual multi-step workflow can be used as a fallback for initial deployments.

*Sources:* `conversations/conv_pines021_item_purging.eml`

#### REQ-085

**Purge Scheduling** · *Functional · Priority: Should*

The system shall support scheduling of purge-report generation so administrators can run candidate-generation automatically at configured intervals; scheduled runs shall generate read-only Purge Candidate reports rather than automatically performing deletions. Administrators shall be able to define schedule frequency and choose saved Report Templates or queries to run on schedule; any automated deletion action initiated by a schedule must require an explicit confirmation step at run time and comply with Last Copy protections. Scheduling reduces manual effort for routine maintenance while preserving a review-and-confirm safety barrier before any destructive operation. Verification is by creating a schedule that executes a saved purge Report Template and by showing scheduled-run outputs as read-only Purge Candidate lists and demonstrating that deletion does not occur without an explicit confirmation step.

*Priority rationale:* Automated candidate generation is useful for maintenance, but deletions must remain explicitly confirmed for safety.

*Sources:* `conversations/conv_pines021_item_purging.eml`

### Patron Demographics & Inactivity Reporting

#### REQ-086

**Anonymized Demographic Statistics** · *Functional · Priority: Must*

The system shall produce demographic statistics (for example transactions by geographic region and age ranges) suitable for program planning while anonymizing data so that personally identifiable information is not disclosed in statistical outputs. Analysts and program planners will use anonymized aggregates to inform decisions without exposing individual patron identities. Anonymization must remove or obfuscate identifying fields and adhere to privacy policies before data export or dashboard display. Verification: generate demographic reports and confirm output contains only aggregated or anonymized values and that sampled outputs do not allow re-identification of individual patrons.

*Priority rationale:* Privacy-preserving statistics were explicitly required and are often mandated by policy; anonymization is essential before sharing demographic outputs.

*Sources:* `early_draft_srs_galecia.txt`, `meeting_minutes/meeting_2009-03-15_minutes.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `survey_results_2009.txt`

#### REQ-087

**Combine Filters With Boolean Logic** · *Functional · Priority: Must*

The system shall allow staff to combine multiple demographic filters using AND and OR Boolean logic when constructing queries and report criteria. This capability enables complex selections such as patrons in a zip code AND within a given age range or patrons in one of several counties. Report authors and analysts will use Boolean combinations to tailor cohorts precisely. Verification: construct queries using AND and OR combinations and confirm returned results match the logical expression.

*Priority rationale:* Stakeholders explicitly requested AND/OR combinations to support real-world queries; without it many selections cannot be expressed.

*Sources:* `conversations/conv_pines023_patron_characteristics.eml`

#### REQ-088

**Configurable Age Ranges** · *Functional · Priority: Must*

The system shall allow configuring age ranges used for filtering and grouping, where the system computes age at query time from the birth_date field and maps patrons into the configured bins. This allows reports to use age buckets that match program or analysis needs (for example, 0-5, 6-10, 11-17, etc.). Administrators or report authors will define ranges per report or template as needed. Verification: create a report with custom age bins and confirm patrons are placed in bins derived from birth_date as configured.

*Priority rationale:* Custom age bins are necessary for accurate demographic reporting and were requested explicitly; computing from birth_date avoids data-entry inconsistencies.

*Sources:* `conversations/conv_pines023_patron_characteristics.eml`

#### REQ-089

**Configure Inactivity Window** · *Functional · Priority: Must*

The system shall allow administrators to configure the inactivity cutoff (the X-day window) used by inactive patron reports, including providing common presets (for example 30, 90, 180, 365) and allowing fully custom day values. Configurability enables libraries to apply business rules that match local retention and outreach policies. Administrators or authorized reporting staff will set the value when creating or scheduling reports. Verification: change the inactivity window to a preset and a custom value and confirm the generated list reflects the configured cutoff.

*Priority rationale:* Stakeholders noted varying operational practices (monthly, quarterly, annual) and explicitly requested configurable and custom cutoffs; this is required for correct operational behavior.

*Sources:* `conversations/conv_pines024_inactive_patrons.eml`

#### REQ-090

**Filter By Patron Characteristics** · *Functional · Priority: Must*

The system shall allow staff to limit query results and reports by patron characteristics including age range, zip code, county of residence, home branch, patron type, and preferred language. This enables targeted analysis and outreach by permitting precise selections of patron subsets. Administrators and reporting staff will use the filter controls when creating or running reports to narrow result sets. Verification: run reports with each filter and confirm returned patrons match the selected characteristic values.

*Priority rationale:* Multiple stakeholders explicitly requested these filters as critical for reporting and outreach; basic filtering is required for usable reporting.

*Sources:* `conversations/conv_pines023_patron_characteristics.eml`, `early_draft_srs_galecia.txt`

#### REQ-091

**Generate Inactive Patrons List** · *Functional · Priority: Must*

The system shall generate a report listing patrons whose most recent activity (including circulation and electronic activity) is older than a configurable X-day cutoff, where electronic activity is aggregated across defined sources such as OPAC logins, online holds, online renewals, and digital resource access. Staff use this list to identify accounts for outreach, reactivation, or administrative handling. The system will aggregate activity across sources so the last-activity basis for each patron is accurate. Verification: run the report with a known dataset and confirm that patrons with no qualifying activity within X days are listed and that electronic activity sources contribute to last-activity calculations.

*Priority rationale:* Inactive patron reporting was requested by multiple stakeholders and is essential for account maintenance and outreach; it requires including electronic activity and correct last-activity determination.

*Sources:* `conversations/conv_pines024_inactive_patrons.eml`, `early_draft_srs_galecia.txt`

#### REQ-092

**Group By Patron Characteristics** · *Functional · Priority: Must*

The system shall allow staff to group report results by patron characteristics such as age range, zip code, county of residence, home branch, patron type, and preferred language and present aggregated metrics (for example, patron counts or checkout counts) per group. Grouping supports comparative analysis and program planning by summarizing activity by demographic buckets. Reporting staff and analysts will use grouping when generating summaries or dashboards. Verification: run a report grouping by a chosen characteristic and confirm aggregated metrics are correctly computed and displayed per group.

*Priority rationale:* Grouping plus aggregated metrics were repeatedly requested as essential for analysis and program planning by multiple stakeholders.

*Sources:* `conversations/conv_pines023_patron_characteristics.eml`

#### REQ-093

**Include Null Values In Reports** · *Functional · Priority: Must*

The system shall include records with null or missing patron characteristic values in report result sets rather than silently excluding them, and surface a distinguishable null/unknown bucket when grouping. Including nulls ensures staff can see which patrons lack demographic data and avoid biasing statistics. Reporting staff will use these results to drive data-completion efforts. Verification: run reports where some patrons have null values and confirm those records appear and nulls are represented in groupings.

*Priority rationale:* Stakeholders explicitly asked to include nulls to avoid data bias and to identify incomplete patron records; omission would produce misleading statistics.

*Sources:* `conversations/conv_pines023_patron_characteristics.eml`

#### REQ-094

**Background Processing And Performance** · *Functional · Priority: Should*

The system shall support running inactivity and large demographic reports as background jobs and apply performance measures such as result caching and query optimization to avoid blocking interactive system usage. Background execution and caching improve responsiveness for staff and reduce load on the transactional system. System administrators will schedule or run reports as background tasks and verify completion status and cached result availability. Verification: run a large-scope report as a background job and confirm it completes without blocking other operations, that caching speeds repeated runs, and that query optimization metrics meet agreed performance targets.

*Priority rationale:* Performance and non-blocking behavior are important for usability and system stability, especially for large federated datasets; can be phased to balance implementation effort.

*Sources:* `conversations/conv_pines024_inactive_patrons.eml`

#### REQ-095

**Configure Inactive Report Scope** · *Functional · Priority: Should*

The system shall allow reports and report templates to be scoped to organizational levels such as System, home branch, County, and additional extensible levels as required, and provide System-level visibility into which branches have the most inactive patrons. Scoping supports appropriate operational views for system administrators, branch managers, and county-level administrators. Administrators will select the scope when running or scheduling reports and use System-level rollups for oversight. Verification: run the inactive patrons report at multiple scopes and confirm results reflect only patrons within the selected scope and that system-level summaries aggregate branch counts correctly.

*Priority rationale:* Multi-level scoping is important for operational use across federated organizations but can be phased in after basic reporting; System-level insight is valuable for oversight.

*Sources:* `conversations/conv_pines024_inactive_patrons.eml`

#### REQ-096

**Export Inactive Report** · *Functional · Priority: Should*

The system shall allow staff to export inactive patron reports in CSV format for offline processing, printing, or mailing-label generation. Export capability supports integration with mailing and outreach workflows used by branch staff and administrators. Users with appropriate roles will execute exports from the reporting interface. Verification: export a report to CSV and confirm the file contains the expected headers and rows matching the report output.

*Priority rationale:* CSV export is a standard interoperability requirement for outreach workflows and was explicitly requested; important but not blocking for initial report generation.

*Sources:* `conversations/conv_pines024_inactive_patrons.eml`

#### REQ-097

**Include Contact Fields And Exclusions** · *Functional · Priority: Should*

The system shall include current mailing address and other designated contact fields in inactive patron reports for outreach, and allow excluding certain patron types or flagged accounts (for example do-not-disturb, staff, VIP, or opted-out patrons) and optionally separate inactive patrons who still owe fines. Including contact data and exclusion rules supports compliant and targeted outreach while honoring opt-outs and special handling. Reporting staff will configure exclusions and verify included contact fields when exporting or printing lists. Verification: run reports with exclusion criteria and confirm excluded patron types are absent, that patrons with fines are flagged or separated, and that mailing addresses appear for included patrons.

*Priority rationale:* Mailing addresses and exclusion handling are commonly needed for outreach and account policy compliance; important but not strictly blocking for initial delivery of basic inactive lists.

*Sources:* `conversations/conv_pines024_inactive_patrons.eml`

#### REQ-098

**Patron Behavior And Predictive Analytics** · *Functional · Priority: Should*

The system shall produce statistics and support analytic features used to understand and predict patron behavior and material usage, such as average return time, renewal likelihood, and interest patterns, to inform collection management and programming. Analysts and collection managers will use these statistics to plan acquisitions, identify at-risk items, and tailor services. Predictive analytics capabilities may use historical transaction data and demographic groupings while respecting anonymization and data-retention policies. Verification: run analytics on historical data and confirm calculated metrics (for example average return time) and predictive outputs align with expected baselines and documented algorithms.

*Priority rationale:* Predictive analytics supports strategic planning and was requested by stakeholders, but it is a heavier capability that can follow core reporting and anonymized statistics.

*Sources:* `early_draft_srs_galecia.txt`, `survey_results_2009.txt`

#### REQ-099

**Assign Cleanup Tasks To Home Branches** · *Functional · Priority: Could*

The system shall allow a home branch-level user (subject to RBAC) to assign cleanup or follow-up tasks to specific branches or branch contacts based on report results, enabling operational follow-through from inactive patron lists. This supports distributed workflows where branch staff act on assigned tasks for local outreach or account actions. Verification: using an account with appropriate role, assign a task from a report and confirm the assignment is recorded and visible to the target branch user.

*Priority rationale:* Task assignment improves workflow efficiency but is an operational convenience that can be implemented after core reporting capabilities.

*Sources:* `conversations/conv_pines024_inactive_patrons.eml`

### Financial Reporting & Transactions

#### REQ-100

**Attach Financial Data To Records** · *Functional · Priority: Must*

The system shall attach fines, charges, waivers and ecommerce transactions to patron and item records and present those financial data so staff may view, update, and query patron balances. This ensures financial events are traceable to the patron and the Item, supports per-library accounting, and enables staff workflows such as queries for accounts above a specified balance. Finance and circulation staff use this capability to reconcile payments, apply waivers, and produce branch-level summaries. Verification is by creating sample fines/charges/waivers/ecommerce transactions, confirming they appear on the associated patron and Item records, and executing queries that filter by balance thresholds and library.

*Priority rationale:* Core data model required for all financial workflows, reporting, and reconciliation; explicitly requested by stakeholders and a prerequisite for reports and audit.

*Sources:* `early_draft_srs_galecia.txt`, `email_financial_reports.eml`

#### REQ-101

**Compliance, Archiving And Retention** · *Non-functional · Priority: Must*

The system shall archive and retain financial reports, ledgers, and related transaction records in compliance with applicable state, county and municipal accounting and auditing requirements and configurable retention rules (for example, retaining specified data for seven years where required). Finance and records staff rely on these capabilities to satisfy external audits and legal retention obligations while protecting privacy. Archiving shall use authorized storage (for example a Transaction Archive) and provide policies to meet local requirements; retention periods must be configurable to reflect jurisdictional rules. Verification is by validating archived datasets and retention settings against sample retention policies and demonstrating the system preserves required records for the configured period and restricts deletion accordingly.

*Priority rationale:* Legal and auditing requirements drive retention and archiving needs; noncompliance has regulatory risk and so is essential.

*Sources:* `early_draft_srs_galecia.txt`, `email_financial_reports.eml`

#### REQ-102

**Financial Audit Trail And Ledger** · *Functional · Priority: Must*

The system shall maintain a transaction-level financial ledger and audit trail that records payments, which charges/payments they apply to, and verification metadata sufficient for reconciliation and audit. Finance staff and auditors use the ledger to trace every financial event from origin through application to balances, supporting internal control and external auditing. The ledger must be immutable or revision-controlled, include timestamps, actor identity, and references to associated patron and Item records, and produce reconciliation reports. Verification is by performing sample payment and adjustment scenarios and demonstrating that each event and its application to charges can be traced and reconciled using the ledger.

*Priority rationale:* Explicitly marked critical by stakeholders and required for correct reconciliation and audit; underpins legal and financial controls.

*Sources:* `early_draft_srs_galecia.txt`, `email_financial_reports.eml`, `meeting_minutes/meeting_2009-03-15_minutes.txt`

#### REQ-103

**Financial Reports** · *Functional · Priority: Must*

The system shall provide financial reports for staff and administrators showing patron balances by patron/home library/system, fines and charges accrued by configurable time periods, payments broken down by time period and payment method, fines waived by time period and branch, and breakdowns by type of charge. These reports support operational reconciliation, branch end-of-month reporting, and management oversight by summarizing and aggregating financial events across the system. Staff and finance users run and export these reports using report templates or ad-hoc queries; report output must be verifiable against source transactions. Verification is by running each report type with test data and confirming aggregates and filters (time period, branch, payment method, charge type) produce expected results.

*Priority rationale:* Requested by multiple stakeholders for operations and reconciliation; necessary for branch and system financial management and dependent on attached financial data.

*Sources:* `early_draft_srs_galecia.txt`, `email_financial_reports.eml`

#### REQ-104

**Real-Time Payment Updates** · *Functional · Priority: Must*

The system shall reflect payments and corresponding balance updates immediately after payment events so front-desk staff and automated services see up-to-date patron balances in real time. The system must update patron account balances, payment ledgers, and any OLTP-backed views or derived fields that front-desk workflows or immediate-release processes rely on atomically within the payment transaction so those front-line operations observe a consistent state. Reporting Warehouse-backed reports and historical or aggregated views that depend on asynchronous replication are not required to update instantaneously; such warehouse-backed reports may reflect payment events after replication or ETL lag and shall be treated as eventual in consistency. Verification is by executing payments at the front desk and confirming the patron account balance, ledger entry, and OLTP-backed dependent views update immediately and consistently while warehouse-backed reports reflect the documented lag and pass reconciliation checks.

*Priority rationale:* 

*Sources:* `email_financial_reports.eml`

#### REQ-105

**Role-Based Access To Financial Reports** · *Non-functional · Priority: Must*

The system shall control access to financial reports and financial data using Role-based Access Control so that director-level and other authorized roles can view appropriate reports while unauthorized users cannot. Directors, finance staff, and branch managers rely on role-based access to receive required information without exposing sensitive financial data to inappropriate audiences. RBAC policies must be configurable to assign report visibility, export rights, and management permissions by role. Verification is by assigning test users to director and non-director roles and confirming report access, export, and management capabilities match role assignments.

*Priority rationale:* Protecting financial data and providing appropriate access levels is a security necessity; stakeholders specifically requested director-level access control.

*Sources:* `meeting_minutes/meeting_2009-07-20_minutes.txt`

#### REQ-106

**Historical Snapshot Of Bills** · *Functional · Priority: Should*

The system shall provide historical snapshots of patron bills as-of a past date so staff can reproduce the bill state at a historical point in time for dispute resolution and reporting. Finance and circulation staff use snapshots to verify prior billing, calculate historical balances, and support audits or patron inquiries. Snapshots must capture bill line-items, applied payments and waivers, and the as-of date, and must be queryable by date range. Verification is by creating transactions over time, requesting an as-of snapshot for a prior date, and confirming the reconstructed bill matches stored historical events.

*Priority rationale:* Valuable for dispute resolution and historical auditing; requested by stakeholders but the system can operate with manual reconciliation workarounds in the short term.

*Sources:* `evergreen_reference_2009.txt`, `survey_results_2009.txt`

#### REQ-107

**Value Of Items Report** · *Functional · Priority: Should*

The system shall generate a Value Of Items Report that computes Item value from Item record fields (including purchase price) for the entire collection or selectable subsets and with filters such as Item status, collection type, and location. Collection managers and finance staff will use this report to estimate collection value for budgeting, insurance, and accounting purposes; the report must accept scope and filter parameters and produce aggregations and Item-level listings that reconcile to Item record data. Verification is by running the report with known Item purchase-price values and filters (status, collection type, location) and confirming the computed totals and filtered lists match the Item records.

*Priority rationale:* Valuation assists finance and collection planning; it is desirable but not blocking for initial operations.

*Sources:* `early_draft_srs_galecia.txt`, `email_financial_reports.eml`

### System Architecture, Performance & Operations

#### REQ-108

**Accessibility and Assistive Technology Compliance** · *Non-functional · Priority: Must*

The system shall comply with applicable accessibility requirements (including Section 508) and be compatible with assistive technologies such as screen readers and screen-magnification tools. Patrons and staff who rely on assistive technologies will be able to access management and staff-facing interfaces without functional barriers. This is required by law/policy for public-library services and ensures equitable access. Verification includes formal accessibility testing, compatibility checks with representative screen readers and magnifiers, and conformance reports against the applicable standard(s).

*Priority rationale:* Legal and policy obligations (Section 508) and stakeholder priority make accessibility a non-negotiable requirement.

*Sources:* `early_draft_srs_galecia.txt`, `evergreen_reference_2009.txt`, `interview_sysadmin_2009-05-10.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`

#### REQ-109

**Accessible HTML Online Help** · *Non-functional · Priority: Must*

The system shall provide an online, hierarchical, cross-linked, searchable HTML help system that documents system functions and usage and is accessible to screen readers and other assistive technologies. Staff and administrators will use the help system for training, troubleshooting, and daily operations guidance while accessibility ensures compliance with inclusive service goals. Verification includes demonstrable searchable help pages, hierarchical navigation, cross-links, and successful use with a screen reader.

*Priority rationale:* Accessible help is required to support inclusive service delivery for public library staff and patrons and was requested by stakeholders.

*Sources:* `early_draft_srs_galecia.txt`, `interview_sysadmin_2009-05-10.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`

#### REQ-110

**Background Processing and Queuing** · *Non-functional · Priority: Must*

The system shall implement queuing and background processing for long-running reports and batch jobs so they do not block interactive workflows. System operators and report submitters will submit jobs to the queue and monitor status while interactive clients remain responsive. This prevents heavy reporting activity from slowing circulation and OPAC workflows and enables scheduled or throttled execution. Verification includes submitting large reports to the queue and showing successful completion without measurable impact to interactive transaction latencies, and proving queue management (prioritization, retries, monitoring).

*Priority rationale:* Operational staff and sysadmins identified queued background processing as essential to prevent interference with live operations.

*Sources:* `evergreen_reference_2009.txt`, `interview_sysadmin_2009-05-10.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`

#### REQ-111

**Consortium Scale Support** · *Non-functional · Priority: Must*

The system shall support operation at consortium scale, including performance and data volumes consistent with hundreds of locations and associated circulation and acquisitions load. Consortium administrators and system operators will use this capability to plan capacity, monitor health, and validate functional behavior under expected load. Verification includes capacity/load testing, performance benchmarks, and demonstration runs using representative datasets and traffic profiles.

*Priority rationale:* Explicitly requested by stakeholders as a fundamental requirement for the consortium; without this the system would not meet operational needs.

*Sources:* `conversations/conv_pines015_capacity_interface.eml`, `early_draft_srs_galecia.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`

#### REQ-112

**Enterprise-Grade Centralized Service** · *Non-functional · Priority: Must*

The system shall operate as a centralized, enterprise-grade service that accepts input and provides services to multiple locations and can rely on redundant servers, backup systems, and network connectivity. Consortium operators and IT staff rely on centralized management for consistent policies, consolidated reporting, and efficient operations across branches. Enterprise-grade infrastructure increases availability and supports scale for multi-location service delivery. Verification is by deployment architecture documentation showing centralization, redundancy (e.g., redundant servers/backups), and live failover/backup procedures.

*Priority rationale:* Centralized, resilient infrastructure is required for consortium-scale operations and was specified by multiple stakeholders as an expectation.

*Sources:* `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`

#### REQ-113

**Environment Separation And Configuration Migration** · *Non-functional · Priority: Must*

The system shall provide separate development, training, and production environments and support migration of configurations (including Report Templates, permission settings, and saved queries) between those environments. Developers, trainers, and administrators will use isolated environments to test reports, train staff, and stage configuration changes before applying them to production while promoting tested configurations safely. The training environment must not alter production data; training activity shall not modify production records and training environments shall use anonymized or obfuscated production-like data, read-only snapshots, or synthetic datasets and enforce protections preventing any training operation from changing production systems. Verification includes the existence of distinct environments, documented migration/import-export mechanisms, demonstration of prevented training-to-production writes, and successful promotion of configuration changes from non-production to production.

*Priority rationale:* 

*Sources:* `early_draft_srs_galecia.txt`, `evergreen_reference_2009.txt`, `interview_sysadmin_2009-05-10.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`

#### REQ-114

**Error Reporting and Diagnostic Feedback** · *Non-functional · Priority: Must*

The system shall provide structured error reporting and diagnostic feedback that includes high-level summaries for operators and low-level, query-specific diagnostics for Local and Global Administrators. Administrators will use these diagnostics to detect, triage, and resolve operational faults rapidly and to guide users when recoverable errors occur. Verification includes provoking error conditions and confirming administrators receive both summarized error reports and detailed diagnostics sufficient to reproduce and fix issues.

*Priority rationale:* Administrators explicitly requested both high-level and low-level diagnostics; these are required for maintainability and rapid incident response.

*Sources:* `early_draft_srs_galecia.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`

#### REQ-115

**OPAC Independence and Performance Protection** · *Non-functional · Priority: Must*

The system shall ensure that management, reporting, and background processing do not constrain OPAC functionality or impair patron-facing performance through architectural isolation, read-only reporting patterns, and throttling/queuing as needed. System administrators will use isolation mechanisms and controls so that large queries or report generation do not degrade OPAC responsiveness used by patrons. Verification includes load tests showing OPAC response-time SLAs remain within limits while reports/background jobs execute and architectural reviews demonstrating read-only or isolated access patterns.

*Priority rationale:* Multiple stakeholders explicitly demanded that patron-facing services not be degraded; protecting OPAC performance is essential to baseline usability.

*Sources:* `early_draft_srs_galecia.txt`, `interview_sysadmin_2009-05-10.txt`, `meeting_minutes/meeting_2009-03-15_minutes.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`

#### REQ-116

**Operational Performance During Open Hours** · *Non-functional · Priority: Must*

The system shall maintain acceptable performance during busy operational hours so that report generation and management workflows do not degrade patron access or OPAC responsiveness. Staff and administrators rely on timely reports and transaction processing during open hours; the system must schedule or throttle heavy work and use architectural separation to protect OPAC performance. This ensures service quality for patrons while providing necessary management data. Verification is by load and concurrency tests simulating busy hours showing report jobs meet agreed SLAs and OPAC response times remain within targets.

*Priority rationale:* Stakeholders reported unacceptable slowdowns when reports run during busy periods; preventing impact to patron services is essential for operational acceptance.

*Sources:* `meeting_tech_subcommittee_2009-06-30.txt`, `survey_results_2009.txt`

#### REQ-117

**Platform And Database Support** · *Non-functional · Priority: Must*

The system shall operate on supported Linux or Solaris server platforms and explicitly support PostgreSQL as the designated relational database engine for production and disaster-recovery sites. System administrators will deploy, operate, and recover the system on those platforms to match existing operational practices and secondary-site architectures. Specifying PostgreSQL ensures compatibility with candidate deployment architectures and provides a consistent, supported platform for database administration and recovery procedures. Verification includes successful installation, configuration, and end-to-end tests on supported Linux (including Red Hat variants) or Solaris environments and demonstration of database compatibility with PostgreSQL.

*Priority rationale:* 

*Sources:* `early_draft_srs_galecia.txt`, `interview_sysadmin_2009-05-10.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`

#### REQ-118

**Predefined Administrative Roles** · *Non-functional · Priority: Must*

The system shall provide predefined administrative role profiles (including Global Admin, Local Admin, Library Manager, and Staff) with the documented, distinct permission sets needed for common operational duties. System administrators use these profiles to ensure consistent privilege separation across locations while simplifying on-boarding and reporting access. Having standard roles reduces configuration errors and supports predictable delegation of responsibilities. Verification is by demonstrating role-based capabilities match the documented profiles and by tests that users in each role can perform only their allowed actions.

*Priority rationale:* Stakeholders specified these roles and their capabilities explicitly; predefined roles are required for secure and consistent operations across the consortium.

*Sources:* `meeting_tech_subcommittee_2009-06-30.txt`

#### REQ-119

**Process Documentation** · *Non-functional · Priority: Must*

The system shall be delivered with high-level process documentation that describes major operational processes such as Bibliographic Record import/export, validation against authority sources, Report Template and reporting workflows, and scheduled-run behaviors so administrators, integrators, and developers can plan integrations and operational handover. Administrators and integrators will use the documentation to verify data mappings, understand expected report behaviors (including how survey-name filters and scheduled runs resolve names to identifiers), and train staff on standard procedures; the documentation shall be verifiable by reviewing delivered documents and performing sample import/export and report-generation tasks using the documented steps. Providing clear process documentation reduces misconfiguration risk, supports integration testing, and improves operational handover.

*Priority rationale:* High-level process documentation is required by integrators and operational staff and was elevated to Must to avoid duplicate/missed expectations from overlapping sources.

*Sources:* `early_draft_srs_galecia.txt`, `meeting_minutes/meeting_2009-03-15_minutes.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`

#### REQ-120

**Relational Database Back-End And Design** · *Non-functional · Priority: Must*

The system shall operate on PostgreSQL and use a normalized relational schema to preserve data integrity and support complex queries and reporting. Database architects and developers will rely on schema-driven integrity constraints and normalization to avoid synchronization issues between transaction and reporting stores. Using PostgreSQL as the supported back-end provides a defined platform for schema design, migrations, and performance tuning while enabling use of vendor-supplied and community tooling for backup and recovery. Verification includes successful deployment on PostgreSQL, schema reviews, normalization checks, and tests that demonstrate correct query results and consistent reporting behavior.

*Priority rationale:* 

*Sources:* `early_draft_srs_galecia.txt`, `interview_sysadmin_2009-05-10.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`

#### REQ-121

**Reporting Warehouse** · *Functional · Priority: Must*

The system shall provide a Reporting Warehouse to serve reporting workloads separately from the live OLTP system and to support historical, aggregated, and point-in-time queries without impacting production. Administrators and report authors will use the Reporting Warehouse to run long-running and aggregated queries while protecting transactional performance; the Reporting Warehouse may be updated asynchronously and the system shall not assume instantaneous, perfect synchronization with the live database. Where needed, the system shall provide reconciliation and verification tools so users can detect and understand expected replication lag or divergence for sensitive use cases. Verification includes demonstration of the Reporting Warehouse serving report queries while production load remains unaffected and exercising reconciliation checks that surface known lag characteristics.

*Priority rationale:* Separation of reporting workloads is required to protect production performance while acknowledging asynchronous update models.

*Sources:* `evergreen_reference_2009.txt`, `interview_sysadmin_2009-05-10.txt`, `meeting_tech_subcommittee_2009-06-30.txt`

#### REQ-122

**Role-Based Access Control** · *Non-functional · Priority: Must*

The system shall implement Role-based Access Control (RBAC) where permissions are defined and granted to roles and administrators can create, manage, and assign roles to users and groups. System administrators and managers use RBAC to govern access to reporting, configuration, transfer utilities, deletion/purge operations, and other administrative functions, ensuring consistent permission sets and predictable behavior when staff change duties. The RBAC model shall support role inheritance, configurable scopes (local and global), and administrative controls to create, edit, and audit roles and assignments. Verification includes role creation and assignment tests, demonstration that changing a user's role updates effective permissions across governed features, and administrative auditing of role management actions.

*Priority rationale:* Many stakeholders requested RBAC for consistent, scalable permissions management; it is critical for security and operations.

*Sources:* `early_draft_srs_galecia.txt`, `email_report_features.eml`, `email_staff_login.eml`, `interview_sysadmin_2009-05-10.txt`, `meeting_minutes/meeting_2009-03-15_minutes.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`

#### REQ-123

**Staff Authentication and Audit** · *Non-functional · Priority: Must*

The system shall support streamlined and traditional staff authentication methods (e.g., optional card-swipe and username/password fallback), require per-user authentication, and record the logged-in user for auditing. Staff and auditors will use these mechanisms to enable efficient sign-on while preserving accountability and traceability for operations. This balances operational convenience with security and auditability requirements. Verification includes login method configuration tests, audit-log entries proving user identity per action, and demonstration that card-based logins are optional with username/password fallback.

*Priority rationale:* Stakeholders required efficient staff login options together with auditability and per-user accountability for security and operational tracking.

*Sources:* `early_draft_srs_galecia.txt`, `email_staff_login.eml`

#### REQ-124

**Standards-Compliant HTML and Semantic Markup** · *Non-functional · Priority: Must*

The system shall produce standards-compliant HTML output with appropriate semantic structure, ARIA attributes, and alt text where applicable for web-based components, and shall target W3C validation for representative pages. Web developers and accessibility reviewers will use this output to ensure pages are machine-readable, accessible to assistive technologies, and maintain cross-browser compatibility. Verification includes automated HTML/CSS validation, accessibility linting (including ARIA checks), and manual inspection confirming semantic structure and alt attributes.

*Priority rationale:* Standards-compliant output is tied to accessibility and cross-browser support; stakeholders specified it as a required property.

*Sources:* `early_draft_srs_galecia.txt`, `interview_sysadmin_2009-05-10.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`

#### REQ-125

**Transaction Archive, Retention, and Privacy** · *Non-functional · Priority: Must*

The system shall provide a Transaction Archive with configurable retention policies that protect patron privacy while enabling required statistics and legally mandated retention. Administrators and reporting staff will use the archive and retention configuration to produce demographic and aggregate statistics while excluding or anonymizing personally identifiable information as required by law; the system shall also retain monthly and annual aggregates indefinitely for permitted long-term reporting per local policy. The archive shall allow configurable retention windows for transaction-level records, automated removal according to policy, and controls to produce anonymized or aggregated exports to prevent disclosure of PII. Verification includes demonstrating configurable retention parameters, anonymized/no-PII exports, and the presence of retained monthly/annual aggregates for reporting.

*Priority rationale:* Legal requirements and stakeholder guidance make compliant transaction retention and privacy protection essential.

*Sources:* `early_draft_srs_galecia.txt`, `email_financial_reports.eml`, `email_report_features.eml`, `survey_results_2009.txt`

#### REQ-126

**Web Client Browser Support** · *Non-functional · Priority: Should*

The system shall support access via modern web browsers and shall document an explicit compatibility matrix identifying supported browser engines and versions (minimum: the current stable and the prior major release of Google Chrome, Mozilla Firefox, Microsoft Edge (Chromium), and Apple Safari on desktop; and the current stable major releases of mobile Safari and Chrome on Android for mobile workflows). Administrators, staff, and testers will rely on the documented compatibility targets for functional and accessibility testing and for help-desk guidance; the compatibility matrix shall be published with the product documentation and revisited during lifecycle maintenance. Verification includes cross-browser functional and accessibility testing against the documented compatibility matrix and publication of the matrix in product documentation.

*Priority rationale:* Explicit browser compatibility targets are important for predictable support and verification but may be updated during lifecycle maintenance.

*Sources:* `early_draft_srs_galecia.txt`, `interview_sysadmin_2009-05-10.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`

### Cataloging & Data Quality

#### REQ-127

**Bibliographic Import And Export** · *Functional · Priority: Must*

The system shall support import and export of Bibliographic Records in standard formats and provide high-level documentation of the import/export processes. Cataloging and integration staff will use these capabilities to move Bibliographic Records to and from the system and between vendors or other systems. This capability is essential for interoperability, batch migrations, and ongoing data exchange. Verification is by importing and exporting Bibliographic Records in a standard format and confirming field mappings and record integrity.

*Priority rationale:* Fundamental to cataloging workflows and integrations; stakeholders expect import/export capability.

*Sources:* `meeting_tech_subcommittee_2009-06-30.txt`

#### REQ-128

**Complete Data Specifications** · *Non-functional · Priority: Must*

The system shall include complete, published data specifications for Authority Records, Bibliographic Records, Order Records, Item Records, Hold records, and any other records maintained or accessed by Management Processes. Developers, integrators, and administrators will use these specifications to build integrations, write queries, and understand record semantics. Providing authoritative data specifications ensures interoperability, correct mapping for import/export, and reduces integration errors. Verification is by the presence of a published specification document covering each listed record type, with field-level definitions and examples.

*Priority rationale:* Required for integration, developer work, and many stakeholders explicitly requested complete specifications.

*Sources:* `early_draft_srs_galecia.txt`, `meeting_minutes/meeting_2009-03-15_minutes.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`

#### REQ-129

**Data Quality Reporting** · *Functional · Priority: Must*

The system shall generate data quality reports that identify issues such as Items with invalid item type, Items with excessively long call numbers, and Bibliographic Records with no attached Item records. Cataloging and collection maintenance staff will use these reports to find and remediate metadata and collection-record problems that affect discovery, circulation, and reporting. These reports improve data integrity and operational responses to errors and are requested by stakeholders. Verification is by running each report, validating that known defects are listed, and exporting results for remediation workflows.

*Priority rationale:* Multiple stakeholders requested data quality reporting and it is essential for maintaining usable metadata and collections.

*Sources:* `interview_cataloging_2009-05-08.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`

#### REQ-130

**Integration With Acquisitions And Cataloging Modules** · *Functional · Priority: Must*

The system shall provide data structures and functionality that support enterprise-level Acquisitions and Cataloging modules, enabling Management Processes to rely on integrated cataloging and acquisitions workflows. Cataloging and acquisitions staff will use the integrated modules for ordering, receiving, invoicing, and creating Bibliographic Records and Item Records. Integration ensures consistent data across workflows and reduces duplicate data entry and errors. Verification is by demonstrating interconnected workflows (order to item/Bibliographic Record creation) and by validating data consistency across modules.

*Priority rationale:* Described as a dependency for Management Processes and key to enterprise workflows.

*Sources:* `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`

#### REQ-131

**Patron Fields For Reporting** · *Functional · Priority: Must*

The system shall provide and expose patron table fields for reporting, including age range, zip code, county of residence, home branch, patron type, and preferred language. Administrative and reporting staff will use these fields to generate demographic, branch, and program-performance reports. This capability is required to support stakeholder-requested analytic and compliance reports and to enable grouping and filtering by patron attributes. It can be verified by inspecting the patron table schema and by creating and running reports that filter or aggregate on each listed field.

*Priority rationale:* Marked critical by stakeholders and required for essential reporting and analytics.

*Sources:* `conversations/conv_pines023_patron_characteristics.eml`

#### REQ-132

**Vendor Data Interfaces** · *Functional · Priority: Must*

The system shall interface with vendor websites and systems using published APIs and/or automated transfer of standard-format data files (for example, USMARC21 and EDIFACT) to support order, acquisition, and record exchange workflows. Acquisitions and cataloging staff will use these interfaces to receive vendor-supplied bibliographic, order, and invoice data and to maintain synchronization with external systems. Supporting common industry formats and APIs enables efficient integrations and reduces manual data entry. Verification is by performing end-to-end transfers using a vendor API or standard-format file and confirming correct ingestion and mapping.

*Priority rationale:* Necessary for acquisitions and vendor integrations; supported by existing requirements and dependencies.

*Sources:* `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`

#### REQ-133

**WorldCat Integration** · *Functional · Priority: Must*

The system shall integrate with WorldCat to support cataloging workflows, enabling catalogers to search, retrieve, match, and import Bibliographic Records and related metadata from WorldCat. Cataloging staff will use this integration to accelerate record creation and improve metadata consistency across the collection. Stakeholders have identified WorldCat integration as critical to efficient cataloging and to reducing duplicate record creation. Verification is by performing a search against WorldCat from the system, importing a Bibliographic Record, and confirming the imported record and metadata fields appear correctly.

*Priority rationale:* Explicitly described as critical by stakeholders and central to cataloging efficiency.

*Sources:* `interview_cataloging_2009-05-08.txt`

#### REQ-134

**Authority Validation Process** · *Functional · Priority: Should*

The system shall provide validation of Bibliographic Records against internal and external authority sources as part of import and cataloging workflows to improve metadata accuracy and consistency. Cataloging staff will use authority validation to detect and correct heading and subject inconsistencies and to apply controlled vocabularies. Validating against authorities reduces discoverability issues and cataloging errors. Verification is by running the validation process on a sample of records and confirming that matches, mismatches, and suggested corrections are reported.

*Priority rationale:* Important for metadata quality but can be staged after core import/export and integration capabilities.

*Sources:* `meeting_tech_subcommittee_2009-06-30.txt`

#### REQ-135

**Data Dictionaries For Staff** · *Non-functional · Priority: Should*

The system shall provide data dictionaries describing field names, data types, and relationships for records used by staff, enabling staff to write effective queries and understand data structures. Reporting and technical staff will use the dictionaries to create reports, transforms, and integrations without guesswork about field usage. This reduces errors in reports and custom queries and speeds troubleshooting. Verification is by the availability of searchable/published data dictionaries and by staff successfully creating queries that reference documented fields.

*Priority rationale:* Important for staff productivity and correct querying but not strictly required for initial system operation.

*Sources:* `meeting_tech_subcommittee_2009-06-30.txt`

#### REQ-136

**MARC Field Extraction Across Rows** · *Functional · Priority: Should*

The system shall extract specific MARC fields and subfields even when their data is distributed across multiple MARC variable field occurrences or rows. Cataloging and import processes will rely on this capability to accurately capture and map bibliographic metadata from incoming MARC-formatted data. Proper extraction ensures that multi-occurrence MARC data is not lost or mis-aggregated during import and reporting. Verification is by importing MARC records where target data is split across multiple field occurrences and confirming that the correct consolidated values are present in the resulting Bibliographic Records.

*Priority rationale:* Needed for robust MARC handling and advertised import/export fidelity, but some imports could be handled with workarounds initially.

*Sources:* `survey_results_2009.txt`

#### REQ-137

**Uncataloged Item Inventory Tracking** · *Functional · Priority: Should*

The system shall track uncataloged Items as inventory and support rapid processing workflows that minimize branch labor while allowing staff to identify usage and include those Items' transactions in circulation statistics and reports. Circulation and branch staff will use this capability to receive large shipments of uncataloged Items, distribute them quickly, and capture usage data without requiring full Bibliographic Record creation. Verification is by processing a batch of uncataloged Items through the inventory workflow, confirming minimal per-Item staff steps, and confirming their transactions appear in circulation and Item reports.

*Priority rationale:* Support for uncataloged Items improves processing throughput and ensures circulation counts include high-volume low-cost materials.

*Sources:* `early_draft_srs_galecia.txt`, `interview_cataloging_2009-05-08.txt`

### General

#### REQ-138

**Patron Access Via OPAC Displays** · *Functional · Priority: Must*

The system shall expose any patron-facing reporting or item-status information indirectly through OPAC displays and patron-facing pages rather than by granting direct access to staff reporting tools, ensuring patrons see relevant information via the OPAC UI. Patrons will use the OPAC to see hold statuses, item availability, and other permitted details; staff reporting tools remain for internal use and require RBAC privileges. This separation preserves appropriate information boundaries, simplifies patron workflows, and reduces accidental disclosure of internal audit or deletion lists. Verification includes demonstrating that patron-accessible views are served via the OPAC and that internal Report Templates or Purge Candidate lists are not directly accessible to patron accounts.

*Priority rationale:* Patron-facing information must be provided through the OPAC to satisfy stakeholder privacy and UX requirements.

*Sources:* `meeting_tech_subcommittee_2009-06-30.txt`

## 5. Discarded Requirements (Blacklist)

| # | Name | Kind | Reason | Sources |
|---|---|---|---|---|
| D-001 | Coordinate testing with branch managers | not-software | This item describes a coordination/testing activity (organizing branch managers for testing) rather than a software capability; it is out of scope for software requirements. | conversations/conv_pines016_shelf_space.eml |
| D-002 | Last Edit Only (Exclude Last Circulation) | conflict | This candidate requests displaying only a last edit date and explicitly not including last circulation date, which conflicts with the better-supported requirement that last edit and last circulation be separate fields. The separate-fields requirement is supported by multiple sources and aligns with cataloging and circulation reporting needs; therefore this candidate is discarded in favor of the winning requirement 'Last Edit And Last Circulation Fields'. | interview_cataloging_2009-05-08.txt |
| D-003 | Document Reports Functionality (Project Task) | not-software | This candidate describes a project documentation task rather than a software capability and is out of scope for functional requirements. | meeting_minutes/meeting_2009-03-15_minutes.txt |
| D-004 | Develop Requirements List (Project Task) | not-software | This candidate is an activity (develop a list of requirements) for project planning and not a software requirement. | meeting_minutes/meeting_2009-03-15_minutes.txt |
| D-005 | Establish Reports Testing Group (Project Task) | not-software | This candidate prescribes an organizational/testing process rather than a software capability and is therefore not a software requirement. | meeting_minutes/meeting_2009-03-15_minutes.txt |
| D-006 | Compile Executive Reports List (Project Task) | not-software | This candidate directs compilation of a report list (a planning/organizing action) rather than defining system behavior and is not a software requirement. | meeting_minutes/meeting_2009-03-15_minutes.txt |
| D-007 | Create PINES Templates (Implementation Task) | not-software | This candidate requests determining and creating templates for a specific consortium (PINES); that is an implementation/operational activity using the system's template management capability rather than a distinct software feature. The system already includes template management requirements; the actionable organizational task is outside the scope of software requirements. | meeting_minutes/meeting_2009-03-15_minutes.txt |
| D-008 | Reporting Data Kept Only In Main Database | conflict | This candidate conflicts with multiple higher-supported candidates requiring reporting isolation (reporting warehouse/replicas and background queuing). Read-only replicas/warehouse and queued processing better protect OPAC performance and are supported by multiple operational stakeholders and sysadmin evidence; therefore the 'keep everything in main DB' candidate is discarded. | interview_sysadmin_2009-05-10.txt |
| D-009 | UI/Data Structures Development Methodology | not-software | This candidate describes a development methodology (iterative, prototype-oriented) rather than a testable software capability or operational requirement; it is a project/process decision and thus out of scope for the software requirements consolidation. | meeting_minutes/meeting_2009-03-15_minutes.txt |
| D-010 | Reuse Galecia Group SRS Foundation | not-software | This candidate records a sourcing/design provenance decision (basis on an existing SRS) rather than a directly testable system capability or non-functional requirement; it belongs in project documentation and procurement strategy rather than the software requirements set. | meeting_minutes/meeting_2009-03-15_minutes.txt |
| D-011 | Data Specifications and Process Documentation | conflict | R127 bundled two separate capabilities (complete data specifications and high-level process documentation) that are specified separately by REQ-128 (Complete Data Specifications) and REQ-119 (Process Documentation). To avoid duplication and to keep each capability atomic, the content of R127 is consolidated into the existing REQ-128 and the revised REQ-119; R127 is discarded as a bundled duplicate in favor of those two requirements. | early_draft_srs_galecia.txt, meeting_minutes/meeting_2009-03-15_minutes.txt |

## 6. Traceability Matrix (Document → Requirements)

| Document | Requirements |
|---|---|
| `conversations/conv_pines014_material_volume.eml` | REQ-006, REQ-010, REQ-035, REQ-036, REQ-037, REQ-038, REQ-039 |
| `conversations/conv_pines015_capacity_interface.eml` | REQ-041, REQ-042, REQ-043, REQ-044, REQ-045, REQ-050, REQ-051, REQ-052, REQ-111 |
| `conversations/conv_pines016_shelf_space.eml` | REQ-040, REQ-046, REQ-047, REQ-048, REQ-051 |
| `conversations/conv_pines018_item_transfer.eml` | REQ-053, REQ-054, REQ-055, REQ-056, REQ-057, REQ-058, REQ-059, REQ-060, REQ-061, REQ-062, REQ-063, REQ-064, REQ-065, REQ-066, REQ-067 |
| `conversations/conv_pines019_020_missing_intransit.eml` | REQ-068, REQ-069, REQ-070, REQ-071, REQ-072, REQ-074 |
| `conversations/conv_pines021_item_purging.eml` | REQ-075, REQ-076, REQ-077, REQ-078, REQ-079, REQ-080, REQ-081, REQ-083, REQ-084, REQ-085 |
| `conversations/conv_pines022_deletions.eml` | REQ-075, REQ-082 |
| `conversations/conv_pines023_patron_characteristics.eml` | REQ-087, REQ-088, REQ-090, REQ-092, REQ-093, REQ-131 |
| `conversations/conv_pines024_inactive_patrons.eml` | REQ-089, REQ-091, REQ-094, REQ-095, REQ-096, REQ-097, REQ-099 |
| `early_draft_srs_galecia.txt` | REQ-001, REQ-003, REQ-005, REQ-007, REQ-011, REQ-012, REQ-013, REQ-015, REQ-016, REQ-017, REQ-018, REQ-021, REQ-022, REQ-027, REQ-028, REQ-030, REQ-037, REQ-045, REQ-048, REQ-055, REQ-068, REQ-069, REQ-077, REQ-082, REQ-086, REQ-090, REQ-091, REQ-098, REQ-100, REQ-101, REQ-102, REQ-103, REQ-107, REQ-108, REQ-109, REQ-111, REQ-113, REQ-114, REQ-115, REQ-117, REQ-119, REQ-120, REQ-122, REQ-123, REQ-124, REQ-125, REQ-126, REQ-128, REQ-137 |
| `email_financial_reports.eml` | REQ-100, REQ-101, REQ-102, REQ-103, REQ-104, REQ-107, REQ-125 |
| `email_report_features.eml` | REQ-001, REQ-003, REQ-007, REQ-013, REQ-015, REQ-016, REQ-017, REQ-021, REQ-024, REQ-027, REQ-122, REQ-125 |
| `email_staff_login.eml` | REQ-122, REQ-123 |
| `evergreen_reference_2009.txt` | REQ-004, REQ-005, REQ-007, REQ-008, REQ-009, REQ-014, REQ-015, REQ-016, REQ-017, REQ-018, REQ-019, REQ-020, REQ-025, REQ-029, REQ-031, REQ-032, REQ-033, REQ-034, REQ-106, REQ-108, REQ-110, REQ-113, REQ-121 |
| `interview_cataloging_2009-05-08.txt` | REQ-037, REQ-048, REQ-053, REQ-056, REQ-057, REQ-058, REQ-060, REQ-068, REQ-069, REQ-073, REQ-075, REQ-077, REQ-078, REQ-080, REQ-081, REQ-082, REQ-083, REQ-129, REQ-133, REQ-137 |
| `interview_sysadmin_2009-05-10.txt` | REQ-108, REQ-109, REQ-110, REQ-113, REQ-115, REQ-117, REQ-120, REQ-121, REQ-122, REQ-124, REQ-126 |
| `meeting_minutes/meeting_2009-03-15_minutes.txt` | REQ-025, REQ-049, REQ-086, REQ-102, REQ-115, REQ-119, REQ-122, REQ-128 |
| `meeting_minutes/meeting_2009-07-20_minutes.txt` | REQ-015, REQ-022, REQ-025, REQ-040, REQ-068, REQ-069, REQ-077, REQ-086, REQ-105, REQ-108, REQ-109, REQ-110, REQ-111, REQ-112, REQ-113, REQ-114, REQ-115, REQ-117, REQ-119, REQ-120, REQ-122, REQ-124, REQ-126, REQ-128, REQ-129, REQ-130, REQ-132 |
| `meeting_tech_subcommittee_2009-06-30.txt` | REQ-002, REQ-008, REQ-013, REQ-023, REQ-025, REQ-109, REQ-112, REQ-113, REQ-114, REQ-115, REQ-116, REQ-118, REQ-119, REQ-120, REQ-121, REQ-122, REQ-124, REQ-127, REQ-128, REQ-130, REQ-132, REQ-134, REQ-135, REQ-138 |
| `survey_results_2009.txt` | REQ-002, REQ-008, REQ-009, REQ-013, REQ-014, REQ-015, REQ-016, REQ-017, REQ-019, REQ-020, REQ-022, REQ-023, REQ-025, REQ-026, REQ-029, REQ-031, REQ-053, REQ-056, REQ-058, REQ-082, REQ-086, REQ-098, REQ-106, REQ-116, REQ-125, REQ-136 |

## 7. Refinement Log

- Round 1: 37 edit operations (15 merges, 1 splits, 3 rewrites, 0 requirement discards, 15 attaches, 0 additions) -> 138 requirements
- Round 2: 26 edit operations (2 merges, 1 splits, 21 rewrites, 0 requirement discards, 0 attaches, 2 additions) -> 139 requirements
- Round 3: 16 edit operations (0 merges, 0 splits, 13 rewrites, 0 requirement discards, 3 attaches, 0 additions) -> 139 requirements
- Round 4: 15 edit operations (0 merges, 0 splits, 12 rewrites, 1 requirement discards, 2 attaches, 0 additions) -> 138 requirements

## 8. Open Issues

- Candidates both used in a requirement and blacklisted (decide one): C177, C178, C431
- REQ-001 and REQ-022 substantially duplicate the same transaction-reporting capability: both require transaction counts/grouping, per-patron counts, jurisdictional grouping, and renewal-percentage validation. Consolidate them or clearly separate their scopes and remove duplicate coverage such as C203.
- REQ-026 and REQ-039 overlap on point-in-time reporting. Clarify that REQ-026 covers historical fields beyond Item counts, or consolidate the overlapping capability so developers have one unambiguous requirement.
- REQ-101 and REQ-125 conflict on Transaction Archive privacy: REQ-101 permits archiving identifiable financial ledgers and related records in the Transaction Archive, while REQ-125 requires transaction-level records there to exclude or anonymize PII. Specify separate stores or define how legally required identifiable financial records coexist with the archive’s privacy rules.
- REQ-078 identifies Last Copies but does not require deletion to be blocked or otherwise protected; REQ-076 only surfaces Last Copy flags during confirmation. Add an enforceable safeguard that prevents accidental deletion of a Last Copy, or clarify the required protection, consistent with the glossary purpose and C096, C097, and C104.
- REQ-012 does not include several periodic report types explicitly called for by C197, including invalid Item type, long call number, Bibliographic Records without Items, and patrons with invalid home-branch assignments. REQ-129 covers some as data-quality reports but does not require them to be periodic, canned, or schedulable as REQ-012 requires.
- REQ-005 does not preserve the specific canned reports in C318–C321 (Patron Count by Home Library and the three Bills reports). Include those reports explicitly or identify where their canned-template requirement is met.
- REQ-002’s candidate references do not support its stated capability: C501 and C502 concern output formats, and C546 concerns pivot output; the email-delivery and address-book needs are C325, C326, C554, and C555. Correct the mapping and ensure those candidate needs are explicitly covered.
- REQ-085 says scheduled purge runs produce read-only candidates and do not automatically delete, but also describes a confirmation step for automated deletion ‘at run time.’ Clarify whether scheduled runs can ever initiate deletion and how a human can provide the required confirmation.
- REQ-083 uses ‘Purge Candidate’ as an example Item status, but the glossary defines it as an eligibility classification, not a status. Replace that example with a valid Item status or specify a separate status field without conflating the concepts.
- REQ-028–REQ-019 do not clearly require the relative date-selection presets for canned reports listed in C229 (yesterday, last week, last month, and last year). Add those run-date options or identify the requirement that provides them.

Vocabulary warnings (non-blocking):

- Synonym 'request' used instead of glossary term 'Hold' in REQ-076.
