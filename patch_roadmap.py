with open("streamlit_app.py", "r") as f:
    content = f.read()

import re

# We need to find the `generate_pdf_report` and `get_practical_steps` and replace them.
# The `generate_pdf_report` definition ends before `def get_career_path(skills_list):`

start_idx = content.find("def get_learning_time(skill):")
end_idx = content.find("def get_career_path(skills_list):")

new_roadmap_logic = """
def get_roadmap_content(skill, user_state, user_exp, live_prob, effective_skills_str):
    skill_lower = skill.lower()
    
    # Generic template switching based on skill category
    if any(k in skill_lower for k in ['python', 'java', 'c++', 'javascript', 'react', 'node', 'angular', 'php', 'ruby', 'go', 'framework', 'sql']):
        stage1 = ["Understand the syntax and core concepts.", "Set up your development environment.", "Write your first 'Hello World' programs."]
        stage2 = ["Build 2-3 small interactive projects (calculators, to-do lists, simple APIs).", "Learn debugging and basic version control (Git)."]
        stage3 = ["Build a complex portfolio project solving a real problem.", "Deploy it live.", "Prepare for technical coding interviews."]
        est_time = "2-3 months"
        desc = f"A core technical skill that empowers you to build robust software systems and applications."
    elif any(k in skill_lower for k in ['machine learning', 'deep learning', 'data science', 'ai', 'artificial intelligence', 'data', 'analytics', 'bi', 'tableau']):
        stage1 = ["Master the underlying math and basic theory.", "Learn to manipulate data (e.g. using Pandas or SQL).", "Understand basic exploratory data analysis."]
        stage2 = ["Train simple models on clean datasets (like Kaggle Titanic).", "Learn to evaluate model performance metrics."]
        stage3 = ["Tackle a messy, real-world dataset end-to-end.", "Deploy your model as a simple web app or API.", "Prepare a presentation explaining your findings."]
        est_time = "3-4 months"
        desc = f"A high-demand analytical skill for extracting value and predictions from data."
    elif any(k in skill_lower for k in ['aws', 'azure', 'cloud', 'devops', 'docker', 'kubernetes', 'ci/cd', 'git', 'linux']):
        stage1 = ["Understand the fundamental concepts of cloud computing or containerization.", "Create a free tier account and explore the console."]
        stage2 = ["Deploy a basic web application manually.", "Learn to use the CLI and basic scripting to automate tasks."]
        stage3 = ["Implement a simple CI/CD pipeline.", "Study for a foundational certification (like AWS Cloud Practitioner).", "Implement basic security best practices."]
        est_time = "2-3 months"
        desc = f"A critical infrastructure skill for deploying, scaling, and maintaining modern applications."
    elif any(k in skill_lower for k in ['sales', 'marketing', 'seo', 'business development', 'b2b', 'b2c', 'lead generation']):
        stage1 = ["Learn the core principles, terminology, and standard metrics (KPIs) of the field.", "Understand the customer journey and funnel."]
        stage2 = ["Practice creating mock campaigns, pitches, or outreach strategies.", "Familiarize yourself with industry-standard CRM or analytics tools."]
        stage3 = ["Execute a small real-world campaign or shadow an experienced professional.", "Build a portfolio of case studies or successful metrics.", "Practice handling objections."]
        est_time = "1-2 months"
        desc = f"A vital business skill focused on driving growth, revenue, and customer acquisition."
    elif any(k in skill_lower for k in ['communication', 'leadership', 'management', 'agile', 'scrum', 'project management']):
        stage1 = ["Read industry-standard books or frameworks (e.g. Scrum Guide).", "Understand the theory behind effective team dynamics and planning."]
        stage2 = ["Apply these frameworks to small personal projects or current workflows.", "Practice active listening and clear written communication."]
        stage3 = ["Take on a small leadership or coordination role in a project.", "Consider a foundational certification (e.g. CSM or CAPM).", "Quantify past experiences on your resume."]
        est_time = "1-2 months"
        desc = f"A foundational soft skill essential for team collaboration, execution, and career progression."
    else:
        stage1 = ["Start with a highly-rated beginner online course to understand the fundamentals.", "Familiarize yourself with the core terminology."]
        stage2 = ["Practice with small, real-world exercises or case studies.", "Seek out communities or forums to ask questions."]
        stage3 = ["Apply the skill to a capstone project.", "Add the skill to your resume and LinkedIn.", "Prepare to discuss your hands-on experience in interviews."]
        est_time = "1-2 months"
        desc = f"A valuable professional skill to enhance your domain expertise."
        
    new_str = effective_skills_str + " " + skill_lower
    new_prob = predict_match_likelihood(new_str, user_exp, state_df[state_df['state'] == user_state]['UR'].values[0])
    uplift = max(0, new_prob - live_prob)
    
    top_states = skill_demand[skill_demand['skill'] == skill_lower].sort_values('demand_score', ascending=False).head(3)['state'].tolist()
    if not top_states: top_states = ["Nationwide"]
    
    roles = get_job_examples(new_str, top_n=3)
    
    return {
        "skill": skill.title(),
        "desc": desc,
        "est_time": est_time,
        "stage1": stage1,
        "stage2": stage2,
        "stage3": stage3,
        "top_states": top_states,
        "roles": roles,
        "uplift": uplift,
        "new_prob": new_prob
    }

def render_onsite_roadmap(roadmap_data):
    st.markdown(f\"\"\"
    <div style="background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 25px; margin-bottom: 20px;">
        <h2 style="color: #00D2FF; margin-top:0;">🗺️ Roadmap: {roadmap_data['skill']}</h2>
        <p style="color: #A0AEC0; font-size: 1.1rem; margin-bottom: 20px;">{roadmap_data['desc']}</p>
        
        <div style="display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 25px;">
            <div style="background: rgba(0,0,0,0.3); padding: 15px; border-radius: 8px; flex: 1; min-width: 200px;">
                <div style="color: #A0AEC0; font-size: 0.9rem;">⏱️ Estimated Time</div>
                <div style="font-size: 1.2rem; font-weight: bold;">{roadmap_data['est_time']}</div>
            </div>
            <div style="background: rgba(0,0,0,0.3); padding: 15px; border-radius: 8px; flex: 1; min-width: 200px;">
                <div style="color: #A0AEC0; font-size: 0.9rem;">📈 Employability Uplift</div>
                <div style="font-size: 1.2rem; font-weight: bold; color: #00D2FF;">+{roadmap_data['uplift']*100:.1f}%</div>
            </div>
            <div style="background: rgba(0,0,0,0.3); padding: 15px; border-radius: 8px; flex: 1; min-width: 200px;">
                <div style="color: #A0AEC0; font-size: 0.9rem;">📍 Top Demand States</div>
                <div style="font-size: 1.1rem; font-weight: bold;">{', '.join(roadmap_data['top_states'])}</div>
            </div>
        </div>
        
        <h4 style="margin-bottom: 10px;">Step-by-Step Learning Path</h4>
        
        <div style="border-left: 3px solid #00D2FF; padding-left: 15px; margin-bottom: 15px;">
            <b style="color: #fff;">Stage 1: Fundamentals</b>
            <ul style="color: #A0AEC0; margin-top: 5px;">
                {''.join([f"<li>{s}</li>" for s in roadmap_data['stage1']])}
            </ul>
        </div>
        <div style="border-left: 3px solid #00D2FF; padding-left: 15px; margin-bottom: 15px;">
            <b style="color: #fff;">Stage 2: Practical Application</b>
            <ul style="color: #A0AEC0; margin-top: 5px;">
                {''.join([f"<li>{s}</li>" for s in roadmap_data['stage2']])}
            </ul>
        </div>
        <div style="border-left: 3px solid #00D2FF; padding-left: 15px; margin-bottom: 25px;">
            <b style="color: #fff;">Stage 3: Get Job-Ready</b>
            <ul style="color: #A0AEC0; margin-top: 5px;">
                {''.join([f"<li>{s}</li>" for s in roadmap_data['stage3']])}
            </ul>
        </div>
        
        <h4 style="margin-bottom: 10px;">💼 Example Roles Unlocked</h4>
        <ul style="color: #A0AEC0; margin-top: 5px;">
            {''.join([f"<li>{r.title()}</li>" for r in roadmap_data['roles']])}
        </ul>
    </div>
    \"\"\", unsafe_allow_html=True)

def generate_pdf_report(user_state, user_exp, current_skills, base_prob, roadmaps_data):
    pdf = FPDF()
    
    # Colors
    bg_r, bg_g, bg_b = 14, 17, 23
    text_r, text_g, text_b = 230, 230, 230
    accent_r, accent_g, accent_b = 0, 210, 255
    sub_r, sub_g, sub_b = 160, 174, 192
    
    def add_dark_page():
        pdf.add_page()
        pdf.set_fill_color(bg_r, bg_g, bg_b)
        pdf.rect(0, 0, 210, 297, 'F')
        
    add_dark_page()
    
    # Title
    pdf.set_text_color(accent_r, accent_g, accent_b)
    pdf.set_font("Helvetica", "B", 24)
    pdf.cell(0, 15, "Personal Skill & Job Match Report", ln=True, align="C")
    pdf.ln(5)
    
    # Profile Box
    pdf.set_fill_color(30, 41, 59)
    pdf.set_text_color(text_r, text_g, text_b)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, " Your Profile", ln=True, fill=True)
    
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(sub_r, sub_g, sub_b)
    pdf.cell(0, 8, f" Target State: {user_state}", ln=True, fill=True)
    pdf.cell(0, 8, f" Experience: {user_exp} years", ln=True, fill=True)
    pdf.cell(0, 8, f" Current Placement Chance: {base_prob*100:.1f}%", ln=True, fill=True)
    pdf.cell(0, 8, f" Current Skills: {', '.join(current_skills)}", ln=True, fill=True)
    pdf.ln(10)
    
    for rd in roadmaps_data:
        add_dark_page()
        
        pdf.set_text_color(accent_r, accent_g, accent_b)
        pdf.set_font("Helvetica", "B", 20)
        pdf.cell(0, 10, f"Roadmap: {rd['skill']}", ln=True)
        
        pdf.set_text_color(sub_r, sub_g, sub_b)
        pdf.set_font("Helvetica", "I", 12)
        pdf.multi_cell(0, 8, rd['desc'])
        pdf.ln(5)
        
        # Stats
        pdf.set_text_color(text_r, text_g, text_b)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, f"Estimated Time: {rd['est_time']}", ln=True)
        pdf.set_text_color(accent_r, accent_g, accent_b)
        pdf.cell(0, 8, f"Employability Uplift: +{rd['uplift']*100:.1f}%", ln=True)
        pdf.set_text_color(text_r, text_g, text_b)
        pdf.cell(0, 8, f"Top Demand States: {', '.join(rd['top_states'])}", ln=True)
        pdf.ln(8)
        
        # Stages
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(text_r, text_g, text_b)
        pdf.cell(0, 10, "Step-by-Step Learning Path:", ln=True)
        
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(accent_r, accent_g, accent_b)
        pdf.cell(0, 8, "Stage 1: Fundamentals", ln=True)
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(sub_r, sub_g, sub_b)
        for s in rd['stage1']: pdf.cell(0, 6, f"- {s}", ln=True)
        pdf.ln(3)
        
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(accent_r, accent_g, accent_b)
        pdf.cell(0, 8, "Stage 2: Practical Application", ln=True)
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(sub_r, sub_g, sub_b)
        for s in rd['stage2']: pdf.cell(0, 6, f"- {s}", ln=True)
        pdf.ln(3)
        
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(accent_r, accent_g, accent_b)
        pdf.cell(0, 8, "Stage 3: Get Job-Ready", ln=True)
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(sub_r, sub_g, sub_b)
        for s in rd['stage3']: pdf.cell(0, 6, f"- {s}", ln=True)
        pdf.ln(8)
        
        # Roles
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(text_r, text_g, text_b)
        pdf.cell(0, 10, "Example Roles Unlocked:", ln=True)
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(sub_r, sub_g, sub_b)
        for r in rd['roles']: pdf.cell(0, 6, f"- {r.title()}", ln=True)
            
    return pdf.output(dest='S')
"""

content = content[:start_idx] + new_roadmap_logic + content[end_idx:]

with open("streamlit_app.py", "w") as f:
    f.write(content)
