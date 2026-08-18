import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import db as realtime_db


# ==========================================
# Initialize Firebase
# ==========================================

if not firebase_admin._apps:

    cred = credentials.Certificate(
        "firebase_key.json"
    )

    firebase_admin.initialize_app(
        cred,
        {
            "databaseURL":
            "https://smartsocialanalyticsplatform-default-rtdb.firebaseio.com/"
        }
    )


# ==========================================
# Firestore Database
# ==========================================

# Keep this name as "db" because auth.py uses it
db = firestore.client()


# ==========================================
# Firebase Realtime Database
# ==========================================

live_posts_ref = realtime_db.reference(
    "live_posts"
)

live_sentiment_ref = realtime_db.reference(
    "live_sentiment"
)

live_trends_ref = realtime_db.reference(
    "live_trends"
)