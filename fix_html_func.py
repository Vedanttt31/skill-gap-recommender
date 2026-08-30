with open("streamlit_app.py", "r") as f:
    content = f.read()

# Replace render_html function
old_render_html = """def render_html(html_content: str):
    st.markdown(textwrap.dedent(html_content), unsafe_allow_html=True)"""

new_render_html = """def render_html(html_content: str):
    # Strip all leading spaces from every line to prevent Markdown code blocks
    cleaned = "\\n".join([line.lstrip() for line in html_content.split("\\n")])
    st.markdown(cleaned, unsafe_allow_html=True)"""

content = content.replace(old_render_html, new_render_html)

with open("streamlit_app.py", "w") as f:
    f.write(content)
