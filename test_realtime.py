from firebase_config import live_sentiment_ref
from datetime import datetime


test_data = {
    "text": "I love this product",
    "sentiment": "Positive",
    "confidence": 0.95,
    "timestamp": datetime.now().isoformat()
}


new_record = live_sentiment_ref.push(test_data)

print("Data saved successfully")
print("Record ID:", new_record.key)