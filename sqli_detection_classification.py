# -*- coding: utf-8 -*-
"""sqli_detection_classification.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1aaQ1Mwg70g0kkh9VQgzXMW6V5LwII-aA
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

df_stage1 = pd.read_csv("all_attacks.csv")
df_stage1 = df_stage1[["payload", "type"]].dropna()
df_stage1.columns = ["payload", "label"]

df_stage2 = pd.read_csv("sqli_classification_dataset.csv")
df_stage2 = df_stage2[["payload", "label"]].dropna()

mapping = {
    "tautology": "SQLi",
    "boolean-blind": "SQLi",
    "error-based": "SQLi",
    "union": "SQLi",
    "stacked-queries": "SQLi",
    "blind-time": "SQLi",
    "stored": "XSS",
    "reflected": "XSS"

}


df_stage1["label"] = df_stage1["label"].replace(mapping)

print(df_stage1["label"].value_counts())

df_stage1

print("Stage 1 Labels:")
print(df_stage1['label'].value_counts())

print("\nStage 2 Labels:")
print(df_stage2['label'].value_counts())

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer


tfidf = TfidfVectorizer(ngram_range=(1, 4), max_features=3000, sublinear_tf=True)

X1 = tfidf.fit_transform(df_stage1["payload"])
y1 = df_stage1["label"]
X1_train, X1_test, y1_train, y1_test = train_test_split(X1, y1, test_size=0.2, stratify=y1, random_state=42)

X2 = tfidf.transform(df_stage2["payload"])
y2 = df_stage2["label"]
X2_train, X2_test, y2_train, y2_test = train_test_split(X2, y2, test_size=0.2, stratify=y2, random_state=42)

from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier
from sklearn.metrics import classification_report

models = {
    "Logistic Regression": LogisticRegression(max_iter=1000,class_weight='balanced'),
    "Naive Bayes": MultinomialNB(),
    "Random Forest": RandomForestClassifier(class_weight='balanced',random_state=42),
    "SVM": SVC(probability=True),
    "AdaBoost": AdaBoostClassifier(),
    "XGBoost": XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', random_state=42)

}

print("STAGE 1: Attack Detection Results\n")
stage1_results = {}

for name, model in models.items():
    if name == "XGBoost":
        from sklearn.preprocessing import LabelEncoder
        le = LabelEncoder()
        y1_train_encoded = le.fit_transform(y1_train)
        model.fit(X1_train, y1_train_encoded)
        y1_test_encoded = le.transform(y1_test)
        y_pred = model.predict(X1_test)
        y_pred_decoded = le.inverse_transform(y_pred)
        print(f" {name}")
        print(classification_report(y1_test, y_pred_decoded, zero_division=0))
        print("-" * 60)
        stage1_results[name] = model
    else:
        model.fit(X1_train, y1_train)
        y_pred = model.predict(X1_test)
        print(f" {name}")
        print(classification_report(y1_test, y_pred, zero_division=0))
        print("-" * 60)
        stage1_results[name] = model

print(stage1_results)

print("STAGE 2: SQLi Type Classification Results\n")
stage2_results = {}

for name, model in models.items():
    if name == "XGBoost":
        from sklearn.preprocessing import LabelEncoder
        le = LabelEncoder()
        y2_train_encoded = le.fit_transform(y2_train)
        model.fit(X2_train, y2_train_encoded)
        y2_test_encoded = le.transform(y2_test)
        y_pred = model.predict(X2_test)
        y_pred_decoded = le.inverse_transform(y_pred)
        print(f" {name}")
        print(classification_report(y2_test, y_pred_decoded, zero_division=0))
        print("-" * 60)
        stage2_results[name] = model
    else:
        model.fit(X2_train, y2_train)
        y_pred = model.predict(X2_test)
        print(f" {name}")
        print(classification_report(y2_test, y_pred, zero_division=0))
        print("-" * 60)
        stage2_results[name] = model

from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder

def get_f1_scores(X_test, y_test,X_train,y_train):
    scores = {}
    for name, model in models.items():
        if name == "XGBoost":
            le = LabelEncoder()
            y_train_encoded = le.fit_transform(y_train)
            model.fit(X_train, y_train_encoded)
            y_test_encoded = le.transform(y_test)
            y_pred = model.predict(X_test)
            y_pred_decoded = le.inverse_transform(y_pred)
            report = classification_report(y_test, y_pred_decoded, output_dict=True, zero_division=0)
        else:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)

        print(report)
        f1_macro = report['macro avg']['f1-score']
        scores[name] = round(f1_macro, 4)
    return scores

stage1_f1_scores = get_f1_scores(X1_test, y1_test,X1_train,y1_train)
stage2_f1_scores = get_f1_scores(X2_test, y2_test,X2_train,y2_train)

print("Stage 1 Model F1 Scores:")
for model, score in sorted(stage1_f1_scores.items(), key=lambda x: x[1], reverse=True):
    print(f"{model:<20} → F1: {score}")

print("\n Stage 2 Model F1 Scores:")
for model, score in sorted(stage2_f1_scores.items(), key=lambda x: x[1], reverse=True):
    print(f"{model:<20} → F1: {score}")

best_stage1_name = max(stage1_f1_scores, key=stage1_f1_scores.get)
best_stage2_name = max(stage2_f1_scores, key=stage2_f1_scores.get)

best_stage1_model = stage1_results[best_stage1_name]
best_stage2_model = stage2_results[best_stage2_name]

print(f"\n Best Stage 1 Model: {best_stage1_name}")
print(f" Best Stage 2 Model: {best_stage2_name}")

import joblib
joblib.dump(tfidf, "vectorizer.pkl")

from sklearn.preprocessing import LabelEncoder
import joblib  # for saving models

# Train and save Stage 1 model
for name, model in models.items():
    if name == best_stage1_name:
        if name == "XGBoost":
            le1 = LabelEncoder()
            y1_train_encoded = le1.fit_transform(y1_train)
            model.fit(X1_train, y1_train_encoded)
            joblib.dump(le1, "label_encoder_stage1.pkl")  # save label encoder
        else:
            model.fit(X1_train, y1_train)
        joblib.dump(model, "attack_detector.pkl")  # save trained model

# Train and save Stage 2 model
for name, model in models.items():
    if name == best_stage2_name:
        if name == "XGBoost":
            le2 = LabelEncoder()
            y2_train_encoded = le2.fit_transform(y2_train)
            model.fit(X2_train, y2_train_encoded)
            joblib.dump(le2, "label_encoder_stage2.pkl")  # save label encoder
        else:
            model.fit(X2_train, y2_train)
        joblib.dump(model, "sqli_classifier.pkl")  # save trained model

from sklearn.metrics import precision_score, recall_score
from sklearn.preprocessing import LabelEncoder

for name, model in models.items():
    if name == best_stage1_name:
        if best_stage1_name == "XGBoost":
          le = LabelEncoder()
          y_train_encoded = le.fit_transform(y1_train)
          model.fit(X1_train, y_train_encoded)
          y_test_encoded = le.transform(y1_test)
          y_pred = model.predict(X1_test)
          y_pred = le.inverse_transform(y_pred)
        else:
            model.fit(X1_train, y1_train)
            y_pred = model.predict(X1_test)
print("📈 Stage 1 Precision:", precision_score(y1_test, y_pred, average='macro', zero_division=0))
print("📈 Stage 1 Recall:", recall_score(y1_test, y_pred, average='macro', zero_division=0))

for name, model in models.items():
    if name == best_stage2_name:
        if best_stage2_name == "XGBoost":
          le = LabelEncoder()
          y_train_encoded = le.fit_transform(y2_train)
          model.fit(X2_train, y_train_encoded)
          y_test_encoded = le.transform(y2_test)
          y_pred = model.predict(X2_test)
          y_pred = le.inverse_transform(y_pred)
        else:
            model.fit(X2_train, y2_train)
            y_pred = model.predict(X2_test)
print("📈 Stage 2 Precision:", precision_score(y2_test, y_pred, average='macro', zero_division=0))
print("📈 Stage 2 Recall:", recall_score(y2_test, y_pred, average='macro', zero_division=0))

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

best_stage1_model = joblib.load("attack_detector.pkl")
best_stage2_model = joblib.load("sqli_classifier.pkl")

le_stage2 = joblib.load("label_encoder_stage2.pkl")  # Only needed for SQLi type classification

tfidf = joblib.load("vectorizer.pkl")  # you must have saved this earlier

def detect_and_classify(payload):
    vec = tfidf.transform([payload])

    # Predict stage 1
    attack_type = best_stage1_model.predict(vec)
    print("Attack Detected:", attack_type)

    # Predict stage 2 if needed
    if attack_type == "SQLi":
        stage2_pred = best_stage2_model.predict(vec)
        sqli_type = le_stage2.inverse_transform(stage2_pred)[0] if le_stage2 else stage2_pred[0]

        return f"SQL Injection → {sqli_type}"
    else:
        return f"Detected: {attack_type}"

# Results
print(detect_and_classify("<script>alert('XSS3')</script>"))
print(detect_and_classify("<img src='https://target.com/delete-account?confirm=yes' style='display:none'/>"))
print(detect_and_classify("memcached://127.0.0.1:11211"))
print(detect_and_classify("; echo $(echo $(whoami)"))
print(detect_and_classify("Submit AND 7363=(SELECT COUNT(*) FROM SYSMASTER:SYSPAGHDR)# pHgf"))
print(detect_and_classify("UNION ALL SELECT 'INJ'||'ECT'||'XXX',2,3,4,5,6,7#"))
print(detect_and_classify("and (select substring(@@version,1,1))='X'"))
print(detect_and_classify(" or pg_sleep(5)--"))
print(detect_and_classify(" admin or 1=1"))

import joblib
joblib.dump(best_stage1_model, "attack_detector.pkl")

import joblib
joblib.dump(best_stage2_model, "sqli_classifier.pkl")

from sklearn.metrics import ConfusionMatrixDisplay
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder

# Decode XGBoost predictions for Stage 1 if best model is XGBoost
y1_pred_decoded = best_stage1_model.predict(X1_test)
if best_stage1_name == "XGBoost":
    le1 = LabelEncoder()
    le1.fit(y1_train) # Fit on training labels to ensure all possible labels are included
    y1_pred_decoded = le1.inverse_transform(y1_pred_decoded)

ConfusionMatrixDisplay.from_predictions(y1_test, y1_pred_decoded, xticks_rotation=45)
plt.title("Stage 1 Confusion Matrix")
plt.show()

# Decode XGBoost predictions for Stage 2 if best model is XGBoost
y2_pred_decoded = best_stage2_model.predict(X2_test)
if best_stage2_name == "XGBoost":
    le2 = LabelEncoder()
    le2.fit(y2_train) # Fit on training labels to ensure all possible labels are included
    y2_pred_decoded = le2.inverse_transform(y2_pred_decoded)

ConfusionMatrixDisplay.from_predictions(y2_test, y2_pred_decoded, xticks_rotation=45)
plt.title("Stage 2 Confusion Matrix")
plt.show()