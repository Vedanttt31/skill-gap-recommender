with open("02_feature_engineering.py", "r") as f:
    content = f.read()
import re
# We just want everything up to the existing apply_canonical
parts = content.split("naukri['skills_list'] = naukri['skills_list'].apply(apply_canonical)")
new_logic = """naukri['skills_list'] = naukri['skills_list'].apply(apply_canonical)
    
    print("Calculating state-level skill demand scores (Canonical)...")
    naukri_exploded = naukri.explode('skills_list').dropna(subset=['skills_list', 'state'])
    state_skill_counts = naukri_exploded.groupby(['state', 'skills_list']).size().reset_index(name='count')
    state_totals = naukri_exploded.groupby('state').size().reset_index(name='state_total')
    skill_demand_df = pd.merge(state_skill_counts, state_totals, on='state')
    skill_demand_df['demand_score'] = skill_demand_df['count'] / skill_demand_df['state_total']
    skill_demand_df = skill_demand_df.rename(columns={'skills_list': 'skill'})
    skill_demand_df.to_csv('data/skill_demand_scores.csv', index=False)

    print("Generating Embeddings...")
"""
# find "naukri['skills_str'] = naukri['skills_list'].apply(lambda x: ' '.join(x))"
parts2 = parts[1].split("naukri['skills_str'] = naukri['skills_list'].apply(lambda x: ' '.join(x))")
content = parts[0] + new_logic + "    naukri['skills_str'] = naukri['skills_list'].apply(lambda x: ' '.join(x))" + parts2[1]

with open("02_feature_engineering.py", "w") as f:
    f.write(content)
