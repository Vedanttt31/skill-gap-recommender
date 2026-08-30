import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pickle

def main():
    print("="*50)
    print("PHASE 3: STATE CLUSTERING (SKILL-GAP ARCHETYPES)")
    print("="*50)
    
    # Load state features
    try:
        df = pd.read_csv('data/merged_state_features.csv')
    except Exception as e:
        print(f"Error loading data: {e}")
        return
    
    features = ['UR', 'WPR', 'LFPR', 'job_count']
    
    # We only cluster states that have full data for these features
    df_cluster = df.dropna(subset=features).copy()
    
    print(f"Clustering {len(df_cluster)} states based on {features}...")
    
    X = df_cluster[features]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Fit KMeans (Let's use 4 clusters)
    k = 4
    kmeans = KMeans(n_clusters=k, random_state=42)
    df_cluster['Cluster'] = kmeans.fit_predict(X_scaled)
    
    # Save the model and scaler
    with open('models/kmeans_model.pkl', 'wb') as f:
        pickle.dump({'kmeans': kmeans, 'scaler': scaler}, f)
        
    print("\n--- Cluster Interpretations ---")
    
    # Calculate means of each feature per cluster to interpret them
    cluster_means = df_cluster.groupby('Cluster')[features].mean()
    
    for cluster_idx in range(k):
        c_data = cluster_means.loc[cluster_idx]
        states_in_cluster = df_cluster[df_cluster['Cluster'] == cluster_idx]['state'].tolist()
        
        # Simple heuristic interpretations
        ur = c_data['UR']
        job = c_data['job_count']
        
        if ur > df_cluster['UR'].mean() and job < df_cluster['job_count'].mean():
            archetype = "High Unemployment, Low Job Demand (Severe Skill Gap)"
        elif ur > df_cluster['UR'].mean() and job > df_cluster['job_count'].mean():
            archetype = "High Unemployment, High Job Demand (Mismatched Skills)"
        elif ur < df_cluster['UR'].mean() and job > df_cluster['job_count'].mean():
            archetype = "Low Unemployment, High Job Demand (Healthy / High Opportunity)"
        else:
            archetype = "Low Unemployment, Low Job Demand (Stagnant / Saturated)"
            
        print(f"\nCluster {cluster_idx}: {archetype}")
        print(f"Average UR: {ur:.2f} | Avg WPR: {c_data['WPR']:.2f} | Avg LFPR: {c_data['LFPR']:.2f} | Avg Job Count: {job:.0f}")
        print(f"States: {', '.join(states_in_cluster)}")
        
        # Save interpretation back to dataframe
        df_cluster.loc[df_cluster['Cluster'] == cluster_idx, 'Archetype'] = archetype

    # Save updated state features
    df_cluster.to_csv('data/merged_state_features.csv', index=False)
    
    print("\nModel saved to 'models/kmeans_model.pkl'")
    print("="*50)

if __name__ == "__main__":
    main()
