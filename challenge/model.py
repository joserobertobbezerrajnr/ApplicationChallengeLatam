import pandas as pd
import numpy as np
from datetime import datetime
import xgboost as xgb
from typing import Tuple, Union, List

class DelayModel:

    def __init__(
        self
    ):
        self._model = None # Model should be saved in this attribute.

    def preprocess(
        self,
        data: pd.DataFrame,
        target_column: str = None,
        columns: str = None
    ) -> Union[Tuple[pd.DataFrame, pd.DataFrame], pd.DataFrame]:
        """
        Prepare raw data for training or predict.

        Args:
            data (pd.DataFrame): raw data.
            target_column (str, optional): if set, the target is returned.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: features and target.
            or
            pd.DataFrame: features.
        """
        top_10_features = [
            "OPERA_Latin American Wings", 
            "MES_7",
            "MES_10",
            "OPERA_Grupo LATAM",
            "MES_12",
            "TIPOVUELO_I",
            "MES_4",
            "MES_11",
            "OPERA_Sky Airline",
            "OPERA_Copa Air"
        ]

        
        if target_column:
            def get_period_day(date):
                date_time = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').time()
                morning_min = datetime.strptime("05:00", '%H:%M').time()
                morning_max = datetime.strptime("11:59", '%H:%M').time()
                afternoon_min = datetime.strptime("12:00", '%H:%M').time()
                afternoon_max = datetime.strptime("18:59", '%H:%M').time()
                evening_min = datetime.strptime("19:00", '%H:%M').time()
                evening_max = datetime.strptime("23:59", '%H:%M').time()
                night_min = datetime.strptime("00:00", '%H:%M').time()
                night_max = datetime.strptime("04:59", '%H:%M').time()

                if(date_time > morning_min and date_time < morning_max):
                    return 'mañana'
                elif(date_time > afternoon_min and date_time < afternoon_max):
                    return 'tarde'
                elif(
                    (date_time > evening_min and date_time < evening_max) or
                    (date_time > night_min and date_time < night_max)
                ):
                    return 'noche'

            data['period_day'] = data['Fecha-I'].apply(get_period_day)

            def is_high_season(fecha):
                fecha_año = int(fecha.split('-')[0])
                fecha = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S')
                range1_min = datetime.strptime('15-Dec', '%d-%b').replace(year = fecha_año)
                range1_max = datetime.strptime('31-Dec', '%d-%b').replace(year = fecha_año)
                range2_min = datetime.strptime('1-Jan', '%d-%b').replace(year = fecha_año)
                range2_max = datetime.strptime('3-Mar', '%d-%b').replace(year = fecha_año)
                range3_min = datetime.strptime('15-Jul', '%d-%b').replace(year = fecha_año)
                range3_max = datetime.strptime('31-Jul', '%d-%b').replace(year = fecha_año)
                range4_min = datetime.strptime('11-Sep', '%d-%b').replace(year = fecha_año)
                range4_max = datetime.strptime('30-Sep', '%d-%b').replace(year = fecha_año)
            
                if ((fecha >= range1_min and fecha <= range1_max) or 
                    (fecha >= range2_min and fecha <= range2_max) or 
                    (fecha >= range3_min and fecha <= range3_max) or
                    (fecha >= range4_min and fecha <= range4_max)):
                    return 1
                else:
                    return 0
            
            data['high_season'] = data['Fecha-I'].apply(is_high_season)

            def get_min_diff(data):
                fecha_o = datetime.strptime(data['Fecha-O'], '%Y-%m-%d %H:%M:%S')
                fecha_i = datetime.strptime(data['Fecha-I'], '%Y-%m-%d %H:%M:%S')
                min_diff = ((fecha_o - fecha_i).total_seconds())/60
                return min_diff
            data['min_diff'] = data.apply(get_min_diff, axis = 1)

            threshold_in_minutes = 15
            data['delay'] = np.where(data['min_diff'] > threshold_in_minutes, 1, 0)
            features = data.drop(columns=[target_column])
            features = pd.concat([
                pd.get_dummies(data['OPERA'], prefix = 'OPERA'),
                pd.get_dummies(data['TIPOVUELO'], prefix = 'TIPOVUELO'), 
                pd.get_dummies(data['MES'], prefix = 'MES')], 
                axis = 1
            )
            features= features[top_10_features]
            target = data[[target_column]]
            return features, target
        else:
            features = pd.get_dummies(data, columns=["OPERA", "TIPOVUELO", "MES"])
            features = features.reindex(columns=top_10_features, fill_value=0)
            return features

    def fit(
        self,
        features: pd.DataFrame,
        target: pd.DataFrame
    ) -> None:
        """
        Fit model with preprocessed data.

        Args:
            features (pd.DataFrame): preprocessed data.
            target (pd.DataFrame): target.
        """

        #Data balance
        n_y0 = len(target[target == 0])
        n_y1 = len(target[target == 1])
        scale = 4.4402380952380955
        # Create an XGBoost model
        xgb_model = xgb.XGBClassifier(random_state=1, learning_rate=0.01, scale_pos_weight = scale)

        # Train the model on the training data
        xgb_model.fit(features, target)

        # Set the trained XGBoost model to the _model attribute
        self._model = xgb_model

    def predict(
        self,
        features: pd.DataFrame
    ) -> List[int]:
        """
        Predict delays for new flights.

        Args:
            features (pd.DataFrame): preprocessed data.
        
        Returns:
            (List[int]): predicted targets.
        """
        if self._model is None:
            print('No se ha entrenado el modelo')
            
        # Use the trained XGBoost model to make predictions
        predictions = self._model.predict(features)

        # Convert the predicted probabilities to 0 or 1 based on a threshold (e.g., 0.5)
        binary_predictions = [1 if prob > 0.5 else 0 for prob in predictions]

        return binary_predictions
