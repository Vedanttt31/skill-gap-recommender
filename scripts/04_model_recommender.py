import pandas as pd
import numpy as np
import pickle
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

def get_recommendations_tfidf(user_skills_str, tfidf_matrix, tfidf_vectorizer, df, top_n=5):
    user_vec = tfidf_vectorizer.transform([user_skills_str])
    sim_scores = cosine_similarity(user_vec, tfidf_matrix).flatten()
    top_indices = sim_scores.argsort()[-top_n:][::-1]
    
    results = []
    for idx in top_indices:
        results.append({
            'job_title': df.iloc[idx]['job_title'],
            'skills': df.iloc[idx]['skills_str'],
            'score': sim_scores[idx]
        })
    return results

def get_recommendations_st(user_skills_str, st_model, st_dict, df, top_n=5):
    user_vec = st_model.encode([user_skills_str])
    
    # We precomputed embeddings for unique skill strings. Let's map back to the dataframe.
    # To do this quickly, we can get embeddings for all jobs from the dict.
    job_embeddings = np.array([st_dict.get(s, np.zeros(384)) for s in df['skills_str']])
    
    sim_scores = cosine_similarity(user_vec, job_embeddings).flatten()
    top_indices = sim_scores.argsort()[-top_n:][::-1]
    
    results = []
    for idx in top_indices:
        results.append({
            'job_title': df.iloc[idx]['job_title'],
            'skills': df.iloc[idx]['skills_str'],
            'score': sim_scores[idx]
        })
    return results

def main():
    print("="*50)
    print("PHASE 4: RECOMMENDER SYSTEM COMPARISON")
    print("="*50)
    
    df = pd.read_csv('data/naukri_features.csv')
    df = df.dropna(subset=['skills_str'])
    df = df.reset_index(drop=True)
    
    # Load TF-IDF
    with open('models/tfidf_vectorizer.pkl', 'rb') as f:
        tfidf = pickle.load(f)
    tfidf_matrix = tfidf.transform(df['skills_str'])
    
    # Load Sentence Transformers
    st_model = SentenceTransformer('all-MiniLM-L6-v2')
    with open('models/sentence_embeddings_dict.pkl', 'rb') as f:
        st_dict = pickle.load(f)
        
    # Test User Profile
    test_user_skills = "python sql machine learning pandas"
    # Note: cleaned up for matching
    cleaned_test_user = "python sql ml pandas" 
    
    print(f"\nTest User Skills: '{test_user_skills}' (Cleaned: '{cleaned_test_user}')\n")
    
    print("--- TF-IDF Recommendations ---")
    tfidf_res = get_recommendations_tfidf(cleaned_test_user, tfidf_matrix, tfidf, df)
    for i, r in enumerate(tfidf_res):
        print(f"{i+1}. {r['job_title']} (Score: {r['score']:.3f})")
        print(f"   Skills: {r['skills']}")
        
    print("\n--- Sentence Transformers Recommendations ---")
    st_res = get_recommendations_st(cleaned_test_user, st_model, st_dict, df)
    for i, r in enumerate(st_res):
        print(f"{i+1}. {r['job_title']} (Score: {r['score']:.3f})")
        print(f"   Skills: {r['skills']}")
        
    print("\nConclusion: Sentence Transformers generally captures semantic similarity better")
    print("(e.g., matching 'ml' with 'data science' or 'ai'), whereas TF-IDF is strictly lexical.")
    print("We will proceed with Sentence Transformers as the winning artifact for the app.")
    print("="*50)

if __name__ == "__main__":
    main()
