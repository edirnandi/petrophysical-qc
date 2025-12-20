"""
porosity_prediction.py

ML workflow to predict Porosity from conventional logs
(GR, RHOB, NPHI, RT, DT).

Designed for:
- Large mature fields with many wells
- Consistent and scalable porosity prediction

Features:
- Tkinter file browser (CSV / LAS)
- Robust preprocessing
- Random Forest regression
- Cross-validation
- Model versioning by Field + Date

Author: Edy Irnandi Sudjana
License: MIT
"""

import os
import joblib
import numpy as np
import pandas as pd

from datetime import datetime
from tkinter import Tk, filedialog

from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_squared_error, r2_score

# Optional LAS support
try:
    import lasio
    HAS_LASIO = True
except Exception:
    HAS_LASIO = False


# -------------------------
# 1. File Selection
# -------------------------
def browse_file():
    Tk().withdraw()
    return filedialog.askopenfilename(
        title="Select CSV or LAS Well Log File",
        filetypes=[("CSV files", "*.csv"), ("LAS files", "*.las"), ("All files", "*.*")]
    )


# -------------------------
# 2. Data Loading
# -------------------------
def load_data(filepath):
    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".csv":
        return pd.read_csv(filepath)

    if ext == ".las":
        if not HAS_LASIO:
            raise ImportError("Install lasio to read LAS files.")
        las = lasio.read(filepath)
        df = las.df().reset_index()
        df.rename(columns={'DEPT': 'Depth'}, inplace=True)
        return df

    raise ValueError("Unsupported file format.")


# -------------------------
# 3. Feature Preparation
# -------------------------
def prepare_features(df, feature_cols, target_col):
    df = df.copy()

    # Drop rows without porosity (training only)
    df = df.dropna(subset=[target_col])

    X = df[feature_cols]
    y = df[target_col].values

    # Robust imputation for mature fields
    imputer = SimpleImputer(strategy="median")
    X = imputer.fit_transform(X)

    return X, y


# -------------------------
# 4. Model Builder
# -------------------------
def build_model():
    return Pipeline([
        ('scaler', StandardScaler()),
        ('model', RandomForestRegressor(
            n_estimators=300,
            random_state=42,
            n_jobs=-1
        ))
    ])


# -------------------------
# 5. Evaluation
# -------------------------
def evaluate(model, X_test, y_test):
    preds = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    r2 = r2_score(y_test, preds)

    print(f"Porosity → RMSE = {rmse:.4f}")
    print(f"Porosity → R²   = {r2:.4f}")


# -------------------------
# 6. MAIN WORKFLOW
# -------------------------
if __name__ == "__main__":

    print("Select your input CSV/LAS well log file...")
    file_path = browse_file()

    if not file_path:
        print("No file selected. Exiting.")
        exit()

    print(f"\nLoading file: {file_path}")
    df = load_data(file_path)

    FEATURES = ['GR', 'RHOB', 'NPHI', 'RT', 'DT']
    TARGET = 'Porosity'

    FEATURES = [c for c in FEATURES if c in df.columns]

    if not FEATURES:
        raise ValueError("No valid predictor logs found.")

    if TARGET not in df.columns:
        raise ValueError("Porosity column not found.")

    X, y = prepare_features(df, FEATURES, TARGET)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = build_model()

    print("\nRunning 5-fold cross-validation...")
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    cv_mse = -cross_val_score(
        model, X_train, y_train,
        cv=kf,
        scoring='neg_mean_squared_error'
    )
    print("CV RMSE (Porosity):", np.sqrt(cv_mse).round(4))

    print("\nTraining porosity prediction model...")
    model.fit(X_train, y_train)

    print("\nModel Performance on Test Data:")
    evaluate(model, X_test, y_test)

    # ---------------------------------------------------------------------------------------------------------------------------------
    # Save model with versioning
    # note that Save model is responsible for persisting (saving) the trained ML model to disk, so it can be reused later without retraining
    # ---------------------------------------------------------------------------------------------------------------------------------
    FIELD_NAME = "MatureField_A"   # change as needed
    RUN_DATE = datetime.now().strftime("%Y%m%d")

    model_dir = os.path.join(
        "saved_model",
        FIELD_NAME,
        RUN_DATE
    )

    os.makedirs(model_dir, exist_ok=True)

    model_filename = f"porosity_rf_model_{FIELD_NAME}_{RUN_DATE}.joblib"
    model_path = os.path.join(model_dir, model_filename)

    joblib.dump(model, model_path)

    print(f"\nModel saved to: {model_path}")
