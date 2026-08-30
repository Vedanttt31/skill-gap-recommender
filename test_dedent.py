with open('streamlit_app.py') as f:
    lines = f.readlines()
# let's just print the exact characters of lines 280 to 290
for i in range(276, 285):
    print(repr(lines[i]))
