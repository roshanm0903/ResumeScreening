from pathlib import Path
s=Path('tmp/pdfs/build_submission.py').read_text()
s=s[:s.index('# D1\n')]+s[s.index('# D2\n'):]
s=s.replace('3 November 2026','4 November 2026')
s=s.replace("y+=205","y+=192")
s=s.replace("y=heading('Dynamic role templates with explicit evidence anchors',y)","""y=heading('Resume extraction, redaction and injection controls',y)
y=para('<b>Text-first cost choice.</b> Extract text locally; OCR scanned pages. Send only normalized, redacted text and the approved rubric to the LLM, not the PDF or page images. Use rendered-page OCR to cross-check the PDF text layer; measure OCR cost, token cost and extraction accuracy in the pilot.',M,y,size=8.4,leading=11.1)+5
y=para('<b>Before scoring.</b> Remove names, email and phone from all model-bound text, including clarifications; keep identity/contact separately with controlled access. Retain page/span references for evidence. Redaction limits identity exposure; it does not remove every bias proxy.',M,y,size=8.4,leading=11.1)+5
y=para('<b>Hidden-content gate.</b> Compare extracted text with rendered-page OCR; inspect low-contrast/white, transparent, tiny, off-page and hidden-layer text. Exclude metadata, annotations and embedded files from scoring. Flag material discrepancies, Unicode obfuscation, instruction-like text and keyword stuffing. Preserve legitimate multilingual content. Isolate suspicious files for re-upload/clarification or unresolved-case review; do not reject solely on an anomaly.',M,y,size=8.4,leading=11.1)+5
y=para('<b>Contain injection.</b> Treat every resume and reply as untrusted evidence. The scorer has no tools or policy-write access. Validate output schema, ranges and cited evidence; compute totals and apply thresholds outside the model. Filters and OCR are imperfect; test attacks and benign controls before release.',M,y,size=8.4,leading=11.1)+9
y=heading('Role templates and decision rules',y)""")
s=s.replace("],y,size=8.4,padding=6)","],y,size=8.0,padding=3)")
s=s.replace("y=body(text,y)","y=body(text,y)")
s=s.replace("def body(text,y,after=6):return para(text,M,y)+after","def body(text,y,after=5):return para(text,M,y,size=8.6,leading=11.4)+after")
s=s.replace("y=para('<b>Scope.</b> Include structured WhatsApp clarification. Assessments and background verification remain future extensions; explore earlier checks with consent and local approval.',M,y,size=8.8,leading=12)","")
s=s.replace('Test prompt injection, extraction failure, duplicate applications, competing bookings, time zones, provider outages and role closure notifications.','Test white-on-white, transparent/off-page text, OCR-layer mismatch, Unicode obfuscation, visible instructions, keyword stuffing, PII leaks and benign multilingual/layout controls; also test duplicate applications, calendar conflicts, time zones and outages.')
s=s.replace('production evidence anchors and enterprise approvals remain to be implemented.','production evidence anchors, OCR/hidden-text gates and enterprise approvals remain to be implemented.')
# Keep prototype and release material within the two-page assignment limit.
s=s.replace('size=8.6,leading=11.8','size=8.2,leading=11.0')
s=s.replace("check(y,'D2 page 2');c.save()","y=para('Security reference: <link href=\"https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html\" color=\"#256450\">OWASP prompt injection prevention</link>. Controls above are proposed; no guarantee of complete detection.',M,y+6,size=7.2,leading=9.3)\ncheck(y,'D2 page 2');c.save()")
Path('tmp/pdfs/build_d2_controls.py').write_text(s)
