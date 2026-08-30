with open("streamlit_app.py", "r") as f:
    content = f.read()

# Replace ln=True with new_x="LMARGIN", new_y="NEXT"
content = content.replace('ln=True', 'new_x="LMARGIN", new_y="NEXT"')
# Also fix the return output
content = content.replace("return pdf.output(dest='S')", "return pdf.output()")

with open("streamlit_app.py", "w") as f:
    f.write(content)
