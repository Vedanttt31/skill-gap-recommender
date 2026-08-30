import re

with open("streamlit_app.py", "r") as f:
    content = f.read()

# Find the bento_html block
bento_match = re.search(r'bento_html = """(.*?)"""', content, re.DOTALL)
if bento_match:
    raw_bento = bento_match.group(1)
    
    # Strip all leading whitespace from every line, and remove entirely blank lines
    new_lines = []
    for line in raw_bento.split('\n'):
        stripped = line.strip()
        if stripped:  # only keep non-empty lines
            new_lines.append(stripped)
            
    # Re-join with spaces or newlines (newlines are fine as long as there are NO empty lines and NO indents)
    new_bento = '\n'.join(new_lines)
    
    content = content.replace(bento_match.group(0), f'bento_html = """{new_bento}"""')
    
    with open("streamlit_app.py", "w") as f:
        f.write(content)
    print("Fixed bento HTML by removing all indents and blank lines.")
else:
    print("Could not find bento_html.")
