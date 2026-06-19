import pandera as pa
from pandera import Column, Check

# Define the expected schema for our upstream data
# This catches schema drift, missing columns, and bad types/ranges
features_schema = pa.DataFrameSchema({
    "customer_id": Column(str, required=True),
    "tenure_months": Column(int, Check.ge(0), required=True, description="Tenure cannot be negative"),
    "monthly_charges": Column(float, Check.ge(0.0), required=True),
    "total_charges": Column(float, Check.ge(0.0), required=True),
    "subscription_type": Column(str, Check.isin(["Basic", "Standard", "Premium"])),
    "payment_method": Column(str, Check.isin(["CreditCard", "PayPal", "BankTransfer"])),
})

# Training data schema extends feature schema with the target variable
training_schema = features_schema.add_columns({
    "churn": Column(int, Check.isin([0, 1]), required=True)
})

def validate_training_data(df):
    """Validates historical data before training."""
    try:
        validated_df = training_schema.validate(df)
        print("✅ Training data passed validation.")
        return validated_df
    except pa.errors.SchemaError as e:
        print(f"❌ Validation Error in Training Data: {e}")
        raise

def validate_batch_data(df):
    """Validates daily batch data before scoring."""
    try:
        validated_df = features_schema.validate(df)
        print("✅ Batch data passed validation.")
        return validated_df
    except pa.errors.SchemaError as e:
        print(f"❌ Validation Error in Batch Data: {e}")
        raise