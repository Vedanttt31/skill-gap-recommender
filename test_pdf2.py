from fpdf import FPDF

def test():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(14, 17, 23)
    pdf.rect(0, 0, 210, 297, 'F')
    pdf.set_font("Helvetica", "B", 24)
    pdf.set_text_color(0, 210, 255)
    pdf.cell(0, 15, "Personal Skill & Job Match Report", ln=True, align="C")
    
    out = pdf.output(dest='S')
    with open("test_out.pdf", "wb") as f:
        f.write(bytes(out) if isinstance(out, bytearray) else out.encode('latin-1'))
    print("Success")

test()
