import re

with open("streamlit_app.py", "r") as f:
    content = f.read()

# 1. Update pages
content = content.replace(
    'pages = ["🏠 Home", "🎯 Get My Recommendation", "📊 Dashboard", "🔍 Compare Skills"]',
    'pages = ["🏠 Home", "🎯 Get My Recommendation", "🗺️ Skill Roadmaps", "📊 Dashboard", "🔍 Compare Skills"]'
)
content = content.replace(
    "icons=['house', 'bullseye', 'bar-chart', 'search']",
    "icons=['house', 'bullseye', 'map', 'bar-chart', 'search']"
)

# 2. Fix generate_pdf_report signature call inside the Recommendation tab
old_pdf_call = "pdf_output = generate_pdf_report(s_user_state, s_user_exp, s_current_skills, live_prob, top3, combo_text, top_other_state_text)"
new_pdf_call = """
            roadmaps_data = []
            for i, row in top3.iterrows():
                rd = get_roadmap_content(row['Recommended Skill'], s_user_state, s_user_exp, live_prob, effective_skills_str)
                roadmaps_data.append(rd)
            pdf_output = generate_pdf_report(s_user_state, s_user_exp, s_current_skills, live_prob, roadmaps_data)
"""
content = content.replace(old_pdf_call, new_pdf_call)

# 3. Insert the Skill Roadmaps tab logic at the end of the file
roadmap_tab_logic = """
elif selected_page == "🗺️ Skill Roadmaps":
    st.markdown("<h1 style='text-align: center; color: #00D2FF;'>🗺️ Skill Roadmaps</h1>", unsafe_allow_html=True)
    st.write("Explore detailed learning paths and career impact for any skill in our database.")
    
    # We need a state and exp to calculate uplift context. Let's provide defaults or use session state.
    rs_state = st.selectbox("Your State Context:", sorted(state_df['state'].dropna().unique().tolist()), index=0)
    rs_exp = st.slider("Your Experience (Years) Context:", 0.0, 15.0, 2.0, 0.5)
    
    selected_skill = st.selectbox("Select a Skill to view its Roadmap:", all_skills)
    
    if selected_skill:
        # We assume base skills is empty for a generic uplift calculation, or we can just pass an empty string
        rd = get_roadmap_content(selected_skill, rs_state, rs_exp, 0.0, "") # base prob 0
        render_onsite_roadmap(rd)
        
        st.write("---")
        pdf_output = generate_pdf_report(rs_state, rs_exp, [], 0.0, [rd])
        pdf_bytes = bytes(pdf_output) if isinstance(pdf_output, bytearray) else pdf_output
        st.download_button(
            label=f"Download {rd['skill']} Roadmap (PDF)",
            data=pdf_bytes,
            file_name=f"{rd['skill'].replace(' ', '_')}_Roadmap.pdf",
            mime="application/pdf",
            use_container_width=True
        )
"""
content += roadmap_tab_logic

with open("streamlit_app.py", "w") as f:
    f.write(content)
