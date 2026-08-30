import re

with open("streamlit_app.py", "r") as f:
    content = f.read()

# The section to replace:
old_section = """            rc1, rc2, rc3 = st.columns(3)
            cols = [rc1, rc2, rc3]
            
            def on_skill_checked(s):
                if st.session_state[f"chk_{s}"]:
                    if s not in st.session_state['learned_skills']:
                        st.session_state['learned_skills'].append(s)
                else:
                    if s in st.session_state['learned_skills']:
                        st.session_state['learned_skills'].remove(s)
            
            for i, (idx, row) in enumerate(top3.iterrows()):
                with cols[i].container(border=True):
                    skill_name = row['Recommended Skill']
                    st.write(f"### ⭐ {skill_name}")
                    
                    boost_pct = row['Uplift'] * 100
                    st.write(f"Boosts your chances by **{boost_pct:.1f}%**.")
                    
                    est_time = get_learning_time(skill_name)
                    st.caption(f"⏱️ **Estimated time to learn:** {est_time}")
                    
                    st.checkbox(f"I'm learning this!", key=f"chk_{skill_name}", on_change=on_skill_checked, args=(skill_name,))"""

new_section = """            def on_skill_checked(s):
                if st.session_state[f"chk_{s}"]:
                    if s not in st.session_state['learned_skills']:
                        st.session_state['learned_skills'].append(s)
                else:
                    if s in st.session_state['learned_skills']:
                        st.session_state['learned_skills'].remove(s)
            
            for idx, row in top3.iterrows():
                skill_name = row['Recommended Skill']
                rd = get_roadmap_content(skill_name, s_user_state, s_user_exp, live_prob, effective_skills_str)
                
                # Render the shared HTML roadmap component
                render_onsite_roadmap(rd)
                
                # Render the interactive checkbox directly beneath it
                st.checkbox(f"I'm learning {skill_name}!", key=f"chk_{skill_name}", on_change=on_skill_checked, args=(skill_name,))
                st.write("") # Spacer"""

content = content.replace(old_section, new_section)

with open("streamlit_app.py", "w") as f:
    f.write(content)
