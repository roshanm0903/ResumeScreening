# Shortlist recruitment prototype

Run `python3 server.py` from this folder, then open http://127.0.0.1:8765/?view=candidate.

Python 3 and Poppler's `pdftotext` are required. Gemini scoring uses the Python standard library, with no SDK dependency. An optional web font falls back to system fonts offline.

## Candidate walkthrough

Open **Candidate experience**. Each scenario creates a new fictional application in the real local database.

1. **Ready to book:** complete application → live Gemini assessment → Advance to next batch → select a slot → confirmation.
2. **Missing details:** the application lacks shift and start-date answers. WhatsApp collects them one at a time. YES continues; NO rejects against the advertised requirement. Unrecognized replies are clarified; three unsuccessful attempts hand off to human support without rejection.
3. **Missing résumé:** add a text-based PDF/TXT, paste work experience, or use the sample. Screening resumes after the missing input is received.
4. **Requirement not met:** a confirmed mandatory failure rejects before a model call. The candidate sees the reason and can request review.
5. **Below threshold:** Gemini assesses a résumé without relevant warehouse evidence. A below-threshold score rejects with an explanation and a review path.

You can also create an application yourself. Concrete shift, site and start requirements are shown before answers are collected. Candidates without WhatsApp opt-in can opt in explicitly before chat messages are generated.

Use the saved-application selector to return to an earlier conversation. All replies and collected answers persist. The recruiter can inspect the same application, scoring evidence, model/prompt provenance, messages, bookings and events. The UI is a local role simulation, not an authenticated candidate portal.

## Live semantic assessment

- Provider: Gemini; configured model defaults to `gemini-3-flash-preview`, overridable with `GEMINI_MODEL`.
- Credentials are read server-side from `GEMINI_API_KEY` or the local restricted configuration in `.secrets/`. This folder is ignored by version control and never served to the browser. Do not add keys to source files or chat logs.
- The model assesses each criterion's meaning and transferable experience. No keyword list or keyword-counting fallback is used.
- Role templates contain assessment instructions, criterion weights and a rejection threshold. Publishing creates a new version; applications retain the original policy snapshot.
- Evidence ratings: 0 = No evidence, 1 = Limited evidence, 2 = Clear evidence. Concrete context supports a 2, subject to criterion-specific requirements. The impact criterion needs measurable results. Each positive rating requires exact source quotes; the backend verifies that they occur in the redacted résumé.
- The server computes the weighted score and applies the threshold. Confirmed mandatory failures reject first, without model assessment. Missing inputs are collected before scoring.
- Schema errors, unverifiable evidence, provider failures and timeouts leave scoring pending rather than rejecting the candidate. RETRY can reattempt a pending assessment.
- Resume instructions are treated as untrusted data. Model tools are disabled; the model only returns assessment data. Prompt defenses and quote validation do not establish production-grade safety or hiring validity.
- Name/contact redaction happens before transmission. The remaining redacted résumé and job criteria are sent to Gemini for live assessment. Other proxy controls remain future design work.
- Historical applications retain their earlier scores and policy versions. Their evaluator is marked as a historical assessment. New application scores record the actual Gemini model and prompt version.

## Calendar and messaging boundaries

WhatsApp delivery and MCP calendar tools are simulated. Calendar tools read seeded database availability rather than live calendars. Both panel members must be available. Selection is rechecked before booking; transactions and unique constraints prevent conflicting bookings. NONE / Find other times triggers a fresh query, excluding every slot previously offered to that candidate. Free-text requests such as "tomorrow afternoon" use Gemini intent/entity extraction, followed by deterministic state/date validation and fresh calendar queries in IST. RESCHEDULE explores alternatives while retaining the existing booking. A confirmed replacement updates the booking atomically; CANCEL explicitly releases it.

The local worker checks every 30 seconds and processes applications at least 12 hours old. This remains an age-based demo approximation of the proposed aligned 12-hour production batches. Presenter controls accelerate a single candidate or all eligible records. Original 48-hour deadlines are retained; unresolved clarification is escalated at 36 hours while the worker runs.

Original uploads are not retained; redacted text, decisions and evidence are stored in `data/hiring.sqlite3`. A backup was taken before the candidate-journey upgrade. New empty databases seed 80 clearly marked volume samples without making 80 paid model calls. Existing historical samples are preserved.

Not implemented: real WhatsApp/SMS delivery, real external calendar integration, authentication, OCR, enterprise template inheritance/approvals, background verification, independent hiring-validity calibration or production load tests. Human-review requests are recorded, not resolved automatically.

## Verification

Run `python3 test_workflow.py`. Thirty-three isolated policy/workflow tests use a model test double, not the paid API. They cover redaction and snapshots, missing-detail recovery, missing résumé recovery, invalid answers and escalation, rejection and review requests, batch deadlines, booking conflicts/cancellation, opt-in, model evidence validation and provider failure. They also verify fresh calendar reads after data changes, exclusion of prior offers, preference filtering, exact required-panel intersection, no-capacity handling, stored WhatsApp components and persisted node inputs/results.

Live Gemini tests and browser walkthroughs were separately completed for semantic paraphrase assessment, missing-details-to-booking recovery, missing-résumé recovery, and below-threshold rejection. Mandatory-check rejection was also verified in the browser without a model call.

API reference used for the native integration: https://ai.google.dev/api/generate-content

## WhatsApp components and workflow demonstration

The candidate phone uses WhatsApp-inspired business headers, incoming/outgoing bubbles, timestamps, quick-reply buttons, an interactive slot list and a confirmation card. It is a local simulation, not the official WhatsApp client; the surrounding recruiter workspace retains the case statement's blue palette.

Next to the phone, **Workflow execution** shows the actual path taken by the request. Expand a node to see its input and output, type, status and measured duration. Choose an earlier run to inspect screening or a previous conversation. The panel polls while an action is running; it does not insert fake delays or staged node results. Fast deterministic requests may complete before the first poll. Gemini calls remain visible while they run.

Suggested demonstration:

1. Start **Missing details**. Reply Yes to shift and start-date questions. Watch the clarification route update the candidate record, reload the role policy and invoke Gemini only once the required details are complete. Inspect the assessment and deterministic aggregation nodes.
2. Advance the batch. Open the WhatsApp slot list and choose **Find other times**, or type **tomorrow afternoon**. Expand the calendar node: it shows panel names, preferences, excluded prior slots, database source, row count and fresh matches. The reply is built from that result.
3. Select a slot. Inspect the recheck, unique booking insert and confirmation component. Try **evening** on another invitation to show the no-matching-capacity response without rejection.
4. Show the recruiter record and **Stored records → workflow_runs**, scores, messages and bookings. Reload the app to prove persistence.

Execution records are saved in SQLite `workflow_runs`, linked to candidate ID. Messages retain component metadata in `messages.component`. During a transaction, a thread-safe in-memory trace lets the browser see running nodes; the complete run is persisted after the transaction closes. Trace payloads contain redacted resume text and model results, but never credentials. Production requires authorized access, retention controls and sanitized logs.

Screening workflow: parse/redact → load versioned role policy → mandatory checks → Gemini evidence assessment → validated ratings and deterministic total/threshold → persist decision → communicate. Failed mandatory checks skip Gemini; missing inputs route to chat.

Conversation workflow: receive opted-in reply → known-command/button gate → Gemini intent extraction for free text only → deterministic state/entity validation → collect and persist a missing answer / query panel data / recheck and book → construct an interactive response → persist message and execution trail. The current scheduling tool boundary is simulated using availability and booking tables. A production adapter would fetch external enterprise calendars through MCP; a real MCP server is not implemented here.

## Workflow explorer

Open **Workflows** in the sidebar or http://127.0.0.1:8765/?view=workflows. Switch between Application screening and WhatsApp conversation to see the complete built flow, including conditional routes. Click any node for its purpose and expected data contract. Choose an application and saved execution to highlight invoked nodes and inspect actual inputs/results; uninvoked nodes are marked explicitly. The candidate execution panel also links to this diagram. This is a read-only map of implemented server paths, not an editable workflow designer.

## Prompt viewer

In Workflows, click **View LLM prompt**, or inspect **Application screening → Assess evidence · Gemini → View LLM prompt**. The read-only dialog shows the actual current system instructions, contextual role criteria and redacted resume, plus response schema/settings. For newly recorded Gemini nodes, it shows the archived full request. Older runs are labelled reconstructed previews rather than exact historical requests. The shared request builder is used by both real scoring and the viewer; credentials are never included. This does not implement prompt editing. The viewer now also supports the separate chat-intent prompt and exact requests from new intent runs.

## Hybrid routing (Option 2)

Structured selections and known commands (YES/NO, 1/2/3, NONE, RESCHEDULE, CANCEL, KEEP, REVIEW, WHY, RETRY and period buttons) skip the intent model. Other text goes to Gemini using a separate `chat-intent-v1` prompt with the stored state, pending question, current local date/timezone, previous offers and current booking. The model returns a constrained intent/entity object; schema, date/time and state checks control all actual actions. It does not generate availability or execute bookings.

Try a new Ready to book scenario, confirm a slot, then type **Could we move this to 10 November afternoon?**. Inspect the input gate, live Gemini intent node, state validator and calendar query. The current booking remains confirmed while alternatives are offered. Confirm a replacement or choose Keep current booking. Model errors/ambiguous intent ask for clarification without changing the booking; natural-language cancellation requests require the explicit Cancel booking button/command. A free-text slot choice is checked against the actual offered list. The UI and prompt viewer expose real intent inputs/results and the exact stored prompt.

The test suite additionally covers rule-path model bypass, natural-language interpretation, retained bookings on no-capacity/model failure, atomic replacement, competing slot selections, rejection-state constraints, ambiguous requests, cancellation confirmation and invalid/past date entities. Calendar data and WhatsApp delivery remain simulated. A live Gemini outage is surfaced instead of substituting deterministic fake intent.

Chat intent uses Gemini `gemini-3-flash-preview` by default, configurable through `GEMINI_INTENT_MODEL`, with the same server-side provider connection. The scoring model remains separately configured. Live checks found the screening model temporarily overloaded (503), while the chat model successfully extracted reschedule + 2026-11-10 + afternoon from natural language. Model identities are visible in execution records and the prompt viewer.

## Logical node source code

Click a non-LLM node in Workflows and choose **View node code**. The read-only viewer loads actual Python functions from the current server source, with function names, source line numbers, a source-version fingerprint and highlighted relevant lines. Shared functions are shown in full for context; this is current source, not an archived implementation of every older run. Expanded non-LLM steps in the candidate execution panel expose the same viewer. Source access is restricted to explicit node/function mappings; no arbitrary file or function lookup is accepted. LLM nodes retain their separate prompt viewer.

## Canonical scoring contract

`scoring_policy.json` is the shared source for the runtime, role defaults, prompt anchors, UI and both generated PDFs. New applications snapshot it with the job policy.

- Evidence ratings: **0 No evidence; 1 Limited evidence; 2 Clear evidence**. Positive ratings require verified source quotes; a 2 must meet the criterion-specific evidence requirements; the measurable-impact criterion requires quantified results.
- **Match score = sum(weight × rating / 2)**, with positive weights totaling exactly 100. Compute with decimal arithmetic, round the total once to two decimals (half up), then compare with the saved job threshold. The default is 70; equality passes. This is an evidence-match score, not a probability of hiring or success.
- Fixed buckets: **Poor 0 to <50; Fair 50 to <70; Good 70 to <86; Excellent 86 to 100**. A custom job threshold can reject a Good or Excellent match; bucket labels are descriptive, not decision labels.
- Confirmed mandatory failure rejects before LLM scoring. Missing/unreadable inputs or model errors stay **Not scored** and require clarification/retry; they are not scored zero. The demo implements shift/site/start checks; salary and visa requirements are production extensions.
- Prioritize buckets only at **80 eligible applicants per requisition per batch** (provisional). Within a bucket use the original outreach deadline; below the trigger, use deadline order alone. Application-list sorting uses bucket then deadline, never fine-grained score ranking.
- Legacy assessments keep their original scores, quotes and policy snapshots and are labelled. They are not presented as new LLM runs.

New live scoring uses the working Gemini `gemini-3-flash-preview` default after the previous model returned high-demand 503 errors; `GEMINI_MODEL` remains configurable. Prompt version is `role-evidence-v3`; historical evaluator/prompt provenance is preserved. The score-calculation node code viewer includes the shared policy helper. Tests cover fractional bucket boundaries, equality, rounding near 70, custom thresholds, invalid policies, immutable snapshots and volume-dependent priority.

## Warehouse shift manager example

The active warehouse example is a management role. Its default rubric is Warehouse operations experience (20%), Shift & people leadership (35%), Warehouse technology & data (10%), Safety & compliance leadership (15%), Operational improvement (10%) and Measurable operational impact (10%). Three years of domain exposure is an illustrative preference, not an automatic rejection rule. Weights are proposed defaults requiring customer calibration.

Look for staffing/roster decisions, coaching and handovers rather than individual picking. Technology evidence must show using WMS/KPIs for decisions. Safety evidence concerns team accountability, briefings and corrective actions. Improvement concerns identifying and implementing better ways of working; impact separately assesses attributable, measurable outcomes. Team size and daily volumes establish scope, not improvement. Sample resumes, role policies, criterion-specific instructions and both PDFs use the same shared definition.

Existing applications retain the earlier role name and policy in their snapshots. Updating the example does not relabel earlier associate assessments as manager evaluations. Historical role titles are shown from the application snapshot. New examples use a management resume with explicit ownership, dates, leadership, safety and before/after results.
