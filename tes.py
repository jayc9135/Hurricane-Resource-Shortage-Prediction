# test.py
import pandas as pd
import numpy as np
import pickle
from sklearn.metrics import mean_absolute_error, r2_score, mean_absolute_percentage_error

# Settings
CSV_PATH = "./datasets/resource_dataset_with_id_category_storm_features.csv"   # <<<--- update this
MODEL_PATH = "./xgb_model.pkl"  # <<<--- update this

# Features your model expects
in_features = [
    'maximum_sustained_wind_knots_max',
    'maximum_sustained_wind_knots_mean',
    'central_pressure_mb_min',
    'central_pressure_mb_mean',
    'radius_of_max_wind_nm_max',
    'radius_of_max_wind_nm_mean'
]

# Load data
df = pd.read_csv(CSV_PATH)

# Load model
with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

# Prepare data
X = df[in_features]
y_true = df["shelters"]  # <<<--- whatever your true target column is

# Make predictions (assuming model trained on log1p)
y_pred_log = model.predict(X)
y_pred = np.expm1(y_pred_log)  # inverse log1p

# Evaluate
mae = mean_absolute_error(y_true, y_pred)
r2 = r2_score(y_true, y_pred)
adj_r2 = 1 - (1 - r2) * (len(y_true) - 1) / (len(y_true) - X.shape[1] - 1)
mape = mean_absolute_percentage_error(y_true, y_pred)

# Print results
print(f"MAE         : {mae:.2f}")
print(f"R2 Score    : {r2:.3f}")
print(f"Adjusted R2 : {adj_r2:.3f}")
print(f"MAPE        : {mape*100:.2f}%")