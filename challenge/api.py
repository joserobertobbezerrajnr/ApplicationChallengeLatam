import fastapi
import pandas as pd
from typing import List
from challenge.model import DelayModel
from pydantic import BaseModel
from fastapi import HTTPException

app = fastapi.FastAPI()

class Flight(BaseModel):
    OPERA: str
    TIPOVUELO: str
    MES: int

class FlightData(BaseModel):
    flights: List[Flight]

@app.get("/health", status_code=200)
async def get_health() -> dict:
    return {
        "status": "OK"
    }

#EndPoint for predict the delay of a flight
@app.post("/predict", status_code=200)
async def post_predict(codigo: FlightData) -> dict:
        predictions = []
        for flight in codigo.flights:
            error_text = ''
            #Check if OPERA and Mes is valid
            if (flight.TIPOVUELO not in ['N', 'I']) or (flight.MES < 1 or flight.MES > 12):
                error_text=f"TIPOVUELO o MES no válido para el vuelo con OPERA {flight.OPERA}"
                raise HTTPException(status_code=400, detail=error_text)
            else: #Predict the delay
                df = pd.DataFrame([flight.dict()])
                features = model.preprocess(
                data=df
                )
                prediction = model.predict(features=features)
                predictions=prediction
                return {"predict":  predictions}

#Initialize the model
def initialize_model():
    data = pd.read_csv(filepath_or_buffer="./data/data.csv")
    model = DelayModel()
    features, target = model.preprocess(
        data=data,
        target_column="delay"
    )
    model.fit(features, target)
    return model

if "__main__" == "__main__":
    model = initialize_model()


