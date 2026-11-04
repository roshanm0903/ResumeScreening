from pathlib import Path
p=Path('tmp/pdfs/build_submission.py');s=p.read_text()
a=s.index("y=heading('North star metric',y+12)")
b=s.index("check(y,'D1 page 1')",a)
s=s[:a]+s[b:]
a=s.index("y=page_start('D1','Success measures and launch controls'")
b=s.index("y=heading('Country approval and decision evidence',y)",a)
s=s[:a]+'''y=page_start('D1','Launch controls and success metrics','Measurement accountability and staged rollout',2)
metrics_start=y
y=heading('Success metrics and guardrails',y)
y=body('<b>North star:</b> Qualified candidates with a confirmed first-round interview booking each week; count once per requisition against approved job criteria.',y,5)
y=body('<b>Business:</b> 1 Time to fill a position; 2 recruiter hours per confirmed booking, including exceptions; 3 cost per qualified booking, including processing, messaging and human effort.',y,5)
y=body('<b>Performance:</b> 1 Meaningful outreach within 48 hours, excluding generic acknowledgements; 2 invitation-to-booking conversion; 3 WhatsApp exceptions resolved without human intervention.',y,5)
y=body('<b>Guardrails:</b> 1 Reduce unsuitable interview referrals; pilot ceiling of 2% qualified candidates incorrectly excluded, with independent sampling and fairness checks; 2 prevent conflicting or duplicate bookings and track system-caused changes; 3 no score-only rejection, retain decision evidence and a review path, and escalate unresolved cases at 36 hours.',y,5)
metrics_height=y-metrics_start
print('Success metrics height',round(metrics_height,1),'points;',round(metrics_height/H*100,1),'percent of page')
assert metrics_height <= .25*(H-80), 'Metrics exceed one quarter of usable page height'
y+=8
'''+s[b:]
p.write_text(s);Path('tmp/pdfs/build_decision_only.py').write_text(s[:s.index('# D2\n')])
