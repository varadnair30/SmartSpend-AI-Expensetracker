# api/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated 
from .serializers import YourDataSerializer  

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics.pairwise import cosine_similarity

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
nltk.download('punkt')
nltk.download('stopwords')


# Utility: Text Preprocessing
def preprocess_text(text):
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(text.lower())
    tokens = [t for t in tokens if t.isalnum() and t not in stop_words]
    return ' '.join(tokens)


# API Endpoint: Predict Expense Category
class PredictCategory(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_input = request.data.get('description')

        # Load existing dataset
        data = pd.read_csv('dataset.csv')

        # Preprocess the input text
        user_input = preprocess_text(user_input)

        # Vectorization & Model Training
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_vectorizer.fit(data['clean_description'])
        X = tfidf_vectorizer.transform(data['clean_description'])

        model = RandomForestClassifier()
        model.fit(X, data['category'])

        # Prediction
        user_input_vector = tfidf_vectorizer.transform([user_input])
        similarities = cosine_similarity(user_input_vector, X)
        closest_match_index = similarities.argmax()
        predicted_category = model.predict(X[closest_match_index])

        return Response({'predicted_category': predicted_category[0]}, status=status.HTTP_200_OK)


# API Endpoint: Add New Data to Dataset
class UpdateDataset(APIView):
    # Optional: Enable if you want authenticated access
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        new_data = request.data.get('new_data')

        if 'description' in new_data and 'category' in new_data:
            # Load existing dataset
            data = pd.read_csv('dataset.csv')

            # Preprocess and append new data
            new_row = {
                'description': new_data['description'],
                'category': new_data['category'],
                'clean_description': preprocess_text(new_data['description'])
            }
            data = pd.concat([data, pd.DataFrame([new_row])], ignore_index=True)
            data.to_csv('dataset.csv', index=False)

            # Retrain the model (optional - just for consistency)
            tfidf_vectorizer = TfidfVectorizer()
            tfidf_vectorizer.fit(data['clean_description'])
            X = tfidf_vectorizer.transform(data['clean_description'])

            model = RandomForestClassifier()
            model.fit(X, data['category'])

            return Response({'message': 'Dataset updated and model retrained.'}, status=200)

        return Response({'error': 'Missing fields in new_data'}, status=400)
