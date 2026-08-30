import re
import textwrap

with open("streamlit_app.py", "r") as f:
    content = f.read()

# 1. Add import textwrap and define render_html near the top imports
imports = "import io\nimport textwrap\n\ndef render_html(html_content: str):\n    st.markdown(textwrap.dedent(html_content), unsafe_allow_html=True)\n"
content = content.replace("import io\n", imports)

# 2. Replace render_onsite_roadmap's st.markdown call with render_html
# Also, remove the unsafe_allow_html=True from the call since render_html handles it
def replace_roadmap_html(match):
    html_block = match.group(1)
    return f"    render_html(f\"\"\"{html_block}\"\"\")"

content = re.sub(r'st\.markdown\(f\"\"\"(.*?)\"\"\",\s*unsafe_allow_html=True\)', replace_roadmap_html, content, flags=re.DOTALL)

# 3. Fix the bento_html call
content = content.replace("st.markdown(bento_html, unsafe_allow_html=True)", "render_html(bento_html)")

# 4. Fix the hero container call
content = content.replace(
    "st.markdown('<div class=\"hero-container\"><div class=\"hero-title\">Find Your Next Skill.<br/>Get Hired Faster.</div><div class=\"hero-subtitle\">Stop guessing what employers want. We analyze real job postings across India to tell you exactly what you need to learn.</div></div>', unsafe_allow_html=True)",
    "render_html('<div class=\"hero-container\"><div class=\"hero-title\">Find Your Next Skill.<br/>Get Hired Faster.</div><div class=\"hero-subtitle\">Stop guessing what employers want. We analyze real job postings across India to tell you exactly what you need to learn.</div></div>')"
)

# 5. Fix the st.markdown call for the Skill Roadmaps title
content = content.replace(
    "st.markdown(\"<h1 style='text-align: center; color: #00D2FF;'>🗺️ Skill Roadmaps</h1>\", unsafe_allow_html=True)",
    "render_html(\"<h1 style='text-align: center; color: #00D2FF;'>🗺️ Skill Roadmaps</h1>\")"
)

# 6. Fix any other st.markdown calls that pass raw strings with unsafe_allow_html=True
# We'll use a regex for this generic replacement if any exist
content = re.sub(r'st\.markdown\(\"\"\"(.*?)\"\"\",\s*unsafe_allow_html=True\)', lambda m: f"render_html(\"\"\"{m.group(1)}\"\"\")", content, flags=re.DOTALL)

with open("streamlit_app.py", "w") as f:
    f.write(content)
