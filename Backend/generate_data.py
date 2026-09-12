"""
Generate synthetic but realistic customer churn data
with proper feature distributions mimicking telecom/SaaS churn patterns
"""

import pandas as pd
import numpy as np
import os

def generate_churn_data(n_samples=10000, random_state=42):
    np.random.seed(random_state)
    
    # --- Customer Demographics ---
    age = np.random.normal(45, 15, n_samples).clip(18, 85).astype(int)
    gender = np.random.choice(['Male', 'Female'], n_samples, p=[0.48, 0.52])
    
    # --- Account Information ---
    tenure_months = np.random.exponential(30, n_samples).clip(1, 120).astype(int)
    contract_type = np.random.choice(
        ['Month-to-Month', 'One-Year', 'Two-Year'], 
        n_samples, p=[0.50, 0.30, 0.20]
    )
    
    # --- Service Usage ---
    monthly_charges = np.where(
        contract_type == 'Month-to-Month',
        np.random.normal(70, 25, n_samples),
        np.where(
            contract_type == 'One-Year',
            np.random.normal(60, 20, n_samples),
            np.random.normal(50, 15, n_samples)
        )
    ).clip(15, 150).round(2)
    
    total_charges = (monthly_charges * tenure_months * 
                     np.random.uniform(0.85, 1.15, n_samples)).round(2)
    
    # Number of products/services used
    num_products = np.random.poisson(2.5, n_samples).clip(1, 8)
    
    # Support tickets
    num_support_tickets = np.random.poisson(1.5, n_samples).clip(0, 15)
    
    # Days since last interaction
    days_since_last_interaction = np.random.exponential(30, n_samples).clip(0, 365).astype(int)
    
    # --- Engagement Metrics ---
    avg_session_duration_min = np.random.exponential(15, n_samples).clip(0.5, 120).round(1)
    login_frequency_monthly = np.random.poisson(12, n_samples).clip(0, 60)
    
    # Feature usage rate (0-100%)
    feature_usage_rate = np.random.beta(2, 3, n_samples) * 100
    feature_usage_rate = feature_usage_rate.round(1)
    
    # --- Payment ---
    payment_method = np.random.choice(
        ['Credit Card', 'Bank Transfer', 'Electronic Check', 'Mailed Check'],
        n_samples, p=[0.35, 0.25, 0.25, 0.15]
    )
    
    # Payment delays in last 12 months
    payment_delays = np.random.poisson(0.8, n_samples).clip(0, 12)
    
    # --- Satisfaction ---
    satisfaction_score = np.random.normal(3.5, 1.0, n_samples).clip(1, 5).round(1)
    nps_score = np.random.normal(6.5, 2.5, n_samples).clip(0, 10).round(0).astype(int)
    
    # --- Derived Features ---
    has_partner = np.random.choice([0, 1], n_samples, p=[0.45, 0.55])
    has_dependents = np.random.choice([0, 1], n_samples, p=[0.60, 0.40])
    
    # Referral count
    referral_count = np.random.poisson(0.5, n_samples).clip(0, 10)
    
    # Discount applied
    discount_pct = np.where(
        contract_type == 'Two-Year',
        np.random.uniform(10, 30, n_samples),
        np.where(
            contract_type == 'One-Year',
            np.random.uniform(5, 15, n_samples),
            np.random.uniform(0, 5, n_samples)
        )
    ).round(1)
    
    # --- CHURN LABEL (Realistic probability-based) ---
    churn_prob = np.zeros(n_samples)
    
    # Contract type effect
    churn_prob += np.where(contract_type == 'Month-to-Month', 0.25, 
                  np.where(contract_type == 'One-Year', 0.08, 0.03))
    
    # Tenure effect (lower tenure = higher churn)
    churn_prob += np.clip(0.3 - (tenure_months / 120) * 0.3, 0, 0.3)
    
    # Monthly charges effect
    churn_prob += np.clip((monthly_charges - 50) / 400, 0, 0.15)
    
    # Support tickets effect
    churn_prob += np.clip(num_support_tickets * 0.03, 0, 0.2)
    
    # Satisfaction effect
    churn_prob += np.clip((4 - satisfaction_score) * 0.08, -0.1, 0.25)
    
    # Login frequency effect (less engagement = more churn)
    churn_prob += np.clip((10 - login_frequency_monthly) * 0.01, 0, 0.1)
    
    # Payment delays effect
    churn_prob += payment_delays * 0.04
    
    # Days since last interaction effect
    churn_prob += np.clip(days_since_last_interaction / 1000, 0, 0.15)
    
    # Feature usage effect
    churn_prob += np.clip((50 - feature_usage_rate) / 300, 0, 0.15)
    
    # Payment method effect
    churn_prob += np.where(payment_method == 'Electronic Check', 0.05, 0)
    
    # NPS effect
    churn_prob += np.clip((5 - nps_score) * 0.02, -0.05, 0.1)
    
    # Referral effect (people who refer are less likely to churn)
    churn_prob -= referral_count * 0.03
    
    # Products effect (more products = less churn - switching cost)
    churn_prob -= num_products * 0.02
    
    # Clip probabilities
    churn_prob = np.clip(churn_prob, 0.02, 0.95)
    
    # Add noise
    churn_prob += np.random.normal(0, 0.05, n_samples)
    churn_prob = np.clip(churn_prob, 0.01, 0.99)
    
    # Generate churn labels
    churn = (np.random.random(n_samples) < churn_prob).astype(int)
    
    # Build DataFrame
    df = pd.DataFrame({
        'customer_id': [f'CUST_{i:06d}' for i in range(1, n_samples + 1)],
        'age': age,
        'gender': gender,
        'tenure_months': tenure_months,
        'contract_type': contract_type,
        'monthly_charges': monthly_charges,
        'total_charges': total_charges,
        'num_products': num_products,
        'num_support_tickets': num_support_tickets,
        'days_since_last_interaction': days_since_last_interaction,
        'avg_session_duration_min': avg_session_duration_min,
        'login_frequency_monthly': login_frequency_monthly,
        'feature_usage_rate': feature_usage_rate,
        'payment_method': payment_method,
        'payment_delays': payment_delays,
        'satisfaction_score': satisfaction_score,
        'nps_score': nps_score,
        'has_partner': has_partner,
        'has_dependents': has_dependents,
        'referral_count': referral_count,
        'discount_pct': discount_pct,
        'churn': churn
    })
    
    print(f"\n{'='*60}")
    print(f"Dataset Generated Successfully!")
    print(f"{'='*60}")
    print(f"Total samples: {n_samples}")
    print(f"Churn rate: {churn.mean()*100:.1f}%")
    print(f"Features: {len(df.columns) - 2}")  # exclude id and target
    print(f"{'='*60}\n")
    
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/customer_churn_data.csv', index=False)
    
    return df

if __name__ == '__main__':
    df = generate_churn_data(n_samples=10000)
    print(df.head())
    print(f"\nClass distribution:\n{df['churn'].value_counts(normalize=True)}")