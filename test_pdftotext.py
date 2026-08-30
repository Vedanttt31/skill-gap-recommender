import sys
import streamlit_app as app

rd = app.get_roadmap_content("agile", "Maharashtra", 2.0, 0.0, "")
pdf_output = app.generate_pdf_report("Maharashtra", 2.0, [], 0.0, [rd])
with open("test_z.pdf", "wb") as f:
    f.write(bytes(pdf_output) if isinstance(pdf_output, bytearray) else pdf_output.encode('latin-1'))
