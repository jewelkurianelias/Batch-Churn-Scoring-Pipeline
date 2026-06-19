import pandas as pd
import numpy as np
import os

def generate_data(num_records=1000, output_path="data/raw_churn_data.csv", include_target=True):
    np.random.seed(42)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    data = {
        "customer_id": [f"CUST_{i:04d}" for i in range(num_records)],
        "tenure_months": np.random.randint(0, 72, size=num_records),
        "monthly_charges": np.round(np.random.uniform(15.0, 120.0, size=num_records), 2),
        "subscription_type": np.random.choice(["Basic", "Standard", "Premium"], size=num_records),
        "payment_method": np.random.choice(["CreditCard", "PayPal", "BankTransfer"], size=num_records)
    }
    
    # Calculate realistic total charges
    data["total_charges"] = np.round(data["tenure_months"] * data["monthly_charges"], 2)
    
    df = pd.DataFrame(data)
    
    if include_target:
        # Simulate churn logic: higher churn for low tenure & high charges
        churn_prob = (1 - (df["tenure_months"] / 72)) * 0.5 + (df["monthly_charges"] / 120) * 0.3
        df["churn"] = (np.random.rand(num_records) < churn_prob).astype(int)
        
    df.to_csv(output_path, index=False)
    print(f"Generated {num_records} records at {output_path}")

if __name__ == "__main__":
    # Generate historical data for training
    generate_data(1000, "data/raw_churn_data.csv", include_target=True)
    # Generate daily batch for scoring (no target column)
    generate_data(50, "data/daily_batch.csv", include_target=False)