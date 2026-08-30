import sys
import pandas as pd
# Mock some parts to run the function
import streamlit_app as app

# Test 1: Generate PDF for a single skill (Skill Roadmaps tab)
rd = app.get_roadmap_content("python", "Maharashtra", 2.0, 0.0, "")
pdf_output = app.generate_pdf_report("Maharashtra", 2.0, [], 0.0, [rd])
with open("test_roadmap_tab.pdf", "wb") as f:
    f.write(bytes(pdf_output) if isinstance(pdf_output, bytearray) else pdf_output.encode('latin-1'))
print("Test 1 successful.")

# Test 2: Generate PDF for multiple skills (Get My Recommendation tab)
rd1 = app.get_roadmap_content("java", "Maharashtra", 2.0, 0.2, "python sql")
rd2 = app.get_roadmap_content("aws", "Maharashtra", 2.0, 0.2, "python sql")
pdf_output2 = app.generate_pdf_report("Maharashtra", 2.0, ["python", "sql"], 0.2, [rd1, rd2])
with open("test_recommendation_tab.pdf", "wb") as f:
    f.write(bytes(pdf_output2) if isinstance(pdf_output2, bytearray) else pdf_output2.encode('latin-1'))
print("Test 2 successful.")
