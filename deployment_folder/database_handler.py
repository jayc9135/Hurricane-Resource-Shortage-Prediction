import pandas as pd
import pickle
import logging
import boto3
import io
from botocore import UNSIGNED
from botocore.config import Config

# Constants
BUCKET_NAME = "..."
MODEL_S3_KEY = "..."
STORED_OBSERVATIONS_S3_KEY = "..."

# Create S3 client
s3 = boto3.client("s3", config=Config(signature_version=UNSIGNED))

def insert_new_observation(record: dict) -> None:
    """Insert a new observation into the stored observations on S3."""
    try:
        # Load existing data from S3
        df_existing = get_stored_observations()

        # Create new observation DataFrame
        df_new_observation = pd.DataFrame([record])

        # Combine
        if df_existing.empty:
            df_combined = df_new_observation
            logging.warning("[DB Handler] No existing observations found. Creating new dataset.")
        else:
            df_combined = pd.concat([df_existing, df_new_observation], ignore_index=True)
            logging.info(f"[DB Handler] Existing observations found. Appending new observation. Total records: {len(df_combined)}")

        # Upload back to S3
        post_updated_observations(df_combined)
        logging.info("[DB Handler] Updated observations uploaded successfully to S3.")

    except Exception as e:
        logging.error(f"[DB Handler] Error inserting new observation: {e}")


def get_stored_observations() -> pd.DataFrame:
    """Fetch all stored observations from S3."""
    try:
        response = s3.get_object(Bucket=BUCKET_NAME, Key=STORED_OBSERVATIONS_S3_KEY)
        df = pd.read_csv(io.BytesIO(response["Body"].read()))
        logging.info(f"[DB Handler] Retrieved {len(df)} observations from S3.")
        return df
    except s3.exceptions.NoSuchKey:
        logging.warning(f"[DB Handler] File {STORED_OBSERVATIONS_S3_KEY} not found in S3 bucket. Returning empty DataFrame.")
        return pd.DataFrame()
    except Exception as e:
        logging.error(f"[DB Handler] Error fetching stored observations: {e}")
        return pd.DataFrame()


def get_model():
    """Load and return the Ridge model from S3."""
    try:
        response = s3.get_object(Bucket=BUCKET_NAME, Key=MODEL_S3_KEY)
        model = pickle.load(io.BytesIO(response["Body"].read()))
        logging.info("[DB Handler] Model loaded successfully from S3.")
        return model
    except Exception as e:
        logging.error(f"[DB Handler] Error fetching model from S3: {e}")
        return None


def post_updated_observations(df: pd.DataFrame) -> None:
    """Upload the updated DataFrame to S3."""
    try:
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        s3.put_object(Bucket=BUCKET_NAME, Key=STORED_OBSERVATIONS_S3_KEY, Body=csv_buffer.getvalue())
        logging.info("[DB Handler] Updated observations uploaded to S3 successfully.")
    except Exception as e:
        logging.error(f"[DB Handler] Error uploading observations to S3: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    # 1. Test loading model
    model = get_model()
    if model:
        print("[TEST] Model loaded successfully from S3!")

    # 2. Test fetching stored observations
    df = get_stored_observations()
    if not df.empty:
        print(f"[TEST] Retrieved {len(df)} records from stored observations.")
    else:
        print("[TEST] No records found in stored observations.")

    # 3. Test inserting a new observation
    sample_observation = {
        'storm_id': 'TEST123',
        'storm_name': 'TESTSTORM',
        'num_of_obs': 1,
        'datetime': '2025-04-17 12:00:00',
        'category': 1,
        'record_identifier': '',
        'status_of_system': 'HU',
        'latitude': 25.0,
        'longitude': -80.0,
        'maximum_sustained_wind_knots': 75,
        'central_pressure_mb': 980.0,
        '34_kt_ne_nm': 100.0,
        '34_kt_se_nm': 100.0,
        '34_kt_sw_nm': 100.0,
        '34_kt_nw_nm': 100.0,
        '50_kt_ne_nm': 50.0,
        '50_kt_se_nm': 50.0,
        '50_kt_sw_nm': 50.0,
        '50_kt_nw_nm': 50.0,
        '64_kt_ne_nm': 20.0,
        '64_kt_se_nm': 20.0,
        '64_kt_sw_nm': 20.0,
        '64_kt_nw_nm': 20.0,
        'radius_of_max_wind_nm': 10.0
    }

    insert_new_observation(sample_observation)
    print("[TEST] Inserted new observation successfully.")