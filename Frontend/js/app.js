/**
 * ChurnGuard AI - Main Application Logic
 * Handles navigation, API calls, and UI interactions
 */

const API_BASE = 'http://localhost:5000/api';

// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', () => {
    // Loading screen
    setTimeout(() => {
        document.getElementById('loading-screen').classList.add('hidden');
    }, 2000);

    // Initialize navigation
    initNavigation();

    // Initialize sliders
    initSliders();

    // Load dashboard data
    loadDashboardData();

    // Entry animations
    initAnimations();
});

// ==================== NAVIGATION ====================
function initNavigation() {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const section = link.dataset.section;

            // Update active nav
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            link.classList.add('active');

            // Show section
            document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
            document.getElementById(section).classList.add('active');

            // Scroll to top
            window.scrollTo({ top: 0, behavior: 'smooth' });

            // Reinitialize charts for the section
            if (section === 'analytics') {
                setTimeout(() => loadAnalyticsCharts(), 300);
            }
        });
    });
}

// ==================== SLIDERS ====================
function initSliders() {
    const sliders = [
        { id: 'inp-usage', display: 'usage-value', suffix: '%' },
        { id: 'inp-satisfaction', display: 'satisfaction-value', suffix: '' },
        { id: 'inp-nps', display: 'nps-value', suffix: '' },
    ];

    sliders.forEach(({ id, display, suffix }) => {
        const slider = document.getElementById(id);
        const displayEl = document.getElementById(display);

        if (slider && displayEl) {
            slider.addEventListener('input', () => {
                displayEl.textContent = slider.value + suffix;
            });
        }
    });
}

// ==================== DASHBOARD DATA ====================
async function loadDashboardData() {
    try {
        const [statsRes, infoRes] = await Promise.all([
            fetch(`${API_BASE}/dashboard-stats`),
            fetch(`${API_BASE}/model-info`)
        ]);

        const statsData = await statsRes.json();
        const infoData = await infoRes.json();

        if (statsData.success) {
            updateKPIs(statsData.stats);

            if (statsData.stats.models_comparison) {
                chartManager.createPerformanceChart('performanceChart', statsData.stats.models_comparison);
                buildLeaderboard(statsData.stats.models_comparison, statsData.stats.best_model);
                buildModelCards(statsData.stats.models_comparison, statsData.stats.best_model);
            }
        }

        if (infoData.success) {
            if (infoData.feature_importance) {
                chartManager.createFeatureChart('featureChart', infoData.feature_importance);
            }

            // Store for analytics
            window._modelResults = infoData.results;
            window._modelsComparison = statsData.stats?.models_comparison;
        }

        showToast('Dashboard loaded successfully', 'success');

    } catch (error) {
        console.error('Dashboard load error:', error);
        showToast('Failed to connect to API. Make sure the server is running.', 'error');
        // Load with demo data
        loadDemoData();
    }
}

function loadDemoData() {
    const demoModels = [
        { name: 'Logistic Regression', accuracy: 0.76, precision: 0.69, recall: 0.68, f1: 0.685, roc_auc: 0.82 },
        { name: 'Random Forest', accuracy: 0.82, precision: 0.75, recall: 0.74, f1: 0.745, roc_auc: 0.88 },
        { name: 'XGBoost', accuracy: 0.84, precision: 0.78, recall: 0.76, f1: 0.77, roc_auc: 0.90 },
        { name: 'LightGBM', accuracy: 0.83, precision: 0.77, recall: 0.75, f1: 0.76, roc_auc: 0.89 },
        { name: 'Stacking Ensemble', accuracy: 0.85, precision: 0.79, recall: 0.77, f1: 0.78, roc_auc: 0.91 },
    ];

    const demoFeatures = [
        { feature: 'satisfaction_score', shap_importance: 0.145 },
        { feature: 'tenure_months', shap_importance: 0.132 },
        { feature: 'contract_type', shap_importance: 0.118 },
        { feature: 'monthly_charges', shap_importance: 0.098 },
        { feature: 'support_tickets', shap_importance: 0.087 },
        { feature: 'engagement_score', shap_importance: 0.076 },
        { feature: 'payment_delays', shap_importance: 0.065 },
        { feature: 'login_frequency', shap_importance: 0.058 },
        { feature: 'loyalty_score', shap_importance: 0.051 },
        { feature: 'feature_usage', shap_importance: 0.045 },
    ];

    updateKPIs({
        best_auc: 0.91,
        best_f1: 0.78,
        total_models_trained: 6,
        models_comparison: demoModels
    });

    chartManager.createPerformanceChart('performanceChart', demoModels);
    chartManager.createFeatureChart('featureChart', demoFeatures);
    buildLeaderboard(demoModels, 'Stacking Ensemble');
    buildModelCards(demoModels, 'Stacking Ensemble');

    window._modelsComparison = demoModels;
    window._modelResults = {};
}

function updateKPIs(stats) {
    const bestModel = stats.models_comparison?.find(m => m.name === stats.best_model) ||
        stats.models_comparison?.[stats.models_comparison.length - 1];

    if (bestModel) {
        animateValue('kpi-accuracy', 0, (bestModel.accuracy * 100).toFixed(1), 1500, '%');
        animateValue('kpi-auc', 0, (bestModel.roc_auc * 100).toFixed(1), 1500, '%');
        animateValue('kpi-f1', 0, (bestModel.f1 * 100).toFixed(1), 1500, '%');
    } else {
        animateValue('kpi-accuracy', 0, (stats.best_auc * 100).toFixed(1), 1500, '%');
        animateValue('kpi-auc', 0, (stats.best_auc * 100).toFixed(1), 1500, '%');
        animateValue('kpi-f1', 0, (stats.best_f1 * 100).toFixed(1), 1500, '%');
    }

    animateValue('kpi-models', 0, stats.total_models_trained || 6, 1500, '');
}

function animateValue(elementId, start, end, duration, suffix) {
    const element = document.getElementById(elementId);
    if (!element) return;

    const endNum = parseFloat(end);
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 4);
        const current = start + (endNum - start) * eased;

        if (suffix === '%') {
            element.textContent = current.toFixed(1) + suffix;
        } else {
            element.textContent = Math.round(current);
        }

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
}

// ==================== LEADERBOARD ====================
function buildLeaderboard(models, bestModel) {
    const container = document.getElementById('leaderboard');
    if (!container) return;

    // Sort by ROC-AUC
    const sorted = [...models].sort((a, b) => b.roc_auc - a.roc_auc);

    let html = `
        <div class="leaderboard-item header">
            <span>#</span>
            <span>Model</span>
            <span>Accuracy</span>
            <span>Precision</span>
            <span>Recall</span>
            <span>F1</span>
            <span>ROC-AUC</span>
        </div>
    `;

    sorted.forEach((model, i) => {
        const isBest = model.name === bestModel;
        const rankClass = i === 0 ? 'gold' : i === 1 ? 'silver' : i === 2 ? 'bronze' : '';
        const rankSymbol = i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : (i + 1);

        html += `
            <div class="leaderboard-item ${isBest ? 'best' : ''}" style="animation-delay: ${i * 100}ms">
                <span class="lb-rank ${rankClass}">${rankSymbol}</span>
                <span class="lb-name">
                    ${model.name}
                    ${isBest ? '<span class="lb-best-badge">BEST</span>' : ''}
                </span>
                <span class="lb-value">${(model.accuracy * 100).toFixed(1)}%</span>
                <span class="lb-value">${(model.precision * 100).toFixed(1)}%</span>
                <span class="lb-value">${(model.recall * 100).toFixed(1)}%</span>
                <span class="lb-value">${(model.f1 * 100).toFixed(1)}%</span>
                <span class="lb-value" style="color: var(--accent-cyan); font-weight: 700;">
                    ${(model.roc_auc * 100).toFixed(1)}%
                </span>
            </div>
        `;
    });

    container.innerHTML = html;
}

// ==================== MODEL CARDS ====================
function buildModelCards(models, bestModel) {
    const container = document.getElementById('models-grid');
    if (!container) return;

    const modelTypes = {
        'Logistic Regression': 'Linear Classification',
        'Random Forest': 'Ensemble - Bagging',
        'Gradient Boosting': 'Ensemble - Boosting',
        'XGBoost': 'Gradient Boosting Framework',
        'LightGBM': 'Light Gradient Boosting',
        'Stacking Ensemble': 'Meta-Learning Ensemble'
    };

    let html = '';
    models.forEach(model => {
        const isBest = model.name === bestModel;
        html += `
            <div class="model-card ${isBest ? 'best-model' : ''}">
                <h3 class="model-name">${model.name}</h3>
                <p class="model-type">${modelTypes[model.name] || 'Machine Learning'}</p>
                <div class="model-metrics">
                    <div class="metric-item">
                        <span class="metric-value">${(model.accuracy * 100).toFixed(1)}%</span>
                        <span class="metric-label">Accuracy</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-value">${(model.roc_auc * 100).toFixed(1)}%</span>
                        <span class="metric-label">ROC-AUC</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-value">${(model.f1 * 100).toFixed(1)}%</span>
                        <span class="metric-label">F1-Score</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-value">${(model.recall * 100).toFixed(1)}%</span>
                        <span class="metric-label">Recall</span>
                    </div>
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}

// ==================== ANALYTICS CHARTS ====================
function loadAnalyticsCharts() {
    if (window._modelsComparison) {
        chartManager.createRadarChart('radarChart', window._modelsComparison);
    }

    if (window._modelResults) {
        chartManager.createConfusionMatrix('confusionChart', window._modelResults);
    }
}

// ==================== PREDICTION ====================
async function makePrediction() {
    const btn = document.getElementById('predict-btn');
    const btnText = btn.querySelector('.btn-text');

    // Button loading state
    btnText.textContent = 'Analyzing...';
    btn.disabled = true;
    btn.style.opacity = '0.7';

    const inputData = {
        age: document.getElementById('inp-age').value,
        gender: document.getElementById('inp-gender').value,
        tenure_months: document.getElementById('inp-tenure').value,
        contract_type: document.getElementById('inp-contract').value,
        monthly_charges: document.getElementById('inp-monthly').value,
        total_charges: document.getElementById('inp-total').value,
        num_products: document.getElementById('inp-products').value,
        num_support_tickets: document.getElementById('inp-tickets').value,
        days_since_last_interaction: document.getElementById('inp-inactive').value,
        avg_session_duration_min: document.getElementById('inp-session').value,
        login_frequency_monthly: document.getElementById('inp-login').value,
        feature_usage_rate: document.getElementById('inp-usage').value,
        payment_method: document.getElementById('inp-payment').value,
        payment_delays: document.getElementById('inp-delays').value,
        satisfaction_score: document.getElementById('inp-satisfaction').value,
        nps_score: document.getElementById('inp-nps').value,
        has_partner: document.getElementById('inp-partner').value,
        has_dependents: document.getElementById('inp-dependents').value,
        referral_count: document.getElementById('inp-referrals').value,
        discount_pct: document.getElementById('inp-discount').value
    };

    try {
        const response = await fetch(`${API_BASE}/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(inputData)
        });

        const data = await response.json();

        if (data.success) {
            displayResults(data);
            showToast(`Prediction complete: ${data.prediction.risk_level} Risk`,
                data.prediction.churn_probability > 0.5 ? 'error' : 'success');
        } else {
            showToast('Prediction failed: ' + data.error, 'error');
        }

    } catch (error) {
        console.error('Prediction error:', error);
        // Demo prediction
        const demoResult = generateDemoPrediction(inputData);
        displayResults(demoResult);
        showToast('Using demo prediction (server not connected)', 'info');
    }

    // Reset button
    btnText.textContent = 'Analyze Churn Risk';
    btn.disabled = false;
    btn.style.opacity = '1';
}

function generateDemoPrediction(data) {
    let prob = 0.3;

    if (data.contract_type === 'Month-to-Month') prob += 0.15;
    if (parseInt(data.tenure_months) < 12) prob += 0.1;
    if (parseFloat(data.satisfaction_score) < 3) prob += 0.15;
    if (parseInt(data.num_support_tickets) > 3) prob += 0.1;
    if (parseInt(data.payment_delays) > 1) prob += 0.1;
    if (parseInt(data.days_since_last_interaction) > 30) prob += 0.05;
    if (parseFloat(data.feature_usage_rate) < 30) prob += 0.08;
    if (parseInt(data.login_frequency_monthly) < 5) prob += 0.05;
    if (parseInt(data.referral_count) > 0) prob -= 0.05;
    if (parseInt(data.num_products) > 3) prob -= 0.05;

    prob = Math.max(0.05, Math.min(0.95, prob));

    let risk_level, risk_color;
    if (prob < 0.3) { risk_level = 'Low'; risk_color = '#00e676'; }
    else if (prob < 0.6) { risk_level = 'Medium'; risk_color = '#ffab00'; }
    else if (prob < 0.8) { risk_level = 'High'; risk_color = '#ff6d00'; }
    else { risk_level = 'Critical'; risk_color = '#ff1744'; }

    return {
        success: true,
        prediction: {
            churn_probability: prob,
            churn_prediction: prob >= 0.5 ? 1 : 0,
            risk_level, risk_color,
            confidence: Math.abs(prob - 0.5) * 2
        },
        risk_factors: [
            ...(data.contract_type === 'Month-to-Month' ? [{ factor: 'Month-to-month contract', impact: 85 }] : []),
            ...(parseInt(data.tenure_months) < 12 ? [{ factor: `Short tenure (${data.tenure_months} months)`, impact: 75 }] : []),
            ...(parseFloat(data.satisfaction_score) < 3 ? [{ factor: `Low satisfaction (${data.satisfaction_score})`, impact: 90 }] : []),
            ...(parseInt(data.num_support_tickets) > 3 ? [{ factor: `High support tickets (${data.num_support_tickets})`, impact: 70 }] : []),
            ...(parseInt(data.payment_delays) > 1 ? [{ factor: `Payment delays (${data.payment_delays})`, impact: 65 }] : []),
        ].slice(0, 5),
        recommendations: [
            { icon: '📋', priority: 'High', action: 'Offer annual contract with discount' },
            { icon: '😊', priority: 'Medium', action: 'Schedule satisfaction survey call' },
            { icon: '🎁', priority: prob > 0.6 ? 'Critical' : 'Low', action: 'Send loyalty reward offer' },
            { icon: '📧', priority: 'Medium', action: 'Launch re-engagement email campaign' },
        ]
    };
}

function displayResults(data) {
    const placeholder = document.getElementById('results-placeholder');
    const content = document.getElementById('results-content');

    placeholder.style.display = 'none';
    content.style.display = 'block';

    const { prediction, risk_factors, recommendations } = data;
    const prob = prediction.churn_probability * 100;

    // Animate gauge
    let currentVal = 0;
    const gaugeInterval = setInterval(() => {
        currentVal += prob / 50;
        if (currentVal >= prob) {
            currentVal = prob;
            clearInterval(gaugeInterval);
        }
        chartManager.drawGauge('gaugeCanvas', currentVal, prediction.risk_color);
    }, 20);

    // Update value with animation
    const gaugeValue = document.getElementById('gauge-value');
    animateValue2(gaugeValue, 0, prob, 1000);

    // Update color
    gaugeValue.style.color = prediction.risk_color;

    // Risk badge
    const badge = document.getElementById('risk-badge');
    const badgeText = document.getElementById('risk-level-text');
    badgeText.textContent = prediction.risk_level + ' Risk';
    badge.style.background = prediction.risk_color + '18';
    badge.style.color = prediction.risk_color;
    badge.style.border = `1px solid ${prediction.risk_color}40`;

    // Risk factors
    const factorsList = document.getElementById('factors-list');
    if (risk_factors && risk_factors.length > 0) {
        factorsList.innerHTML = risk_factors.map((f, i) => `
            <div class="factor-item" style="animation: fadeSlideIn 0.3s ease ${i * 100}ms both">
                <div class="factor-bar">
                    <div class="factor-bar-fill" style="width: ${f.impact}%"></div>
                </div>
                <span class="factor-text">${f.factor}</span>
            </div>
        `).join('');
    } else {
        factorsList.innerHTML = '<p style="color: var(--accent-green); font-size: 13px;">✓ No significant risk factors detected</p>';
    }

    // Recommendations
    const recsList = document.getElementById('recs-list');
    if (recommendations && recommendations.length > 0) {
        recsList.innerHTML = recommendations.map((r, i) => `
            <div class="rec-item" style="animation: fadeSlideIn 0.3s ease ${i * 100 + 300}ms both">
                <span class="rec-icon">${r.icon}</span>
                <div class="rec-content">
                    <span class="rec-priority ${r.priority}">${r.priority}</span>
                    <p class="rec-action">${r.action}</p>
                </div>
            </div>
        `).join('');
    }

    // Add CSS animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes fadeSlideIn {
            from { opacity: 0; transform: translateX(-10px); }
            to { opacity: 1; transform: translateX(0); }
        }
    `;
    document.head.appendChild(style);

    // Pulse animation on results card
    const resultsCard = document.getElementById('results-card');
    resultsCard.style.borderColor = prediction.risk_color + '40';
    resultsCard.style.boxShadow = `0 0 30px ${prediction.risk_color}15`;
}

function animateValue2(element, start, end, duration) {
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 4);
        const current = start + (end - start) * eased;
        element.textContent = current.toFixed(1) + '%';

        if (progress < 1) requestAnimationFrame(update);
    }

    requestAnimationFrame(update);
}

// ==================== ANIMATIONS ====================
function initAnimations() {
    // GSAP animations for elements entering viewport
    if (typeof gsap !== 'undefined' && typeof ScrollTrigger !== 'undefined') {
        gsap.registerPlugin(ScrollTrigger);

        gsap.utils.toArray('[data-animate="fade-up"]').forEach(el => {
            gsap.from(el, {
                scrollTrigger: {
                    trigger: el,
                    start: 'top 85%',
                    toggleActions: 'play none none none'
                },
                y: 40,
                opacity: 0,
                duration: 0.8,
                delay: parseInt(el.dataset.delay || 0) / 1000,
                ease: 'power3.out'
            });
        });

        gsap.utils.toArray('[data-animate="fade-right"]').forEach(el => {
            gsap.from(el, {
                x: -40,
                opacity: 0,
                duration: 0.8,
                ease: 'power3.out'
            });
        });

        gsap.utils.toArray('[data-animate="fade-left"]').forEach(el => {
            gsap.from(el, {
                x: 40,
                opacity: 0,
                duration: 0.8,
                delay: 0.2,
                ease: 'power3.out'
            });
        });
    }
}

// ==================== TOAST NOTIFICATIONS ====================
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;

    setTimeout(() => {
        toast.classList.remove('show');
    }, 4000);
}

// ==================== AUTO-CALCULATE TOTAL CHARGES ====================
document.addEventListener('DOMContentLoaded', () => {
    const monthlyInput = document.getElementById('inp-monthly');
    const tenureInput = document.getElementById('inp-tenure');
    const totalInput = document.getElementById('inp-total');

    function updateTotal() {
        if (monthlyInput && tenureInput && totalInput) {
            const monthly = parseFloat(monthlyInput.value) || 0;
            const tenure = parseInt(tenureInput.value) || 0;
            totalInput.value = (monthly * tenure).toFixed(2);
        }
    }

    if (monthlyInput) monthlyInput.addEventListener('input', updateTotal);
    if (tenureInput) tenureInput.addEventListener('input', updateTotal);
});