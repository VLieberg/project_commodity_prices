import numpy as np
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from dateutil.relativedelta import relativedelta
import joblib



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
def index():
    return {"greeting": "Hello world"}


@app.get("/csv")
def index():
    df_fut_price = pd.read_csv("gs://commodity-price-storage/dataset_daily_prices_soybean/soybean_daily_price.csv").to_dict()
    df_predc_price = pd.read_csv("gs://commodity-price-storage/dataset_daily_prices_soybean/predicted_soybean_prices.csv").to_dict()

    return [df_fut_price,df_predc_price]


@app.get("/predict")
def predict():
    # GET TODO: get model from GCP
    df_soybean = pd.read_csv('gs://commodity-price-storage/dataset_daily_prices_soybean/soybean_daily_price.csv')
    X = df_soybean[-253:].drop(columns = 'Date').to_numpy().reshape(1,253,5)
    soybean_date = pd.to_datetime(df_soybean['Date'])
    date = soybean_date.iloc[-1]
    month_days = [date + relativedelta(days=+days) for days in range(1,32) if datetime.weekday(date + relativedelta(days=+days)) < 5]
    month_days = month_days[:23]


    # pipeline = get_model_from_gcp()
    pipeline = joblib.load('model.joblib')

    # make prediction
    results = pipeline.predict(X)
    dicionario = {}
    for result , month in zip(results[0].tolist(), month_days):
        date_format = '%Y/%m/%d'
        month_str = month.strftime(date_format)
        dicionario[month_str] = result
    return dicionario
