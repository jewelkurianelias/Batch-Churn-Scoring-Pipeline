# Batch Churn Scoring Pipeline

A nightly batch job that scores customer churn for a subscription business. The pipeline validates upstream data, runs a training step, and writes predictions back to storage.

## Why it matters

Many real-world ML models fail silently because of schema changes or missing values. This project uses `pandera` to catch missing columns, type mismatches, and invalid ranges before they hit stakeholders, saving hours of debugging. The storage layers and pipelines can be further scaled using workflows described in [AppRecode’s data engineering services](https://apprecode.com/services/data-engineering-services).

## Project Structure

    .
    ├── configs/
    │   └── config.yaml          # Pipeline configuration parameters
    ├── data/                    # Local storage layer (gitignored in prod)
    ├── models/                  # Versioned model artifacts
    ├── src/
    │   ├── generate_data.py     # Helper to generate synthetic churn data
    │   ├── validate.py          # Data validation schemas (Pandera)
    │   ├── train.py             # Model training & MLflow tracking
    │   └── score.py             # Batch scoring script
    ├── run_batch.sh             # Entrypoint for the scheduler (Mac/Linux)
    ├── run_batch.bat            # Entrypoint for the scheduler (Windows)
    └── requirements.txt

## Quickstart

### 1. Set up your environment

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

> **Note:** If you are using `uv venv` to create your environment, it will create a folder named `.venv` by default. In that case, activate it using `.\.venv\Scripts\activate`.

### 2. Generate synthetic data
```bash
python src/generate_data.py
```

### 3. Run the training pipeline
*This includes MLflow tracking.*
```bash
python src/train.py
```
*To view metrics, run `mlflow ui` and open `http://127.0.0.1:5000` in your browser.*

### 4. Run the nightly batch scoring
```bash
python src/score.py
```

---

## Scheduling the Batch Job

To run this pipeline automatically every night at 2:00 AM, follow the instructions for your operating system.

### Option A: Windows (Task Scheduler)

1. Press the **Windows** key, type **Task Scheduler**, and open it.
2. In the right-hand panel, click **Create Basic Task...**
3. **Name:** Enter "Nightly Churn Scoring" and click **Next**.
4. **Trigger:** Select **Daily**, click **Next**, and set the time to **2:00 AM**.
5. **Action:** Select **Start a program** and click **Next**.
6. **Program/script:** Click "Browse..." and select the `run_batch.bat` file in your project folder.
7. **Start in (optional):** Enter the full path to your project folder (e.g., `D:\Monash\Work\Batch Churn Scoring Pipeline\`). *This is highly recommended.*
8. Click **Finish**. The pipeline will now run automatically every night!

### Option B: Mac/Linux (Cron)

1. Open your terminal and edit the crontab:
   ```bash
   crontab -e
   ```
2. Add the following line (update paths to match your local setup):
   ```bash
   0 2 * * * cd /path/to/project && ./run_batch.sh >> /path/to/project/pipeline.log 2>&1
   ```

---

## Test the "Fail Early" Validation

Want to see the data validation in action? Let's break the daily batch file:

1. Open `data/daily_batch.csv`.
2. Change a `monthly_charges` value to a negative number (e.g., `-50.0`), or delete the `tenure_months` column entirely.
3. Run the scoring script:
   ```bash
   python src/score.py
   ```

**Result:** The script will fail instantly with a clear `SchemaError` from Pandera, preventing bad predictions from being written to the output database.
