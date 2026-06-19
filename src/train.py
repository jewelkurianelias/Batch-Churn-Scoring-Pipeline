import os
import yaml
import time
import joblib
import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score

# Import validation logic
from validate import validate_training_data

def load_config():
    with open("configs/config.yaml", "r") as f:
        return yaml.safe_load(f)

def build_pipeline(config):
    numeric_features = config["features"]["numerical"]
    categorical_features = config["features"]["categorical"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ]
    )

    clf = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(n_estimators=100, random_state=42))
    ])
    return clf

def main():
    config = load_config()
    
    print("Loading data...")
    df = pd.read_csv(config["data"]["raw_data_path"])
    
    # 1. FAIL EARLY: Validate data before doing any ML work
    df = validate_training_data(df)

    X = df.drop(columns=[config["features"]["target"], "customer_id"])
    y = df[config["features"]["target"]]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 2. EXPERIMENT TRACKING: Setup MLflow
    mlflow.set_experiment(config["model"]["experiment_name"])
    
    with mlflow.start_run():
        clf = build_pipeline(config)
        
        print("Training model...")
        clf.fit(X_train, y_train)

        preds = clf.predict(X_test)
        preds_proba = clf.predict_proba(X_test)[:, 1]

        acc = accuracy_score(y_test, preds)
        auc = roc_auc_score(y_test, preds_proba)

        print(f"Metrics - Accuracy: {acc:.4f}, AUC: {auc:.4f}")

        # Log metrics and parameters
        mlflow.log_param("n_estimators", 100)
        mlflow.log_metric("accuracy", acc)
        mlflow.log_metric("roc_auc", auc)
        mlflow.sklearn.log_model(clf, "random_forest_pipeline")

        # 3. SAVE VERSIONED ARTIFACT
        os.makedirs(config["model"]["model_dir"], exist_ok=True)
        version = int(time.time())
        model_path = os.path.join(config["model"]["model_dir"], f"model_v{version}.pkl")
        joblib.dump(clf, model_path)
        print(f"✅ Model saved to {model_path}")

if __name__ == "__main__":
    main()