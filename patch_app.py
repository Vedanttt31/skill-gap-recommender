import re

with open("streamlit_app.py", "r") as f:
    content = f.read()

# 1. Remove Sidebar
sidebar_str = """# --- Sidebar ---
with st.sidebar:
    st.markdown(f"## ⚡ Skill & Job Matcher")
    st.markdown("Find the exact skills you need to get hired.")
    st.divider()
    
    with st.expander("ℹ️ About this tool"):
        st.write(\"\"\"
        We analyzed **22,000 real job postings** and **government employment data** across India. 
        
        Using AI, this tool understands the meaning of your skills and compares them to what companies are actively looking for right now. We then recommend the missing skills that will boost your chances of getting a job.
        \"\"\")

# --- Main App ---
st.markdown("<h1 style='text-align: center;'>⚡ What should you learn next?</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.1em; color: #A0AEC0;'>We look at real job postings across India to tell you which skill will improve your chances of getting hired.</p>", unsafe_allow_html=True)
st.write("")"""

new_header_str = """# --- Main App ---
st.markdown("<h1 style='text-align: center;'>⚡ Skill & Job Matcher</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.1em; color: #A0AEC0;'>Find the exact skills you need to get hired. We analyze real job postings across India to tell you what to learn next.</p>", unsafe_allow_html=True)

with st.expander("ℹ️ About this tool"):
    st.write(\"\"\"
    We analyzed **22,000 real job postings** and **government employment data** across India. 
    
    Using AI, this tool understands the meaning of your skills and compares them to what companies are actively looking for right now. We then recommend the missing skills that will boost your chances of getting a job.
    \"\"\")
st.write("")"""

content = content.replace(sidebar_str, new_header_str)

# 2, 3, 4, 5. Fix Job Openings, Market Condition truncate, Bubble Chart Y-axis, Rebalance
old_cluster_str = """    c3, c4 = st.columns((2, 3))
    
    with c3:
        st.write("#### 🏢 Job Market Health by State")
        st.caption("Comparing Unemployment against Available Jobs.")
        fig_cluster = px.scatter(
            state_df, x='UR', y='job_count', color='Archetype', hover_name='state',
            size='LFPR', log_y=True, color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_cluster.update_layout(xaxis_title="Unemployment Rate", yaxis_title="Job Postings", margin={"r":0,"t":30,"l":0,"b":0}, paper_bgcolor="#0E1117", plot_bgcolor="#0E1117", font_color="#FFFFFF", legend=dict(orientation="h", y=-0.3))
        st.plotly_chart(fig_cluster, use_container_width=True)
        
    with c4:
        st.write("#### ⚠️ Toughest Job Markets")
        st.caption("States ranked by severity (high unemployment + low job postings).")
        state_df['Severity_Score'] = state_df['UR'] + (1 / (state_df['job_count'] + 1)) * 100
        ranking_df = state_df.sort_values('Severity_Score', ascending=False)[['state', 'UR', 'job_count', 'Archetype']].head(6)
        ranking_df.rename(columns={'state': 'State', 'UR': 'Unemployment %', 'job_count': 'Job Openings', 'Archetype': 'Market Condition'}, inplace=True)
        st.dataframe(ranking_df, use_container_width=True, hide_index=True)"""

new_cluster_str = """    c3, c4 = st.columns((1, 1))
    
    with c3:
        st.write("#### 🏢 Job Market Health by State")
        st.caption("Comparing Unemployment against Available Jobs.")
        
        # Add 1 to job_count so 0s don't disappear on log scale
        state_df['job_count_display'] = state_df['job_count'] + 1
        
        fig_cluster = px.scatter(
            state_df, x='UR', y='job_count_display', color='Archetype', hover_name='state',
            size='LFPR', log_y=True, color_discrete_sequence=px.colors.qualitative.Pastel,
            hover_data={'job_count_display': False, 'job_count': True}
        )
        fig_cluster.update_layout(
            xaxis_title="Unemployment Rate (%)", 
            margin={"r":0,"t":30,"l":0,"b":0}, 
            paper_bgcolor="#0E1117", 
            plot_bgcolor="#0E1117", 
            font_color="#FFFFFF", 
            legend=dict(orientation="h", y=-0.3, title="")
        )
        # Clean up the y-axis labels
        fig_cluster.update_yaxes(
            title="Job Postings",
            tickvals=[1, 10, 100, 1000, 10000],
            ticktext=["0", "10", "100", "1K", "10K"]
        )
        st.plotly_chart(fig_cluster, use_container_width=True)
        
    with c4:
        st.write("#### ⚠️ Toughest Job Markets")
        st.caption("States ranked by severity (high unemployment + low job postings).")
        state_df['Severity_Score'] = state_df['UR'] + (1 / (state_df['job_count'] + 1)) * 100
        ranking_df = state_df.sort_values('Severity_Score', ascending=False)[['state', 'UR', 'job_count', 'Archetype']].head(8)
        
        ranking_df['job_count'] = ranking_df['job_count'].astype(int)
        ranking_df['UR'] = ranking_df['UR'].round(1)
        ranking_df.rename(columns={'state': 'State', 'UR': 'Unemployment %', 'job_count': 'Job Openings', 'Archetype': 'Market Condition'}, inplace=True)
        
        st.dataframe(
            ranking_df, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Market Condition": st.column_config.TextColumn(width="large"),
                "State": st.column_config.TextColumn(width="medium")
            }
        )"""

content = content.replace(old_cluster_str, new_cluster_str)

with open("streamlit_app.py", "w") as f:
    f.write(content)
print("Patched.")
