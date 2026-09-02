import streamlit as st
from streamlit_option_menu import option_menu
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pickle
import torch
import torch.nn as nn
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import ast
import json
import urllib.request
from fpdf import FPDF
import io
import textwrap

def render_html(html_content: str):
    # Strip all leading spaces from every line to prevent Markdown code blocks
    cleaned = "\n".join([line.lstrip() for line in html_content.split("\n")])
    st.markdown(cleaned, unsafe_allow_html=True)

# 1. Page Config
st.set_page_config(
    page_title="Skill & Job Matcher",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

class EmployabilityMLP(nn.Module):
    def __init__(self, input_dim):
        super(EmployabilityMLP, self).__init__()
        self.fc1 = nn.Linear(input_dim, 128)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, 1)
        self.sigmoid = nn.Sigmoid()
        
    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.sigmoid(self.fc3(x))
        return x

# --- Caching Data & Models ---
@st.cache_data
def load_data():
    state_df = pd.read_csv('data/merged_state_features.csv')
    naukri_df = pd.read_csv('data/naukri_features.csv')
    skill_demand = pd.read_csv('data/skill_demand_scores.csv')
    
    naukri_df['skills_list'] = naukri_df['skills_list'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith('[') else x)
    
    # Load India GeoJSON
    url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
    try:
        with urllib.request.urlopen(url) as response:
            india_geojson = json.loads(response.read().decode())
    except:
        india_geojson = None
        
    state_mapping = {
        'Andaman & Nicobar Islands': 'Andaman & Nicobar',
        'Dadra & Nagar Haveli & Daman & Diu': 'Dadra and Nagar Haveli and Daman and Diu',
    }
    state_df['map_state'] = state_df['state'].replace(state_mapping)
        
    return state_df, naukri_df, skill_demand, india_geojson

@st.cache_resource
def load_models():
    st_model = SentenceTransformer('all-MiniLM-L6-v2')
    with open('models/sentence_embeddings_dict.pkl', 'rb') as f:
        st_dict = pickle.load(f)
        
    with open('models/best_predictive_model.pkl', 'rb') as f:
        pred_meta = pickle.load(f)
    
    if pred_meta['type'] == 'mlp':
        model = EmployabilityMLP(pred_meta['input_dim'])
        model.load_state_dict(torch.load('models/best_predictive_model.pth', map_location=torch.device('cpu')))
        model.eval()
    else:
        model = pred_meta['model']
        
    return st_model, st_dict, model, pred_meta

try:
    state_df, naukri_df, skill_demand, india_geojson = load_data()
    st_model, st_dict, pred_model, pred_meta = load_models()
    model_type = pred_meta['type']
    model_accuracy = pred_meta.get('accuracy', 0.73) * 100 
except Exception as e:
    st.error(f"Error loading required data or models: {e}")
    st.stop()

all_skills_raw = skill_demand['skill'].dropna().astype(str).tolist()
all_skills = sorted(list(set([s.strip().lower() for s in all_skills_raw if s.strip()])))

# --- Helper Functions ---
def predict_match_likelihood(skills_str, experience, state_ur):
    emb = st_model.encode([skills_str])[0]
    feats = np.hstack(([experience, state_ur], emb)).reshape(1, -1)
    
    if model_type == 'mlp':
        with torch.no_grad():
            t_feats = torch.FloatTensor(feats)
            prob = pred_model(t_feats).item()
    else:
        prob = pred_model.predict_proba(feats)[0][1]
    return prob

def get_job_examples(skills_str, top_n=3):
    user_vec = st_model.encode([skills_str])
    job_embeddings = np.array([st_dict.get(s, np.zeros(384)) for s in naukri_df['skills_str']])
    sim_scores = cosine_similarity(user_vec, job_embeddings).flatten()
    top_indices = sim_scores.argsort()[-top_n:][::-1]
    return naukri_df.iloc[top_indices]['job_title'].unique().tolist()[:top_n]



def get_learning_time(skill):
    skill_lower = skill.lower()
    if any(k in skill_lower for k in ['python', 'java', 'c++', 'javascript', 'react', 'node', 'angular', 'php', 'ruby', 'go']):
        return "2-3 months"
    if any(k in skill_lower for k in ['machine learning', 'deep learning', 'data science', 'ai', 'artificial intelligence']):
        return "3-4 months"
    if any(k in skill_lower for k in ['sql', 'database', 'mysql', 'postgresql']):
        return "1-2 months"
    if any(k in skill_lower for k in ['excel', 'word', 'powerpoint']):
        return "1-2 months"
    if any(k in skill_lower for k in ['aws', 'azure', 'cloud', 'docker', 'kubernetes', 'devops']):
        return "2-3 months"
    return "1-2 months"

def get_practical_steps(skill):
    skill_lower = skill.lower()
    if any(k in skill_lower for k in ['python', 'java', 'c++', 'javascript', 'react', 'node', 'angular', 'php', 'ruby', 'go']):
        return ["Start with a beginner syntax course (e.g., freeCodeCamp, Codecademy).", "Build 2-3 small interactive projects to apply your knowledge.", "Push your code to GitHub and add the link to your resume."]
    if any(k in skill_lower for k in ['machine learning', 'deep learning', 'data science', 'ai', 'artificial intelligence']):
        return ["Take an introductory course (e.g., Andrew Ng's Coursera class).", "Practice analyzing free datasets on Kaggle.", "Create a simple portfolio project showing your insights."]
    if any(k in skill_lower for k in ['sql', 'database', 'mysql', 'postgresql']):
        return ["Learn basic SELECT, JOIN, and GROUP BY statements online.", "Practice querying a sample database.", "Solve beginner SQL challenges on HackerRank."]
    if any(k in skill_lower for k in ['excel', 'word', 'powerpoint']):
        return ["Watch a crash course on YouTube.", "Practice standard formulas (e.g., VLOOKUP) or formatting.", "Use it to organize your own personal data or budget."]
    if any(k in skill_lower for k in ['aws', 'azure', 'cloud', 'devops', 'docker', 'kubernetes']):
        return ["Familiarize yourself with the core services (Compute, Storage).", "Follow a tutorial to deploy a basic app.", "Consider studying for a foundational certification."]
    if any(k in skill_lower for k in ['communication', 'leadership', 'management', 'sales']):
        return ["Read industry-standard books or articles on the topic.", "Practice the skills in your current role or personal projects.", "Highlight relevant experiences where you used this skill on your resume."]
    return ["Start with a highly-rated beginner online course.", "Practice with small, real-world exercises.", "Add the skill to your resume once you master the basics."]


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
        render_html(f"""
    <div style="background: rgba(13, 13, 15, 0.5); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 25px; margin-bottom: 20px;">
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
    """)

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
    pdf.cell(0, 15, "Personal Skill & Job Match Report", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)
    
    # Profile Box
    pdf.set_fill_color(30, 41, 59)
    pdf.set_text_color(text_r, text_g, text_b)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, " Your Profile", new_x="LMARGIN", new_y="NEXT", fill=True)
    
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(sub_r, sub_g, sub_b)
    pdf.cell(0, 8, f" Target State: {user_state}", new_x="LMARGIN", new_y="NEXT", fill=True)
    pdf.cell(0, 8, f" Experience: {user_exp} years", new_x="LMARGIN", new_y="NEXT", fill=True)
    pdf.cell(0, 8, f" Current Placement Chance: {base_prob*100:.1f}%", new_x="LMARGIN", new_y="NEXT", fill=True)
    pdf.cell(0, 8, f" Current Skills: {', '.join(current_skills)}", new_x="LMARGIN", new_y="NEXT", fill=True)
    pdf.ln(10)
    
    for rd in roadmaps_data:
        add_dark_page()
        
        pdf.set_text_color(accent_r, accent_g, accent_b)
        pdf.set_font("Helvetica", "B", 20)
        pdf.cell(0, 10, f"Roadmap: {rd['skill']}", new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_text_color(sub_r, sub_g, sub_b)
        pdf.set_font("Helvetica", "I", 12)
        pdf.multi_cell(0, 8, rd['desc'])
        pdf.ln(5)
        
        # Stats
        pdf.set_text_color(text_r, text_g, text_b)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, f"Estimated Time: {rd['est_time']}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(accent_r, accent_g, accent_b)
        pdf.cell(0, 8, f"Employability Uplift: +{rd['uplift']*100:.1f}%", new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(text_r, text_g, text_b)
        pdf.cell(0, 8, f"Top Demand States: {', '.join(rd['top_states'])}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(8)
        
        # Stages
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(text_r, text_g, text_b)
        pdf.cell(0, 10, "Step-by-Step Learning Path:", new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(accent_r, accent_g, accent_b)
        pdf.cell(0, 8, "Stage 1: Fundamentals", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(sub_r, sub_g, sub_b)
        for s in rd['stage1']: pdf.cell(0, 6, f"- {s}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)
        
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(accent_r, accent_g, accent_b)
        pdf.cell(0, 8, "Stage 2: Practical Application", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(sub_r, sub_g, sub_b)
        for s in rd['stage2']: pdf.cell(0, 6, f"- {s}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)
        
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(accent_r, accent_g, accent_b)
        pdf.cell(0, 8, "Stage 3: Get Job-Ready", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(sub_r, sub_g, sub_b)
        for s in rd['stage3']: pdf.cell(0, 6, f"- {s}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(8)
        
        # Roles
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(text_r, text_g, text_b)
        pdf.cell(0, 10, "Example Roles Unlocked:", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(sub_r, sub_g, sub_b)
        for r in rd['roles']: pdf.cell(0, 6, f"- {r.title()}", new_x="LMARGIN", new_y="NEXT")
            
    return pdf.output()
def get_career_path(skills_list):
    skills_str = " ".join(skills_list).lower()
    paths = {
        "software": {
            "keywords": ["java", "python", "c++", "c#", "javascript", "react", "node", "angular", "software", "developer"],
            "path": "Software Engineer ➡️ Senior Software Engineer ➡️ Technical Lead",
            "next": "System Design, Cloud Architecture"
        },
        "data": {
            "keywords": ["data", "machine learning", "sql", "excel", "analytics", "statistics", "tableau", "power bi"],
            "path": "Data Analyst ➡️ Data Scientist ➡️ Machine Learning Engineer",
            "next": "Advanced Machine Learning, MLOps"
        },
        "sales": {
            "keywords": ["sales", "marketing", "business development", "b2b", "b2c", "lead generation"],
            "path": "Sales Executive ➡️ Area Sales Manager ➡️ Regional Sales Manager",
            "next": "Strategic Sales, Account Management"
        },
        "support": {
            "keywords": ["customer support", "bpo", "voice", "inbound", "outbound", "telecalling"],
            "path": "Customer Support Executive ➡️ Team Leader ➡️ Operations Manager",
            "next": "Team Management, Conflict Resolution"
        },
        "hr": {
            "keywords": ["hr", "recruitment", "human resources", "talent acquisition"],
            "path": "HR Executive ➡️ HR Generalist ➡️ HR Manager",
            "next": "Employee Relations, Payroll Management"
        },
        "finance": {
            "keywords": ["accounting", "finance", "tally", "taxation", "gst"],
            "path": "Accountant ➡️ Senior Accountant ➡️ Finance Manager",
            "next": "Financial Modeling, Advanced Taxation"
        },
        "digital_marketing": {
            "keywords": ["seo", "digital marketing", "social media", "content"],
            "path": "Digital Marketing Executive ➡️ SEO/SEM Analyst ➡️ Marketing Manager",
            "next": "Performance Marketing, Campaign Strategy"
        },
        "admin": {
            "keywords": ["admin", "data entry", "office", "clerk", "operations"],
            "path": "Data Entry Operator ➡️ Admin Executive ➡️ Office Manager",
            "next": "Office Administration, Vendor Management"
        }
    }
    
    best_match = None
    max_hits = 0
    for category, details in paths.items():
        hits = sum(1 for kw in details["keywords"] if kw in skills_str)
        if hits > max_hits:
            max_hits = hits
            best_match = details
            
    if best_match is None:
        # Generic fallback
        return "Associate ➡️ Senior Associate ➡️ Team Lead", "Communication, Leadership"
    return best_match["path"], best_match["next"]

# Theme accent color
ACCENT_COLOR = "#00D2FF"

# --- Session State Init ---
if 'results_active' not in st.session_state:
    st.session_state['results_active'] = False
if 'learned_skills' not in st.session_state:
    st.session_state['learned_skills'] = []

# For persona presets, we use session state keys directly bound to the widgets
if 'p_state' not in st.session_state:
    st.session_state.p_state = sorted(state_df['state'].dropna().unique().tolist())[0]
if 'p_exp' not in st.session_state:
    st.session_state.p_exp = 2.0
if 'p_edu' not in st.session_state:
    st.session_state.p_edu = "Undergraduate"
if 'p_skills' not in st.session_state:
    st.session_state.p_skills = []

def apply_persona(state, exp, edu, skills):
    st.session_state.p_state = state
    st.session_state.p_exp = float(exp)
    st.session_state.p_edu = edu
    # Filter skills to ensure they exist in all_skills
    valid_skills = [s for s in skills if s in all_skills]
    st.session_state.p_skills = valid_skills
    st.session_state.results_active = True
    st.session_state.learned_skills = []

# --- Navigation & Page Routing ---
if 'active_page' not in st.session_state:
    st.session_state['active_page'] = "Home"

def set_page(page_name):
    st.session_state['active_page'] = page_name

pages = ["Home", "Get My Recommendation", "Skill Roadmaps", "Dashboard", "Compare Skills"]
idx = pages.index(st.session_state['active_page']) if st.session_state['active_page'] in pages else 0

selected_page = option_menu(
    menu_title=None,
    options=pages,
    icons=['house', 'bullseye', 'map', 'bar-chart', 'search'],
    default_index=idx,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#000000"},
        "icon": {"color": "#00D2FF", "font-size": "16px"},
        "nav-link": {"font-size": "15px", "text-align": "center", "margin":"0px", "--hover-color": "#0D0D0F"},
        "nav-link-selected": {"background-color": "#0D0D0F", "color": "#00D2FF", "border-bottom": "2px solid #00D2FF"}
    }
)

if selected_page != st.session_state['active_page']:
    st.session_state['active_page'] = selected_page
    st.rerun()

# --- Custom CSS for Landing Page Animations ---
render_html("""
<style>
@keyframes textGlow {
    0% { font-weight: 500; text-shadow: 0 0 10px rgba(0,210,255,0); }
    100% { font-weight: 800; text-shadow: 0 0 30px rgba(0,210,255,0.6); }
}
@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(30px) scale(0.95); }
    to { opacity: 1; transform: translateY(0) scale(1); }
}
@keyframes patternMove {
    from { background-position: 0 0; }
    to { background-position: 100px 100px; }
}

/* Hero Section */
.hero-container {
    text-align: center;
    padding: 80px 20px 40px;
    position: relative;
}
/* Subtle repeating pattern overlay on hero */
.hero-container::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image: radial-gradient(rgba(255,255,255,0.05) 1px, transparent 1px);
    background-size: 20px 20px;
    z-index: -1;
    animation: patternMove 20s linear infinite;
    pointer-events: none;
    opacity: 0.5;
}
.hero-title {
    font-size: 4rem;
    margin-bottom: 15px;
    background: linear-gradient(270deg, #FFFFFF, #E2E8F0);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: textGlow 1.5s ease-out forwards;
}
.hero-subtitle {
    font-size: 1.3rem;
    color: #A0AEC0;
    max-width: 600px;
    margin: 0 auto 40px;
    opacity: 0;
    animation: fadeSlideUp 0.8s ease-out 0.2s forwards;
}

/* Primary Button Override */
div[data-testid="stButton"] button[kind="primary"] {
    background: linear-gradient(135deg, #00D2FF 0%, #3A7BD5 100%);
    border: none;
    padding: 10px 20px;
    font-size: 1.1rem;
    font-weight: 600;
    box-shadow: 0 0 15px rgba(0, 210, 255, 0.4);
    transition: all 0.3s ease;
}
div[data-testid="stButton"] button[kind="primary"]:hover {
    box-shadow: 0 0 25px rgba(0, 210, 255, 0.8);
    transform: scale(1.05);
}

/* Bento Grid */
.bento-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    grid-auto-rows: minmax(180px, auto);
    gap: 24px;
    margin-top: 40px;
    padding: 0 20px 60px;
}
@media (max-width: 1000px) {
    .bento-grid { grid-template-columns: repeat(2, 1fr); }
    .card-wide { grid-column: span 2; }
}
@media (max-width: 600px) {
    .bento-grid { grid-template-columns: 1fr; }
    .card-wide { grid-column: span 1; }
}

.bento-card {
    background: rgba(13, 13, 15, 0.7);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 20px;
    padding: 24px;
    color: white;
    opacity: 0;
    animation: fadeSlideUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.bento-card:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 15px 30px rgba(0, 210, 255, 0.15);
    border-color: rgba(0, 210, 255, 0.3);
}

.card-wide { grid-column: span 2; }
.card-tall { grid-row: span 2; justify-content: flex-start; }

.delay-1 { animation-delay: 0.1s; }
.delay-2 { animation-delay: 0.2s; }
.delay-3 { animation-delay: 0.3s; }
.delay-4 { animation-delay: 0.4s; }
.delay-5 { animation-delay: 0.5s; }
.delay-6 { animation-delay: 0.6s; }

.card-title { font-size: 1.1rem; color: #A0AEC0; margin-bottom: 8px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
.card-value { font-size: 2.8rem; font-weight: 800; color: #00D2FF; margin-bottom: 5px; line-height: 1; }
</style>
""")

# === PAGE ROUTING ===

if st.session_state['active_page'] == "Home":
    # --- NEW HERO SECTION ---
    st.markdown('''
    <style>
        /* Custom Button Styling */
        div[data-testid="stMarkdownContainer"]:has(.hero-btn-wrapper) + div button {
            background-color: white !important;
            color: black !important;
            border-radius: 50px !important;
            border: none !important;
            font-weight: 700 !important;
            padding: 0.6rem 1.4rem !important;
            font-size: 1rem !important;
        }
        div[data-testid="stMarkdownContainer"]:has(.hero-btn-wrapper) + div button:hover {
            background-color: #f0f0f0 !important;
            color: black !important;
            border: none !important;
        }
        /* Top Spacing */
        .hero-spacer { margin-top: 60px; }
    </style>
    ''', unsafe_allow_html=True)

    h_col1, h_col2 = st.columns([1.1, 0.9])
    
    with h_col1:
        st.markdown('<div class="hero-spacer"></div>', unsafe_allow_html=True)
        st.markdown('''
        <h1 style="font-size: 4.5rem; line-height: 1.05; font-weight: 700; margin-bottom: 24px; color: white;">
            From skill gap<br/>to job offer.
        </h1>
        <p style="color: #A0AEC0; font-size: 1.25rem; max-width: 480px; line-height: 1.6; margin-bottom: 40px;">
            Stop guessing what employers want. We analyze real job postings across India to tell you exactly what to learn next.
        </p>
        ''', unsafe_allow_html=True)
        
        b1, b2 = st.columns([0.4, 0.6])
        with b1:
            st.markdown('<div class="hero-btn-wrapper"></div>', unsafe_allow_html=True)
            if st.button("Get Started", key="hero_cta"):
                set_page("Get My Recommendation")
                st.rerun()
        with b2:
            # We add a subtle link that visually mirrors the reference
            st.markdown('<div style="padding-top: 10px;"><a href="#" style="color: #A0AEC0; font-weight: 500; font-size: 1rem; text-decoration: none;">See how it works &rarr;</a></div>', unsafe_allow_html=True)
        
        st.markdown('<div style="margin-top: 60px; color: #555; font-size: 0.85rem; font-weight: 500;">Powered by real job market data across India</div>', unsafe_allow_html=True)

    with h_col2:
        threejs_code = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { margin: 0; overflow: hidden; background-color: #000000; }
                #canvas-container { width: 100vw; height: 100vh; position: absolute; top: 0; left: 0; display: flex; justify-content: center; align-items: center; }
                .glow {
                    position: absolute;
                    top: 50%; left: 50%;
                    transform: translate(-50%, -50%);
                    width: 350px; height: 350px;
                    background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, rgba(0,0,0,0) 70%);
                    border-radius: 50%;
                    z-index: 1;
                }
                canvas { position: absolute; top: 0; left: 0; z-index: 2; }
            </style>
        </head>
        <body>
            <div id="canvas-container">
                <div class="glow"></div>
            </div>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
            <script>
                const container = document.getElementById('canvas-container');
                const scene = new THREE.Scene();
                
                const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
                camera.position.z = 7;

                const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
                renderer.setSize(window.innerWidth, window.innerHeight);
                renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
                container.appendChild(renderer.domElement);

                const material = new THREE.MeshStandardMaterial({
                    color: 0x151515,
                    metalness: 0.8,
                    roughness: 0.15,
                });

                const crystal = new THREE.Group();
                const boxGeo = new THREE.BoxGeometry(0.9, 0.9, 0.9);
                for(let x = -1; x <= 1; x++) {
                    for(let y = -1; y <= 1; y++) {
                        for(let z = -1; z <= 1; z++) {
                            const cubie = new THREE.Mesh(boxGeo, material);
                            cubie.position.set(x * 0.95, y * 0.95, z * 0.95);
                            crystal.add(cubie);
                        }
                    }
                }
                crystal.rotation.x = Math.PI / 4;
                crystal.rotation.y = Math.PI / 4;
                scene.add(crystal);

                // Strong rim/key lighting to highlight edges against black
                const keyLight = new THREE.DirectionalLight(0xffffff, 4);
                keyLight.position.set(5, 5, 5);
                scene.add(keyLight);

                const rimLight = new THREE.DirectionalLight(0xffffff, 8);
                rimLight.position.set(-5, 5, -5);
                scene.add(rimLight);
                
                const fillLight = new THREE.AmbientLight(0x333333);
                scene.add(fillLight);

                let mouseX = 0;
                let mouseY = 0;
                
                document.addEventListener('mousemove', (e) => {
                    mouseX = (e.clientX / window.innerWidth) * 2 - 1;
                    mouseY = -(e.clientY / window.innerHeight) * 2 + 1;
                });

                function animate() {
                    requestAnimationFrame(animate);
                    crystal.rotation.x += 0.003;
                    crystal.rotation.y += 0.005;
                    crystal.rotation.z += 0.002;
                    
                    crystal.position.x += (mouseX * 0.5 - crystal.position.x) * 0.05;
                    crystal.position.y += (mouseY * 0.5 - crystal.position.y) * 0.05;

                    renderer.render(scene, camera);
                }
                animate();
                
                window.addEventListener('resize', () => {
                    camera.aspect = window.innerWidth / window.innerHeight;
                    camera.updateProjectionMatrix();
                    renderer.setSize(window.innerWidth, window.innerHeight);
                });
            </script>
        </body>
        </html>
        """
        components.html(threejs_code, height=500)
        
    st.write("") # Spacer before bento grid

            
    # Bento Grid HTML
    bento_html = f"""<div class="bento-grid">
<!-- Pipeline (Tall, Col span 1) -->
<div class="bento-card card-tall delay-1" style="align-items: center;">
<div class="card-title">Match Pipeline</div>
<div style="display:flex; flex-direction:column; align-items:center; margin-top:30px; width:100%;">
<div style="background:rgba(255,255,255,0.02); padding:12px; border-radius:12px; border:1px solid rgba(255,255,255,0.1); width:100%; text-align:center; font-weight:600;">Your Skills</div>
<div style="width:2px; height:40px; background:linear-gradient(to bottom, rgba(255,255,255,0.3), rgba(255,255,255,0.1)); margin: 5px 0;"></div>
<div style="background:rgba(255,255,255,0.02); padding:12px; border-radius:12px; border:1px solid rgba(255,255,255,0.1); width:100%; text-align:center; font-weight:600;">Job Market Data</div>
<div style="width:2px; height:40px; background:linear-gradient(to bottom, rgba(255,255,255,0.1), rgba(255,255,255,0.3)); margin: 5px 0;"></div>
<div style="background:rgba(255,255,255,0.08); padding:12px; border-radius:12px; border:1px solid rgba(255,255,255,0.3); width:100%; text-align:center; font-weight:bold; box-shadow:0 0 15px rgba(255,255,255,0.1); color: white;">Recommendation</div>
</div>
</div>
<!-- Real-Time Insight (Wide) -->
<div class="bento-card card-wide delay-2" style="flex-direction:row; justify-content:space-between; align-items:center; overflow:hidden;">
<div style="z-index:2;">
<div class="card-title">Live Job Data</div>
<div class="card-value">{len(naukri_df):,}+</div>
<div style="color:#A0AEC0; font-size:1rem; max-width: 200px;">Real job postings analyzed across India.</div>
</div>
<!-- Glowing CSS Sphere Graphic -->
<div style="width:160px; height:160px; border-radius:50%; background:radial-gradient(circle at 35% 35%, rgba(255,255,255,0.3), #000000 70%); box-shadow:0 0 20px rgba(255,255,255,0.1); opacity:0.9; margin-right:20px; position: relative;">
<div style="position:absolute; top:0; left:0; width:100%; height:100%; border-radius:50%; border:1px solid rgba(255,255,255,0.1); transform: rotateX(60deg);"></div>
<div style="position:absolute; top:0; left:0; width:100%; height:100%; border-radius:50%; border:1px solid rgba(255,255,255,0.1); transform: rotateY(60deg);"></div>
</div>
</div>
<!-- Model Accuracy -->
<div class="bento-card delay-3" style="align-items:center;">
<div class="card-title">Model Accuracy</div>
<div style="position:relative; width:120px; height:120px; border-radius:50%; background:conic-gradient(rgba(255,255,255,0.7) {model_accuracy:.0f}%, rgba(255,255,255,0.05) 0); display:flex; justify-content:center; align-items:center; margin-top:15px; box-shadow: inset 0 0 10px rgba(0,0,0,0.5);">
<div style="width:100px; height:100px; border-radius:50%; background:#0D0D0F; display:flex; justify-content:center; align-items:center; font-size:1.8rem; font-weight:bold; color:white; box-shadow: 0 0 10px rgba(0,0,0,0.5);">{model_accuracy:.0f}%</div>
</div>
</div>
<!-- National Reach -->
<div class="bento-card delay-4">
<div class="card-title">National Reach</div>
<div class="card-value" style="font-size:2.2rem;">{state_df["state"].nunique()}</div>
<div style="color:#A0AEC0; font-size:0.9rem;">States & Union Territories</div>
<!-- Animated bar chart -->
<div style="display:flex; align-items:flex-end; gap:6px; height:45px; margin-top:20px;">
<div style="width:18%; background:rgba(255,255,255,0.1); height:40%; border-radius:4px;"></div>
<div style="width:18%; background:rgba(255,255,255,0.8); height:100%; border-radius:4px; box-shadow:0 0 12px rgba(255,255,255,0.2);"></div>
<div style="width:18%; background:rgba(255,255,255,0.1); height:70%; border-radius:4px;"></div>
<div style="width:18%; background:rgba(255,255,255,0.1); height:50%; border-radius:4px;"></div>
<div style="width:18%; background:rgba(255,255,255,0.1); height:85%; border-radius:4px;"></div>
</div>
</div>
<!-- Trusted Sources -->
<div class="bento-card delay-5" style="align-items:center; text-align:center;">
<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="color: #A0AEC0; margin-bottom: 15px;"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
<div class="card-title" style="margin-bottom:5px;">Trusted Data</div>
<div style="color:#A0AEC0; font-size:0.85rem;">Sourced directly from official gov surveys & live portals.</div>
</div>
<!-- Skill Roadmaps Feature -->
<div class="bento-card delay-6" style="align-items:center; text-align:center; background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.1);">
<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="color: #A0AEC0; margin-bottom: 15px;"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>
<div class="card-title" style="margin-bottom:5px;">Targeted Growth</div>
<div style="color:#A0AEC0; font-size:0.85rem;">Step-by-step roadmaps to master high-demand skills.</div>
</div>
</div>"""
    render_html(bento_html)

elif st.session_state['active_page'] == "Dashboard":
    st.write("### 🌍 National Job Market Overview")
    
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(label="📉 Avg Unemployment Rate", value=f"{state_df['UR'].mean():.1f}%")
    with m2:
        st.metric(label="💼 Total Jobs Analyzed", value=f"{len(naukri_df):,}")
    with m3:
        st.metric(label="🗺️ States Covered", value=f"{state_df['state'].nunique()}")
    with m4:
        top_national = skill_demand.groupby('skill')['demand_score'].sum().idxmax().title()
        st.metric(label="🔥 Top Skill Nationally", value=top_national)
        
    st.divider()
    
    st.write("#### 🗺️ Unemployment Rate Across India")
    st.caption("Hover over a state to see its unemployment percentage.")
    if india_geojson:
        fig_map = px.choropleth(
            state_df, 
            geojson=india_geojson, 
            featureidkey='properties.ST_NM', 
            locations='map_state', 
            color='UR',
            color_continuous_scale="Reds",
            hover_name='state',
            hover_data={'map_state': False, 'UR': True}
        )
        fig_map.update_geos(fitbounds="locations", visible=False, bgcolor="#000000")
        fig_map.update_layout(height=700, margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="#000000", plot_bgcolor="#000000", font_color="#FFFFFF")
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning("Could not load map data. Please check your internet connection.")
        
    st.divider()

    st.write("#### 🏆 Top 10 Most Wanted Skills")
    st.caption("The skills that appear in the most job descriptions nationally.")
    
    top_skills = skill_demand.groupby('skill')['demand_score'].sum().sort_values(ascending=False).head(10).reset_index()
    fig_bar = px.bar(
        top_skills.sort_values('demand_score', ascending=True), 
        x='demand_score', y='skill', orientation='h',
        color='demand_score', color_continuous_scale="Greens"
    )
    fig_bar.update_layout(height=450, margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="#000000", plot_bgcolor="#000000", font_color="#FFFFFF", showlegend=False, xaxis_title="Demand Score", yaxis_title="")
    st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()
    
    c3, c4 = st.columns((1, 1))
    
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
            paper_bgcolor="#000000", 
            plot_bgcolor="#000000", 
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
        )

# === TAB Compare Skills ===
elif st.session_state['active_page'] == "Compare Skills":
    st.write("### 🔍 Compare Any Two Skills")
    st.write("See which skill is more in-demand and where.")
    
    cmp1, cmp2 = st.columns(2)
    with cmp1:
        skill_a = st.selectbox("Select Skill A", options=all_skills, index=min(10, len(all_skills)-1))
    with cmp2:
        skill_b = st.selectbox("Select Skill B", options=all_skills, index=min(20, len(all_skills)-1))
        
    if skill_a and skill_b:
        st.divider()
        c_res1, c_res2 = st.columns(2)
        
        total_jobs = len(naukri_df)
        
        demand_a = skill_demand[skill_demand['skill'] == skill_a]['demand_score'].sum()
        pct_a = (demand_a / total_jobs) * 100
        states_a = skill_demand[skill_demand['skill'] == skill_a].sort_values('demand_score', ascending=False).head(3)['state'].tolist()
        
        demand_b = skill_demand[skill_demand['skill'] == skill_b]['demand_score'].sum()
        pct_b = (demand_b / total_jobs) * 100
        states_b = skill_demand[skill_demand['skill'] == skill_b].sort_values('demand_score', ascending=False).head(3)['state'].tolist()
        
        with c_res1:
            with st.container(border=True):
                st.write(f"### {skill_a.title()}")
                st.metric("Total National Demand", f"{int(demand_a)} postings", help="Relative frequency of this skill in job postings nationwide.")
                st.write(f"This skill appears in roughly **{pct_a:.1f}%** of all jobs.")
                st.write("**Top States for this skill:**")
                for s in states_a:
                    st.caption(f"📍 {s}")
                    
        with c_res2:
            with st.container(border=True):
                st.write(f"### {skill_b.title()}")
                st.metric("Total National Demand", f"{int(demand_b)} postings", help="Relative frequency of this skill in job postings nationwide.")
                st.write(f"This skill appears in roughly **{pct_b:.1f}%** of all jobs.")
                st.write("**Top States for this skill:**")
                for s in states_b:
                    st.caption(f"📍 {s}")

# === TAB 3: Get My Recommendation ===
elif st.session_state['active_page'] == "Get My Recommendation":
    st.write("### 🎯 Find Your Next Skill")
    
    st.write("Or try a quick demo persona:")
    btn1, btn2, btn3, _ = st.columns([1.5, 2, 1.5, 1])
    with btn1:
        st.button("🎓 Fresh Graduate, Delhi", on_click=apply_persona, args=("Delhi", 0.0, "Undergraduate", ["communication", "ms office"]))
    with btn2:
        st.button("💼 3 Yrs Exp, Mumbai, Excel Only", on_click=apply_persona, args=("Maharashtra", 3.0, "Undergraduate", ["excel"]))
    with btn3:
        st.button("🏭 Diploma Holder, Bihar", on_click=apply_persona, args=("Bihar", 1.0, "Diploma", ["data entry", "typing"]))
        
    st.write("")
    
    with st.form("user_input_form"):
        st.write("Tell us where you stand today, and we'll tell you what to learn tomorrow.")
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            user_state = st.selectbox("Where do you live? (Or want to work)", options=sorted(state_df['state'].dropna().unique().tolist()), key="p_state", help="We will look for jobs specifically in this state.")
            user_exp = st.number_input("Years of Experience", min_value=0.0, max_value=50.0, step=0.5, key="p_exp", help="How many years have you been working?")
            user_edu = st.selectbox("Education Level", ["10th/12th", "Diploma", "Undergraduate", "Postgraduate", "PhD"], key="p_edu", help="Your highest degree.")
        
        with col_f2:
            current_skills = st.multiselect(
                "What skills do you already have?", 
                options=all_skills, 
                key="p_skills", 
                help="Select the skills you already know. We'll figure out what's missing."
            )
            
        st.write("")
        submit = st.form_submit_button("🚀 Find My Missing Skills", use_container_width=True)
        
    if submit:
        if not current_skills:
            st.error("Please select at least one skill you currently have so we can find matches!")
            st.session_state['results_active'] = False
        else:
            st.session_state['results_active'] = True
            st.session_state['learned_skills'] = []
            
    if st.session_state.get('results_active') and st.session_state.p_skills:
        st.markdown("---")
        st.write("### 💡 Your Personalized Recommendations")
        
        s_user_state = st.session_state.p_state
        s_user_exp = st.session_state.p_exp
        s_current_skills = st.session_state.p_skills
        
        effective_skills = s_current_skills + st.session_state['learned_skills']
        
        base_skills_str = " ".join(s_current_skills)
        effective_skills_str = " ".join(effective_skills)
        
        state_ur = state_df[state_df['state'] == s_user_state]['UR'].values[0]
        
        original_base_prob = predict_match_likelihood(base_skills_str, s_user_exp, state_ur)
        live_prob = predict_match_likelihood(effective_skills_str, s_user_exp, state_ur)
        
        state_top_skills = skill_demand[skill_demand['state'] == s_user_state].sort_values('demand_score', ascending=False)
        skills_to_test = [s for s in state_top_skills['skill'].tolist() if s not in effective_skills][:30]
        
        if len(skills_to_test) < 30:
            national_top = skill_demand.groupby('skill')['demand_score'].sum().sort_values(ascending=False).index.tolist()
            for s in national_top:
                if s not in effective_skills and s not in skills_to_test:
                    skills_to_test.append(s)
                if len(skills_to_test) == 30:
                    break
        
        uplift_results = []
        for new_skill in skills_to_test:
            new_str = effective_skills_str + " " + new_skill
            new_prob = predict_match_likelihood(new_str, s_user_exp, state_ur)
            uplift = new_prob - live_prob
            uplift_results.append({
                'Recommended Skill': new_skill.title(),
                'New Match Rate': new_prob,
                'Uplift': uplift,
                'new_str': new_str
            })
            
        uplift_df = pd.DataFrame(uplift_results).sort_values('Uplift', ascending=False)
        
        if len(uplift_df) > 0:
            top_skill = uplift_df.iloc[0]['Recommended Skill']
            top_new_prob = uplift_df.iloc[0]['New Match Rate']
            top_uplift = uplift_df.iloc[0]['Uplift']
            
            st.write("### 📈 Your Placement Chance")
            st.write("Watch your placement chance grow as you learn new skills. The live tracker below updates immediately when you check off a skill you've started learning.")
            
            b1, b2 = st.columns(2)
            with b1:
                with st.container(border=True):
                    delta = None
                    if len(st.session_state['learned_skills']) > 0:
                        delta = f"+{(live_prob - original_base_prob)*100:.1f}% (Progress)"
                    st.metric("Live Placement Chance", f"{live_prob*100:.1f}%", delta=delta, help="Probability of matching jobs based on your current + newly learned skills.")
            with b2:
                with st.container(border=True):
                    st.metric(f"Potential Chance with '{top_skill}'", f"{top_new_prob*100:.1f}%", delta=f"+{top_uplift*100:.1f}%", help=f"Your probability if you add {top_skill} next.")
            
            st.divider()
            
            path_desc, next_skills = get_career_path(effective_skills)
            st.info(f"🛣️ **Common Career Progression for your skills:** {path_desc}\n\n**To reach the next step, focus on:** {next_skills}")
            
            st.divider()
            
            st.write("### 💡 Top Skills to Learn Next")
            st.caption("Check the box when you start learning a skill to add it to your profile and watch your live placement chance grow!")
            
            top3 = uplift_df.head(3)
            def on_skill_checked(s):
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
                st.write("") # Spacer
                    
            st.divider()
            
            st.write("### 🚀 Power Combo Recommendation")
            combo_text = ""
            if len(top3) >= 2:
                combo_skills = [top3.iloc[0]['Recommended Skill'], top3.iloc[1]['Recommended Skill']]
                combo_str = effective_skills_str + " " + " ".join(combo_skills).lower()
                combo_prob = predict_match_likelihood(combo_str, s_user_exp, state_ur)
                combo_uplift = combo_prob - live_prob
                
                combo_text = f"Learn {combo_skills[0]} + {combo_skills[1]} together: Combined Placement Chance {combo_prob*100:.1f}% (+{combo_uplift*100:.1f}%)"
                with st.container(border=True):
                    st.write(f"**Learn {combo_skills[0]} + {combo_skills[1]} together**")
                    st.metric(label="Combined Placement Chance", value=f"{combo_prob*100:.1f}%", delta=f"+{combo_uplift*100:.1f}%")
                    st.write(f"Learning both of these highly demanded skills in combination maximizes your employability footprint in {s_user_state}.")
            else:
                st.write("Not enough missing skills to form a combo.")
                
            st.divider()
            
            st.write("### 📍 Where your skills are most in demand")
            
            state_probs = []
            for s in state_df['state'].dropna().unique():
                s_ur = state_df[state_df['state'] == s]['UR'].values[0]
                p = predict_match_likelihood(effective_skills_str, s_user_exp, s_ur)
                state_probs.append({'state': s, 'prob': p})
                
            state_probs_df = pd.DataFrame(state_probs).sort_values('prob', ascending=False)
            
            other_states = state_probs_df[state_probs_df['state'] != s_user_state]
            top_other_state_text = ""
            if len(other_states) > 0:
                top_other_state = other_states.iloc[0]['state']
                top_other_prob = other_states.iloc[0]['prob']
                
                if top_other_prob > live_prob:
                    top_other_state_text = f"Relocation Tip: Based on your skills, you have a higher placement chance in {top_other_state} ({top_other_prob*100:.1f}%) than in your selected state."
                    st.info(top_other_state_text)
                else:
                    top_other_state_text = f"You're in a great spot! The next best state for your profile is {top_other_state}."
                    st.info(top_other_state_text)
            
            st.divider()
            
            st.write("### 📄 Take Your Roadmap With You")
            st.write("Download a neat 1-page summary of your current profile and your recommended skills to review later.")
            
            roadmaps_data = []
            for i, row in top3.iterrows():
                rd = get_roadmap_content(row['Recommended Skill'], s_user_state, s_user_exp, live_prob, effective_skills_str)
                roadmaps_data.append(rd)
            pdf_output = generate_pdf_report(s_user_state, s_user_exp, s_current_skills, live_prob, roadmaps_data)

            pdf_bytes = bytes(pdf_output) if isinstance(pdf_output, bytearray) else pdf_output
            
            st.download_button(
                label="Download My Skill Report (PDF)",
                data=pdf_bytes,
                file_name="My_Skill_Match_Report.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
        st.divider()
        st.caption(f"🤖 **How confident is this?** Our AI recommendation model is **{model_accuracy:.1f}% accurate** based on testing against {len(naukri_df):,} real job postings.")


elif selected_page == "Skill Roadmaps":
    render_html("<h1 style='text-align: center; color: #00D2FF;'>🗺️ Skill Roadmaps</h1>")
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
