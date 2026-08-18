import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np



def prepare_trend_data(history_data):


    df = pd.DataFrame(history_data)



    if df.empty:

        return None



    # Remove missing sentiment

    df = df.dropna(
        subset=["Sentiment"]
    )



    # Convert to uppercase

    df["Sentiment"] = df["Sentiment"].str.upper()



    sentiment_score = {

        "NEGATIVE": -1,

        "NEUTRAL": 0,

        "POSITIVE": 1

    }



    # Convert sentiment to score

    df["score"] = df["Sentiment"].map(
        sentiment_score
    )



    # Remove unknown values

    df = df.dropna(
        subset=["score"]
    )



    if df.empty:

        return None



    df["index"] = range(
        len(df)
    )



    return df





def predict_trend(history_data):


    df = prepare_trend_data(
        history_data
    )



    if df is None or len(df) < 3:

        return None



    X = df[["index"]]

    y = df["score"]



    model = LinearRegression()



    model.fit(
        X,
        y
    )



    future_index = np.array(
        range(
            len(df),
            len(df)+7
        )
    ).reshape(-1,1)



    prediction = model.predict(
        future_index
    )



    return prediction