"""
Flask API for Customer Churn Prediction
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib
import json
import os
import sys


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_DIR = os.path.join(BASE_DIR, 'saved_models')
FRONTEND_DIR = os.path.join(BASE_DIR, '..', 'Frontend')


# ============================================================
# FLASK APP
# ============================================================

app = Flask(
    __name__,
    static_folder=FRONTEND_DIR,
    static_url_path=''
)

CORS(app)


# ============================================================
# GLOBAL MODEL ARTIFACTS
# ============================================================

model = None
scaler = None
label_encoders = None
feature_names = None
model_results = None


# ============================================================
# LOAD MODEL ARTIFACTS
# ============================================================

def load_artifacts():
    """Load all saved model artifacts."""

    global model
    global scaler
    global label_encoders
    global feature_names
    global model_results

    try:

        model = joblib.load(
            os.path.join(
                MODEL_DIR,
                'best_model.pkl'
            )
        )

        scaler = joblib.load(
            os.path.join(
                MODEL_DIR,
                'scaler.pkl'
            )
        )

        label_encoders = joblib.load(
            os.path.join(
                MODEL_DIR,
                'label_encoders.pkl'
            )
        )

        with open(
            os.path.join(
                MODEL_DIR,
                'feature_names.json'
            ),
            'r'
        ) as f:

            feature_names = json.load(f)

        with open(
            os.path.join(
                MODEL_DIR,
                'model_results.json'
            ),
            'r'
        ) as f:

            model_results = json.load(f)

        print("✓ All model artifacts loaded successfully!")

        return True

    except Exception as e:

        print(f"✗ Error loading artifacts: {e}")

        return False


# ============================================================
# LOAD ARTIFACTS FOR API
# ============================================================

# Load the trained model when the application starts.
#
# IMPORTANT:
# We do NOT import churn_model.py here.
# churn_model.py contains training-only dependencies such as
# SHAP and imbalanced-learn, which are not needed by production.
#
# This keeps the Vercel deployment lightweight.
load_artifacts()


# ============================================================
# FEATURE ENGINEERING
# ============================================================

def engineer_features(data):
    """Apply the same feature engineering as training."""

    df = data.copy()

    df['charge_per_tenure'] = (
        df['monthly_charges'] /
        (df['tenure_months'] + 1)
    )

    df['total_charge_ratio'] = (
        df['total_charges'] /
        (
            df['monthly_charges'] *
            df['tenure_months'] +
            1
        )
    )

    df['support_per_tenure'] = (
        df['num_support_tickets'] /
        (df['tenure_months'] + 1)
    )

    df['engagement_score'] = (
        df['login_frequency_monthly'] * 0.3 +
        df['avg_session_duration_min'] * 0.3 +
        df['feature_usage_rate'] * 0.4
    )

    tenure = df['tenure_months'].iloc[0]

    if tenure <= 6:

        tenure_group = '0-6m'

    elif tenure <= 12:

        tenure_group = '6-12m'

    elif tenure <= 24:

        tenure_group = '1-2y'

    elif tenure <= 48:

        tenure_group = '2-4y'

    else:

        tenure_group = '4y+'

    df['tenure_group'] = tenure_group

    df['clv_proxy'] = (
        df['monthly_charges'] *
        df['tenure_months'] *
        (
            1 -
            df['discount_pct'] /
            100
        )
    )

    df['satisfaction_nps_ratio'] = (
        df['satisfaction_score'] /
        (df['nps_score'] + 1)
    )

    df['inactivity_score'] = (
        df['days_since_last_interaction'] /
        (
            df['login_frequency_monthly'] +
            1
        )
    )

    df['payment_risk'] = (
        df['payment_delays'] *
        df['monthly_charges'] /
        100
    )

    df['loyalty_score'] = (
        df['tenure_months'] * 0.3 +
        df['referral_count'] * 10 +
        df['num_products'] * 5 -
        df['payment_delays'] * 8
    )

    return df


# ============================================================
# FRONTEND
# ============================================================

@app.route('/')
def serve_frontend():
    """Serve the frontend application."""

    return send_from_directory(
        app.static_folder,
        'index.html'
    )


# ============================================================
# PREDICTION
# ============================================================

@app.route('/api/predict', methods=['POST'])
def predict():
    """Make churn prediction for a customer."""

    try:

        if model is None:
            return jsonify({
                'success': False,
                'error': 'Model artifacts are not loaded.'
            }), 500

        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({
                'success': False,
                'error': 'Request body must be a JSON object.'
            }), 400

        input_data = pd.DataFrame([{

            'age': int(
                data.get(
                    'age',
                    35
                )
            ),

            'gender': data.get(
                'gender',
                'Male'
            ),

            'tenure_months': int(
                data.get(
                    'tenure_months',
                    12
                )
            ),

            'contract_type': data.get(
                'contract_type',
                'Month-to-Month'
            ),

            'monthly_charges': float(
                data.get(
                    'monthly_charges',
                    65
                )
            ),

            'total_charges': float(
                data.get(
                    'total_charges',
                    780
                )
            ),

            'num_products': int(
                data.get(
                    'num_products',
                    2
                )
            ),

            'num_support_tickets': int(
                data.get(
                    'num_support_tickets',
                    1
                )
            ),

            'days_since_last_interaction': int(
                data.get(
                    'days_since_last_interaction',
                    15
                )
            ),

            'avg_session_duration_min': float(
                data.get(
                    'avg_session_duration_min',
                    20
                )
            ),

            'login_frequency_monthly': int(
                data.get(
                    'login_frequency_monthly',
                    10
                )
            ),

            'feature_usage_rate': float(
                data.get(
                    'feature_usage_rate',
                    45
                )
            ),

            'payment_method': data.get(
                'payment_method',
                'Credit Card'
            ),

            'payment_delays': int(
                data.get(
                    'payment_delays',
                    0
                )
            ),

            'satisfaction_score': float(
                data.get(
                    'satisfaction_score',
                    3.5
                )
            ),

            'nps_score': int(
                data.get(
                    'nps_score',
                    7
                )
            ),

            'has_partner': int(
                data.get(
                    'has_partner',
                    1
                )
            ),

            'has_dependents': int(
                data.get(
                    'has_dependents',
                    0
                )
            ),

            'referral_count': int(
                data.get(
                    'referral_count',
                    0
                )
            ),

            'discount_pct': float(
                data.get(
                    'discount_pct',
                    5
                )
            )

        }])

        # ----------------------------------------------------
        # Feature engineering
        # ----------------------------------------------------

        input_data = engineer_features(
            input_data
        )

        # ----------------------------------------------------
        # Encode categorical features
        # ----------------------------------------------------

        cat_features = [
            'gender',
            'contract_type',
            'payment_method',
            'tenure_group'
        ]

        for col in cat_features:

            if col in label_encoders:

                try:

                    input_data[col] = (
                        label_encoders[col]
                        .transform(
                            input_data[col]
                        )
                    )

                except ValueError:

                    # Unknown categorical value.
                    # Preserve existing production behavior.
                    input_data[col] = 0

        # ----------------------------------------------------
        # Select and order features
        # ----------------------------------------------------

        X = input_data[
            feature_names
        ].copy()

        X.replace(
            [np.inf, -np.inf],
            0,
            inplace=True
        )

        X.fillna(
            0,
            inplace=True
        )

        # ----------------------------------------------------
        # Scale
        # ----------------------------------------------------

        X_scaled = pd.DataFrame(
            scaler.transform(X),
            columns=feature_names
        )

        # ----------------------------------------------------
        # Prediction
        # ----------------------------------------------------

        churn_probability = float(
            model.predict_proba(
                X_scaled
            )[0][1]
        )

        churn_prediction = int(
            churn_probability >= 0.5
        )

        # ----------------------------------------------------
        # Risk level
        # ----------------------------------------------------

        if churn_probability < 0.3:

            risk_level = 'Low'
            risk_color = '#00e676'

        elif churn_probability < 0.6:

            risk_level = 'Medium'
            risk_color = '#ffab00'

        elif churn_probability < 0.8:

            risk_level = 'High'
            risk_color = '#ff6d00'

        else:

            risk_level = 'Critical'
            risk_color = '#ff1744'

        # ----------------------------------------------------
        # Recommendations
        # ----------------------------------------------------

        recommendations = generate_recommendations(
            data,
            churn_probability
        )

        # ----------------------------------------------------
        # Risk factors
        # ----------------------------------------------------

        risk_factors = get_risk_factors(
            data
        )

        # ----------------------------------------------------
        # Response
        # ----------------------------------------------------

        return jsonify({

            'success': True,

            'prediction': {

                'churn_probability': round(
                    churn_probability,
                    4
                ),

                'churn_prediction':
                    churn_prediction,

                'risk_level':
                    risk_level,

                'risk_color':
                    risk_color,

                'confidence': round(
                    abs(
                        churn_probability -
                        0.5
                    ) * 2,
                    4
                )

            },

            'recommendations':
                recommendations,

            'risk_factors':
                risk_factors

        })

    except Exception as e:

        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================
# RECOMMENDATIONS
# ============================================================

def generate_recommendations(
    data,
    churn_prob
):
    """Generate actionable recommendations."""

    recs = []

    if data.get(
        'contract_type'
    ) == 'Month-to-Month':

        recs.append({
            'icon': '📋',
            'priority': 'High',
            'action':
                'Offer annual contract with 15-20% discount to increase retention'
        })

    if float(
        data.get(
            'satisfaction_score',
            5
        )
    ) < 3:

        recs.append({
            'icon': '😊',
            'priority': 'Critical',
            'action':
                'Immediate personal outreach - satisfaction critically low'
        })

    if int(
        data.get(
            'num_support_tickets',
            0
        )
    ) > 3:

        recs.append({
            'icon': '🎧',
            'priority': 'High',
            'action':
                'Assign dedicated support manager - high ticket volume indicates issues'
        })

    if int(
        data.get(
            'days_since_last_interaction',
            0
        )
    ) > 30:

        recs.append({
            'icon': '📧',
            'priority': 'Medium',
            'action':
                'Re-engagement campaign - customer has been inactive'
        })

    if float(
        data.get(
            'feature_usage_rate',
            100
        )
    ) < 30:

        recs.append({
            'icon': '📚',
            'priority': 'Medium',
            'action':
                'Provide onboarding session and feature tutorials'
        })

    if int(
        data.get(
            'payment_delays',
            0
        )
    ) > 2:

        recs.append({
            'icon': '💳',
            'priority': 'High',
            'action':
                'Offer flexible payment plans to reduce payment friction'
        })

    if int(
        data.get(
            'num_products',
            0
        )
    ) <= 1:

        recs.append({
            'icon': '📦',
            'priority': 'Medium',
            'action':
                'Cross-sell complementary products to increase switching costs'
        })

    if churn_prob > 0.7:

        recs.append({
            'icon': '🎁',
            'priority': 'Critical',
            'action':
                'Offer loyalty reward or special retention package immediately'
        })

    if int(
        data.get(
            'referral_count',
            0
        )
    ) == 0:

        recs.append({
            'icon': '🤝',
            'priority': 'Low',
            'action':
                'Introduce referral program with incentives'
        })

    return recs[:6]


# ============================================================
# RISK FACTORS
# ============================================================

def get_risk_factors(data):
    """Identify key risk factors."""

    factors = []

    risk_checks = [

        (
            'contract_type',
            lambda v:
                v == 'Month-to-Month',
            'Month-to-month contract',
            85
        ),

        (
            'tenure_months',
            lambda v:
                int(v) < 12,
            f'Short tenure ({data.get("tenure_months", 0)} months)',
            75
        ),

        (
            'satisfaction_score',
            lambda v:
                float(v) < 3,
            f'Low satisfaction ({data.get("satisfaction_score", 0)})',
            90
        ),

        (
            'num_support_tickets',
            lambda v:
                int(v) > 3,
            f'High support tickets ({data.get("num_support_tickets", 0)})',
            70
        ),

        (
            'payment_delays',
            lambda v:
                int(v) > 1,
            f'Payment delays ({data.get("payment_delays", 0)})',
            65
        ),

        (
            'days_since_last_interaction',
            lambda v:
                int(v) > 45,
            f'Inactive for {data.get("days_since_last_interaction", 0)} days',
            60
        ),

        (
            'feature_usage_rate',
            lambda v:
                float(v) < 25,
            f'Low feature usage ({data.get("feature_usage_rate", 0)}%)',
            55
        ),

        (
            'login_frequency_monthly',
            lambda v:
                int(v) < 5,
            f'Low login frequency ({data.get("login_frequency_monthly", 0)}/month)',
            50
        ),

        (
            'monthly_charges',
            lambda v:
                float(v) > 90,
            f'High monthly charges (${data.get("monthly_charges", 0)})',
            45
        ),

        (
            'nps_score',
            lambda v:
                int(v) < 5,
            f'Low NPS score ({data.get("nps_score", 0)})',
            55
        )

    ]

    for field, check_fn, desc, impact in risk_checks:

        if field in data:

            try:

                if check_fn(
                    data[field]
                ):

                    factors.append({
                        'factor': desc,
                        'impact': impact
                    })

            except (
                ValueError,
                TypeError
            ):

                pass

    factors.sort(
        key=lambda x: x['impact'],
        reverse=True
    )

    return factors[:5]


# ============================================================
# MODEL INFORMATION
# ============================================================

@app.route(
    '/api/model-info',
    methods=['GET']
)
def model_info():
    """Return model information and metrics."""

    try:

        if model_results is None:

            return jsonify({
                'success': False,
                'error':
                    'Model information is not available.'
            }), 500

        return jsonify({

            'success': True,

            'model_name':
                model_results.get(
                    'best_model',
                    'Unknown'
                ),

            'results':
                model_results.get(
                    'results',
                    {}
                ),

            'feature_importance':
                model_results.get(
                    'feature_importance',
                    []
                ),

            'training_date':
                model_results.get(
                    'training_date',
                    ''
                ),

            'num_features':
                model_results.get(
                    'num_features',
                    0
                )

        })

    except Exception as e:

        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================
# BATCH PREDICTION
# ============================================================

@app.route(
    '/api/batch-predict',
    methods=['POST']
)
def batch_predict():
    """Predict churn for multiple customers."""

    try:

        request_data = request.get_json(
            silent=True
        )

        if not isinstance(
            request_data,
            dict
        ):

            return jsonify({
                'success': False,
                'error':
                    'Request body must be a JSON object.'
            }), 400

        customers = request_data.get(
            'customers',
            []
        )

        if not isinstance(
            customers,
            list
        ):

            return jsonify({
                'success': False,
                'error':
                    '"customers" must be a list.'
            }), 400

        results = []

        for customer in customers:

            if not isinstance(
                customer,
                dict
            ):

                continue

            with app.test_request_context(
                json=customer
            ):

                response = predict()

                if isinstance(
                    response,
                    tuple
                ):

                    response_object = response[0]

                else:

                    response_object = response

                result_data = (
                    response_object.get_json()
                )

                results.append({

                    'customer_id':
                        customer.get(
                            'customer_id',
                            'N/A'
                        ),

                    **result_data.get(
                        'prediction',
                        {}
                    )

                })

        return jsonify({

            'success': True,

            'results': results

        })

    except Exception as e:

        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================
# DASHBOARD STATISTICS
# ============================================================

@app.route(
    '/api/dashboard-stats',
    methods=['GET']
)
def dashboard_stats():
    """Return dashboard statistics."""

    try:

        if model_results is None:

            return jsonify({
                'success': False,
                'error':
                    'Model information is not available.'
            }), 500

        stats = {

            'total_models_trained':
                len(
                    model_results.get(
                        'results',
                        {}
                    )
                ),

            'best_model':
                model_results.get(
                    'best_model',
                    'Unknown'
                ),

            'best_auc': 0,

            'best_f1': 0,

            'models_comparison': []

        }

        for name, metrics in model_results.get(
            'results',
            {}
        ).items():

            stats['models_comparison'].append({

                'name':
                    name,

                'accuracy':
                    metrics.get(
                        'accuracy',
                        0
                    ),

                'precision':
                    metrics.get(
                        'precision',
                        0
                    ),

                'recall':
                    metrics.get(
                        'recall',
                        0
                    ),

                'f1':
                    metrics.get(
                        'f1',
                        0
                    ),

                'roc_auc':
                    metrics.get(
                        'roc_auc',
                        0
                    )

            })

            if name == model_results.get(
                'best_model'
            ):

                stats['best_auc'] = metrics.get(
                    'roc_auc',
                    0
                )

                stats['best_f1'] = metrics.get(
                    'f1',
                    0
                )

        return jsonify({

            'success': True,

            'stats': stats

        })

    except Exception as e:

        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================
# LOCAL DEVELOPMENT / TRAINING
# ============================================================

if __name__ == '__main__':

    # --------------------------------------------------------
    # Check if trained model exists
    # --------------------------------------------------------

    if not os.path.exists(
        os.path.join(
            MODEL_DIR,
            'best_model.pkl'
        )
    ):

        print(
            "\n⚠ No trained model found. "
            "Running training pipeline..."
        )

        # ----------------------------------------------------
        # Generate data if needed
        # ----------------------------------------------------

        data_file = os.path.join(
            BASE_DIR,
            'data',
            'customer_churn_data.csv'
        )

        if not os.path.exists(
            data_file
        ):

            print(
                "Generating synthetic data..."
            )

            from generate_data import (
                generate_churn_data
            )

            generate_churn_data(
                n_samples=10000
            )

        # ----------------------------------------------------
        # Import training pipeline ONLY when running locally
        # ----------------------------------------------------

        from churn_model import (
            ChurnModelPipeline
        )

        pipeline = ChurnModelPipeline(
            data_file
        )

        pipeline.run_full_pipeline()

        # ----------------------------------------------------
        # Reload newly created artifacts
        # ----------------------------------------------------

        if not load_artifacts():

            print(
                "Failed to load newly trained model artifacts."
            )

            sys.exit(1)

    # --------------------------------------------------------
    # Start Flask server
    # --------------------------------------------------------

    print(
        "\n🚀 Starting Flask API server..."
    )

    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000
    )