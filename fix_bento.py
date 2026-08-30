with open("streamlit_app.py", "r") as f:
    content = f.read()

# 1. bento_html = """ -> bento_html = f"""
content = content.replace('bento_html = """<div class="bento-grid">', 'bento_html = f"""<div class="bento-grid">')

# 2. 22,000+ -> {len(naukri_df):,}+
content = content.replace('<div class="card-value">22,000+</div>', '<div class="card-value">{len(naukri_df):,}+</div>')

# 3. Model Accuracy 73% -> {model_accuracy:.0f}%
content = content.replace('background:conic-gradient(#00D2FF 73%,', 'background:conic-gradient(#00D2FF {model_accuracy:.0f}%,')
content = content.replace('0 0 10px rgba(0,0,0,0.5);">73%</div>', '0 0 10px rgba(0,0,0,0.5);">{model_accuracy:.0f}%</div>')

# 4. National Reach 36 -> {state_df['state'].nunique()}
content = content.replace('<div class="card-value" style="font-size:2.2rem;">36</div>', '<div class="card-value" style="font-size:2.2rem;">{state_df["state"].nunique()}</div>')

# 5. Replace the decorative rocket card
old_rocket = """<!-- Decorative -->
<div class="bento-card delay-6" style="justify-content:center; align-items:center; background:linear-gradient(135deg, rgba(0,210,255,0.1), rgba(58,123,213,0.05)); border:none;">
<div style="font-size:4rem; opacity:0.9; filter:drop-shadow(0 0 15px rgba(0,210,255,0.6));">🚀</div>
</div>"""

new_rocket = """<!-- Skill Roadmaps Feature -->
<div class="bento-card delay-6" style="align-items:center; text-align:center; background:linear-gradient(135deg, rgba(0,210,255,0.05), rgba(58,123,213,0.05)); border:1px solid rgba(0,210,255,0.15);">
<div style="font-size:3.5rem; margin-bottom:15px; filter:drop-shadow(0 0 15px rgba(0,210,255,0.6));">🎯</div>
<div class="card-title" style="margin-bottom:5px;">Targeted Growth</div>
<div style="color:#A0AEC0; font-size:0.85rem;">Step-by-step roadmaps to master high-demand skills.</div>
</div>"""

content = content.replace(old_rocket, new_rocket)

# 6. testing against 22,000 real job postings -> {len(naukri_df):,}
content = content.replace('testing against 22,000 real job postings.', 'testing against {len(naukri_df):,} real job postings.')

with open("streamlit_app.py", "w") as f:
    f.write(content)

