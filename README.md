# 🛡️ Spam Message Detection System

**Aditya University – CSE NLP Project**  
Team: P. Rohith · V. Sri Ramcharan · T.S.N. Srikhar Reddy

---

## Overview

An end-to-end NLP + Machine Learning system that classifies incoming SMS and
email messages as **Spam** or **Legitimate (Ham)**. Built with Python, scikit-learn,
NLTK, and Flask.

---

## Project Structure

```
spam_detection/
├── data/
│   └── spam_dataset.csv        # 100-sample labelled dataset
├── models/                     # Saved model artefacts (auto-created after training)
│   ├── spam_model.pkl
│   ├── tfidf_vectorizer.pkl
│   └── model_meta.pkl
├── templates/
│   └── index.html              # Web UI
├── train.py                    # Preprocessing + model training
├── predictor.py                # Inference module (used by Flask + CLI)
├── app.py                      # Flask web application
├── requirements.txt
└── README.md
```

---

## Workflow

```
Message Input
    ↓
Data Cleaning / Preprocessing
  • Lowercase
  • Remove URLs, emails, phone numbers
  • Strip punctuation / special characters
  • Tokenisation
  • Stopword removal (NLTK English)
  • Porter Stemming
    ↓
TF-IDF Feature Extraction
  (max 3000 features, unigrams + bigrams)
    ↓
Model Training  (3 classifiers compared)
  • Multinomial Naive Bayes
  • Logistic Regression
  • Linear SVM
    ↓
Best Model Selected (by F1 score)
    ↓
Spam / Legitimate Prediction
```

---

## Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Train the model
```bash
python train.py
```
This prints accuracy, precision, recall and F1 for all three classifiers,
saves the best model to `models/`, and shows a confusion matrix.

### 3. Start the web app
```bash
python app.py
```
Open **http://127.0.0.1:5000** in your browser.

### 4. (Optional) Quick CLI test
```bash
python predictor.py
```

---

## Dataset

| Attribute       | Details                                     |
|-----------------|---------------------------------------------|
| Source          | Publicly available spam datasets (curated)  |
| Format          | CSV                                         |
| Size            | 100 messages (50 spam, 50 ham)              |
| Columns         | `label`, `message`                          |
| Label values    | `spam`, `ham`                               |
| Features used   | Message text, length, keywords, URLs        |

---

## Tech Stack

| Component        | Technology                        |
|------------------|-----------------------------------|
| Language         | Python 3.10+                      |
| NLP              | NLTK (stopwords, stemming)        |
| ML               | scikit-learn                      |
| Feature Extraction | TF-IDF Vectorizer               |
| Web Framework    | Flask                             |
| Frontend         | HTML5 / CSS3 / Vanilla JS         |

---

## Expected Outcomes

- Automatically identify spam in SMS and email messages  
- Classify newly entered messages as spam or legitimate in real time  
- Detect suspicious messages before they reach the user  
- Improve user safety on SMS and email platforms  
- Reduce exposure to fraudulent and unwanted communication  

---

## Future Enhancements

- Integrate larger datasets (e.g., UCI SMS Spam Collection ~5500 samples)  
- Experiment with advanced models: BERT, DistilBERT  
- Add multilingual support  
- Deploy as a REST API or browser extension  
