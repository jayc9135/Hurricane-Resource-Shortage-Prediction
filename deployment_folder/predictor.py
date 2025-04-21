import pandas as pd
import numpy as np
import logging
from database_handler import get_model
from feature_engineer import get_aggregated_observations

# List of input features
in_features = [
    'maximum_sustained_wind_knots_max',
    'maximum_sustained_wind_knots_mean',
    'central_pressure_mb_min',
    'central_pressure_mb_mean',
    'radius_of_max_wind_nm_max',
    'radius_of_max_wind_nm_mean'
]

def predict_shelter_count():
    """
    Predicts the number of shelters needed based on aggregated observations.
    :return: DataFrame with predictions
    """
    aggregated_observations = get_aggregated_observations()

    # Check if the input DataFrame is empty
    if aggregated_observations.empty:
        logging.warning("[PREDICTOR] No observations available for prediction.")
        return pd.DataFrame()

    # Select only the relevant features for prediction
    X_input = aggregated_observations[in_features]

    # Make predictions using the loaded model. Prediction is in log1p(y)
    model = get_model()
    if model is None:
        logging.error("[PREDICTOR] Model loading failed. Cannot make prediction.")
        return pd.DataFrame()

    y_pred_log = model.predict(X_input)

    # Convert predictions back from log1p
    y_pred_original = np.expm1(y_pred_log)

    # Convert results to integer
    prediction = int(np.ceil(y_pred_original.flatten()[0]))
    logging.info(f"[PREDICTOR] Shelter prediction completed. Predicted shelters: {prediction}")

    return prediction

def predict_custom_aggregated_features(aggregated_features: dict):
    """
    Predict shelters given a manually provided aggregated feature set.
    :param aggregated_features: dict containing required input features
    :return: integer prediction
    """
    try:
        # Convert dict to DataFrame
        X_input = pd.DataFrame([aggregated_features])

        # Select correct columns
        X_input = X_input[in_features]

        # Load model
        model = get_model()
        if model is None:
            logging.error("[PREDICTOR] Model loading failed. Cannot make prediction.")
            return pd.DataFrame()

        # Predict
        y_pred_log = model.predict(X_input)

        # Invert log1p
        y_pred_original = np.expm1(y_pred_log)

        # Convert results to integer
        prediction = int(np.ceil(y_pred_original.flatten()[0]))
        logging.info(f"[PREDICTOR] Shelter prediction completed. Predicted shelters: {prediction}")

        return prediction

    except Exception as e:
        logging.error(f"[PREDICTOR] Error in custom prediction: {e}")
        return None