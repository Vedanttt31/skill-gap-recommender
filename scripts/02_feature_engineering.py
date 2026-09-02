import pandas as pd
import numpy as np
import re
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
from sentence_transformers import SentenceTransformer

from collections import defaultdict

def is_valid_skill(s):
    # Age patterns
    if re.search(r'\d+\+?\s*(yrs?|years?)?\s*age', s) or re.search(r'age\s*\d+', s):
        return False
    # Salary patterns
    if re.search(r'\d+.*(lpa|lacs|lakh|ctc|per annum|p\.a\.|₹|rs\.?|rupees)', s):
        return False
    # Shift / Availability
    if re.search(r'(24/7|24x7|night shift|day shift|rotational shift|work from home|wfh)', s):
        return False
    # Experience / Duration
    if re.search(r'\d+[\-\s]?\d*\s*(yrs?|years?)\s*(of\s*)?.*experience', s):
        return False
    if re.search(r'(year|yrs?)\s+(of\s+)?experience|years?\s+in|yrs?\s+in|banking experience', s):
        return False
    # Purely numeric codes
    if re.match(r'^\d+$', s):
        return False
    if re.match(r'^[\d\s&]+$', s):
        return False
    if re.match(r'^(1040s?|1065|1099.*)$', s):
        return False
    # Vague generic terms
    vague_terms = {'agreement', 'agreement for sale', 'required', 'preferred', 'must have', 'mandatory'}
    if s in vague_terms:
        return False
    # Previous rules
    if '#' in s:
        return False
    if re.match(r'^[-.*]|^[0-9]+[.)]', s):
        return False
    if len(s.split()) > 6:
        return False
    edu_patterns = {'10th', '12th', '10th pass', '12th pass', 'graduate', 'post graduate', 'undergraduate', '10+2'}
    if s in edu_patterns:
        return False
    return True

def clean_skill_string(s):
    s = s.strip()
    s = re.sub(r'(preferred|required|must have|mandatory)\.?$', '', s).strip()
    s = s.rstrip('.')
    return s.strip()

# We need to process the dataframe directly to build the canonical map
def process_skills(df):
    canonical_map = defaultdict(list)
    
    # 1. First pass filtering and normalization mapping
    for skill_str in df['skills'].dropna():
        skills = str(skill_str).lower().split(',')
        for s in skills:
            s = clean_skill_string(s)
            if not s: continue
            
            s = re.sub(r'(ms excel|microsoft excel)', 'excel', s)
            s = re.sub(r'(ms office|microsoft office)', 'office', s)
            s = re.sub(r'(machine learning)', 'ml', s)
            s = re.sub(r'(artificial intelligence)', 'ai', s)
            s = re.sub(r'(amazon web services)', 'aws', s)
            s = re.sub(r'(google cloud platform)', 'gcp', s)
            
            if len(s) > 1 and is_valid_skill(s):
                key = re.sub(r'[^a-z0-9\s]', '', s)
                key = re.sub(r'\s+', ' ', key).strip()
                canonical_map[key].append(s)
                
    best_phrasing = {}
    for key, variants in canonical_map.items():
        if not key: continue
        counts = pd.Series(variants).value_counts()
        best_phrasing[key] = counts.index[0]
        
    def apply_clean(skill_str):
        if pd.isna(skill_str): return []
        skills = str(skill_str).lower().split(',')
        res = []
        for s in skills:
            s = clean_skill_string(s)
            if not s: continue
            s = re.sub(r'(ms excel|microsoft excel)', 'excel', s)
            s = re.sub(r'(ms office|microsoft office)', 'office', s)
            s = re.sub(r'(machine learning)', 'ml', s)
            s = re.sub(r'(artificial intelligence)', 'ai', s)
            s = re.sub(r'(amazon web services)', 'aws', s)
            s = re.sub(r'(google cloud platform)', 'gcp', s)
            if len(s) > 1 and is_valid_skill(s):
                key = re.sub(r'[^a-z0-9\s]', '', s)
                key = re.sub(r'\s+', ' ', key).strip()
                if key in best_phrasing:
                    res.append(best_phrasing[key])
        return list(set(res)) # return unique
        
    df['skills_list'] = df['skills'].apply(apply_clean)
    return df

# We override the main function call to use process_skills

def encode_experience(exp_str):
    if pd.isna(exp_str):
        return np.nan
    try:
        nums = re.findall(r'\d+', str(exp_str))
        if not nums:
            return np.nan
        nums = [int(n) for n in nums]
        return np.mean(nums)
    except:
        return np.nan

city_to_state = {
    'bengaluru': 'Karnataka',
    'bangalore': 'Karnataka',
    'mumbai': 'Maharashtra',
    'pune': 'Maharashtra',
    'hyderabad': 'Telangana',
    'secunderabad': 'Telangana',
    'chennai': 'Tamil Nadu',
    'noida': 'Uttar Pradesh',
    'ghaziabad': 'Uttar Pradesh',
    'lucknow': 'Uttar Pradesh',
    'delhi': 'Delhi',
    'ncr': 'Delhi',
    'new delhi': 'Delhi',
    'gurgaon': 'Haryana',
    'gurugram': 'Haryana',
    'ahmedabad': 'Gujarat',
    'gandhinagar': 'Gujarat',
    'kolkata': 'West Bengal',
    'kochi': 'Kerala',
    'trivandrum': 'Kerala',
    'thiruvananthapuram': 'Kerala',
    'chandigarh': 'Chandigarh',
    'jaipur': 'Rajasthan',
    'indore': 'Madhya Pradesh',
    'bhopal': 'Madhya Pradesh',
    'bhubaneswar': 'Odisha',
    'patna': 'Bihar',
    # Expanded mappings for 2025 dataset
    'navi mumbai': 'Maharashtra',
    'thane': 'Maharashtra',
    'kanpur': 'Uttar Pradesh',
    'agra': 'Uttar Pradesh',
    'faridabad': 'Haryana',
    'surat': 'Gujarat',
    'vadodara': 'Gujarat',
    'rajkot': 'Gujarat',
    'nagpur': 'Maharashtra',
    'visakhapatnam': 'Andhra Pradesh',
    'vizag': 'Andhra Pradesh',
    'coimbatore': 'Tamil Nadu',
    'madurai': 'Tamil Nadu',
    'mysore': 'Karnataka',
    'mysuru': 'Karnataka',
    'ludhiana': 'Punjab',
    'amritsar': 'Punjab',
    'guwahati': 'Assam',
    'dehradun': 'Uttarakhand',
    'ranchi': 'Jharkhand',
    'raipur': 'Chhattisgarh'
}

def map_to_state(location):
    if pd.isna(location):
        return np.nan
    loc_lower = str(location).lower()
    for city, state in city_to_state.items():
        if city in loc_lower:
            return state
    # Handle pure state names directly if present
    for state in set(city_to_state.values()):
        if state.lower() in loc_lower:
            return state
    return np.nan

def main():
    print("PHASE 2: FEATURE ENGINEERING")

    try:
        naukri = pd.read_csv('data/combined_job_postings.csv')
        plfs = pd.read_csv('data/plfs_merged_2024.csv')
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    # Map Location
    naukri['state'] = naukri['location'].apply(map_to_state)
    match_count = naukri['state'].notna().sum()
    total_count = len(naukri)
    print(f"\nLocation-to-State Match Rate: {match_count/total_count*100:.1f}% ({match_count}/{total_count})")
    
    # Drop rows without state since state is essential for merges
    naukri = naukri.dropna(subset=['state'])

    # Clean and split skills
    naukri = process_skills(naukri)
    naukri['experience_num'] = naukri['experience'].apply(encode_experience)
    
    # Compute mid_salary where possible
    naukri['mid_salary'] = (naukri['min_salary'] + naukri['max_salary']) / 2
    
    # 1. State-level aggregated table
    state_job_counts = naukri.groupby('state').size().reset_index(name='job_count')
    
    def get_top_skills(df, n=5):
        all_skills = [s for sublist in df['skills_list'] for s in sublist]
        if not all_skills:
            return ""
        return ", ".join(pd.Series(all_skills).value_counts().head(n).index)
        
    def get_top_industry(df):
        return df['industry'].value_counts().idxmax() if not df['industry'].dropna().empty else np.nan

    state_aggs = naukri.groupby('state').apply(
        lambda x: pd.Series({
            'top_5_skills': get_top_skills(x),
            'top_industry': get_top_industry(x),
            'average_salary_by_state': x['mid_salary'].mean()
        })
    ).reset_index()

    state_features = plfs.merge(state_job_counts, on='state', how='left')
    state_features = state_features.merge(state_aggs, on='state', how='left')
    state_features['job_count'] = state_features['job_count'].fillna(0)
    
    # 2. Skill-demand frequency table and average salary by skill
    print("\nCalculating skill frequencies and average salaries...")
    skill_stats = []
    
    # Explode skills list to get one row per skill per posting to compute averages
    naukri_exploded = naukri[['skills_list', 'mid_salary', 'state']].explode('skills_list')
    naukri_exploded = naukri_exploded.dropna(subset=['skills_list'])
    
    skill_salary_aggs = naukri_exploded.groupby('skills_list').agg(
        count=('skills_list', 'count'),
        average_salary_by_skill=('mid_salary', 'mean')
    ).reset_index()
    skill_salary_aggs = skill_salary_aggs.rename(columns={'skills_list': 'skill'})
    skill_salary_aggs['pct_of_postings'] = (skill_salary_aggs['count'] / len(naukri)) * 100
    skill_salary_aggs = skill_salary_aggs.sort_values('count', ascending=False)
    
    print("\n--- Top Engineered Skills ---")
    print(skill_salary_aggs.head(10))

    

    # 3. Embeddings/Vectors (TF-IDF and Sentence Transformers)

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
    
    print("Calculating state-level skill demand scores (Canonical)...")
    naukri_exploded = naukri.explode('skills_list').dropna(subset=['skills_list', 'state'])
    state_skill_counts = naukri_exploded.groupby(['state', 'skills_list']).size().reset_index(name='count')
    state_totals = naukri_exploded.groupby('state').size().reset_index(name='state_total')
    skill_demand_df = pd.merge(state_skill_counts, state_totals, on='state')
    skill_demand_df['demand_score'] = skill_demand_df['count'] / skill_demand_df['state_total']
    skill_demand_df = skill_demand_df.rename(columns={'skills_list': 'skill'})
    skill_demand_df.to_csv('data/skill_demand_scores.csv', index=False)

    print("Generating Embeddings...")
    naukri['skills_str'] = naukri['skills_list'].apply(lambda x: ' '.join(x))
    naukri['skills_str'] = naukri['skills_str'].replace('', 'unknown_skill')
    
    # TF-IDF
    tfidf = TfidfVectorizer(max_features=500)
    tfidf_matrix = tfidf.fit_transform(naukri['skills_str'])
    with open('models/tfidf_vectorizer.pkl', 'wb') as f:
        pickle.dump(tfidf, f)
        
    # Sentence Transformers
    print("Loading SentenceTransformer model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    unique_skills_strs = naukri['skills_str'].unique().tolist()
    print(f"Generating embeddings for {len(unique_skills_strs)} unique skill profiles...")
    embeddings = model.encode(unique_skills_strs, show_progress_bar=True)
    skill_str_to_embedding = {s: e for s, e in zip(unique_skills_strs, embeddings)}
    
    with open('models/sentence_embeddings_dict.pkl', 'wb') as f:
        pickle.dump(skill_str_to_embedding, f)

    # Save outputs
    state_features.to_csv('data/merged_state_features.csv', index=False)
    naukri.to_csv('data/naukri_features.csv', index=False)
    
    print("\n--- Plain Language Summary ---")
    print("1. Standardized job skills and mapped 117K locations to states.")
    print("2. Created state-level dataset with new 'average_salary_by_state'.")
    print("3. Extracted numeric experience.")
    print("4. Exploded skills to calculate 'average_salary_by_skill' across non-null salary rows.")
    print("5. Generated semantic vectors using TF-IDF & SentenceTransformers on the larger corpus.")
    print("6. Saved 'merged_state_features.csv' and 'naukri_features.csv'.")

if __name__ == "__main__":
    main()
