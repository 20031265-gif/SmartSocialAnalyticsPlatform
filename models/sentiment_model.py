from transformers import pipeline


# Load 3-class sentiment model

sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment"
)



def analyse_sentiment(text):

    result = sentiment_pipeline(text)[0]


    label = result["label"]


    # Convert model labels

    if label == "LABEL_2":
        sentiment = "POSITIVE"

    elif label == "LABEL_1":
        sentiment = "NEUTRAL"

    else:
        sentiment = "NEGATIVE"



    return {

        "sentiment": sentiment,

        "confidence": round(
            result["score"] * 100,
            2
        )

    }