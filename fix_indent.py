with open("streamlit_app.py", "r") as f:
    content = f.read()

# I will just replace the st.markdown call with a dedented version
old_code = "st.markdown(bento_html, unsafe_allow_html=True)"
new_code = "import textwrap\n    st.markdown(textwrap.dedent(bento_html), unsafe_allow_html=True)"

if old_code in content:
    content = content.replace(old_code, new_code)
    with open("streamlit_app.py", "w") as f:
        f.write(content)
    print("Fixed markdown indentation.")
else:
    print("Could not find the code to replace.")
