"""
Model Evaluation Script
========================
Extracts data from Neo4j, trains multiple ML models,
evaluates and compares performance, outputs the best model.

Run this script standalone:
    python src/model_evaluation.py

Do NOT integrate this into the main diagnostic system.
After reviewing results, the chosen model can be integrated
into the main system when instructed.
"""

import os
import numpy as np
from dotenv import load_dotenv
from neo4j import GraphDatabase

from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import LabelEncoder, MultiLabelBinarizer
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import classification_report, accuracy_score
import warnings
warnings.filterwarnings('ignore')

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

# ─── Neo4j Connection ────────────────────────────────────────────────────────

NEO4J_URI      = os.getenv("NEO4J_URI",      "neo4j+ssc://5830d6bf.databases.neo4j.io")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "5830d6bf")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "GPrI0zK7MaGw0uczDSPTjxCtef4LgMUJ4BM_6BUq4Ko")


# ─── Data Extraction ─────────────────────────────────────────────────────────

def extract_data_from_neo4j():
    """
    Pull disease→symptom relationships from Neo4j.
    Returns:
        all_symptoms  : sorted list of all unique symptom names
        disease_names : list of disease labels
        X_raw         : list of (symptom_name, weight) pairs per disease
    """
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    records = []

    with driver.session() as session:
        result = session.run("""
            MATCH (d:Disease)-[r:HAS_SYMPTOM]->(s:Symptom)
            RETURN d.name AS disease, s.name AS symptom, r.weight AS weight
            ORDER BY d.name, s.name
        """)
        for rec in result:
            records.append({
                "disease": rec["disease"],
                "symptom": rec["symptom"],
                "weight":  float(rec["weight"]) if rec["weight"] else 1.0
            })

    driver.close()

    if not records:
        raise RuntimeError("No data returned from Neo4j. Ensure knowledge is loaded first.")

    # Build symptom universe
    all_symptoms = sorted(set(r["symptom"] for r in records))
    symptom_index = {s: i for i, s in enumerate(all_symptoms)}

    # Group by disease
    from collections import defaultdict
    disease_map = defaultdict(dict)
    for r in records:
        disease_map[r["disease"]][r["symptom"]] = r["weight"]

    disease_names = sorted(disease_map.keys())

    # Build feature matrix: each row = one disease, columns = symptom weights (0 if absent)
    X = np.zeros((len(disease_names), len(all_symptoms)), dtype=float)
    for i, disease in enumerate(disease_names):
        for symptom, weight in disease_map[disease].items():
            j = symptom_index[symptom]
            X[i, j] = weight

    print(f"  Diseases  : {len(disease_names)}")
    print(f"  Symptoms  : {len(all_symptoms)}")
    print(f"  Matrix    : {X.shape}")

    return all_symptoms, disease_names, X


# ─── Synthetic Sample Generation ─────────────────────────────────────────────

def generate_samples(disease_names, X_base, n_samples_per_disease=40, noise_std=0.3, seed=42):
    """
    Each disease has one 'true' symptom profile (X_base row).
    We generate synthetic patient samples by adding Gaussian noise
    and randomly zeroing out some symptoms (simulating partial reports).
    This gives the classifiers enough samples to train on.
    """
    rng = np.random.RandomState(seed)
    X_out, y_out = [], []

    for i, disease in enumerate(disease_names):
        base = X_base[i]
        for _ in range(n_samples_per_disease):
            sample = base.copy()
            # Add noise only to non-zero features
            noise = rng.normal(0, noise_std, size=base.shape)
            sample = np.where(base > 0, np.clip(sample + noise, 0, 3), 0)
            # Randomly drop ~20% of symptoms
            mask = rng.rand(len(base)) > 0.20
            sample = sample * mask
            X_out.append(sample)
            y_out.append(i)

    return np.array(X_out), np.array(y_out)


# ─── Model Definitions ───────────────────────────────────────────────────────

def get_models():
    return {
        "Decision Tree": DecisionTreeClassifier(
            max_depth=15, min_samples_split=4, random_state=42
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=200, max_depth=None, random_state=42, n_jobs=-1
        ),
        "Gradient Boosting": GradientBoostingClassifier(
            n_estimators=150, learning_rate=0.1, max_depth=5, random_state=42
        ),
        "Neural Network (MLP)": MLPClassifier(
            hidden_layer_sizes=(256, 128, 64),
            activation='relu',
            max_iter=500,
            random_state=42,
            early_stopping=True,
            validation_fraction=0.1
        ),
        "SVM (RBF)": SVC(
            kernel='rbf', C=10, gamma='scale', probability=True, random_state=42
        ),
        "Naive Bayes": GaussianNB(),
    }


# ─── Evaluation ──────────────────────────────────────────────────────────────

def evaluate_models(X, y, disease_names):
    models = get_models()
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    results = {}

    print("\n" + "=" * 60)
    print(f"{'Model':<25} {'CV Acc (mean)':<16} {'CV Acc (std)':<14} {'Status'}")
    print("=" * 60)

    for name, model in models.items():
        try:
            scores = cross_val_score(model, X, y, cv=cv, scoring='accuracy', n_jobs=-1)
            results[name] = {
                "model":    model,
                "mean_acc": scores.mean(),
                "std_acc":  scores.std(),
                "scores":   scores,
                "error":    None
            }
            print(f"{name:<25} {scores.mean():.4f}          ±{scores.std():.4f}        OK")
        except Exception as e:
            results[name] = {"model": model, "mean_acc": 0, "std_acc": 0, "scores": [], "error": str(e)}
            print(f"{name:<25} FAILED                              {str(e)[:30]}")

    return results


def detailed_report(best_name, best_model, X, y, disease_names):
    """Fit on full data and show per-class report."""
    best_model.fit(X, y)
    y_pred = best_model.predict(X)
    print(f"\n{'─'*60}")
    print(f"  Detailed Report: {best_name} (fitted on full data)")
    print(f"{'─'*60}")
    print(classification_report(
        y, y_pred,
        target_names=disease_names,
        zero_division=0
    ))


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "=" * 60)
    print("  MEDICAL DIAGNOSTIC SYSTEM — MODEL EVALUATION")
    print("=" * 60)

    # 1. Extract from Neo4j
    print("\n[1/4] Extracting data from Neo4j...")
    all_symptoms, disease_names, X_base = extract_data_from_neo4j()

    # 2. Generate synthetic samples
    print("\n[2/4] Generating synthetic patient samples...")
    X, y = generate_samples(disease_names, X_base, n_samples_per_disease=40)
    print(f"  Total samples : {len(X)}")
    print(f"  Features      : {X.shape[1]}")

    # 3. Evaluate all models
    print("\n[3/4] Evaluating models (5-fold cross-validation)...")
    results = evaluate_models(X, y, disease_names)

    # 4. Determine best model
    print("\n[4/4] Results Summary")
    print("=" * 60)

    valid = {k: v for k, v in results.items() if v["error"] is None}
    if not valid:
        print("All models failed. Check Neo4j data and dependencies.")
        return

    ranked = sorted(valid.items(), key=lambda x: x[1]["mean_acc"], reverse=True)

    print(f"\n{'Rank':<6} {'Model':<25} {'Mean Accuracy':<16} {'Std Dev'}")
    print("-" * 60)
    for rank, (name, info) in enumerate(ranked, 1):
        marker = "  ← BEST" if rank == 1 else ""
        print(f"{rank:<6} {name:<25} {info['mean_acc']:.4f}          ±{info['std_acc']:.4f}{marker}")

    best_name, best_info = ranked[0]

    print(f"\n{'=' * 60}")
    print(f"  RECOMMENDATION: Use '{best_name}'")
    print(f"  Cross-val accuracy: {best_info['mean_acc']:.4f} ± {best_info['std_acc']:.4f}")
    print(f"{'=' * 60}")

    # 5. Detailed classification report for best model
    detailed_report(best_name, best_info["model"], X, y, disease_names)

    print("\nNOTE: When instructed, integrate the best model into")
    print("      diagnostic_system.py alongside the Bayesian Network.")
    print("      This file is evaluation-only and does not modify any system files.\n")


if __name__ == "__main__":
    main()
