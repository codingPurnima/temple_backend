import os
import json
import firebase_admin
from firebase_admin import credentials

if "FIREBASE_SERVICE_ACCOUNT_JSON" in os.environ:
    firebase_credentials = json.loads(
        os.environ["FIREBASE_SERVICE_ACCOUNT_JSON"]
    )
    cred = credentials.Certificate(firebase_credentials)
else:
    cred = credentials.Certificate(
        "app/firebase/serviceAccountKey.json"
    )

firebase_admin.initialize_app(cred)