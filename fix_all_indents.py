import re

with open("streamlit_app.py", "r") as f:
    content = f.read()

# 1. Fix bento_html
bento_match = re.search(r'bento_html = """(.*?)"""', content, re.DOTALL)
if bento_match:
    raw_bento = bento_match.group(1)
    # manually dedent
    lines = raw_bento.split('\n')
    new_lines = []
    for line in lines:
        if line.startswith('    '):
            new_lines.append(line[4:])
        else:
            new_lines.append(line)
    new_bento = '\n'.join(new_lines)
    content = content.replace(bento_match.group(0), f'bento_html = """{new_bento}"""')

# 2. Fix the st.markdown(textwrap.dedent(bento_html)) back to normal
content = content.replace("import textwrap\n    st.markdown(textwrap.dedent(bento_html), unsafe_allow_html=True)", "st.markdown(bento_html, unsafe_allow_html=True)")

# 3. Fix render_background iframe which had 4 spaces on the first line
bg_match = re.search(r'    <iframe id=\'vanta-bg-iframe\'.*?<html>', content, re.DOTALL)
if bg_match:
    content = content.replace("    <iframe id='vanta-bg-iframe'", "<iframe id='vanta-bg-iframe'")

# 4. Fix style block in render_background which has 4 spaces
style_match = re.search(r'    <style>\n    .stApp > header { background-color: transparent !important; }\n    .stApp { background-color: transparent !important; }\n    </style>', content, re.DOTALL)
if style_match:
    content = content.replace(style_match.group(0), "<style>\n.stApp > header { background-color: transparent !important; }\n.stApp { background-color: transparent !important; }\n</style>")

with open("streamlit_app.py", "w") as f:
    f.write(content)
print("Fixed all indents.")
