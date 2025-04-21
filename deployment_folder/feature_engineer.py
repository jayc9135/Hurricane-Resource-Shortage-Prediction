import pandas as pd
import logging
from database_handler import get_stored_observations


def get_aggregated_observations():
    """
    Aggregates stored and new observations.
    :return: Aggregated list of observations
    """
    try:
        stored_observations = get_stored_observations()

        # Perform grouping and aggregation
        grouped_df = stored_observations.groupby('storm_id').agg({
            'maximum_sustained_wind_knots': ['mean', 'max'],
            'central_pressure_mb': ['mean', 'min'],
            'radius_of_max_wind_nm': ['mean', 'max']
        }).reset_index()

        # Flatten the MultiIndex columns
        grouped_df.columns = ['_'.join(col).strip('_') for col in grouped_df.columns.values]

        logging.info(f"[Feature Engineer] Successfully aggregated storms.")

        return grouped_df
    except Exception as e:
        logging.error(f"[Feature Engineer] Error during aggregation: {e}. Returning empty DataFrame.")
        return pd.DataFrame()