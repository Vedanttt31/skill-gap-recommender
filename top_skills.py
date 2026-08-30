import pandas as pd
from collections import Counter
import ast

df = pd.read_csv('data/naukri_features.csv', low_memory=False)
skills_counter = Counter()

# Read the skills_list which might be a string representation of a list
for slist in df['skills_list'].dropna():
    try:
        skills = ast.literal_eval(slist)
        if isinstance(skills, list):
            for s in skills:
                skills_counter[s] += 1
    except:
        pass

for k, v in skills_counter.most_common(300):
    print(f"{k}: {v}")
