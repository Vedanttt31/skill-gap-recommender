with open("02_feature_engineering.py", "r") as f:
    content = f.read()

import re

normalization_logic = """
    import json
    with open('data/skill_normalization_map.json', 'r') as f:
        raw_to_canonical = json.load(f)

    def apply_canonical(slist):
        if not isinstance(slist, list):
            return []
        mapped = set()
        for s in slist:
            if s in raw_to_canonical:
                for c in raw_to_canonical[s]:
                    mapped.add(c)
        return list(mapped)

    naukri['skills_list'] = naukri['skills_list'].apply(apply_canonical)
    # the existing logic will create skills_str right after this
    
    # We must also re-calculate skill_demand_scores using canonical
    all_canonical_skills = []
    for clist in naukri['skills_list']:
        all_canonical_skills.extend(clist)
        
    demand_df = pd.DataFrame({'skill': all_canonical_skills})
    skill_counts = demand_df['skill'].value_counts().reset_index()
    skill_counts.columns = ['skill', 'demand_count']
    skill_counts['skill_demand_score'] = skill_counts['demand_count'] / skill_counts['demand_count'].max()
    skill_counts.to_csv('data/skill_demand_scores.csv', index=False)

    print("\\nGenerating Embeddings...")
"""

content = content.replace("    print(\"\\nGenerating Embeddings...\")", normalization_logic)

with open("02_feature_engineering.py", "w") as f:
    f.write(content)
