import pandas as pd
import numpy as np
import pickle
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.metrics import accuracy_score, f1_score
from sentence_transformers import SentenceTransformer

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

def create_dataset(naukri, state_features, st_dict):
    # Positive samples: actual jobs
    pos = naukri[['experience_num', 'state', 'skills_str']].copy()
    pos = pos.dropna()
    pos['label'] = 1
    
    # Negative samples: shuffle skills and states to create mismatch
    neg = pos.copy()
    neg['skills_str'] = np.random.permutation(neg['skills_str'].values)
    neg['experience_num'] = np.clip(neg['experience_num'] - 3, 0, None)
    neg['label'] = 0
    
    df = pd.concat([pos, neg], ignore_index=True)
    df = df.merge(state_features[['state', 'UR']], on='state', how='left')
    df['UR'] = df['UR'].fillna(df['UR'].mean())
    
    X = []
    Y = df['label'].values
    
    zero_emb = np.zeros(384)
    for i, row in df.iterrows():
        exp = row['experience_num']
        ur = row['UR']
        skill_emb = st_dict.get(row['skills_str'], zero_emb)
        features = np.hstack(([exp, ur], skill_emb))
        X.append(features)
        
    return np.array(X), Y

def main():
    print("="*50)
    print("PHASE 5: PREDICTIVE MODELING (RETRAINING)")
    print("="*50)
    
    # OLD ACCURACY CONSTANTS
    OLD_ACCURACY = 0.7354
    OLD_F1 = 0.7695
    
    naukri = pd.read_csv('data/naukri_features.csv')
    state_features = pd.read_csv('data/merged_state_features.csv')
    with open('models/sentence_embeddings_dict.pkl', 'rb') as f:
        st_dict = pickle.load(f)
        
    print("Creating dataset (this may take a moment)...")
    X, Y = create_dataset(naukri, state_features, st_dict)
    
    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=42)
    print(f"Train size: {len(X_train)} | Test size: {len(X_test)}")
    
    # 1. Classical Model (Random Forest with RandomizedSearchCV)
    print("\nRetuning Random Forest (RandomizedSearchCV)...")
    rf_base = RandomForestClassifier(random_state=42, n_jobs=-1)
    
    param_dist = {
        'n_estimators': [50, 100, 150],
        'max_depth': [None, 10, 20],
        'min_samples_split': [2, 5]
    }
    
    rf_random = RandomizedSearchCV(estimator=rf_base, param_distributions=param_dist, 
                                   n_iter=5, cv=3, random_state=42, n_jobs=-1)
    rf_random.fit(X_train, y_train)
    rf = rf_random.best_estimator_
    
    rf_preds = rf.predict(X_test)
    rf_acc = accuracy_score(y_test, rf_preds)
    rf_f1 = f1_score(y_test, rf_preds)
    print(f"Random Forest (Tuned) - Accuracy: {rf_acc:.4f} | F1: {rf_f1:.4f}")
    print(f"Best Params: {rf_random.best_params_}")
    
    # 2. Deep Learning Model (PyTorch MLP)
    print("\nRetraining PyTorch MLP...")
    input_dim = X_train.shape[1]
    mlp = EmployabilityMLP(input_dim)
    criterion = nn.BCELoss()
    optimizer = optim.Adam(mlp.parameters(), lr=0.001)
    
    X_train_t = torch.FloatTensor(X_train)
    y_train_t = torch.FloatTensor(y_train).unsqueeze(1)
    X_test_t = torch.FloatTensor(X_test)
    
    epochs = 10
    batch_size = 128
    for epoch in range(epochs):
        mlp.train()
        permutation = torch.randperm(X_train_t.size()[0])
        for i in range(0, X_train_t.size()[0], batch_size):
            indices = permutation[i:i+batch_size]
            batch_x, batch_y = X_train_t[indices], y_train_t[indices]
            
            optimizer.zero_grad()
            outputs = mlp(batch_x)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            
    mlp.eval()
    with torch.no_grad():
        mlp_preds = (mlp(X_test_t).numpy() > 0.5).astype(int)
    mlp_acc = accuracy_score(y_test, mlp_preds)
    mlp_f1 = f1_score(y_test, mlp_preds)
    print(f"MLP - Accuracy: {mlp_acc:.4f} | F1: {mlp_f1:.4f}")
    
    # Select best model
    if rf_f1 > mlp_f1:
        print(f"\n=> Random Forest wins on new dataset.")
        best_model = rf
        new_acc = rf_acc
        with open('models/best_predictive_model.pkl', 'wb') as f:
            pickle.dump({'model': rf, 'type': 'rf', 'accuracy': rf_acc, 'f1': rf_f1}, f)
    else:
        print(f"\n=> PyTorch MLP wins on new dataset.")
        best_model = mlp
        new_acc = mlp_acc
        torch.save(mlp.state_dict(), 'models/best_predictive_model.pth')
        with open('models/best_predictive_model.pkl', 'wb') as f:
            pickle.dump({'input_dim': input_dim, 'type': 'mlp', 'accuracy': mlp_acc, 'f1': mlp_f1}, f)
            
    print("\n--- PERFORMANCE COMPARISON ---")
    print(f"OLD MODEL (22K rows) -> Accuracy: {OLD_ACCURACY*100:.1f}%")
    print(f"NEW MODEL (~120K rows) -> Accuracy: {new_acc*100:.1f}%")
    print("="*50)

if __name__ == "__main__":
    main()
