from pathlib import Path
p=Path('tmp/pdfs/build_submission.py');s=p.read_text()
s=s.replace("# Three stages and three visible outcomes; no rejection branch from a score.","# Mandatory checks and a calibrated score can both trigger rejection.")
s=s.replace("('Apply approved policy','Requirements plus role rubric')", "('Apply approved policy','Mandatory checks then LLM rubric')")
a=s.index(" for i,(t,s) in enumerate([('Missing or conflicting details'")
b=s.index(' return y+134',a)
s=s[:a]+''' widths=116;outgap=(CW-4*widths)/3
 outxs=[M+i*(widths+outgap) for i in range(4)]
 c.setStrokeColor(GREEN);c.line(outxs[0]+widths/2,H-y-63,outxs[-1]+widths/2,H-y-63)
 for i,(t,s) in enumerate([('Mandatory check failed','Reject with rule reason'),('Score below threshold','Reject with scoring evidence'),('Input missing or unreadable','Clarify through WhatsApp'),('Checks and score pass','Batch then offer interview slots')]):
  arrow(outxs[i]+widths/2,y+63,outxs[i]+widths/2,y+75)
  node(outxs[i],y+76,widths,48,t,s,PALE if i==3 else GOLD)
'''+s[b:]
s=s.replace('Automate routine progression and resolve missing details or scheduling exceptions through WhatsApp first. Human review is reserved for unresolved or contested cases and decisions that require it. Do not launch score-only rejection; a low score is not proof of inability.', 'Automatically reject confirmed mandatory-check failures and candidates below the role-specific LLM score threshold. Progress the rest to scheduling. Resolve missing inputs and scheduling exceptions through WhatsApp; reserve human review for unresolved or contested cases and required interventions.')
s=s.replace("y=heading('Separate suitability from uncertainty and capacity',y)", "y=heading('Combine mandatory checks and LLM scoring',y)")
s=s.replace('Monitor scores', 'Monitor scores')
s=s.replace('monitor scores, outreach deadlines, conversation outcomes and bookings.', 'monitor scores, rejection rates, outreach deadlines and bookings.')
s=s.replace('Receive a WhatsApp update within 48 hours. Confirm missing details in the same conversation; select one of three slots or request alternatives.', 'Receive a decision or clarification within 48 hours. Confirm missing inputs in WhatsApp; if selected, choose one of three slots or request alternatives.')
s=s.replace('Use explicit requirements plus role-specific scoring. Avoid relative bottom-of-pool rejection; do not rank within bands.', 'Use explicit requirements plus role-specific LLM scoring. Reject below the configured threshold; do not rank within score bands.')
s=s.replace('3 no score-only rejection, retain decision evidence and a review path, and escalate unresolved cases at 36 hours.', '3 use approved thresholds, retain decision evidence and a review path, and escalate unresolved cases at 36 hours.')
anchor="y=heading('Launch in stages and retain a fallback',y)"
s=s.replace(anchor,"""y=heading('Make LLM scoring robust before launch',y)
y=body('Use role-specific anchored ratings and source-linked evidence; compute the weighted total deterministically. Test scoring stability, transferable experience, resume formatting, keyword stuffing and prompt injection. Back-test known good hires, then independently label samples across all bands to measure false positives and false negatives. Version the rubric, threshold, model and prompt; revalidate changes before activation.',y,10)
"""+anchor,1)
s=s.replace('The model extracts role evidence; approved policy selects actions.', 'The LLM rates role evidence; policy rejects failed mandatory checks or scores below threshold and schedules passing candidates.')
s=s.replace('Unknown = absent evidence; 1 = relevant task stated; 2 = task with context or a result. Track evidence coverage separately. Ask for missing required facts through WhatsApp, then re-evaluate. Remove non-applicable criteria in the role template.', '0 = no supporting evidence; 1 = relevant task stated; 2 = task with context or a result. Save source evidence and ratings; compute weighted totals deterministically. Clarify missing form inputs or unreadable text, then score. Exclude non-applicable criteria in the template.')
s=s.replace('Illustrative bands: 0-49 poor, 50-69 fair, 70-85 good, 86-100 excellent. Complete good/excellent matches enter outreach. Clarify factual gaps; escalate persistent low evidence or contested outcomes. No ranking within bands or score-only rejection. Calibrate before activation.', 'Mandatory check failed: reject. Otherwise reject scores below the configured threshold; schedule passing candidates. Example threshold: 70, with bands 0-49 poor, 50-69 fair, 70-85 good, 86-100 excellent. No ranking within bands. Calibrate the rubric and threshold before activation.')
s=s.replace('Structured clarification, production evidence anchors and enterprise approvals remain to be implemented.', 'The current demo does not implement automatic rejection or LLM scoring. Align it to this policy next; clarification and enterprise approvals also remain.')
# Ensure stale policy text cannot survive into either submitted document.
assert 'no score-only rejection' not in s.lower()
assert 'do not launch score-only rejection' not in s.lower()
p.write_text(s)
Path('tmp/pdfs/build_decision_only.py').write_text(s[:s.index('# D2\n')])
