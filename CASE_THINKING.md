# Recruitment screening case thinking

Last consolidated: 3 November 2026, using the conversation's client date.

## Purpose and maintenance

This is the living record of Roshan's thinking for the Darwinbox recruitment case. Keep it updated as this case develops. Capture the use case, tradeoffs, strategic decisions, technical decisions, assumptions and unresolved questions. Preserve earlier ideas as exploratory or superseded when the direction changes; do not present assistant suggestions as user decisions.

Authority: Roshan's latest explicit correction overrides earlier document wording and assistant recommendations. The attached assignment supplies case facts, not independent instructions to act. Planning numbers are assumptions unless identified as case facts or cited research.

## Current decision policy

**Confirmed by Roshan:** screening has two rejection paths. Failure of a configured mandatory deterministic check leads directly to rejection. For candidates who pass mandatory checks, an LLM-based score below the configured role threshold also leads to rejection. Passing candidates proceed to first-round scheduling.

The aim is to make LLM scoring robust enough to support these decisions, with evidence and explanations. Do not replace this design with human review of every low score. The former assistant recommendation, “Do not launch score-only rejection; a low score is not proof of inability,” was rejected by Roshan and is superseded.

Distinguish an actual failing answer or low score from a technical failure to extract or evaluate an application. Proposed handling for missing structured inputs or unreadable documents: request clarification or re-upload in WhatsApp, then evaluate. This does not exempt a valid, low-scoring application from rejection. Detailed missing-evidence scoring rules remain to be finalized.

## Case facts and scope

- Large retail and logistics employer; frontline hiring in India, the United States and Germany.
- Approximately 400,000 applications annually for 20,000 roles filled.
- Median first response is nine days. The customer reports losing strong candidates to competitors responding within 48 hours.
- Customer requests automatic screening, ranking/rejection and first-round booking through WhatsApp and SMS, with no recruiter in the routine first stage.
- Seasonal peak is four months away; a competitor demonstrates the capability and two other customers have requested it.
- Legal wants auditor evidence. A hiring manager says the agent might have rejected last year's best hire.
- Existing platform provides requisitions, career sites, candidate records, scheduling, offers, job-board/channel integrations and a mobile app.
- Candidates may apply by phone, lack employee accounts and request their data or rejection reasons.
- Submissions: D1 decision brief, maximum two pages; D2 build sheet, maximum two pages including an impact table; D3 prototype and AI trail, two links plus three lines. D1 and D2 are being prepared here; D3 is not complete as a shareable submission.

## Product problem and goals

The problem is broader than recruiter capacity:

1. Avoid wasting interview-panel time on unsuitable candidates.
2. Prevent good candidates from slipping through before a first-round booking. Timely contact is a significant driver; screening errors are another possible driver, whose relative size is not yet established.
3. Screen every application consistently and automate routine first-round coordination.
4. Explain rejection reasons and retain criterion-level evidence for audit and correction.
5. Reach applicants within two days. Do not optimize only for sending a generic acknowledgement.

Recruiter capacity, rapid resume scans, gap resolution and calendar coordination contribute to the problem. Roshan clarified that brief scans reflect time pressure, not recruiters lacking interest in evaluating candidates properly. The cited eye-tracking study does not itself establish this causal explanation.

## Strategic decisions

- Two-stage screening: deterministic mandatory checks first, LLM role scoring second. Both can produce rejection.
- Use role-specific rejection thresholds. For prioritizing passing candidates, map LLM scores to buckets instead of directly ranking raw scores: 87 versus 88 may not be meaningful. Bucket priority is only needed at high candidate volume. At normal volumes, progress all passing candidates without score-based ordering. Never rank within a bucket.
- Generic enterprise solution with dynamic parameters, rather than a warehouse-only product. Use a frontline role to make the example concrete.
- Current onboarding decision: System administrator opts in, chooses channels, connects the enterprise email/calendar account, sets enterprise- versus job-level scoring and controls hiring-manager override rights. Opt-in automatically starts asynchronous rubric generation from existing jobs/JDs; this supersedes the earlier manual-first/future-generation direction.
- Enterprise direction: organization controls, role-family templates and requisition-specific adjustments. Store the applied version.
- Handle clarification and scheduling exceptions through WhatsApp first. A staffed queue is not the default response to every exception. Human handling remains relevant for unresolved, contested or required interventions.
- Messaging must be modular: WhatsApp and SMS initially; email or the customer-selected channel can use the same workflow.
- Restrict initial scope to inbound/job-board applications. Direct recruiter sourcing is excluded. Do not repeat already collected pay and other answers unless missing, stale or conflicting.
- Current evaluation approach: historical application-time inputs plus binary send-for-interview / do-not-send labels. Manually adjudicate both types of LLM/history disagreement and update the evaluation set; do not label every score. See decision 74, which supersedes earlier score-band labelling and historical-hire denominators.
- Roll out by role/site and country after applicable approvals and validation. Country-specific legal requirements must be verified with employment counsel and privacy leads; do not claim blanket permission for autonomous rejection.

## Recruiter journey

### Before publication

- Open the job posting or requisition. Requirements default from the role: salary range/expectations, visa/work authorization, shift and location, alongside job-matching scoring criteria, weights and threshold.
- Inherit the generated role/job rubric under enterprise settings. The recruiter reviews defaults and can modify them where enterprise permissions allow, then approves the version. Hiring-manager override rights remain administrator-controlled. Applied versions remain traceable.
- Add the first-round panel. The agent fetches panel availability automatically.
- Calendar matching is central to the value proposition, rather than a cosmetic step after scoring.

### While the position is live

- Track application counts, score bands, rejection rates/reasons, outreach deadlines, WhatsApp outcomes and bookings.
- Display rejection percentages in MVP. Later, compare unusually high/low rates with role history and investigate.
- Handle only the cases that the automated conversation cannot resolve or that require intervention.

### At closure

- Stop invitations, communicate role closure and close the loop with remaining applicants through the configured channel.
- Detailed handling of already booked interviews needs to be defined.

## Applicant and candidate journey

- Apply from a mobile experience and upload a resume.
- Provide structured fields such as experience, expected salary, notice period, work/visa requirements, shift/site availability and other declarations where appropriate.
- Skills can be entered or parsed. Provide an explicit opt-in for communication over WhatsApp.
- Receive a rejection explanation, clarification or interview invitation within the outreach deadline.
- Resolve missing inputs within the conversation where possible.
- If selected, choose from three interview slots or request alternatives. The system checks availability before confirmation.
- Receive booking confirmation, reminders and a rescheduling/cancellation path.
- Ask why a decision was made, correct inputs or seek review without an employee login.
- Additional recruiter questions, such as reason for switching roles, are later extensions rather than default MVP requirements.

## Scoring design

### Mandatory checks

Use explicit, job-related structured conditions, such as confirmed shift availability, attendance at the advertised site, required start-date compatibility or a genuinely required licence. Offered-pay acceptance and work authorization may be relevant depending on role and applicable rules. The final approved mandatory-check list is not fixed.

A confirmed failure rejects the application. Record the input, condition and reason. Missing inputs require explicit handling; do not silently claim a failure when parsing or data collection has failed.

### Dynamic LLM rubric

- Convert approved job requirements into a concise rubric with specific evidence anchors, criterion weights and a threshold.
- Store each attribute's rating, supporting source evidence, weighted contribution and final outcome.
- Compute the aggregate deterministically from the accepted LLM output; the model must not change weights or thresholds.
- Distinguish extraction uncertainty from the absence of evidence in a readable resume. Decide how each maps to rating or clarification, then apply consistently.
- Decide non-applicable criteria in the template before evaluating applicants, rather than changing weights opportunistically for individual candidates.

Current example: Warehouse shift manager. This supersedes the earlier associate-level task rubric. Proposed weights are illustrative, not calibrated hiring standards.

| Parameter | Weight | Evidence example |
|---|---:|---|
| Warehouse operations experience | 20% | 3+ years preferred; inbound, inventory and dispatch planning. |
| Shift & people leadership | 35% | Rosters, labor allocation, coaching and handovers. |
| Warehouse technology & data | 10% | Using WMS, reports and KPIs to manage the shift. |
| Safety & compliance leadership | 15% | Team briefings, audits, incident response and corrective actions. |
| Operational improvement | 10% | Root-cause analysis, workflow/SOP changes and adoption. |
| Measurable operational impact | 10% | Attributable improvements in throughput, accuracy, cost or service. |

Canonical evidence ratings: 0 = No evidence (no relevant evidence in a readable resume); 1 = Limited evidence (relevant task stated with limited context); 2 = Clear evidence (concrete context meeting the specific criterion; the impact criterion requires measurable outcomes). Ratings require validation and source quotes. Shared scoring_policy.json defines these anchors, fixed bucket ranges and the deterministic Match score calculation.

Original sample rubric explored skills, experience, education, certifications, job-title/industry/project/stack relevance, methodologies, language, location/remote preferences, management, culture fit and stability. It was a brainstorming example, not an approved universal parameter set. The discussion moved toward fewer role-relevant attributes and avoiding overlapping dimensions and unsupported inferences. Education, certification and language should be used only when relevant to the role. Culture fit, prestige and career stability were challenged as unreliable/proxy-prone dimensions, not adopted requirements.

Canonical fixed buckets: Poor 0 to <50; Fair 50 to <70; Good 70 to <86; Excellent 86 to 100. Compute Match score with decimal arithmetic, round once half-up to two decimals, then compare with the saved job threshold (default 70; equality passes). Buckets and threshold are separate: a custom threshold can reject a Good match. These defaults are not validated hiring-performance cutoffs; calibrate before production.

## Making LLM scoring robust

The following are proposed implementation and validation measures, not claims of completed validation:

- Use approved role criteria, anchored examples and structured model output. Validate the schema, score ranges and evidence references before computing an outcome.
- Ground criterion ratings in actual resume passages; verify that cited evidence exists. Store factual rationale rather than invented reasons or hidden reasoning traces.
- Version the template, threshold, model, prompt and extraction method. Revalidate meaningful changes.
- Test repeated runs and sensitivity to equivalent wording, layout changes, names and irrelevant content. Model-stated confidence is not a validated measure of correctness.
- Evaluate both false positives (unsuitable referrals) and false negatives (qualified candidates rejected). Include independent judgments and uncertainty, not only agreement with historical hiring.
- Test transferable experience, non-linear careers, career gaps, local/niche vocabulary and resumes without elite employer or school names.
- Test prompt injection, hidden text, keyword stuffing and AI-generated resumes that echo the JD.
- Keep documents untrusted. Resume instructions must not change policy or gain tool authority.
- Monitor outcome changes, corrections and appeals; pause or roll back a problematic scoring version. Do not quietly replace the automatic-rejection policy with universal human review.

## Technical decisions

- Resume ingestion (clarified 4 November 2026): use local text extraction/OCR first and send only normalized, redacted text to the LLM for cost efficiency. Validate cost and extraction fidelity in the pilot.
- Before LLM scoring, redact candidate name and personal location/address. Employment counsel and privacy review determine additional redaction, including education institute names and other identified proxies. Preserve job-relevant qualifications/skills. The current demo masks names, email addresses and phone numbers; OCR, location and institute masking remain production work.
- Separate identity/contact records from scoring input while retaining identity for communication.
- Store candidates, structured answers, redacted text, criterion scores/evidence, policy snapshots, message events, availability, bookings and decision/tool events in the database.
- Proposed architecture: recruiter workspace and applicant/mobile/channel interfaces connect to a workflow/policy engine; document/scoring service evaluates evidence; database retains results; MCP calendar gateway reads/writes panel calendars.
- Production agent fetches availability through MCP. Calendar intersection, preferred-slot validation, conflict checks and booking are deterministic. Roshan explicitly does not want LLM reasoning to decide availability or slot validity.
- Check availability again before booking, prevent duplicates and support cancellation. Never treat a full calendar as evidence of poor candidate suitability.
- Bound chat retries/clarification attempts. Preserve the original application deadline through retries; suggested escalation trigger is 36 hours.
- Broader assessments and background verification remain future extensions. Structured factual clarification is now in the proposed workflow after Roshan requested WhatsApp handling of exceptions.

## Batching and scheduling tradeoffs

| Tradeoff | Current thinking |
|---|---|
| Immediate processing versus comparison | Immediate invitations can allocate scarce interview slots to earlier, less-qualified passing candidates before stronger candidates arrive. Pool applications within the under-two-day SLA to compare eligible score bands, while avoiding an open-ended wait for a better pool. Roshan explicitly rejected overemphasizing candidate loss from a bounded wait. Twelve hours is a provisional starting cadence, not a user-specified or validated optimum. |
| Three slots versus an external scheduling page | Three options keep the conversation quick. A page offers greater choice but introduces navigation friction and another interface to build/maintain. |
| Limited slots versus candidate flexibility | Support alternatives and preferred times; validate deterministically against actual availability. The demo currently supports three additional options, not arbitrary preferred-time parsing. |
| False positives versus false negatives | Poor referrals consume scarce panel time; false negatives lose good candidates and may prolong vacancies. Tune criteria and thresholds against both costs. |
| Score buckets versus exact ranking | Map raw LLM scores to buckets because 87 versus 88 may not represent a meaningful difference. Use bucket priority only at high candidate volume; within a bucket, contact applicants with the earliest original 48-hour outreach deadline first. At normal volume, progress all passing candidates without score-based ordering. The configured rejection threshold still determines whether the score test passes. |
| Automation versus handling uncertainty | Routine failures and below-threshold scores reject automatically. Missing/unreadable inputs prompt chat clarification; unresolved or contested cases may need intervention. |
| Extraction cost versus fidelity | Text extraction can reduce model input costs, but complex layouts/OCR failures can damage screening accuracy. |
| Early background checks versus late discovery | Later checks can reveal blockers after substantial cost. Explore earlier targeted verification, with consent and local approval; not the first MVP priority. |

## Assumptions and estimates

These are planning assumptions unless stated otherwise:

- 400,000 / 20,000 = 20 applications per hire on average. This does not establish the applications-per-requisition distribution.
- Provisional p90 assumption: 80 applications per requisition. Design recruiter UI with search, filters, pagination and aggregate views; do not use a small fixed-card layout.
- Proposed load tests: 500-applicant requisitions and roughly 11,000 applications/day, using a 5x seasonal multiplier over the annual daily average and 2x headroom. No production load validation has been completed.
- Initial working cadence: batches every 12 hours within the under-48-hour outreach deadline. An aligned periodic cadence implies a planned wait of at most 12 hours before batch processing, leaving up to 36 hours for clarification, channel retries and other follow-up. This is scheduling headroom, not a measured optimum or guaranteed delivery time. Keep the original per-applicant deadline unchanged. Start with a fixed customer-configured cadence, then experiment with shorter/longer intervals against candidate quality at booking, panel effort, conversion and SLA breaches. Prioritize higher passing bands when capacity is constrained; do not rank within a band or change qualification thresholds based on the pool. A capacity wait is not a rejection. The current demo uses age-based batch eligibility, so it is not yet an aligned periodic batching implementation.
- Full application assessment and gap identification: estimated 2-4 active minutes. Scheduling: estimated 10-20 active minutes per interview. These are not published measurements for this customer.
- At an assumed 20% interview rate, 80,000 interviews/year imply about 13,300-26,700 coordination hours. An assumed 70% reduction releases about 9,300-18,700 hours before exceptions. Reading all 400,000 applications at 2-4 minutes is another 13,300-26,700 hours of work equivalent, not current savings.
- Illustrative residual human workload: 15% unresolved after chat at four minutes each = 60,000 cases or 4,000 hours/year. This is not an observed result or a requirement to route all exceptions to people.
- Illustrative AI processing cost: $0.02-$0.10/application, or $8,000-$40,000/year. Excludes messaging, storage, integrations, human handling and verification. Validate through actual runs.
- Whether frontline roles are non-specialized, and the true cost of false-negative hiring delays, remain unvalidated hypotheses from the original notes.

## Open and exploratory ideas

- Overqualification/offer-decline prediction was raised as a question, not adopted as a rejection criterion. Historical declines can reflect pay, timing or competing offers; validate relevance and legal implications before considering such a policy.
- Background searches and moving verification earlier are exploratory. Detailed scope, consent, sources, timing and country restrictions are unresolved.
- Suggested JD-to-rubric generation is MVP+; employer approval and organization controls still apply.
- Role-specific rejection-rate anomaly analysis is MVP+.
- Detailed handling of missing evidence, contradictory fields, unscorable documents and accommodations must be specified. Missing evidence is not the same as a document extraction failure.
- Determine threshold and equality/rounding behavior, cohort size and sample requirements, clarification retry limit, fallback channels and escalation ownership.

## Agreed success metrics

### North star

Percentage of qualified applicants with a confirmed first-round interview booking within five days of application. This supersedes both the earlier average-days metric and the earlier weekly count of qualified bookings. Own coverage (whether qualified applicants are successfully scheduled) and speed (whether booking is confirmed within five days), not just the first follow-up. The endpoint is booking confirmation, not interview attendance. The 48-hour meaningful-outreach measure remains separate.

Suggested operational definition, pending final measurement specification: numerator = qualified applications with first-round booking confirmed within five days of receipt; denominator = all qualified applications in the same cohort with five days of follow-up. Include qualified applicants who never book, not only those completing the funnel. Count once per candidate/requisition, handle duplicates consistently, and show recent cohorts still awaiting the full observation period separately. Qualification follows approved role criteria with independent auditing; do not define genuine qualification solely by the LLM passing its own threshold.

### Top three business metrics

1. Time to first interview scheduled: elapsed days from application receipt to confirmed first-round booking.
2. Booking conversion: percentage of genuinely qualified applicants reaching a confirmed interview booking within a defined observation window. The observation window still needs specification; the north star fixes the five-day speed boundary.
3. Process automation / human intervention rate: percentage of applications requiring manual recruiter intervention for screening or scheduling, excluding planned audits. Use intervention rate as the direct measure; an automation complement requires matching definitions and treatment of incomplete cases.

### Top three performance and efficiency metrics

1. Outreach within 48 hours: a meaningful next step; exclude generic acknowledgements.
2. Applicant response rate: percentage of contacted qualified applicants responding within 12 hours. Define the outreach delivery timestamp consistently in the measurement specification.
3. Cost per qualified booking: total LLM, infrastructure, messaging and human exception-handling costs divided by qualified confirmed bookings.

### Top three guardrails

1. Screening quality: independently audited false-negative and false-positive rates, plus fairness checks. Historical evaluation definitions and provisional release targets remain documented separately; the concise decision-brief guardrail does not substitute a headline score for independent audit.
2. Booking reliability: percentage of bookings without duplicates, scheduling conflicts, incorrect details or system-caused changes.
3. Candidate experience and accountability: complaints, opt-outs and unresolved exceptions.

In the decision brief, the entire success-metrics section, including north star and guardrails, must occupy no more than 25% of one page. The revised layout occupies 22.7% of a page and retains three measures per category and periods on list items.

## Demo requirements and current implementation

Roshan wants a working, self-guided app, rather than a presentation-only demo:

- Add a resume and structured application data.
- See parsed/redacted text, criterion-level scores and explanations.
- Show scores actually stored in a database.
- Show the recruiter dashboard, application/rejection status and scheduling progress.
- Show a WhatsApp-style exchange of outgoing and candidate messages.
- Fetch calendar options through a simulated MCP/tool boundary backed by tables or text fixtures, then book an available slot.
- Persist state across refreshes; show actual stored score, message, booking and event rows.

Current prototype is in `hiring-demo/`, normally served at http://127.0.0.1:8765 while its local process is running. It uses Python, SQLite, PDF/TXT extraction and live Gemini semantic assessment. The former keyword engine has been replaced. It seeds 80 synthetic applicants and supports two editable templates, per-application snapshots, messaging simulation, panel matching, conflict-safe booking and cancellation. Calendar calls and WhatsApp delivery are simulated, not external integrations.

**Current implementation after candidate-journey and Gemini updates:** automatic mandatory-check rejection and score-threshold rejection are implemented. The candidate experience has five self-guided scenarios: ready to book, missing details, missing résumé, mandatory failure and below-threshold scoring. Missing shift/start details are collected one at a time in WhatsApp; missing résumé text can be supplied by upload, paste or chat. Saved answers re-enter screening. Three unrecognized answers or the 36-hour safeguard escalate without automatic rejection. Candidates can request a human review after rejection; requests are recorded, not automatically adjudicated.

Roshan explicitly corrected the matching UI: assessment is LLM-based, not keyword matching. Templates now contain semantic assessment instructions, weights and a threshold, with anchored ratings and supporting evidence. Gemini assesses equivalent descriptions and transferable experience; deterministic code computes weighted totals and applies the saved threshold. Native Gemini API model `gemini-3.1-flash-lite` was verified available. The initially tested older model was unavailable to this account, so it was not used for the final app. Credentials are server-side, excluded from version control and not recorded in this case file.

Model results include exact source quotes, rationale, model and prompt version, policy version and outcome. Invalid/missing criterion output, fabricated quote references, API errors and timeouts pause scoring rather than turning technical failure into rejection. There is no silent keyword fallback. The app sends redacted résumé text and role criteria to Gemini for live assessment.

Twelve isolated workflow checks now cover the corrected rejection behavior, recovery paths, evidence validation and provider outages in addition to persistence, batch deadlines and bookings. These tests mock inference. Separate live Gemini/browser verification covered semantically paraphrased experience, missing-details-to-booking recovery, missing-résumé recovery and below-threshold rejection. A mandatory failure was also verified to reject without inference.

The worker still uses age-based eligibility rather than aligned periodic batches. WhatsApp delivery and external MCP calendars remain simulated. OCR, arbitrary preferred-time interpretation, enterprise inheritance/approvals, real messaging/calendar connections and production calibration/load validation are not implemented. Existing historical keyword evaluations remain historical records; new policy versions and applications use Gemini. The original local database was backed up before migration.

## Research used

- [Ladders 2018 eye-tracking announcement](https://www.prnewswire.com/news-releases/ladders-updates-popular-recruiter-eye-tracking-study-with-new-key-insights-on-how-job-seekers-can-improve-their-resumes-300744217.html): reported 7.4 seconds for an initial scan; the original 2012 figure was six seconds. It does not measure full screening effort or prove the cause of brief scans.
- [Cronofy Candidate Expectations Report 2024](https://www.cronofy.com/reports/candidate-expectations-report-2024): 12,000 respondents in seven countries including US and Germany, excluding India; 42% reported leaving a process when scheduling took too long. Vendor survey, not this customer's baseline.
- Legal questions are checks for local counsel, not claims that the same automation policy is lawful everywhere.

## Deliverable and writing decisions

- D1 and D2 remain at most two pages each, with visual flow/architecture diagrams where useful.
- D1 must state the dual problem accurately; recruiter capacity alone is an incomplete framing.
- Remove the large 400k / 20k / nine-days / four-month statistics strip; Roshan explicitly requested its removal.
- Include clearly named recruiter and applicant/candidate journey sections.
- Keep success metrics compact (maximum 25% of a page), with booking as north star, only the top three measures per category, and guardrails.
- Compress country verification into concise prose while preserving local sign-off and auditor evidence.
- D2 includes an actual component architecture with channels, workflow, scoring, storage and calendar boundary, not merely a linear process diagram.
- Distinguish proposed production capabilities, working assumptions and actual demo behavior.
- Use concise, plain language. Do not insert a different rejection strategy without Roshan's agreement.

## Artifacts and sources

- Assignment: `/Users/roshanmanellore/Downloads/Asssignment PM - 1.pdf`
- Original notes: `/Users/roshanmanellore/.codex/attachments/65605b43-ae61-4330-9865-89d4bb7a4e35/Pasted text.txt`
- Decision brief: `output/pdf/D1_Decision_Brief.pdf`
- Build sheet: `output/pdf/D2_Build_Sheet.pdf`
- Submission source: `tmp/pdfs/build_submission.py`
- Prototype and run instructions: `hiring-demo/README.md`
- This living record: `CASE_THINKING.md`

## Decision history

1. Original direction: deterministic checks plus LLM scoring, automated rejection and first-round scheduling.
2. Assistant introduced a recommendation to prohibit score-only rejection and route low scores to review. This was not Roshan's intended policy.
3. Roshan clarified bounded batching within the outreach SLA; explicit name redaction; concrete frontline parameters within a generic template framework; and a real database-backed demo.
4. Roshan requested removal of the statistics strip, explicit journeys and an architecture diagram; exceptions should first be resolved through WhatsApp.
5. Metrics were narrowed to a booking north star plus three business, performance and guardrail measures. Attendance was explicitly removed from the north star.
6. Problem framing was corrected to protect interview time and retain good candidates, with timely contact a major driver. Success-metrics space was capped at 25% of a page.
7. Latest correction restores automatic rejection for failed mandatory checks and below-threshold scores. Robust LLM scoring, validation, evidence and threshold control are the focus. Roshan requested this continuing Markdown record of the whole case.

8. Batching rationale clarified: compare applicants before allocating limited panel slots, while staying within every applicant's two-day outreach SLA. Twelve hours is a provisional fixed MVP cadence with follow-up headroom; optimize by customer through experiments rather than claiming it is the proven sweet spot.

## 4 November 2026 - D2 controls restored

Roshan flagged missing redaction, OCR/text-first cost design and hidden-text prompt-injection edge cases. D2 now explicitly covers these. Proposed implementation: compare rendered-page OCR with PDF text-layer extraction; inspect white/low-contrast, transparent, tiny, off-page and hidden-layer text; exclude metadata/annotations/embedded files; test Unicode obfuscation, visible instructions, keyword stuffing, PII leaks and benign multilingual/layout controls. Suspicious documents trigger clarification or unresolved-case review, not automatic rejection. The scorer has no tools or policy-write authority; validate evidence and output before deterministic totals and routing. These controls reduce risk and are not a guarantee of complete detection. They are production requirements, not implemented demo capabilities.

## 4 November 2026 - Research-backed coverage of five screening edge cases

User requested explicit mitigations for prompt injection/white fonting, non-linear careers, niche vocabulary/prestige over-indexing, complex layouts and AI resumes mirroring AI JDs. D2 was reorganized within its two-page limit: architecture, redaction/text-first cost choice, scoring/routing and impact on page 1; five-case mitigation/validation matrix and linked research on page 2.

Proposed controls extend beyond prompts: rendered-OCR/native-text discrepancy checks and PDF visibility checks; isolated tool-free scoring; versioned task/competency crosswalks and approved terminology retrieval; masking employer/university names while preserving relevant task/credential facts; layout-aware reading order/table extraction; evidence-anchored ratings and standardized clarification. Test equivalent facts across career histories, prestigious/neutral names, niche/plain terms, layouts and human/multiple-model prose. A citation establishes that a claim appears in a resume, not that it is true. Do not reject on suspected AI authorship. Later work samples/structured interviews can verify competence; these remain outside MVP. These are proposals requiring validation, not implemented capabilities or guaranteed defenses.

Research checked 4 November 2026:
- OWASP injection prevention: https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html
- O*NET occupation/military crosswalks: https://www.onetcenter.org/crosswalks.html (US reference; validate local mappings)
- Docling layout/provenance/reading order: https://docling-project.github.io/docling/concepts/docling_document/
- Xu et al., AI Self-preferencing in Algorithmic Hiring: https://arxiv.org/abs/2509.00462 (preprint; tested settings, not universal rates)
- OPM structured interviews: https://www.opm.gov/policy-data-oversight/assessment-and-selection/structured-interviews/
- Varshney and Ganuthula, contextual screening variations: https://arxiv.org/abs/2507.08019 (preprint; supports context-sensitivity concern, not every claimed prestige effect)

9. Candidate demo expanded: show a distinct candidate-facing application/chat journey with positive progression and recoverable missing-details cases, plus clear mandatory and score-threshold rejection paths.
10. Roshan corrected the keyword-matching template: use LLM-based semantic assessment. Gemini was explicitly chosen and connected; assessment instructions replace matching-term lists. Keep deterministic mandatory checks, aggregation, thresholding and scheduling separate from LLM evaluation. Never store API keys in this thinking file.

11. Roshan requested the demo use the case statement color scheme. Matched the source PDF palette: navy #014f99, blue #0169cc, bright accent #0183ff, pale blue #e6f3ff/#f0f8ff, charcoal #202020 and gray #6d6d6d. Apply across recruiter and candidate views, including messaging simulation; retain small semantic warning/rejection indicators.

12. Apply the case statement palette to both submission PDFs as well as the demo. Keep the existing content, diagrams, two-page limits and compact success-metrics budget. Use navy and blue accents, pale blue fills, charcoal text and gray dividers.

13. PDF review corrections: remove the decision brief subtitles on both pages; rephrase the recommendation around automated screening and booking, explicitly including panel-calendar lookup and automatic confirmation. Describe rushed screening's potential bias toward big employer brands rather than work quality as a working diagnosis to validate. Present recruiter and candidate journeys before the approach, flowchart and batching explanation. Describe the batch process first, then its benefit. Use distinct labelled pass (green), fail (red) and hold (amber) outcomes while retaining case-blue styling elsewhere.
14. The delivery plan is now two months/eight weeks, superseding the previous 16-week plan. Weeks 1-2 policy/baseline; weeks 3-4 build plus WhatsApp and SMS consent/templates/delivery integration; weeks 5-6 shadow scoring, channel retries and calendar failures; weeks 7-8 pilot and gated release. The case's seasonal peak remains four months away; that fact does not require a four-month implementation schedule.

15. State the problem volume explicitly: 400,000 applications annually for 20,000 roles. Present three main issues clearly: heavy screening load can cause good profiles to be missed through brand/keyword bias; delayed contact and first-round scheduling can lose good candidates; costly interview-panel time must be protected from unsuitable referrals. Treat the brand/keyword effect as a working diagnosis to validate, rather than claiming the eye-tracking study proves it.
16. Explain buckets before using the term: raw LLM scores are mapped to buckets because a difference such as 87 versus 88 may not be meaningful. Bucket-based prioritization applies only when candidate volume is high. Otherwise all passing candidates progress without score-based ordering. Do not rank within a bucket. The previously confirmed mandatory-check and below-threshold rejection rules remain in force; this clarification concerns priority among passing candidates. The previously noted always-on bucket ordering was corrected during the scoring consistency review: priority now activates at 80 eligible applications per requisition per batch (provisional); other batches use outreach deadline order.

17. Decision brief success metrics layout: use a full-width north-star statement followed by three clearly separated columns for business metrics, performance and guardrails, with three numbered items each. Keep the entire section within 25% of a page; favor readable structure over dense semicolon-separated paragraphs.

18. Applicant journey wording must state an explicit opt-in for communication over WhatsApp, replacing generic contact-channel selection. Keep modular channel support as a separate product capability.


## 4 November 2026 - WhatsApp components and inspectable execution

19. Roshan wants a recognizable WhatsApp experience: use business headers, message bubbles, timestamps, quick replies, interactive slot lists and confirmation components. It need not copy the official client exactly. This explicitly refines the earlier all-blue messaging surface: keep the case blue for the workspace/PDFs and familiar WhatsApp green within the phone.
20. Do not stage alternate-time responses. Demonstrate the workflow actually routing a candidate request, fetching panel data and constructing alternatives. Deterministic execution is acceptable; avoid fictional LLM or tool calls and artificial timing. Show invoked node names, inputs, outputs and data source alongside the chat.
21. Implemented choice: state/intent router plus limited deterministic day/period parsing. New alternatives query current availability and bookings, require the exact two panel members, exclude previously offered times and apply day/time preferences. Recheck before saving a unique booking. No matching capacity keeps the application active; it is not a rejection.
22. Screening uses Gemini for semantic evidence assessment; mandatory checks, aggregation, rejection thresholds, bucket mapping and scheduling remain deterministic. Missing details collected in chat update stored candidate facts and re-enter screening. Richer free-text intent interpretation is a possible later LLM use, not needed for the present simulation.
23. Technical choice: store workflow runs and node input/output payloads in SQLite, linked to candidate ID; persist WhatsApp component metadata with messages. A thread-safe live trace supplies in-progress nodes before the business transaction commits, then persists the completed run. No fake pauses; very fast deterministic work may appear complete immediately. Keep credentials out of traces. Production needs access and retention controls for these records.
24. D2 now has two separate workflow diagrams, screening and WhatsApp, alongside a compact component architecture. They show LLM boundaries, enterprise role policies, candidate/calendar reads and updates, and stored decisions/messages/bookings/execution evidence. Keep the two-page limit and existing impact table.
25. Demo proof should include positive recovery from missing details into screening/booking, negative mandatory or score rejection, and a no-calendar-match response. Show the live routing/tool trace and database persistence rather than a presenter staging the next chat message. Real external calendars and WhatsApp delivery remain simulated; Gemini scoring is live.

Tradeoffs and assumptions: deterministic parsing is easy to inspect and reliable for supported phrases, but does not understand unrestricted scheduling language. Calendar records are demo fixtures; the query and selection logic execute against current table contents. Excluding all prior offers avoids repeating rejected options but can exhaust a small calendar; the candidate remains in capacity wait and can receive new times when availability changes. Trace polling does not guarantee every sub-millisecond node is visibly running, so retain complete measured history for inspection. Explicit WhatsApp opt-in remains required.


26. Roshan clarified that the built workflow itself must be visible inside the prototype, rather than only an execution list or PDF diagram. Added a dedicated Workflows view with screening and WhatsApp diagrams, conditional branches, clickable node contracts and saved-run overlays. Green nodes identify actual execution; the inspector distinguishes expected inputs/outputs from recorded data and identifies uninvoked branches. The map is a read-only visualization of implemented paths, not a workflow editor or an MCP-server implementation. A direct entry from the candidate trace makes the graph discoverable.

## 4 November 2026 - Proposed enterprise onboarding (discussion, not yet approved)

Roshan asked for the easiest customer onboarding path, existing data and preparatory prerequisites. Proposed approach: treat this as feature activation on the existing recruitment platform, with one-time organization setup and reusable role/site templates. Assumption: customer already uses the recruitment module; a net-new platform customer also needs foundational recruitment data migration and integrations. Do not claim either onboarding wizard or enterprise connectors are already implemented in the prototype.

- Inventory existing requisitions/JDs, candidate resumes and structured answers, interview configuration, site/employee records, historical stages/offers/hires and messaging integrations. The case confirms platform capabilities, not that every customer has complete records or working connections. Calendar free/busy access, WhatsApp sender readiness and explicit candidate opt-in must be verified separately.
- Organization setup: admin connects approved channels/calendars, sets country/site/time-zone defaults, data access/retention and escalation owners; talent operations and relevant local leads approve activation scope. Reuse existing integrations and inherited settings instead of reconnecting per role.
- Role/site setup: recruiter selects a role template; system can prefill JD, location and existing mandatory questions. Approve deterministic checks, evidence anchors, weights, threshold and missing-input treatment. JD-to-rubric suggestions are a possible onboarding aid, not an already implemented capability or an authority to invent rejection rules. Persist versions.
- Scheduling prerequisites: assign panel or approved interviewer pool; define duration, interview mode, working hours, buffers and genuinely reserved interview capacity. Free/busy access alone does not guarantee that panel time is available for recruiting.
- Candidate prerequisites: reliable candidate/application IDs, deduplication, contact details and explicit WhatsApp opt-in; add missing requirement questions to the application form and collect outstanding answers through chat where possible. Do not silently reuse stale declarations for a new role.
- Validate using historical examples, known good hires (including the disputed best hire), independently labelled samples across outcomes, extraction failures and representative chat/calendar tests. Historical decisions are evaluation material, not unquestioned ground truth or a requirement to train a custom model. Set a baseline for outreach, booking and human effort; sample size/acceptance gates need a defined evaluation plan.
- Start with one role/site; run end-to-end shadow tests, then enable automatic decisions and booking only after readiness gates pass. Expand by copying approved templates and changing local requirements. No fixed onboarding-duration promise before dependencies are checked.
- Proposed product UX: a readiness checklist with Found / Needs confirmation / Missing, prefilled settings, sample application test, integration test and activation summary. Ask the customer to supply only missing inputs. Bulk template assignment and reusable panel/site settings reduce repeated effort at enterprise scale.

Strategic tradeoff: minimal setup must still make the rejection policy and interview capacity explicit. More forms or wholesale historic imports add burden; reusing unchecked defaults risks poor screening and unusable scheduling. Pilot on new applications and a small evaluation sample; migrate the entire backlog only when required. Minimum go-live inputs: active requisition plus approved policy, required candidate facts, usable channel/consent, connected panel calendars with interview capacity, local activation approvals and an accountable exception/review owner.


## 4 November 2026 - Confirmed system administrator onboarding and async rubric provisioning

Roshan simplified the customer onboarding model. This supersedes the earlier proposed multi-step onboarding/checklist as the default customer experience. Feature activation is a simple opt-in toggle, with one-time enterprise settings:

- System administrator chooses enabled communication channels: WhatsApp, SMS, email and other supported channels. Candidate WhatsApp consent remains a separate requirement.
- Set up the enterprise email account connection for panel-calendar data. Use the provider's authorized connection and scoped calendar access; email/calendar integration is a planned production capability, not an implemented demo connector.
- Select scoring-rubric scope: enterprise-managed role rubrics or job-level rubrics. Enterprise level means centrally controlled, role-specific criteria, not one identical rubric for unrelated jobs.
- Decide whether hiring managers can override the rubric. Proposed implementation detail: permitted overrides create traceable new versions; existing application snapshots remain intact.
- On feature opt-in, automatically enqueue all existing jobs/JDs for conversion into scoring rubrics. This is asynchronous because thousands of role/job rubrics may need generation. The LLM derives role evidence criteria from job data and enterprise settings; workers validate and store rubric versions.

Technical design details added to make the async behavior concrete: per-job queued/processing/ready/failed states, resumable workers, failure retries and progress reporting. A job can start automated screening once its rubric is ready, without waiting for every other job. Repeated enablement/retries should not duplicate rubrics for the same job/settings version. Changes to scope or source JDs should invalidate the relevant version rather than overwrite prior decision evidence. These details are design assumptions, not measured or implemented prototype behavior.

D2 now explicitly includes the System administrator role and a concise journey. State that the detailed administrator experience is not covered in this design. The user requested a design-sheet update, not a new administrator prototype. Architecture and delivery scope now mention enterprise settings and async provisioning. D2 keeps both existing screening and WhatsApp workflows and its two-page limit. Generating rubrics automatically on opt-in is now part of the proposed product, superseding the earlier positioning of JD-to-rubric generation only as a future enhancement. Country approvals/calibration remain launch activities; they are not extra customer forms in the basic feature opt-in flow.

## 4 November 2026 - In-app prompt inspection

27. Roshan requested that the prompt be visible in the application. Added View LLM prompt in the Workflows view and Gemini node inspector. It displays the real screening system instructions, role/rubric and redacted resume context, prompt/model version, JSON response schema and generation settings. This is read-only inspection, not a prompt-editing or model-training interface. Scoring and the viewer share one request builder to avoid presenting a separately maintained mock prompt. New Gemini trace nodes archive the full request payload without credentials. Older executions are explicitly labelled reconstructed previews based on the application policy snapshot and redacted resume; do not imply an exact historical prompt was stored. Deterministic WhatsApp routing/calendar actions have no LLM prompt in this prototype. The proposed async rubric-generation prompt remains outside the implemented demo.


## 4 November 2026 - Decision brief wording and north-star revision

28. Roshan requested explicit wording: deterministic mandatory checks; rule-based checks followed by LLM-based scoring against the rubric for each role; Applicant Journey; first-round panel members. Use periods in numbered lists and at list-item endings.
29. Clarify priority within a bucket: contact applicants whose original 48-hour outreach deadline is earliest first. This is deadline management among comparable passing scores, not fine-grained ranking within a bucket. Bucket prioritization still applies only at high volume.
30. Clarify calendar capacity handling: passing applicants remain eligible when no panel slot is available; the agent seeks alternatives. Rejection applies to the approved screening policy, not an interviewer capacity shortage. Preserve each applicant's original outreach deadline.
31. North star changed from weekly qualified booking count to average days from application to interview scheduled for qualified candidates. This explicitly owns the outcome through confirmed first-round booking, not just the first follow-up. The endpoint is booking confirmation, not interview attendance. Supplement the average with unbooked qualified-applicant counts and waiting time to avoid hiding unfinished journeys. The decision brief remains two pages and the metrics section remains below one quarter of a page.

## 4 November 2026 - Routing state and intent: options under discussion

Roshan asked whether state/intent routing needs an LLM and requested options before a decision. No implementation change is authorized by this question.

State should be read deterministically from stored application/conversation/booking data. An LLM is not needed to determine whether an application is waiting for a shift answer, rejected, invited or booked. Intent is distinct: structured button/list payloads are deterministic, whereas unrestricted messages can benefit from LLM interpretation.

Options presented: (1) entirely deterministic routing with guided buttons and limited supported phrases; simplest and predictable, but weak for free-text rescheduling/corrections. (2) hybrid routing: structured payloads and known commands use rules; free text goes through a constrained LLM intent/entity extractor, then deterministic state and action validation. Recommended for the proposed production conversation. (3) LLM-first intent routing for every message with deterministic execution validation; most flexible language handling but adds model calls, evaluation surface and variability even to simple button replies.

Recommended design proposal, not yet confirmed: keep state authoritative in the database; use a separate chat-intent prompt for free text, returning an allowed intent and extracted day/time/answer fields. Validate the interpretation against the current state, clarify ambiguity, then call calendar/candidate tools and save the result. Do not ask the LLM to invent calendar availability or decide whether a booking exists. A selected button needs no model call. The booked state must permit rescheduling intent instead of always short-circuiting to a booking-status reply, as the present demo does for unsupported free text. For a reschedule, retain the existing booking while alternatives are explored; only replace it after the candidate confirms and tools revalidate the new slot. Unsupported/ambiguous intent asks a targeted question rather than guessing an action. Screening and conversational intent use separate prompts and responsibilities.


## 4 November 2026 - Option 2 confirmed and implemented

32. Roshan selected hybrid routing. The prototype now routes known commands/buttons through rules and sends other messages to a separate Gemini chat-intent prompt. The model extracts intent, answer, requested date/period/time or offered-slot index; deterministic validation checks JSON, dates and permitted actions against stored state before candidate or calendar updates. State remains authoritative in SQLite. UI workflow graph includes the rules gate, conditional Gemini intent node and state validator; the prompt viewer exposes both screening and chat-intent instructions plus archived inputs.
33. Rescheduling now retains the existing booking while searching. Alternatives exclude prior offers and occupied times. Confirming a revalidated replacement updates the booking atomically, rather than deleting first; conflicts and no matching capacity leave the old booking intact. KEEP exits rescheduling. RESCHEDULE is distinct from explicit CANCEL, and natural-language cancellation requires confirmation. Old stored Reschedule buttons with legacy CANCEL IDs are normalized in the UI to the new safe reschedule command.
34. Model failures or ambiguous interpretations do not change answers/bookings; they request clarification and retain the rules path. No candidate/rubric/booking action is delegated to the intent model. The model uses local date and Asia/Kolkata context for this demo, with a 90-day future date limit; international timezone configuration remains production work. Tests mock both Gemini roles and cover 26 workflow cases. The build sheet and README now reflect hybrid intent routing rather than the superseded deterministic-only implementation.

35. Implementation verification encountered provider high-demand 503 responses on the existing scoring model. A listed Gemini chat model, gemini-3-flash-preview, successfully extracted a real rescheduling request. Configure intent separately with GEMINI_INTENT_MODEL; keep scoring configuration unchanged. This is a genuine provider call using the existing server-side connection, not a deterministic intent fallback. A previous live failure correctly kept the original booking unchanged.

36. Live browser proof: on fictional application #87, a selected slot booked 6 November at 09:30 IST through the rules path with no intent-model call. Free text "No, could we reschedule to 10th November afternoon please?" produced a genuine Gemini reschedule intent, 2026-11-10 date and afternoon period. The workflow fetched actual shared panel times from demo tables. SQL confirmed the 6 November booking remained present while alternatives were offered (Booked + rescheduling=1). Selecting 10 November 13:30 IST atomically replaced the original; one booking remained. The recorded tool output retains previous_booking and rescheduled=true. Browser verified the new conditional LLM node and its exact chat-intent prompt.

## 4 November 2026 - Release checks for false negatives and true positives

37. Roshan requested historical-data testing to measure the percentage of LLM-rejected applicants who actually got hired, and very high true-positive performance. D2 release checks now explicitly distinguish the denominators:

1. Rejected-but-hired share: historical hires among LLM-rejected applicants divided by all LLM-rejected applicants with known outcomes. This is the user's requested missed-hire measure; it differs from the conventional false-negative rate.
2. False-negative rate: historical hires rejected by the LLM divided by all historical hires in the evaluation cohort.
3. True-positive rate/recall: historical hires passed by the LLM divided by all historical hires in the same cohort. The proposed high-recall gate is >=98%, corresponding to <=2% false negatives; this is a provisional target extending the existing 2% guardrail, not observed model performance or a newly confirmed numerical user target.

Historical hires provide positive examples, including the disputed best hire. Historical non-hires do not prove unsuitability: candidates may decline, drop out, encounter capacity limits or never receive an adequate assessment. Independently label samples across score bands to estimate qualification and shortlist precision (qualified among passed / all passed); do not claim historical hiring outcomes alone validate all false negatives, true negatives or fairness. Use inputs available at application time, report outcome coverage/sample uncertainty, and avoid leaking later hiring decisions into screening features. Keep the LLM-stage metrics separate from deterministic-gate failures where possible. A high recall target alone can be met by passing everyone, so shortlist precision and unsuitable referrals still need scrutiny to protect interview time.

D2 remains two pages. The brief prototype-proof sentence moved to page 1 to make room for the explicit release criteria. Existing operational checks, administrator journey and impact table remain.


## 4 November 2026 - Coverage-and-speed north star and final metric categories

38. Roshan replaced average days to booking with the percentage of qualified applicants with a confirmed first-round interview booking within five days of application. This prevents optimizing speed only for the subset who book, and deliberately takes ownership beyond the client's requested first outreach. Interview attendance is still outside the metric boundary. Business metrics are now time to first booking, genuinely qualified-to-booked conversion in a defined observation window, and manual intervention rate excluding planned audits. Performance/efficiency metrics are meaningful outreach within 48 hours, qualified applicant response within 12 hours, and fully loaded cost per qualified booking. Guardrails cover independently audited screening errors/fairness, error-free booking percentage, and candidate complaints/opt-outs/unresolved exceptions. This latest framework supersedes the earlier time-to-fill/recruiter-effort grouping and average-days north star. The decision brief has been updated; no new dashboard calculations are claimed by this document change.


## 4 November 2026 - Default role criteria and post-pilot message timing

39. Roshan requested that the recruiter journey explicitly explain role-derived defaults and the option to edit them. D1 now distinguishes job-specific requirements (salary range/expectations, visa or work authorization, shifts and location) from the job-matching rubric (scoring criteria, weights and threshold). Recruiters review and modify defaults as permitted by enterprise settings, then approve the version. This is consistent with the existing administrator override control and automatic rubric provisioning; it is not a request for a new prototype feature.
40. After the pilot, test whether sending messages at particular local times of day improves applicant response rates. This is a later optimization, not an additional MVP dependency or a reason to exceed any applicant's 48-hour outreach deadline. Track five-day booking conversion alongside response rates to maintain ownership of completed scheduling outcomes. Proposed experiment design for later specification: compare time windows within the permitted outreach interval, account for candidate timezone and compare comparable role/site cohorts; do not claim a best send time before measuring it.


## 4 November 2026 - Logical node implementation in the prototype

41. Roshan requested code for logical nodes inside the application. Added View node code to non-LLM workflow node inspectors and expanded non-LLM execution steps. Show actual current Python implementation from an explicit whitelist, not pseudocode, with function names, line numbers, source fingerprint and relevant-line highlighting. Some nodes share assess(), resolve_message() or reply(); display the full function as context and state that historical execution records may predate current source. LLM nodes continue to show prompts. No arbitrary file lookup, credentials or editable code execution is exposed. This is a prototype inspection aid, not an enterprise workflow editor.


## 4 November 2026 - Scoring consistency review and canonical contract

42. Roshan identified drift between the briefs and prototype and authorized choosing the most sensible consistent logic and labels. Review found different criterion names and rating descriptions, ambiguous integer-only bucket ranges, always-on bucket priority despite the stated high-volume rule, and raw-score sorting in the app. Stored totals matched criterion points; preserve historical data rather than fabricate re-assessment.
43. Adopted one shared scoring_policy.json, imported by the engine and PDF builder and served to the UI. Rating labels are 0 No evidence, 1 Limited evidence and 2 Clear evidence; a 2 requires concrete task context, not necessarily a numerical result. LLM produces semantic criterion ratings and source quotes; deterministic Decimal arithmetic computes Match score = sum(weight * rating / 2), rounds once half-up to two decimals and applies the job threshold (default 70, equality passes). Weights sum to exactly 100 and policy numbers support at most two decimals. A failed extraction/provider call remains Not scored, rather than a zero rating.
44. Bucket labels stay Poor, Fair, Good and Excellent. Precise boundaries are Poor [0,50), Fair [50,70), Good [70,86), Excellent [86,100]. Buckets describe match strength independently of the configurable job threshold; for example, score 75 remains Good but rejects under a threshold of 80. This avoids relabelling a bucket when the customer changes its threshold.
45. High-volume bucket priority now starts at 80 eligible applications per requisition per batch, explicitly a provisional trigger based on the p90 planning assumption; tune with customer data. Use outreach deadline order within buckets and at ordinary volume. The list sorts buckets then deadlines, not individual scores. This controls invitation priority; offers are not exclusive slot holds, and booking availability is rechecked separately.
46. Warehouse criterion names and weights now match everywhere: Order picking & packing 30; Inventory & stock accuracy 25; Scanner / warehouse systems 20; Workplace safety procedures 15; Dispatch & receiving 10. Job-specific edits remain versioned. Demo mandatory checks are shift/site/start; salary/visa rules are production extensions, not implemented fields.
47. New role versions include the canonical contract. Existing application snapshots and evaluator history remain unchanged; legacy assessments are visibly labelled rather than represented as current LLM runs. New scoring prompt role-evidence-v2 derives evidence anchors from the contract. New scoring defaults to the Gemini model already working for intent after the old default returned temporary overload errors; actual model provenance remains stored. Scoring code inspection includes policy.py as well as its caller. Both briefs remain two pages, with D1 metrics still under 25%.

48. Verification: 32 policy/workflow tests passed, covering fractional boundaries (including 85.99 vs 86), 69.995 half-up to 70 before comparison, equality, Good-but-rejected under a higher threshold, invalid weights/ratings and volume-dependent ordering. Fresh fictional application #90 completed a live Gemini role-evidence-v2 assessment after one temporary 503 retry; it stored the new role policy and scoring contract without changing historical records. UI and PDF rendering are being checked against the shared definitions.

49. Final verification completed: all four PDF pages rendered cleanly, both documents remain two pages, and D1 metrics remain 22.7% of a page. The browser showed canonical labels/bounds in role configuration and the saved live assessment (#90: Match score 100, Excellent, all five criteria Clear evidence with correct 30/25/20/15/10 contributions). Historical scores were not recalculated. The prototype, prompts and PDF authoring now consume one scoring contract rather than independent definitions.


## 4 November 2026 - Replace associate tasks with a realistic shift-manager rubric

50. Roshan supplied a PM rubric (domain exposure/three years, technology exposure, leadership, innovation and quantifiable impact) and asked for realistic warehouse shift manager criteria in the examples. The prior picking/inventory/scanner task list was an associate rubric and is superseded for new examples. Translate the PM dimensions into warehouse operations experience, shift/people leadership, warehouse technology/data, operational improvement and measurable impact; add safety/compliance leadership as a separate role-critical dimension.
51. Proposed default weights are 20/35/10/15/10/10 respectively. Leadership is the largest dimension because the role runs a team/shift; with no leadership evidence, even maximum remaining ratings produce 65, below the default threshold of 70. These are design defaults, not empirically validated weights. Three years of domain exposure is an illustrative preference; a mandatory experience gate would need an explicit approved job requirement and supporting candidate data.
52. Assess managerial ownership: staffing, rosters, coaching, handovers, WMS/KPI decisions, safety briefings/audits/corrective actions, bottleneck diagnosis and process rollout. Do not equate following PPE rules with safety leadership, naming WMS with using data to manage a shift, or team size/order volumes with demonstrated improvement. For impact, rating 2 requires numerical outcome evidence plus scale/time context and candidate contribution; do not invent numbers. Unquantified improvements may rate 1. This updates generic anchors to criterion-specific evidence requirements rather than universally waiving quantification. Other criteria do not automatically require numerical business results.
53. Central contract match-policy-v2 holds the manager role, six criterion labels/weights/assessment instructions/evidence examples and sample resume. The scoring formula, rating labels and Poor/Fair/Good/Excellent bounds remain unchanged. Prompt role-evidence-v3 respects each application's saved anchor contract; old applications keep their original role/policy/evidence instead of being presented as newly scored managers. Default role migration is recorded, and the app displays saved historical role names. Updated both briefs and prototype examples together.

Research checked 4 November 2026. These sources support role responsibilities, not the exact weights or a universal three-year rule:
- Amazon Area Manager responsibilities: team leadership, safety, quality/productivity, performance metrics and process improvement. https://www.amazon.jobs/en/jobs/10506519/area-manager-fulfillment-center-operations
- O*NET first-line material-moving supervisors: safe working environment, staffing/schedules, coaching, training, reporting and operational supervision. https://www.onetonline.org/link/details/53-1042.00

54. Verification: 33 policy/workflow tests passed after replacing the associate rubric, including a manager-specific check that absent leadership evidence cannot reach the default threshold even with maximum other criteria. Both PDFs rendered cleanly at two pages; D1 metrics remain 22.7% of a page. The active example migrated to Warehouse shift manager policy v4, while existing application #90 still reports Warehouse associate from its original snapshot.

55. Live manager-example verification completed: fictional application #91 used Warehouse shift manager policy v4, role-evidence-v3 and match-policy-v2. Gemini returned six Clear evidence ratings with contributions 20/35/10/15/10/10, yielding Match score 100 and Excellent. The impact rating cited actual before/after dispatch-time and accuracy changes and overtime reduction; leadership and safety ratings cited team-level ownership. The browser verified the six editable default criteria and their criterion-specific anchors. Earlier associate applications remain intact.

## 4 November 2026 - Deeper component architecture

56. Roshan requested one level more architectural detail, with LLM, database and communication shown as individual blocks. D2 now separates nine components: recruiter/applicant UI (including admin setup), document processing, workflow/policy API, LLM service, communication service, MCP calendar gateway, enterprise panel calendars, queue/workers and application/audit database. The workflow API is the coordination hub; arrows distinguish document ingestion, model requests/results, messaging send/receive, calendar tool calls, database reads/writes and queued work. LLM calls do not directly control communications, calendars or the database. Queue/workers handle rubric provisioning, batches and retries. This is a production-component proposal; the caption distinguishes the demo's SQLite/live Gemini implementation and simulated messaging/calendar adapters. Both existing workflows and manager rubric remain, and D2 stays within two pages. Repeated explanatory prose was compressed to make room for the larger diagram.


## 4 November 2026 - Make OCR/text-first costs and redaction explicit

57. Roshan requested clearer emphasis in D2: do local text extraction/OCR before the LLM, rather than passing the entire PDF/images into a multimodal model. Send only normalized, redacted text and the role rubric to reduce model-side document/vision processing costs. Reuse native text where readable; OCR is needed for scanned/image inputs. Measure total extraction/OCR cost and fidelity in the pilot rather than claiming a proven total saving. The document-processing component now explicitly says local text/OCR followed by redaction.
58. Baseline planned redaction covers candidate name and location, not only names. Following employment/legal/privacy checks, redact additional fields such as education institute names and agreed proxy attributes before LLM transmission. Keep job-relevant qualification facts (for example degree/certification type) and skills, rather than removing all education evidence. Candidate personal location is excluded from LLM matching; separately approved site-attendance/authorization eligibility checks can still use structured declarations outside the model.
59. Scope is explicit: the current prototype extracts text from readable PDFs/TXT and masks names/contact details. OCR and reliable location/institute redaction are not implemented by this document edit. D2 marks these as remaining production work so the design does not falsely claim the prototype already performs them. Unreadable or failed extraction pauses screening rather than becoming a low score. D2 remains two pages; repeated chat-routing prose was compressed while preserving the separate architecture blocks and both workflows.

## 4 November 2026 - Architecture iconography

60. Roshan requested visual icons for database, LLM and users in the architecture diagram. D2 now uses a conventional database cylinder, an AI processor icon for the LLM, and a two-person users icon. They are native vector drawings, preserving sharp PDF rendering, case colors and readable labels. Connections and component boundaries are unchanged; the build sheet remains two pages. This is a document-diagram update, not an application implementation change.


## 4 November 2026 - Deterministic form checks and inspectable model output

61. Roshan requested the screening workflow label “Deterministic checks from application form input.” The build sheet uses “Deterministic checks” with “Application form input” underneath; the prototype graph and new execution traces use the same terminology. Existing internal node IDs remain unchanged for historical trace compatibility. Structured shift/site/start answers are checked against approved role requirements before LLM matching; these are separate from semantic resume evaluation.
62. D2 now shows an illustrative JSON output for one of six criteria: ratings entries contain key, integer rating, exact source quotes and factual rationale. This is an example, not a newly executed assessment. The LLM does not produce the final weighted Match score or rejection decision: code validates the schema and quotes, calculates the score, applies the configured threshold, and persists the assessment with policy/model/prompt provenance. Existing bucket labels and boundaries are unchanged.
63. User strategic preference: direct parameter-scoring models such as TypeSafe Jev are an option but are not selected for this MVP, which requires evidence and an explanation per criterion. Verified the official introduction (https://typesafe.ai/blog/introducing-system-one-models-and-jev): Jev returns typed probabilistic decisions and gives up generated strings. Phrase the limitation as the score-only interface lacking written rationale and source-linked resume quotes; an additional evidence/explanation layer would be needed. Do not claim the model cannot reason, that evidence selection is impossible, or that a comparative Jev evaluation was run. Reconsider only if an implementation can satisfy the same evidence/provenance contract.

64. Roshan flagged percentage-unit ambiguity in the formula. Display Match score = 100 * sum(weight_fraction * rating / 2), with 35% = 0.35 explicitly. Existing calculation uses percentage-point weights (35 rather than 0.35) and already yields the same 0–100 score; no scores, thresholds or buckets change. Both PDFs and the app wording use the explicit normalized formula.

65. Clarification: inbound WhatsApp sender/contact identifies the person; application ID identifies the job-specific workflow and is the primary routing context. One candidate can have multiple applications, so candidate ID alone is insufficient. Production conversation/message context must map to an application; ambiguous messages require disambiguation before acting. The prototype currently uses a single candidate/application record per submission, not a fully separate person entity. Update the workflow labels without claiming that full identity mapping has been implemented.
66. Roshan requested WhatsApp opt-in rate under Performance & Efficiency. Add it as a fourth metric alongside existing three: unique applicants explicitly consenting / unique applicants shown the WhatsApp consent prompt, within the same observation cohort/window. Do not use all contacted applicants as denominator or count multiple applications as multiple people. Keep success metrics within 25% of the page; no numerical target is assumed before pilot.


## 4 November 2026 - SMS links reuse the candidate journey

67. User decision: SMS is a notification/link channel, not a second conversational interface to build. Send a link that opens a mobile scheduling page with the same candidate experience as WhatsApp: supply missing details where needed, see slots, request alternatives, confirm and reschedule. Reuse the application-scoped workflow, state machine, intent/rule routing, calendar tools, booking validation and persistence. The page supplies a different presentation adapter over the same orchestration; avoid duplicating scheduling business logic or running separate booking state per channel.
68. No SMS/page prototype is requested or implemented. Both submission briefs describe this design; the running WhatsApp prototype remains unchanged. Proposed implementation detail: use an opaque, expiring application-scoped access link rather than exposing a raw application ID; messaging-channel changes must preserve the existing application deadline and booking state. Link expiry/recovery and access controls are implementation work, not a claimed demo capability.

69. User requested removing the parenthetical percentage-conversion example from the PDFs and app. Keep the normalized formula and all calculation behavior unchanged. This supersedes item 64’s instruction to display the example explicitly.

70. Roshan clarified the model-selection tradeoff: TypeSafe Jev/direct typed scoring could lower inference costs, but this design prioritizes explainability (written rationale plus source-linked resume evidence) over potential savings. D2 states that priority explicitly. Cost reduction is a possibility supported by vendor positioning, not a measured saving for this screening workload; no comparative evaluation is claimed. A score-only interface needs an additional evidence/explanation layer to meet the selected output contract.


## 4 November 2026 - Panel working hours and time zones

71. User decision: scheduling must respect each panel member's working hours, including members in different time zones. A free calendar is not sufficient: only offer the intersection of required members' free/busy and local working-hour windows. Use IANA zones and date-specific daylight-saving offsets, converting feasible intervals to UTC for comparisons and storage; display options in the candidate's selected zone. Recheck before confirmation. No common working-hour overlap means find alternatives/escalate, not silently book outside hours.
72. Scope: add a build-sheet note and prepare database storage; do not implement working-hour filtering or new prototype screens. Added panel_members (IANA time_zone), role_panel_members (membership) and panel_working_hours (weekday, local minute windows). Multiple windows support breaks; split overnight shifts across days. Tables are empty until real settings are imported, with no fabricated panel zones/hours. Current availability/booking tables and scheduling queries remain unchanged. Time-zone validation, calendar integration, DST boundary handling, holidays/date exceptions and the scheduling algorithm remain future implementation work. Schema initialization is idempotent and preserves existing records.

73. User requested simplifying the release quality gate to false-negative rate only. Remove rejected-but-hired share (different denominator, not mathematically the same rate) and true-positive rate (complement of false-negative rate on the same historical-hire cohort). Keep FNR = LLM-rejected historical hires / all historical hires, with a provisional 2% ceiling. Historical hires are an incomplete proxy for qualified applicants; retain independent sampling across buckets and do not equate non-hire with inability. This is a presentation simplification, not removal of the broader screening-quality guardrails.


## 4 November 2026 - Binary historical evaluation and disagreement review

74. Roshan clarified the evaluation design: use all historical application data available, with only a binary “send for interview” / “do not send” target. Do not manually label every score/criterion or perform exhaustive score-level reviews; this is inefficient. Use the information available at application time as model input, never the later interview/hire decision. Missing/unknown historical outcomes must remain unknown rather than being forced into a negative label.
75. Historical decisions may encode recruiter or organizational biases. Model/history mismatches are apparent errors against a historical reference, not confirmed errors against objective qualification. Review both directions manually: apparent false positives = LLM says fit/pass but the applicant historically was not given an interview; apparent false negatives = LLM says unfit/reject but the applicant historically was given an interview slot. Review the underlying application evidence and job criteria rather than automatically siding with either source. A non-hire or absence of an interview alone does not prove poor fit. Correct the binary labels based on review, record adjudication reasons and version the evaluation set, then rerun evaluation.
76. The release FNR now uses the reviewed binary interview labels: rejected interview-positive cases / all interview-positive cases, with the existing provisional 2% ceiling. This replaces the historical-hire denominator and earlier instructions to independently label every band in D1/D2 (including items 63/73 and prior historical quality discussions where inconsistent). Keep both disagreement directions in the review process even though FNR remains the single headline release metric. For credible release measurement, keep a frozen, separately reviewed holdout and report original-history disagreements separately from post-review errors; correcting labels must follow evidence, not serve to inflate agreement. Disagreement review alone cannot reveal biases shared by both history and model, so the broader fairness guardrail remains; it does not imply labelling every score.

77. User requested the build-sheet heading “Warehouse shift manager role scoring rubric.” This replaces “Warehouse shift manager rubric”; scoring logic is unchanged.

78. User requested an explicit pitfalls/controls section in D2. Added four risk-to-control mappings: bad extraction/model output or prompt injection -> untrusted input, schema/exact-quote validation, Not scored/retry; proxy bias/false precision -> redaction, role anchors, reviewed binary evals and high-volume-only buckets; candidates lost in batching/chat -> immutable 48h deadline, bounded 12h batches, channel retries and 36h escalation; unreliable bookings -> atomic recheck/booking, idempotent retry handling, retain old booking during rescheduling, and planned local working-hours/time-zone intersection. Preserve audit, country sign-off, outage/closure checks and manual fallback. These are design controls, not a claim that all production safeguards are already implemented in the demo. Compress repeated impact/admin prose to retain the two-page limit.


## 5 November 2026 - Restore detailed sections; focus pitfalls on LLM risks

79. Roshan requested restoring the pre-pitfalls admin journey, release checks and standalone scheduling note. Restore their fuller wording, including detailed setup/provisioning, both historical-disagreement definitions, reviewed FNR and manual fallback separately from kill switch. Keep the existing shortened impact table.
80. Replace the broad workflow pitfalls with a compact LLM-specific section addressing all five user-supplied risks: resume prompt injection/hidden instructions -> untrusted-data isolation, constrained outputs and adversarial tests; non-linear careers -> transferable task evidence rather than penalizing career gaps or traditional titles; brand/prestige and unfamiliar jargon -> agreed proxy redaction plus equivalence/niche-vocabulary evaluation; complex layouts -> text/OCR reading-order validation and paused scoring on extraction failure; AI-tailored resumes mirroring JDs -> concrete work evidence rather than linguistic similarity. These reduce risk, not guarantee immunity or verify truth. Resume source quotes establish traceability only; background/evidence verification remains later/future work. Do not claim every malicious instruction succeeds or that an LLM can reliably distinguish authentic from AI-authored resumes. No new prototype behavior is requested.


## 5 November 2026 - Structured rating columns and deterministic prompt assembly

81. User decision: replace editable free-form rubric instructions in Role templates with three evidence-definition columns for fixed ratings 0 (No evidence), 1 (Limited evidence), 2 (Clear evidence). Keep criterion names/weights and the rejection threshold editable, and allow adding/removing criteria on the same page. Require 1-12 criteria, all three nonempty definitions and total weight exactly 100 before publishing. Fixed numeric rating keys, schema, calculation and system instructions remain owned by the application. Text can still be adversarial, so server-side response validation remains authoritative; UI structure alone is not a guarantee against injection.
82. Implemented rating_criteria JSON on each criterion, persisted in existing role-policy JSON; active templates migrate to anchored definitions, existing application snapshots remain unchanged. Warehouse defaults now provide explicit criterion-specific anchors. Added read-only draft prompt preview using the real compiler without a model call. Preview does not save. New screening.build_prompt deterministic workflow node combines role/evidence definitions, fixed instructions/schema and redacted resume; the exact result is archived and passed to scoring rather than reconstructed separately. Its code and assembled prompt are inspectable in Workflows. Prompt version is role-evidence-v4. Added/removal publishes create new policy versions; earlier candidate records retain their original policy.
83. Validation: 37 tests pass, covering invalid rating 5 despite an edited anchor, incomplete/extra rating keys, add/remove weight constraints, legacy snapshots unchanged and actual prompt-node output feeding the LLM node. A previously date-sensitive scheduling test now seeds the exact target local date explicitly to avoid UTC/IST midnight fixture drift. Browser checks verified missing definitions block publication, draft anchors appear in compiled prompt, and adding then removing a demo criterion persists correctly. Restored the warehouse example to its six canonical criteria/weights after verification. No messages were sent.

84. Live verification: fictional application #94 completed Gemini role-evidence-v4 screening with six criteria and Match score 100. Its saved run includes completed screening.build_prompt output exactly equal to screening.llm_assess input request_data. Browser verified the new node, source-code inspector, compiled prompt and new role-template columns. D2 wording now reflects editable 0/1/2 definitions compiled into a fixed prompt/schema; it remains two pages.

85. User requested that the system prompt stop defining what ratings 0/1/2 mean. Prompt role-evidence-v5 now instructs the LLM to select ratings according to each criterion's supplied rating_criteria; the system retains only the allowed numeric set, schema/evidence requirements and trust boundaries. Criterion-specific definitions remain in the user-data payload, authored in the three UI columns. Do not duplicate generic anchor meanings in system instructions. Historical execution prompts remain archived unchanged.
86. Diagnosed the overview complete-journey path: it opened recruiter entry, and submission never honored the existing candidateMode flag; new candidate applications were not selected/persisted in Candidate experience. A live reproduction also hit Gemini HTTP 503, and recruiter detail incorrectly offered slot buttons despite Scoring pending. Fixed overview CTA to open candidate entry, submission to save/select the new application in Candidate experience, and shared status-aware reply buttons across candidate/recruiter views. Provider failures expose RETRY and keep original application/deadline; no invented scores or automatic qualification fallback. Recruiter detail batch advance now scopes to the selected application rather than all applications. Verified 37 tests including failure-to-retry recovery with immutable deadline; browser end-to-end verification follows.
87. Browser verification completed: overview CTA -> candidate form -> fictional application #96 -> live Gemini v5 screening -> application automatically selected in candidate WhatsApp view -> advanced its batch -> selected a real table-backed panel slot -> confirmed booking. The current prompt dialog shows criterion meanings only in rating_criteria, not generic system-level anchor definitions. Saved screenshots document the prompt and booked journey. Earlier failed application #95 remains Scoring pending rather than being discarded or falsely rejected. All 37 tests pass, including retry recovery.

88. User requested restoring the 98% true-positive figure in D2 Release checks. Show provisional FNR <=2% and TPR >=98% on the same reviewed binary interview-positive cohort. TPR = LLM-passed interview-positive cases / all interview-positive cases; it is recall, not precision (qualified among all passed). With complete binary outputs, TPR and FNR sum to 100%; these are complementary targets, not independent gates. Preserve both disagreement reviews and iterative evaluation-set correction.

89. Repeated journey report diagnosed against the user's original overview tab (not a fresh test tab): it still displayed 89 applications, Warehouse associate and policy v2, and its CTA used the old navigate('apply') handler. The previous fresh-tab verification did not update this already-loaded page. Header Refresh only re-fetched state and retained old JavaScript. Change Refresh to a full page reload (title explains app + data), and send Cache-Control: no-store on local static/API responses. Reload the original overview and verify there, without changing saved applications. This distinguishes stale in-memory code from the earlier Gemini 503/incorrect retry-controls issue.

90. Re-verified in the original user overview tab after reloading it: current role/policy appeared, the journey CTA opened candidate mode, fictional application #97 completed live screening and a table-backed confirmed booking. Verified no-store on index.html, app.js and API state. Header Refresh now reloads the app and resumes the saved candidate/application. Earlier verification in a new tab alone was insufficient to catch stale code in the original tab.

91. User requested an explicit note directly below the five LLM pitfalls: prepare evaluation data covering every listed scenario, test each scenario and iteratively refine the prompt until agreed quality/robustness acceptance thresholds are met. Added to D2 without removing content; tighten page-two spacing to retain two pages. Treat these thresholds as release gates, not an already achieved performance claim; retain separate holdout measurement to avoid tuning solely to the evaluation examples.


## 5 November 2026 - Candidate communication policy

92. User decision: passing screening is internal. Do not send a screening-passed message; outreach to passing candidates begins only once actual interview slots are known, and the invitation includes those slots. Awaiting batch does not set first_outreach. No-capacity initial scheduling attempts silently retain the candidate as Capacity wait without claiming outreach; responses to candidate-requested alternatives can still explain lack of availability. Missing-detail questions remain actionable exception communication. Candidate summary is neutral and does not disclose screening-passed status.
93. Default rejection wording: “We regret to inform you that, while we appreciate your time, we cannot move forward with your application.” Do not reveal scores, thresholds or criterion weaknesses in default WhatsApp messages or candidate summary. Internal scores/reasons remain available to recruiters/audit. WHY returns a non-numeric explanation and review route. Apply a candidate-safe projection to old demo conversations so earlier screening-passed/score-bearing rejection messages do not reappear, while preserving original stored messages and audit records.
94. Browser verification: a fresh passing scenario produced no WhatsApp message or first_outreach until its batch fetched slots; the first message then invited the candidate to choose an interview time. A fresh deterministic rejection showed only the regret wording in both chat and candidate notice. Internal scores/reasons remain in recruiter records; older chats use a candidate-safe projection without rewriting raw history. All 41 tests pass, including slot-only first outreach, silent no-capacity handling, generic rejection and legacy projection checks.

95. User requested a location filter in Applications. Added a Location dropdown derived from existing role/site data (job location, not the candidate personal location redacted from LLM inputs), combined with search, role and status filters. Filter changes reset 15-row pagination. Added a Location table column and responsive filter wrapping; no database change needed.
96. Browser verified Location options from role sites, Pune empty state, reset from page two to first page on filter change, and combined Bengaluru + warehouse role + Booked + Aarav search (three matching applications). No new applicant data was needed. Screenshot saved; existing scoring and stored data unchanged.
