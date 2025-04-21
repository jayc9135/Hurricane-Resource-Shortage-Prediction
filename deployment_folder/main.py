from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional, Dict
from database_handler import insert_new_observation
from predictor import predict_shelter_count, predict_custom_aggregated_features
import logging


# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI()

class Observation(BaseModel):
    storm_id: str
    storm_name: str
    num_of_obs: int
    datetime: str
    category: Optional[int]
    record_identifier: Optional[str]
    status_of_system: str
    latitude: float
    longitude: float
    maximum_sustained_wind_knots: float
    central_pressure_mb: float
    # 34 knots
    kt_34_ne_nm: float = Field(..., alias="34_kt_ne_nm")
    kt_34_se_nm: float = Field(..., alias="34_kt_se_nm")
    kt_34_sw_nm: float = Field(..., alias="34_kt_sw_nm")
    kt_34_nw_nm: float = Field(..., alias="34_kt_nw_nm")
    # 50 knots
    kt_50_ne_nm: float = Field(..., alias="50_kt_ne_nm")
    kt_50_se_nm: float = Field(..., alias="50_kt_se_nm")
    kt_50_sw_nm: float = Field(..., alias="50_kt_sw_nm")
    kt_50_nw_nm: float = Field(..., alias="50_kt_nw_nm")
    # 64 knots
    kt_64_ne_nm: float = Field(..., alias="64_kt_ne_nm")
    kt_64_se_nm: float = Field(..., alias="64_kt_se_nm")
    kt_64_sw_nm: float = Field(..., alias="64_kt_sw_nm")
    kt_64_nw_nm: float = Field(..., alias="64_kt_nw_nm")
    # Radius
    radius_of_max_wind_nm: float

    class Config:
        allow_population_by_field_name = True
        allow_population_by_alias = True

@app.get("/ping")
def ping():
    logging.info("Ping endpoint called.")
    return {"message": "API is running"}


@app.post("/add_new_observation")
def add_new_observation(obs: Observation):
    # Send the observation to the database handler to insert the observation
    try:
        insert_new_observation(obs.model_dump(by_alias=True))
        logging.info(f"New observation inserted for storm_id: {obs.storm_id}")
        return {"message": "Observation added"}
    except Exception as e:
        logging.error(f"Failed adding observation: {e}")
        return {"Failed adding observation - error": str(e)}

@app.get("/predict")
def predict_shelters():
    try:
        # Call the function get the shelter count
        shelter_count = predict_shelter_count()
        logging.info(f"Shelter prediction successful: {shelter_count}")
        return {"shelter_count": shelter_count}
    except Exception as e:
        logging.error(f"Failed predicting shelter count: {e}")
        return {"Failed predicting shelter count - error": str(e)}


@app.post("/predict_from_custom_aggregated_features")
def predict_custom(aggregated_features: Dict[str, float]):
    """
    Accepts manually aggregated hurricane features and predicts shelters.
    """
    try:
        shelter_count = predict_custom_aggregated_features(aggregated_features)
        if shelter_count is None:
            logging.error("[API] Prediction failed inside predict_custom. Returning error to user.")
            return {"error": "Prediction failed. Check server logs."}

        logging.info(f"[API] Custom shelter prediction successful. Predicted shelter count: {shelter_count}")
        return {"shelter_count": shelter_count}

    except Exception as e:
        logging.error(f"[API] Error in /predict_custom: {e}")
        return {"error": str(e)}