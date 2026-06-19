import os
import glob
import yaml
import joblib
import pandas as pd

from validate import validate_batch_data

def load_config():
    with open("configs/config.yaml", "r") as f:
        return yaml.safe_load(f)

def get_latest_model(model_dir):
    """Finds the most recently saved model artifact."""
    list_of_files = glob.glob(f"{model_dir}/*.pkl")
    if not list_of_files:
        raise FileNotFoundError(f"No models found in {model_dir}. Run train.py first.")
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file

def main():
    config = load_config()
    
    print("Loading daily batch data...")
    df = pd.read_csv(config["data"]["daily_batch_path"])
    
    # 1. FAIL EARLY: Validate batch data before inference
    # If the schema changed overnight, the pipeline stops here.
    df = validate_batch_data(df)

    # 2. Load latest model
    latest_model_path = get_latest_model(config["model"]["model_dir"])
    print(f"Loading model artifact: {latest_model_path}")
    model = joblib.load(latest_model_path)

    # 3. Prepare data and score
    # Drop customer_id for prediction but keep it to map predictions back
    X = df.drop(columns=["customer_id"])
    
    print("Scoring batch...")
    probabilities = model.predict_proba(X)[:, 1]
    
    # 4. Save results
    results = pd.DataFrame({
        "customer_id": df["customer_id"],
        "churn_probability": probabilities
    })
    
    output_path = config["data"]["predictions_path"]
    results.to_csv(output_path, index=False)
    print(f"✅ Scored {len(results)} records. Predictions saved to {output_path}")

if __name__ == "__main__":
    main()