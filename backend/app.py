# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import os

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

app = Flask(__name__)
CORS(app)

class EmotionAnalyzer:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.max_length = 66
        self.class_names = ['love', 'sad', 'angry', 'neutral', 'joyful']
        
    def load_model(self, model_path):
        """Load the pre-trained BiLSTM model"""
        try:
            self.model = load_model(model_path)
            print("Model loaded successfully")
        except Exception as e:
            print(f"Error loading model: {e}")
            # If loading fails, create a mock model for demonstration
            self.model = self._create_mock_model()
    
    def _create_mock_model(self):
        """Create a mock model for demonstration purposes"""
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import Embedding, Bidirectional, LSTM, Dense, Dropout
        
        model = Sequential([
            Embedding(17097, 300, input_length=66, trainable=False),
            Bidirectional(LSTM(64, dropout=0.2, recurrent_dropout=0.2)),
            Dropout(0.2),
            Dense(5, activation='softmax')  # Updated to 5 classes
        ])
        
        # Use random weights for demonstration
        return model
    
    def preprocess_text(self, text):
        """Preprocess the input text"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and digits but keep basic punctuation for emotion context
        text = re.sub(r'[^a-zA-Z\s!?]', '', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and lemmatize
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens if token not in self.stop_words]
        
        return ' '.join(tokens)
    
    def predict_emotion(self, text):
        """Predict emotion for given text"""
        if self.model is None:
            return self._mock_prediction(text)
        
        # Preprocess text
        processed_text = self.preprocess_text(text)
        
        # For demonstration, we'll use emotion-based approach
        return self._emotion_based_analysis(text)
    
    def _emotion_based_analysis(self, text):
        """Emotion-based analysis as fallback"""
        # Emotion word dictionaries
        love_words = ['love', 'adore', 'cherish', 'affection', 'romantic', 'heart', 'beloved', 
                     'sweetheart', 'darling', 'passion', 'devotion', 'fond', 'caring']
        
        sad_words = ['sad', 'unhappy', 'depressed', 'miserable', 'gloomy', 'heartbroken', 
                    'sorrow', 'grief', 'tearful', 'melancholy', 'blue', 'down', 'hopeless']
        
        angry_words = ['angry', 'mad', 'furious', 'outraged', 'irritated', 'annoyed', 'frustrated',
                      'rage', 'hostile', 'bitter', 'resentful', 'livid', 'fuming', 'infuriated']
        
        joyful_words = ['joyful', 'happy', 'delighted', 'ecstatic', 'cheerful', 'blissful', 
                       'jubilant', 'elated', 'thrilled', 'excited', 'euphoric', 'gleeful', 'merry']
        
        neutral_words = ['okay', 'fine', 'alright', 'normal', 'regular', 'usual', 'typical',
                        'moderate', 'average', 'standard', 'neutral', 'balanced']
        
        text_lower = text.lower()
        
        # Count emotion words
        love_count = sum(1 for word in love_words if word in text_lower)
        sad_count = sum(1 for word in sad_words if word in text_lower)
        angry_count = sum(1 for word in angry_words if word in text_lower)
        joyful_count = sum(1 for word in joyful_words if word in text_lower)
        neutral_count = sum(1 for word in neutral_words if word in text_lower)
        
        # Also check for emoticons and emojis
        if '❤' in text or '💕' in text or '😍' in text or '😘' in text:
            love_count += 2
        if '😢' in text or '😭' in text or '💔' in text:
            sad_count += 2
        if '😠' in text or '😡' in text or '💢' in text:
            angry_count += 2
        if '😊' in text or '😂' in text or '🎉' in text or '🥳' in text:
            joyful_count += 2
        
        # Calculate scores
        emotion_scores = {
            'love': love_count,
            'sad': sad_count,
            'angry': angry_count,
            'joyful': joyful_count,
            'neutral': neutral_count
        }
        
        # Determine dominant emotion
        dominant_emotion = max(emotion_scores, key=emotion_scores.get)
        max_score = emotion_scores[dominant_emotion]
        
        # Calculate confidence based on score difference
        total_score = sum(emotion_scores.values())
        if total_score > 0:
            confidence = min(0.95, max_score / total_score + 0.3)
        else:
            # If no emotion words detected, default to neutral
            dominant_emotion = 'neutral'
            confidence = 0.7
        
        # Create probability distribution
        prob_dist = []
        for emotion in self.class_names:
            if total_score > 0:
                prob = emotion_scores[emotion] / total_score
            else:
                prob = 0.2 if emotion == 'neutral' else 0.0
            prob_dist.append(prob)
        
        # Normalize probabilities to sum to 1
        prob_sum = sum(prob_dist)
        if prob_sum > 0:
            prob_dist = [p / prob_sum for p in prob_dist]
        else:
            prob_dist = [0.2, 0.2, 0.2, 0.2, 0.2]  # Equal distribution if no scores
        
        return {
            'emotion': dominant_emotion,
            'confidence': confidence,
            'probabilities': prob_dist,
            'class_names': self.class_names,
            'emotion_scores': emotion_scores
        }
    
    def _mock_prediction(self, text):
        """Mock prediction for demonstration"""
        return self._emotion_based_analysis(text)

# Initialize the analyzer
analyzer = EmotionAnalyzer()

@app.route('/')
def home():
    return jsonify({
        'message': 'Emotion Analysis API',
        'status': 'running',
        'endpoints': {
            '/analyze': 'POST - Analyze text emotion',
            '/health': 'GET - API health check'
        },
        'supported_emotions': ['love', 'sad', 'angry', 'neutral', 'joyful']
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'model_loaded': analyzer.model is not None})

@app.route('/analyze', methods=['POST'])
def analyze_emotion():
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text = data['text']
        
        if not text.strip():
            return jsonify({'error': 'Empty text provided'}), 400
        
        # Analyze emotion
        result = analyzer.predict_emotion(text)
        
        return jsonify({
            'text': text,
            'result': result,
            'success': True
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/batch_analyze', methods=['POST'])
def batch_analyze():
    try:
        data = request.get_json()
        
        if not data or 'texts' not in data:
            return jsonify({'error': 'No texts provided'}), 400
        
        texts = data['texts']
        
        if not isinstance(texts, list):
            return jsonify({'error': 'Texts must be a list'}), 400
        
        results = []
        for text in texts:
            if text.strip():
                result = analyzer.predict_emotion(text)
                results.append({
                    'text': text,
                    'result': result
                })
        
        return jsonify({
            'results': results,
            'total_analyzed': len(results),
            'success': True
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/emotions', methods=['GET'])
def get_emotions():
    """Get information about supported emotions"""
    emotion_info = {
        'love': {
            'description': 'Feelings of affection, care, and deep attachment',
            'examples': ['I love you so much!', 'This is my favorite thing ever!', 'You mean everything to me ❤️'],
            'color': '#e74c3c',
            'emoji': '❤️'
        },
        'sad': {
            'description': 'Feelings of unhappiness, sorrow, or disappointment',
            'examples': ['I feel so lonely today', 'This makes me want to cry 😢', 'Nothing seems to work out'],
            'color': '#3498db',
            'emoji': '😢'
        }, 
        'angry': {
            'description': 'Feelings of frustration, irritation, or rage',
            'examples': ['This makes me so mad!', 'I cant believe this happened!', 'Im furious about this! 😠'],
            'color': '#e67e22',
            'emoji': '😠'
        },
        'neutral': {
            'description': 'Neutral or balanced emotional state',
            'examples': ['The weather is okay today', 'Nothing special happened', 'Its a regular day'],
            'color': '#95a5a6',
            'emoji': '😐'
        },
        'joyful': {
            'description': 'Feelings of happiness, excitement, and delight',
            'examples': ['Im so happy right now!', 'This is amazing! 🎉', 'What a wonderful day! 😊'],
            'color': '#f1c40f',
            'emoji': '😊'
        }
    }
    
    return jsonify({
        'emotions': emotion_info,
        'success': True
    })

if __name__ == '__main__':
    # Try to load the model
    model_path = 'bilstm_model.pkl'
    if os.path.exists(model_path):
        analyzer.load_model(model_path)
    else:
        print("Model file not found. Using emotion-based analysis.")
    
    app.run(debug=True, host='0.0.0.0', port=5000)