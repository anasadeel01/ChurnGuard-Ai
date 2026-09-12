"""
Complete ML Pipeline for Customer Churn Prediction
- Data Preprocessing & Feature Engineering
- Exploratory Data Analysis
- Multiple Model Training (Logistic Regression, Random Forest, XGBoost, LightGBM)
- Hyperparameter Tuning
- Model Evaluation & Comparison
- SHAP Explainability
- Model Persistence
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Preprocessing
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder, RobustScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

# Feature Engineering
from sklearn.preprocessing import PolynomialFeatures

# Imbalanced Data Handling
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline

# Models
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import (
    RandomForestClassifier, 
    GradientBoostingClassifier, 
    VotingClassifier,
    StackingClassifier
)
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

# Evaluation
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report,
    precision_recall_curve, roc_curve, average_precision_score
)

# Explainability
import shap

# Persistence
import joblib
import json
import os
from datetime import datetime


class ChurnModelPipeline:
    """
    Production-grade Customer Churn Prediction Pipeline
    """
    
    def __init__(self, data_path='data/customer_churn_data.csv'):
        self.data_path = data_path
        self.df = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.feature_names = None
        self.preprocessor = None
        self.best_model = None
        self.best_model_name = None
        self.models = {}
        self.results = {}
        self.scaler = None
        self.label_encoders = {}
        self.feature_importance = None
        self.shap_values = None
        
        # Feature categories
        self.numerical_features = [
            'age', 'tenure_months', 'monthly_charges', 'total_charges',
            'num_products', 'num_support_tickets', 'days_since_last_interaction',
            'avg_session_duration_min', 'login_frequency_monthly',
            'feature_usage_rate', 'payment_delays', 'satisfaction_score',
            'nps_score', 'referral_count', 'discount_pct'
        ]
        
        self.categorical_features = [
            'gender', 'contract_type', 'payment_method'
        ]
        
        self.binary_features = ['has_partner', 'has_dependents']
        
    def load_data(self):
        """Step 1: Load and initial inspection"""
        print("\n" + "="*70)
        print("STEP 1: DATA LOADING & INITIAL INSPECTION")
        print("="*70)
        
        self.df = pd.read_csv(self.data_path)
        
        print(f"\nDataset Shape: {self.df.shape}")
        print(f"\nColumn Types:\n{self.df.dtypes}")
        print(f"\nFirst 5 rows:\n{self.df.head()}")
        print(f"\nBasic Statistics:\n{self.df.describe()}")
        print(f"\nMissing Values:\n{self.df.isnull().sum()}")
        print(f"\nTarget Distribution:\n{self.df['churn'].value_counts(normalize=True)}")
        
        return self
    
    def exploratory_analysis(self):
        """Step 2: EDA - Understanding patterns"""
        print("\n" + "="*70)
        print("STEP 2: EXPLORATORY DATA ANALYSIS")
        print("="*70)
        
        # Churn rate analysis
        print("\n--- Churn Rate by Contract Type ---")
        print(self.df.groupby('contract_type')['churn'].mean().round(3))
        
        print("\n--- Churn Rate by Payment Method ---")
        print(self.df.groupby('payment_method')['churn'].mean().round(3))
        
        print("\n--- Average Feature Values by Churn Status ---")
        churn_comparison = self.df.groupby('churn')[self.numerical_features].mean().round(2)
        print(churn_comparison.T)
        
        # Correlation analysis
        print("\n--- Top Feature Correlations with Churn ---")
        numeric_df = self.df[self.numerical_features + self.binary_features + ['churn']]
        correlations = numeric_df.corr()['churn'].drop('churn').sort_values(ascending=False)
        print(correlations)
        
        return self
    
    def feature_engineering(self):
        """Step 3: Advanced Feature Engineering"""
        print("\n" + "="*70)
        print("STEP 3: FEATURE ENGINEERING")
        print("="*70)
        
        df = self.df.copy()
        
        # 1. Interaction Features
        df['charge_per_tenure'] = df['monthly_charges'] / (df['tenure_months'] + 1)
        df['total_charge_ratio'] = df['total_charges'] / (df['monthly_charges'] * df['tenure_months'] + 1)
        df['support_per_tenure'] = df['num_support_tickets'] / (df['tenure_months'] + 1)
        df['engagement_score'] = (
            df['login_frequency_monthly'] * 0.3 + 
            df['avg_session_duration_min'] * 0.3 + 
            df['feature_usage_rate'] * 0.4
        )
        
        # 2. Tenure Bins
        df['tenure_group'] = pd.cut(
            df['tenure_months'], 
            bins=[0, 6, 12, 24, 48, 120],
            labels=['0-6m', '6-12m', '1-2y', '2-4y', '4y+']
        ).astype(str)
        
        # 3. CLV Proxy (Customer Lifetime Value)
        df['clv_proxy'] = df['monthly_charges'] * df['tenure_months'] * (1 - df['discount_pct']/100)
        
        # 4. Risk Score Features
        df['satisfaction_nps_ratio'] = df['satisfaction_score'] / (df['nps_score'] + 1)
        df['inactivity_score'] = (
            df['days_since_last_interaction'] / (df['login_frequency_monthly'] + 1)
        )
        
        # 5. Payment Risk
        df['payment_risk'] = df['payment_delays'] * df['monthly_charges'] / 100
        
        # 6. Loyalty Indicators
        df['loyalty_score'] = (
            df['tenure_months'] * 0.3 +
            df['referral_count'] * 10 +
            df['num_products'] * 5 -
            df['payment_delays'] * 8
        )
        
        # Update categorical features
        self.categorical_features.append('tenure_group')
        
        # Update numerical features  
        new_numerical = [
            'charge_per_tenure', 'total_charge_ratio', 'support_per_tenure',
            'engagement_score', 'clv_proxy', 'satisfaction_nps_ratio',
            'inactivity_score', 'payment_risk', 'loyalty_score'
        ]
        self.numerical_features.extend(new_numerical)
        
        self.df = df
        
        print(f"New features created: {len(new_numerical) + 1}")
        print(f"Total features: {len(self.numerical_features) + len(self.categorical_features) + len(self.binary_features)}")
        print(f"New feature names: {new_numerical + ['tenure_group']}")
        
        return self
    
    def preprocess_data(self, test_size=0.2, random_state=42):
        """Step 4: Data Preprocessing"""
        print("\n" + "="*70)
        print("STEP 4: DATA PREPROCESSING")
        print("="*70)
        
        df = self.df.copy()
        
        # Handle missing values
        for col in self.numerical_features:
            if col in df.columns:
                df[col].fillna(df[col].median(), inplace=True)
        
        # Encode categorical features
        for col in self.categorical_features:
            if col in df.columns:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
                self.label_encoders[col] = le
        
        # Prepare features and target
        feature_cols = self.numerical_features + self.categorical_features + self.binary_features
        feature_cols = [c for c in feature_cols if c in df.columns]
        
        X = df[feature_cols].copy()
        y = df['churn'].copy()
        
        self.feature_names = feature_cols
        
        # Replace infinities
        X.replace([np.inf, -np.inf], np.nan, inplace=True)
        X.fillna(X.median(), inplace=True)
        
        # Train-test split with stratification
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        # Scale features
        self.scaler = RobustScaler()
        self.X_train_scaled = pd.DataFrame(
            self.scaler.fit_transform(self.X_train),
            columns=self.feature_names,
            index=self.X_train.index
        )
        self.X_test_scaled = pd.DataFrame(
            self.scaler.transform(self.X_test),
            columns=self.feature_names,
            index=self.X_test.index
        )
        
        # Handle class imbalance with SMOTE
        smote = SMOTE(random_state=random_state, sampling_strategy=0.8)
        self.X_train_resampled, self.y_train_resampled = smote.fit_resample(
            self.X_train_scaled, self.y_train
        )
        
        print(f"\nOriginal training set: {self.X_train.shape}")
        print(f"After SMOTE: {self.X_train_resampled.shape}")
        print(f"Test set: {self.X_test.shape}")
        print(f"Training churn rate (original): {self.y_train.mean():.3f}")
        print(f"Training churn rate (after SMOTE): {self.y_train_resampled.mean():.3f}")
        print(f"Test churn rate: {self.y_test.mean():.3f}")
        print(f"Features used: {len(self.feature_names)}")
        
        return self
    
    def train_models(self):
        """Step 5: Train Multiple Models"""
        print("\n" + "="*70)
        print("STEP 5: MODEL TRAINING")
        print("="*70)
        
        # Define models
        model_configs = {
            'Logistic Regression': LogisticRegression(
                C=1.0, penalty='l2', solver='lbfgs',
                max_iter=1000, random_state=42, class_weight='balanced'
            ),
            'Random Forest': RandomForestClassifier(
                n_estimators=300, max_depth=15, min_samples_split=5,
                min_samples_leaf=2, max_features='sqrt',
                random_state=42, class_weight='balanced', n_jobs=-1
            ),
            'Gradient Boosting': GradientBoostingClassifier(
                n_estimators=200, max_depth=5, learning_rate=0.1,
                subsample=0.8, min_samples_split=10,
                random_state=42
            ),
            'XGBoost': XGBClassifier(
                n_estimators=300, max_depth=6, learning_rate=0.05,
                subsample=0.8, colsample_bytree=0.8,
                min_child_weight=3, gamma=0.1,
                reg_alpha=0.1, reg_lambda=1.0,
                scale_pos_weight=len(self.y_train[self.y_train==0]) / max(len(self.y_train[self.y_train==1]), 1),
                random_state=42, eval_metric='logloss',
                use_label_encoder=False, n_jobs=-1
            ),
            'LightGBM': LGBMClassifier(
                n_estimators=300, max_depth=7, learning_rate=0.05,
                subsample=0.8, colsample_bytree=0.8,
                min_child_samples=20, reg_alpha=0.1, reg_lambda=1.0,
                is_unbalance=True, random_state=42,
                n_jobs=-1, verbose=-1
            )
        }
        
        # Cross-validation setup
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        
        for name, model in model_configs.items():
            print(f"\nTraining {name}...")
            
            # Train
            if name in ['Logistic Regression']:
                model.fit(self.X_train_resampled, self.y_train_resampled)
            else:
                model.fit(self.X_train_scaled, self.y_train)
            
            # Predict
            y_pred = model.predict(self.X_test_scaled)
            y_pred_proba = model.predict_proba(self.X_test_scaled)[:, 1]
            
            # Cross-validation
            if name in ['Logistic Regression']:
                cv_scores = cross_val_score(model, self.X_train_resampled, 
                                          self.y_train_resampled, cv=cv, scoring='roc_auc')
            else:
                cv_scores = cross_val_score(model, self.X_train_scaled, 
                                          self.y_train, cv=cv, scoring='roc_auc')
            
            # Metrics
            metrics = {
                'accuracy': accuracy_score(self.y_test, y_pred),
                'precision': precision_score(self.y_test, y_pred),
                'recall': recall_score(self.y_test, y_pred),
                'f1': f1_score(self.y_test, y_pred),
                'roc_auc': roc_auc_score(self.y_test, y_pred_proba),
                'avg_precision': average_precision_score(self.y_test, y_pred_proba),
                'cv_roc_auc_mean': cv_scores.mean(),
                'cv_roc_auc_std': cv_scores.std(),
                'confusion_matrix': confusion_matrix(self.y_test, y_pred).tolist()
            }
            
            self.models[name] = model
            self.results[name] = metrics
            
            print(f"  Accuracy:  {metrics['accuracy']:.4f}")
            print(f"  Precision: {metrics['precision']:.4f}")
            print(f"  Recall:    {metrics['recall']:.4f}")
            print(f"  F1-Score:  {metrics['f1']:.4f}")
            print(f"  ROC-AUC:   {metrics['roc_auc']:.4f}")
            print(f"  CV AUC:    {metrics['cv_roc_auc_mean']:.4f} ± {metrics['cv_roc_auc_std']:.4f}")
        
        return self
    
    def build_ensemble(self):
        """Step 6: Build Ensemble Model"""
        print("\n" + "="*70)
        print("STEP 6: ENSEMBLE MODEL")
        print("="*70)
        
        # Stacking Ensemble
        estimators = [
            ('rf', self.models['Random Forest']),
            ('xgb', self.models['XGBoost']),
            ('lgbm', self.models['LightGBM'])
        ]
        
        stacking_model = StackingClassifier(
            estimators=estimators,
            final_estimator=LogisticRegression(C=1.0, random_state=42),
            cv=5, n_jobs=-1, passthrough=False
        )
        
        print("Training Stacking Ensemble...")
        stacking_model.fit(self.X_train_scaled, self.y_train)
        
        y_pred = stacking_model.predict(self.X_test_scaled)
        y_pred_proba = stacking_model.predict_proba(self.X_test_scaled)[:, 1]
        
        metrics = {
            'accuracy': accuracy_score(self.y_test, y_pred),
            'precision': precision_score(self.y_test, y_pred),
            'recall': recall_score(self.y_test, y_pred),
            'f1': f1_score(self.y_test, y_pred),
            'roc_auc': roc_auc_score(self.y_test, y_pred_proba),
            'avg_precision': average_precision_score(self.y_test, y_pred_proba),
            'confusion_matrix': confusion_matrix(self.y_test, y_pred).tolist()
        }
        
        self.models['Stacking Ensemble'] = stacking_model
        self.results['Stacking Ensemble'] = metrics
        
        print(f"  Accuracy:  {metrics['accuracy']:.4f}")
        print(f"  Precision: {metrics['precision']:.4f}")
        print(f"  Recall:    {metrics['recall']:.4f}")
        print(f"  F1-Score:  {metrics['f1']:.4f}")
        print(f"  ROC-AUC:   {metrics['roc_auc']:.4f}")
        
        return self
    
    def select_best_model(self):
        """Step 7: Select Best Model"""
        print("\n" + "="*70)
        print("STEP 7: MODEL COMPARISON & SELECTION")
        print("="*70)
        
        print(f"\n{'Model':<25} {'Accuracy':<10} {'Precision':<10} {'Recall':<10} {'F1':<10} {'ROC-AUC':<10}")
        print("-" * 75)
        
        best_auc = 0
        for name, metrics in self.results.items():
            print(f"{name:<25} {metrics['accuracy']:<10.4f} {metrics['precision']:<10.4f} "
                  f"{metrics['recall']:<10.4f} {metrics['f1']:<10.4f} {metrics['roc_auc']:<10.4f}")
            
            # Select based on ROC-AUC (primary) and F1 (secondary)
            composite_score = metrics['roc_auc'] * 0.6 + metrics['f1'] * 0.4
            if composite_score > best_auc:
                best_auc = composite_score
                self.best_model_name = name
                self.best_model = self.models[name]
        
        print(f"\n★ Best Model: {self.best_model_name}")
        print(f"  ROC-AUC: {self.results[self.best_model_name]['roc_auc']:.4f}")
        print(f"  F1-Score: {self.results[self.best_model_name]['f1']:.4f}")
        
        return self
    
    def explain_model(self):
        """Step 8: Model Explainability with SHAP"""
        print("\n" + "="*70)
        print("STEP 8: MODEL EXPLAINABILITY (SHAP)")
        print("="*70)
        
        # Use XGBoost for SHAP (tree-based, fast)
        explain_model = self.models.get('XGBoost', self.best_model)
        
        try:
            explainer = shap.TreeExplainer(explain_model)
            sample_data = self.X_test_scaled.iloc[:200]
            shap_values = explainer.shap_values(sample_data)
            
            # Feature importance from SHAP
            shap_importance = np.abs(shap_values).mean(axis=0)
            importance_df = pd.DataFrame({
                'feature': self.feature_names,
                'shap_importance': shap_importance
            }).sort_values('shap_importance', ascending=False)
            
            print("\n--- SHAP Feature Importance (Top 15) ---")
            print(importance_df.head(15).to_string(index=False))
            
            self.feature_importance = importance_df.to_dict('records')
            self.shap_values = shap_values
            
        except Exception as e:
            print(f"SHAP analysis error: {e}")
            # Fallback to model feature importance
            if hasattr(explain_model, 'feature_importances_'):
                importance_df = pd.DataFrame({
                    'feature': self.feature_names,
                    'importance': explain_model.feature_importances_
                }).sort_values('importance', ascending=False)
                
                print("\n--- Model Feature Importance (Top 15) ---")
                print(importance_df.head(15).to_string(index=False))
                self.feature_importance = importance_df.to_dict('records')
        
        return self
    
    def save_model(self, save_dir='saved_models'):
        """Step 9: Save Model & Artifacts"""
        print("\n" + "="*70)
        print("STEP 9: SAVING MODEL & ARTIFACTS")
        print("="*70)
        
        os.makedirs(save_dir, exist_ok=True)
        
        # Save best model
        model_path = os.path.join(save_dir, 'best_model.pkl')
        joblib.dump(self.best_model, model_path)
        
        # Save scaler
        scaler_path = os.path.join(save_dir, 'scaler.pkl')
        joblib.dump(self.scaler, scaler_path)
        
        # Save label encoders
        le_path = os.path.join(save_dir, 'label_encoders.pkl')
        joblib.dump(self.label_encoders, le_path)
        
        # Save feature names
        features_path = os.path.join(save_dir, 'feature_names.json')
        with open(features_path, 'w') as f:
            json.dump(self.feature_names, f)
        
        # Save results
        serializable_results = {}
        for name, metrics in self.results.items():
            serializable_results[name] = {
                k: float(v) if isinstance(v, (np.float64, np.float32)) else v
                for k, v in metrics.items()
            }
        
        results_path = os.path.join(save_dir, 'model_results.json')
        with open(results_path, 'w') as f:
            json.dump({
                'best_model': self.best_model_name,
                'results': serializable_results,
                'feature_importance': self.feature_importance[:20] if self.feature_importance else [],
                'training_date': datetime.now().isoformat(),
                'num_features': len(self.feature_names),
                'feature_names': self.feature_names,
                'numerical_features': self.numerical_features,
                'categorical_features': self.categorical_features,
                'binary_features': self.binary_features
            }, f, indent=2, default=str)
        
        # Save all models
        all_models_path = os.path.join(save_dir, 'all_models.pkl')
        joblib.dump(self.models, all_models_path)
        
        print(f"✓ Best model saved: {model_path}")
        print(f"✓ Scaler saved: {scaler_path}")
        print(f"✓ Label encoders saved: {le_path}")
        print(f"✓ Results saved: {results_path}")
        print(f"✓ All models saved: {all_models_path}")
        
        return self
    
    def run_full_pipeline(self):
        """Execute the complete pipeline"""
        print("\n" + "★"*70)
        print("   CUSTOMER CHURN PREDICTION - FULL ML PIPELINE")
        print("★"*70)
        
        self.load_data()
        self.exploratory_analysis()
        self.feature_engineering()
        self.preprocess_data()
        self.train_models()
        self.build_ensemble()
        self.select_best_model()
        self.explain_model()
        self.save_model()
        
        print("\n" + "★"*70)
        print("   PIPELINE COMPLETED SUCCESSFULLY!")
        print(f"   Best Model: {self.best_model_name}")
        print(f"   ROC-AUC: {self.results[self.best_model_name]['roc_auc']:.4f}")
        print("★"*70)
        
        return self


if __name__ == '__main__':
    pipeline = ChurnModelPipeline('data/customer_churn_data.csv')
    pipeline.run_full_pipeline()