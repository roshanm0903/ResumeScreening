from pathlib import Path
p=Path('tmp/pdfs/build_submission.py');s=p.read_text()
s=s.replace("('Requirement mismatch','Human decision and reason'),('Unknown or low evidence','Review with a response deadline')", "('Missing or conflicting details','Clarify through WhatsApp first'),('Confirmed or disputed mismatch','Human decision when needed')")
s=s.replace("Automate routine progression; retain human decisions for adverse or uncertain outcomes. Do not launch score-only rejection. This changes the requested no-recruiter model: exceptions need a staffed queue, while clear matches proceed without recruiter coordination.","Automate routine progression and resolve missing details or scheduling exceptions through WhatsApp first. Human review is reserved for unresolved or contested cases and decisions that require it. Do not launch score-only rejection; a low score is not proof of inability.")
s=s.replace('y=stats(y+3)\n','')
s=s.replace("Recruiters cannot read every application. Brief scans under time pressure can miss relevant experience, while gap resolution and calendar coordination add work. Ladders reported a <b>7.4 second initial scan</b>, not a full assessment [1]. Time pressure is our hypothesis, not that study\\'s causal finding. Cronofy found that <b>42%</b> of surveyed candidates had left a process because scheduling took too long [2].", "Recruiters cannot read every application; gap resolution and scheduling add work. Ladders reported a <b>7.4 second initial scan</b>, not a full assessment [1]. Time pressure is our case hypothesis. In Cronofy\\'s survey, <b>42%</b> had left a process because scheduling took too long [2].")
start=s.index("y=heading('Choose a hybrid approach',y)")
end=s.index("check(y,'D1 page 1')",start)
s=s[:start]+'''y=heading('Recruiter journey',y)
y=body('Open the requisition, select the role template and approve job-specific criteria. Add the first-round panel; the agent fetches availability. After publication, monitor scores, outreach deadlines, conversation outcomes and bookings. Act only on escalations. On role closure, stop new invitations and notify remaining applicants.',y)
y=heading('Applicant and candidate journey',y)
y=body('Apply on mobile, upload a resume, provide role requirements and select a contact channel. Receive a WhatsApp update within 48 hours. Confirm missing details in the same conversation; select one of three slots or request alternatives. Receive confirmation and reminders, reschedule if needed, and request reasons or human review without an employee login.',y)
y=body('<b>Approach and scope.</b> Use explicit requirements plus role-specific scoring. Avoid relative bottom-of-pool rejection; do not rank within bands. Assume inbound applications and structured answers already exist. WhatsApp is the first exception-resolution route; SMS or another approved channel is the fallback.',y,0)
'''+s[end:]
s=s.replace("Missing evidence never proves inability.", "Missing evidence never proves inability. Resolve factual gaps in WhatsApp; send only unresolved, contested or legally required cases to a human.")
s=s.replace("Parsing failures enter review.","Request re-upload for parsing failures; escalate only if unresolved.")
s=s.replace("Let candidates request reasons, correct data and seek review through a verified contact link; no employee login is assumed.","Candidates can request reasons, correct data or seek human review through WhatsApp or a verified link; no employee login is assumed.")
s=s.replace("Talent acquisition approves role requirements, weights and thresholds before a job goes live. Each rule records an owner, a job-related reason and a version: for example, which licence a driving role requires and why. The agent cannot invent criteria. Name redaction is included; further proxy controls will be decided during detailed design.","Talent acquisition approves requirements, weights and thresholds before publication. Record each rule\\'s owner, job-related reason and version; for example, why a driving role needs a licence. The agent cannot invent criteria. Redact names; decide further proxy controls during detailed design.")
s=s.replace("Start with one role family and selected sites. Advance only after country approval, quality checks, calendar tests and review staffing pass. Pause automated progression on evidence drift, harmful outcomes or backlog growth; preserve scheduling and candidate updates where safe. Revert to manual screening rather than force a seasonal launch.","Start with one role family and selected sites. Advance after country approval, quality checks, calendar tests and escalation coverage pass. Pause automated progression on harmful outcomes, evidence drift or unresolved backlog; preserve safe scheduling and candidate updates. Retain manual screening as a fallback.")
# Add an actual component architecture with storage and external service boundaries.
start=s.index("y=heading('Workflow and integration boundaries',y)")
end=s.index("y=heading('Dynamic role templates with explicit evidence anchors',y)",start)
s=s[:start]+'''y=heading('Solution architecture',y)
w=150;gap=(CW-3*w)/2;xs=[M+i*(w+gap) for i in range(3)]
for i,(t,sub) in enumerate([('Recruiter workspace','Requisitions, templates, dashboard'),('Applicant mobile journey','Resume and structured answers'),('Channel adapter','WhatsApp / SMS and consent')]):
 node(xs[i],y,w,43,t,sub)
# The three interfaces share a service boundary; replies return through the same channel.
for x in [xs[0]+75,xs[1]+75,xs[2]+75]:
 c.setStrokeColor(GREEN);c.line(x,H-y-43,x,H-y-55)
c.setStrokeColor(GREEN);c.line(xs[0]+75,H-y-55,xs[2]+75,H-y-55)
arrow(xs[1]+75,y+55,xs[1]+75,y+67)
for i,(t,sub) in enumerate([('Document and scoring service','Parse, redact, extract evidence'),('Workflow and policy engine','Batch, clarify, route and retry'),('MCP calendar gateway','Availability and booking tools')]):
 node(xs[i],y+68,w,51,t,sub)
arrow(xs[1],y+93,xs[0]+w,y+93);arrow(xs[0]+w,y+101,xs[1],y+101)
arrow(xs[1]+w,y+93,xs[2],y+93);arrow(xs[2],y+101,xs[1]+w,y+101)
node(M,y+145,2*w+gap,48,'Application database and audit events','Candidates, scores, evidence, policy versions, messages and bookings')
node(xs[2],y+145,w,48,'External panel calendars','Production via MCP; demo tables')
arrow(xs[0]+75,y+119,xs[0]+75,y+144);arrow(xs[1]+75,y+119,xs[1]+75,y+144);arrow(xs[2]+75,y+119,xs[2]+75,y+144)
y+=205
y=para('Candidate replies return to the workflow engine. Validated answers update the database and trigger policy re-evaluation; calendar actions stay deterministic. Every action records its candidate ID and policy version.',M,y,size=8.3,leading=11.2)+12
'''+s[end:]
s=s.replace("Build on existing requisitions, candidate records and scheduling. Keep evaluation separate from tool actions. The model extracts role-related evidence; a versioned policy determines the permitted next step. Scheduling and booking use deterministic checks.","Reuse recruitment records and scheduling. The model extracts role evidence; approved policy selects actions. Resolve factual gaps and scheduling exceptions through the candidate\\'s messaging channel before escalating.")
s=s.replace("Organization controls flow into a role-family template, then approved requisition adjustments. Parameters vary by role. Warehouse associate example below; confirm shift, site, start date and offered pay acceptance separately. Require a licence only where the job needs it.","Organization controls flow into role-family templates and approved requisition adjustments. Warehouse example below. Confirm shift, site, start date and offered pay acceptance separately; require licences only where relevant.")
s=s.replace("Unknown = evidence absent; 1 = relevant task stated; 2 = task plus specific context or result. Keep evidence coverage separate from suitability. Unknown required evidence routes to review. Do not infer soft skills from writing style. Exclude non-applicable criteria in the approved role template before applications are evaluated.","Unknown = absent evidence; 1 = relevant task stated; 2 = task with context or a result. Track evidence coverage separately. Ask for missing required facts through WhatsApp, then re-evaluate. Remove non-applicable criteria in the role template.")
s=s.replace("Illustrative bands: 0-49 poor, 50-69 fair, 70-85 good, 86-100 excellent. Good/excellent plus complete requirements can enter the invitation queue. Lower bands and unknowns enter review. Do not rank within bands or issue final rejection from a score. Calibrate thresholds with independent assessment before activation.","Illustrative bands: 0-49 poor, 50-69 fair, 70-85 good, 86-100 excellent. Complete good/excellent matches enter outreach. Clarify factual gaps; escalate persistent low evidence or contested outcomes. No ranking within bands or score-only rejection. Calibrate before activation.")
start=s.index("y=heading('Scheduling and candidate communication',y)")
end=s.index("check(y,'D2 page 1')",start)
s=s[:start]+'''y=heading('Conversation and scheduling controls',y)
y=body('Use MCP to find panel availability and offer three slots. Accept a choice or find alternatives. Hold, recheck and book once; refresh stale choices. Bound clarification attempts, persist replies and escalate unresolved cases by 36 hours. No response or calendar capacity must not become rejection.',y)
y=para('<b>Scope update.</b> Include narrow, structured clarification in WhatsApp. Broader assessments and background verification remain future extensions; explore earlier checks with consent and local approval.',M,y,size=8.8,leading=12)
'''+s[end:]
s=s.replace("['Review load and cost','Scenario: 15% need review; 4 min each','60,000 reviews/year = 4,000 staff hours. Staff to peak demand; escalate unresolved cases at 36h. This is not measured performance.']", "['Residual human workload','Scenario: 15% remain unresolved after chat; 4 min each','60,000 escalations/year = 4,000 staff hours. Measure chat resolution and handoff rates; escalate by 36h. Assumption, not measured performance.']")
s=s.replace("PM, talent operations and local counsel agree rules, country gates, baseline metrics and exception owners.","PM, talent operations and local counsel agree rules, country gates, metrics and escalation owners.")
s=s.replace("engineering builds templates, evidence storage, queue, messaging and calendar tools.","engineering builds templates, evidence storage, chat clarification and calendar tools.")
s=s.replace("Require complete audit records, staffed review, country sign-off and no unexplained quality regression.","Require complete audit records, human escalation coverage, country sign-off and no unexplained quality regression.")
s=s.replace("Scoring uses keyword rules, not an LLM; production evidence anchors, enterprise approvals and automated review resolution are not implemented.","Scoring uses keyword rules, not an LLM. Structured clarification, production evidence anchors and enterprise approvals remain to be implemented.")
p.write_text(s)
