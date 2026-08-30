import re

with open("streamlit_app.py", "r") as f:
    content = f.read()

# Add import
if "from streamlit_option_menu import option_menu" not in content:
    content = content.replace("import streamlit as st", "import streamlit as st\nfrom streamlit_option_menu import option_menu\nimport streamlit.components.v1 as components")

# The old main app header + tabs
old_main_str = """# --- Main App ---
st.markdown("<h1 style='text-align: center;'>⚡ Skill & Job Matcher</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.1em; color: #A0AEC0;'>Find the exact skills you need to get hired. We analyze real job postings across India to tell you what to learn next.</p>", unsafe_allow_html=True)

with st.expander("ℹ️ About this tool"):
    st.write(\"\"\"
    We analyzed **22,000 real job postings** and **government employment data** across India. 
    
    Using AI, this tool understands the meaning of your skills and compares them to what companies are actively looking for right now. We then recommend the missing skills that will boost your chances of getting a job.
    \"\"\")
st.write("")

tab1, tab2, tab_compare, tab3 = st.tabs(["🏠 Home", "📊 Dashboard", "🔍 Compare Skills", "🎯 Get My Recommendation"])

# === TAB 1: Home ===
with tab1:
    st.write("### Welcome to your career guide")
    st.write(\"\"\"
    Looking for a job but not getting callbacks? You might be missing just one or two key skills that employers in your state are desperately looking for.
    
    **How to use this tool:**
    1. **Go to 'Get My Recommendation':** Tell us your state, experience, and what you already know.
    2. **Get your custom learning path:** Our AI will analyze thousands of open jobs and tell you the exact skills you should learn next to get hired.
    3. **Explore the 'Dashboard':** See where the jobs are and what the overall market looks like right now.
    \"\"\")
    st.info("💡 Click on the 'Get My Recommendation' tab above to start.")

# === TAB 2: Dashboard ===
with tab2:"""

new_main_str = """# --- Navigation & Page Routing ---
if 'active_page' not in st.session_state:
    st.session_state['active_page'] = "🏠 Home"

def set_page(page_name):
    st.session_state['active_page'] = page_name

pages = ["🏠 Home", "🎯 Get My Recommendation", "📊 Dashboard", "🔍 Compare Skills"]
idx = pages.index(st.session_state['active_page']) if st.session_state['active_page'] in pages else 0

selected_page = option_menu(
    menu_title=None,
    options=pages,
    icons=['house', 'bullseye', 'bar-chart', 'search'],
    default_index=idx,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#0E1117"},
        "icon": {"color": "#00D2FF", "font-size": "16px"},
        "nav-link": {"font-size": "15px", "text-align": "center", "margin":"0px", "--hover-color": "#1E2430"},
        "nav-link-selected": {"background-color": "#1E2430", "color": "#00D2FF", "border-bottom": "2px solid #00D2FF"}
    }
)

if selected_page != st.session_state['active_page']:
    st.session_state['active_page'] = selected_page
    st.rerun()

# --- Custom CSS for Landing Page Animations ---
st.markdown(\"\"\"
<style>
@keyframes glow {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
@keyframes slideUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}
.hero-container {
    text-align: center;
    padding: 60px 20px 40px;
}
.hero-title {
    font-size: 3.5rem;
    font-weight: 800;
    margin-bottom: 10px;
    background: linear-gradient(270deg, #00D2FF, #3A7BD5, #00D2FF);
    background-size: 200% 200%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: glow 6s ease infinite, slideUp 0.8s ease-out forwards;
}
.hero-subtitle {
    font-size: 1.2rem;
    color: #A0AEC0;
    margin-bottom: 40px;
    opacity: 0;
    animation: slideUp 0.8s ease-out 0.2s forwards;
}
.step-card {
    background: #1E2430;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #2D3748;
    text-align: center;
    opacity: 0;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.step-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0, 210, 255, 0.15);
    border-color: #00D2FF;
}
.step-delay-1 { animation: slideUp 0.6s ease-out 0.4s forwards; }
.step-delay-2 { animation: slideUp 0.6s ease-out 0.6s forwards; }
.step-delay-3 { animation: slideUp 0.6s ease-out 0.8s forwards; }
</style>
\"\"\", unsafe_allow_html=True)

# === PAGE ROUTING ===

if st.session_state['active_page'] == "🏠 Home":
    st.markdown('<div class="hero-container"><div class="hero-title">Find Your Next Skill.<br/>Get Hired Faster.</div><div class="hero-subtitle">We analyze real job postings across India to tell you exactly what you need to learn.</div></div>', unsafe_allow_html=True)
    
    # CTA Buttons (using Streamlit columns for layout, so we can use native st.button for python callbacks)
    c1, c2, c3, c4 = st.columns([1, 1.2, 1.2, 1])
    with c2:
        if st.button("🎯 Get My Recommendation", use_container_width=True, type="primary"):
            set_page("🎯 Get My Recommendation")
            st.rerun()
    with c3:
        if st.button("📊 Explore the Dashboard", use_container_width=True):
            set_page("📊 Dashboard")
            st.rerun()
            
    st.write("<br><br><h3 style='text-align:center;'>How it works</h3><br>", unsafe_allow_html=True)
    
    s1, s2, s3 = st.columns(3)
    s1.markdown('<div class="step-card step-delay-1"><h3>1️⃣</h3><h4>Tell us your skills</h4><p style="color:#A0AEC0;">Select the skills you already have and your target state.</p></div>', unsafe_allow_html=True)
    s2.markdown('<div class="step-card step-delay-2"><h3>2️⃣</h3><h4>We analyze real data</h4><p style="color:#A0AEC0;">Our AI cross-references your profile against 22,000+ open jobs.</p></div>', unsafe_allow_html=True)
    s3.markdown('<div class="step-card step-delay-3"><h3>3️⃣</h3><h4>Get your roadmap</h4><p style="color:#A0AEC0;">Discover the exact skills that will maximize your hiring chances.</p></div>', unsafe_allow_html=True)
    
    st.write("<br><br>", unsafe_allow_html=True)
    
    # Animated Counter using pure JS in an iframe component
    counter_html = \"\"\"
    <div style="display: flex; justify-content: space-around; background: #0E1117; color: #FFF; font-family: sans-serif; text-align: center;">
        <div>
            <div id="c1" style="font-size: 2.5rem; font-weight: bold; color: #00D2FF;">0</div>
            <div style="color: #A0AEC0;">Jobs Analyzed</div>
        </div>
        <div>
            <div id="c2" style="font-size: 2.5rem; font-weight: bold; color: #00D2FF;">0</div>
            <div style="color: #A0AEC0;">States Covered</div>
        </div>
        <div>
            <div id="c3" style="font-size: 2.5rem; font-weight: bold; color: #00D2FF;">0</div>
            <div style="color: #A0AEC0;">Model Accuracy</div>
        </div>
    </div>
    <script>
    function animateValue(id, start, end, duration, suffix="") {
        let obj = document.getElementById(id);
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            obj.innerHTML = Math.floor(progress * (end - start)) + start + suffix;
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        window.requestAnimationFrame(step);
    }
    // slight delay to ensure it runs nicely when rendered
    setTimeout(() => {
        animateValue("c1", 0, 22000, 2000, "+");
        animateValue("c2", 0, 36, 1500, "");
        animateValue("c3", 0, 73, 1800, "%");
    }, 300);
    </script>
    \"\"\"
    components.html(counter_html, height=120)

elif st.session_state['active_page'] == "📊 Dashboard":"""

if old_main_str in content:
    content = content.replace(old_main_str, new_main_str)
    
    # Also need to replace the other tabs:
    content = content.replace("with tab_compare:", "elif st.session_state['active_page'] == \"🔍 Compare Skills\":")
    content = content.replace("with tab3:", "elif st.session_state['active_page'] == \"🎯 Get My Recommendation\":")
    
    with open("streamlit_app.py", "w") as f:
        f.write(content)
    print("Patched!")
else:
    print("Could not find the old string!")

