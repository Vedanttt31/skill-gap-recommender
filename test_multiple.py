import streamlit_app as app

rd1 = app.get_roadmap_content("agile", "Maharashtra", 2.0, 0.0, "")
rd2 = app.get_roadmap_content("python", "Maharashtra", 2.0, 0.0, "")
pdf_output = app.generate_pdf_report("Maharashtra", 2.0, [], 0.0, [rd1, rd2])
with open("test_mult.pdf", "wb") as f:
    f.write(bytes(pdf_output) if isinstance(pdf_output, bytearray) else pdf_output.encode('latin-1'))
