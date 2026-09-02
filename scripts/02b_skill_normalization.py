import pandas as pd
import numpy as np
import ast
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
import json
import time

print("Loading data...")
df = pd.read_csv('data/naukri_features.csv', low_memory=False)

# Get all unique raw skills
raw_skills = set()
for slist in df['skills_list'].dropna():
    try:
        skills = ast.literal_eval(slist)
        if isinstance(skills, list):
            for s in skills:
                raw_skills.add(s)
    except:
        pass
raw_skills = list(raw_skills)
print(f"Total raw unique skills: {len(raw_skills)}")

# Define canonical categories and their explicit synonyms/rules
canonical_dict = {
    "Python": ["python", "pandas", "numpy", "pyspark"],
    "Java": ["java", "j2ee", "spring", "hibernate", "jsp", "springboot", "spring boot", "core java"],
    "C/C++": ["c++", "c language", "c programming", "c/c++"],
    "C# / .NET": ["c#", ".net", "asp.net", "c#.net"],
    "JavaScript": ["javascript", "js", "jquery", "typescript"],
    "Frontend Frameworks": ["react", "react.js", "angular", "vue", "front end", "bootstrap", "css", "html"],
    "Backend Frameworks": ["node.js", "express", "django", "flask", "backend"],
    "Mobile App Development": ["android", "ios", "flutter", "react native", "mobile & web design"],
    "SQL / Relational DBs": ["sql", "mysql", "oracle", "plsql", "postgresql", "sql server", "complex sql query"],
    "NoSQL DBs": ["mongodb", "cassandra", "nosql", "dynamodb"],
    "Cloud Computing (AWS/GCP/Azure)": ["aws", "amazon web services", "gcp", "google cloud", "azure", "microsoft azure", "cloud"],
    "DevOps & CI/CD": ["devops", "ci/cd", "continuous integration", "jenkins", "docker", "kubernetes", "terraform", "ansible", "microservices"],
    "Git / Version Control": ["git", "github", "gitlab", "version control", "bitbucket"],
    "Machine Learning & AI": ["machine learning", "ml", "artificial intelligence", "ai", "deep learning", "nlp", "natural language processing", "algorithms", "computer vision", "generative ai"],
    "Data Science & Analytics": ["data analysis", "data science", "data analytics", "data modeling", "analytics", "data warehousing", "data management"],
    "Data Engineering (ETL/Big Data)": ["data engineering", "etl", "hadoop", "spark", "hive", "kafka", "snowflake"],
    "Business Intelligence (BI)": ["power bi", "tableau", "business intelligence", "dashboard"],
    "Excel": ["excel", "vlook up", "vlookup", "ms excel", "microsoft excel", "pivot tables"],
    "SAP": ["sap", "sap hana", "sap abap", "sap sd", "sap s hana", "abap"],
    "ERP & CRM": ["erp", "crm", "salesforce", "servicenow", "netsuite", "netsuite erp", "hybris"],
    "Cybersecurity": ["security", "cyber security", "cybersecurity", "aws security", "information security", "risk management"],
    "Software Testing / QA": ["software testing", "qa", "quality assurance", "manual testing", "automation testing", "selenium", "test cases", "regression testing", "unit testing", "performance testing"],
    "Agile & Scrum": ["agile", "scrum", "agile methodology", "jira"],
    "Project & Product Management": ["project management", "product management", "program management", "change management"],
    "Business Analysis": ["business analysis", "business analyst", "requirement gathering"],
    "Sales & Business Development": ["sales", "business development", "b2b", "b2c", "telesales", "inside sales", "field sales", "lead generation", "corporate sales", "cross selling", "client acquisition", "revenue generation"],
    "Marketing & SEO": ["marketing", "digital marketing", "seo", "on page seo", "google webmaster tools", "social media", "campaign", "content writing"],
    "Customer Support / BPO": ["customer service", "customer support", "bpo", "voice process", "ites", "international voice", "customer care", "inbound", "outbound", "technical support", "chat process"],
    "Human Resources (HR) & Recruitment": ["hr", "human resources", "recruitment", "talent acquisition", "hiring", "screening", "employee engagement", "payroll"],
    "Finance & Accounting": ["finance", "accounting", "accounts", "taxation", "gst", "accounts payable", "accounts receivable", "financial reporting", "auditing", "balance sheet", "tally", "reconciliation"],
    "Supply Chain & Logistics": ["supply chain", "logistics", "procurement", "vendor management", "inventory management", "purchase"],
    "Industrial & Manufacturing": ["plc", "scada", "cnc", "manufacturing", "autocad", "cad", "quality control", "engineering design", "production"],
    "Soft Skills (Communication/Leadership)": ["communication skills", "english", "leadership", "team management", "problem solving", "negotiation", "presentation skills", "interpersonal skills", "handling", "coordination"]
}

# Invert rules
rule_map = {}
for category, keywords in canonical_dict.items():
    for kw in keywords:
        rule_map[kw.lower()] = category

# Flatten canonical list
canonical_categories = list(canonical_dict.keys())

print("Loading SentenceTransformer...")
st_model = SentenceTransformer('all-MiniLM-L6-v2')
canonical_embs = st_model.encode(canonical_categories)

print("Applying rules and embeddings...")
start_time = time.time()
raw_to_canonical = {}
uncategorized = []

# Process in batches for ST
batch_size = 1000
for i in range(0, len(raw_skills), batch_size):
    batch = raw_skills[i:i+batch_size]
    
    # 1. Rule-based
    batch_unmapped = []
    for s in batch:
        matches = set()
        s_lower = s.lower()
        # Direct exact match or partial match of tokens
        for kw, cat in rule_map.items():
            if kw == s_lower or kw in s_lower.split() or kw in s_lower:
                # To prevent over-matching (e.g. "a" in "apple"), only match if bounded by word boundaries or is exact
                # For safety, let's use exact match or word-boundary substring
                if re.search(r'\b' + re.escape(kw) + r'\b', s_lower):
                    matches.add(cat)
        if matches:
            raw_to_canonical[s] = list(matches)
        else:
            batch_unmapped.append(s)
            
    # 2. Embedding fallback
    if batch_unmapped:
        unmapped_embs = st_model.encode(batch_unmapped)
        sim_matrix = cosine_similarity(unmapped_embs, canonical_embs)
        
        for j, s in enumerate(batch_unmapped):
            max_sim = np.max(sim_matrix[j])
            if max_sim > 0.70: # Confidence threshold
                best_idx = np.argmax(sim_matrix[j])
                raw_to_canonical[s] = [canonical_categories[best_idx]]
            else:
                uncategorized.append(s)

print(f"Time taken: {time.time() - start_time:.2f}s")

# Save mapping dictionary
with open('data/skill_normalization_map.json', 'w') as f:
    json.dump(raw_to_canonical, f)

print("Applying to dataset...")
def apply_canonical(slist_str):
    try:
        skills = ast.literal_eval(slist_str)
    except:
        return []
    if not isinstance(skills, list):
        return []
        
    mapped = set()
    for s in skills:
        if s in raw_to_canonical:
            for c in raw_to_canonical[s]:
                mapped.add(c)
    return list(mapped)

df['canonical_skills_list'] = df['skills_list'].apply(apply_canonical)
df['skills_str'] = df['canonical_skills_list'].apply(lambda x: " ".join([re.sub(r'[^a-zA-Z0-9]', '', s.lower()) for s in x]))

# Drop empty ones
df = df[df['canonical_skills_list'].map(len) > 0]
df.to_csv('data/naukri_features.csv', index=False)

# Re-calculate skill_demand_scores using canonical
all_canonical_skills = []
for clist in df['canonical_skills_list']:
    all_canonical_skills.extend(clist)
    
demand_df = pd.DataFrame({'skill': all_canonical_skills})
skill_counts = demand_df['skill'].value_counts().reset_index()
skill_counts.columns = ['skill', 'demand_count']
skill_counts['skill_demand_score'] = skill_counts['demand_count'] / skill_counts['demand_count'].max()
skill_counts.to_csv('data/skill_demand_scores.csv', index=False)

print("\n=== OUTPUT FOR REVIEW ===")
print(f"Total raw unique skills before: {len(raw_skills)}")
print(f"Total canonical categories: {len(canonical_categories)}")
print(f"Number of skills mapped by Rules/Embeddings: {len(raw_to_canonical)}")
print(f"Number of skills Uncategorized (dropped): {len(uncategorized)}")

print("\n--- 40 Random Mappings ---")
import random
mapped_keys = list(raw_to_canonical.keys())
for s in random.sample(mapped_keys, min(40, len(mapped_keys))):
    print(f"RAW: '{s}' -> CANONICAL: {raw_to_canonical[s]}")

print("\n--- 30 Random Uncategorized ---")
for s in random.sample(uncategorized, min(30, len(uncategorized))):
    print(s)
