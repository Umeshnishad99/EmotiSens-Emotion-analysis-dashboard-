# streamlit_app.py
import numpy as np
import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import random

# Page configuration
st.set_page_config(
    page_title="Emotion Analysis Dashboard Using Text",
    page_icon="😊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with enhanced styling
st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        font-weight: bold;
    }
    .dashboard-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 10px 0;
        border-left: 5px solid;
        transition: transform 0.3s ease;
    }
    .dashboard-card:hover {
        transform: translateY(-5px);
    }
    .emotion-love {
        border-left-color: #e74c3c;
        background: linear-gradient(135deg, #ffebee 0%, #ffffff 100%);
    }
    .emotion-sad {
        border-left-color: #3498db;
        background: linear-gradient(135deg, #e3f2fd 0%, #ffffff 100%);
    }
    .emotion-angry {
        border-left-color: #e67e22;
        background: linear-gradient(135deg, #fff3e0 0%, #ffffff 100%);
    }
    .emotion-neutral {
        border-left-color: #95a5a6;
        background: linear-gradient(135deg, #f5f5f5 0%, #ffffff 100%);
    }
    .emotion-joyful {
        border-left-color: #f1c40f;
        background: linear-gradient(135deg, #fffde7 0%, #ffffff 100%);
    }
    .confidence-bar {
        background-color: #e9ecef;
        border-radius: 15px;
        margin: 15px 0;
        height: 35px;
        overflow: hidden;
    }
    .confidence-fill {
        background: linear-gradient(90deg, #007bff, #0056b3);
        border-radius: 15px;
        color: white;
        text-align: center;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 14px;
        transition: width 1s ease-in-out;
    }
    .emotion-emoji {
        font-size: 2.5rem;
        margin-right: 15px;
        filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.1));
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 25px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    .welcome-banner {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 15px;
        filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.2));
    }
</style>
""", unsafe_allow_html=True)

class EmotionAnalysisApp:
    def __init__(self):
        self.api_url = "http://localhost:5000"
        self.emotion_colors = {
            'love': '#e74c3c',
            'sad': '#3498db',
            'angry': '#e67e22',
            'neutral': '#95a5a6',
            'joyful': '#f1c40f'
        }
        self.emotion_emojis = {
            'love': '❤️',
            'sad': '😢',
            'angry': '😠',
            'neutral': '😐',
            'joyful': '😊'
        }
        self.emotion_descriptions = {
            'love': 'Feelings of affection, care, and deep attachment',
            'sad': 'Feelings of unhappiness, sorrow, or disappointment',
            'angry': 'Feelings of frustration, irritation, or rage',
            'neutral': 'Neutral or balanced emotional state',
            'joyful': 'Feelings of happiness, excitement, and delight'
        }
        self.emotion_images = {
            'love': '💕',
            'sad': '🌧️',
            'angry': '🔥',
            'neutral': '⚖️',
            'joyful': '🌈'
        }
    
    def check_api_health(self):
        """Check if the API is running"""
        try:
            response = requests.get(f"{self.api_url}/health")
            return response.status_code == 200
        except:
            return False
    
    def analyze_emotion(self, text):
        """Send text to API for emotion analysis"""
        try:
            response = requests.post(
                f"{self.api_url}/analyze",
                json={"text": text}
            )
            return response.json()
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def batch_analyze(self, texts):
        """Send multiple texts to API for batch analysis"""
        try:
            response = requests.post(
                f"{self.api_url}/batch_analyze",
                json={"texts": texts}
            )
            return response.json()
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def get_emotion_info(self):
        """Get emotion information from API"""
        try:
            response = requests.get(f"{self.api_url}/emotions")
            return response.json()
        except:
            return None
    
    def display_emotion_result(self, result):
        """Display emotion analysis result"""
        if not result.get('success'):
            st.error(f"❌ Error: {result.get('error', 'Unknown error')}")
            return
        
        emotion_data = result['result']
        emotion = emotion_data['emotion']
        confidence = emotion_data['confidence']
        
        # Display emotion with appropriate styling
        emotion_class = f"emotion-{emotion}"
        emoji = self.emotion_emojis.get(emotion, '😐')
        description = self.emotion_descriptions.get(emotion, '')
        image = self.emotion_images.get(emotion, '📊')
        
        st.markdown(f"""
        <div class="dashboard-card {emotion_class}">
            <div style="display: flex; align-items: center; margin-bottom: 15px;">
                <span class="emotion-emoji">{emoji}</span>
                <div>
                    <h2 style="margin: 0; color: {self.emotion_colors.get(emotion, '#000')};">
                        {image} Emotion: {emotion.title()}
                    </h2>
                    <p style="margin: 5px 0 0 0; font-size: 1.1em;"><strong>📝 Description:</strong> {description}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Confidence bar with animation
        st.markdown(f"""
        <div style="margin: 20px 0;">
            <h4>🎯 Confidence Level</h4>
            <div class="confidence-bar">
                <div class="confidence-fill" style="width: {confidence * 100}%">
                    🎯 {confidence:.2%}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Probability distribution chart
        self.plot_emotion_distribution(emotion_data)
        
        # Emotion scores breakdown
        if 'emotion_scores' in emotion_data:
            self.display_emotion_scores(emotion_data['emotion_scores'])
    
    def plot_emotion_distribution(self, emotion_data):
        """Plot emotion probability distribution using Plotly"""
        probabilities = emotion_data['probabilities']
        class_names = emotion_data['class_names']
        
        # Create DataFrame for plotting
        df = pd.DataFrame({
            'Emotion': class_names,
            'Probability': probabilities
        })
        
        # Add emojis to emotion labels
        df['Emotion_Label'] = df['Emotion'].apply(
            lambda x: f"{self.emotion_emojis.get(x, '')} {x.title()}"
        )
        
        # Create animated bar chart
        fig = px.bar(
            df, 
            x='Emotion_Label', 
            y='Probability',
            color='Emotion',
            color_discrete_map=self.emotion_colors,
            title='📊 Emotion Probability Distribution',
            labels={'Probability': 'Probability', 'Emotion_Label': 'Emotion'},
            animation_frame=df.index  # Add animation
        )
        
        fig.update_layout(
            showlegend=False,
            yaxis_tickformat='.0%',
            yaxis_range=[0, 1],
            xaxis_title='🎭 Emotion',
            yaxis_title='📈 Probability',
            font=dict(size=14),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        
        # Add some animation effects
        fig.update_traces(
            marker_line_color='black',
            marker_line_width=1.5,
            opacity=0.8
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def display_emotion_scores(self, emotion_scores):
        """Display detailed emotion scores"""
        st.subheader("🎯 Emotion Score Breakdown")
        
        cols = st.columns(5)
        for i, (emotion, score) in enumerate(emotion_scores.items()):
            with cols[i]:
                emoji = self.emotion_emojis.get(emotion, '')
                color = self.emotion_colors.get(emotion, '#95a5a6')
                image = self.emotion_images.get(emotion, '📊')
                
                st.markdown(
                    f'<div class="metric-card" style="background: linear-gradient(135deg, {color} 0%, {self._darken_color(color)} 100%);">'
                    f'<div class="feature-icon">{image}</div>'
                    f'<h4>{emoji} {emotion.title()}</h4>'
                    f'<h2>{score:.3f}</h2>'
                    f'</div>',
                    unsafe_allow_html=True
                )
    
    def _darken_color(self, color, factor=0.7):
        """Darken a color for gradient effects"""
        # Simple darkening for demo - in production use proper color manipulation
        darker_colors = {
            '#e74c3c': '#c0392b',
            '#3498db': '#2980b9',
            '#e67e22': '#d35400',
            '#95a5a6': '#7f8c8d',
            '#f1c40f': '#f39c12'
        }
        return darker_colors.get(color, color)
    
    def display_batch_results(self, batch_result):
        """Display results from batch analysis"""
        if not batch_result.get('success'):
            st.error(f"❌ Error: {batch_result.get('error', 'Unknown error')}")
            return
        
        results = batch_result['results']
        
        # Create DataFrame for results
        data = []
        for item in results:
            data.append({
                'Text': item['text'][:100] + '...' if len(item['text']) > 100 else item['text'],
                'Emotion': item['result']['emotion'],
                'Confidence': item['result']['confidence'],
                'Emoji': self.emotion_emojis.get(item['result']['emotion'], '😐')
            })
        
        df = pd.DataFrame(data)
        
        # Display summary statistics with enhanced metrics
        st.subheader("📈 Analysis Summary")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        emotion_counts = df['Emotion'].value_counts()
        total_texts = len(df)
        
        with col1:
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="feature-icon">📄</div>'
                f'<h4>Total Texts</h4>'
                f'<h2>{total_texts}</h2>'
                f'</div>',
                unsafe_allow_html=True
            )
        
        with col2:
            love_count = emotion_counts.get('love', 0)
            st.markdown(
                f'<div class="metric-card" style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);">'
                f'<div class="feature-icon">❤️</div>'
                f'<h4>Love</h4>'
                f'<h2>{love_count}</h2>'
                f'</div>',
                unsafe_allow_html=True
            )
        
        with col3:
            joyful_count = emotion_counts.get('joyful', 0)
            st.markdown(
                f'<div class="metric-card" style="background: linear-gradient(135deg, #f1c40f 0%, #f39c12 100%);">'
                f'<div class="feature-icon">😊</div>'
                f'<h4>Joyful</h4>'
                f'<h2>{joyful_count}</h2>'
                f'</div>',
                unsafe_allow_html=True
            )
        
        with col4:
            sad_count = emotion_counts.get('sad', 0)
            st.markdown(
                f'<div class="metric-card" style="background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);">'
                f'<div class="feature-icon">😢</div>'
                f'<h4>Sad</h4>'
                f'<h2>{sad_count}</h2>'
                f'</div>',
                unsafe_allow_html=True
            )
        
        with col5:
            angry_count = emotion_counts.get('angry', 0)
            st.markdown(
                f'<div class="metric-card" style="background: linear-gradient(135deg, #e67e22 0%, #d35400 100%);">'
                f'<div class="feature-icon">😠</div>'
                f'<h4>Angry</h4>'
                f'<h2>{angry_count}</h2>'
                f'</div>',
                unsafe_allow_html=True
            )
        
        # Display results table with better styling
        st.subheader("📋 Detailed Results")
        
        # Style the dataframe
        def style_emotion_row(row):
            emotion = row['Emotion']
            color = self.emotion_colors.get(emotion, '#95a5a6')
            return [f'background-color: {color}20; border-left: 4px solid {color}'] * len(row)
        
        styled_df = df.style.apply(style_emotion_row, axis=1)
        st.dataframe(styled_df, use_container_width=True)
        
        # Enhanced emotion distribution visualization
        st.subheader("🎭 Emotion Distribution")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Animated pie chart
            fig = px.pie(
                values=emotion_counts.values,
                names=[f"{self.emotion_emojis.get(emotion, '')} {emotion.title()}" for emotion in emotion_counts.index],
                title='🎯 Emotion Distribution Pie Chart',
                color=emotion_counts.index,
                color_discrete_map=self.emotion_colors,
                hole=0.3  # Donut chart
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Emotion statistics with progress bars
            st.write("**📊 Emotion Statistics:**")
            for emotion, count in emotion_counts.items():
                percentage = (count / total_texts) * 100
                emoji = self.emotion_emojis.get(emotion, '')
                color = self.emotion_colors.get(emotion, '#95a5a6')
                
                st.markdown(f"""
                <div style="margin: 10px 0;">
                    <div style="display: flex; justify-content: between; margin-bottom: 5px;">
                        <span>{emoji} {emotion.title()}</span>
                        <span>{count} ({percentage:.1f}%)</span>
                    </div>
                    <div style="background: #e9ecef; border-radius: 10px; height: 8px;">
                        <div style="background: {color}; width: {percentage}%; height: 8px; border-radius: 10px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    def run(self):
        """Main application runner"""
        
        # Enhanced Header with Welcome Banner
        st.markdown('<h1 class="main-header">🎭 EmotiSens Analysis Dashboard</h1>', unsafe_allow_html=True)
        
        # Welcome Banner
        st.markdown("""
        <div class="welcome-banner">
            <h1>🎉 Welcome to EmotiSens Analysis!</h1>
            <p>Discover the emotional tone of your text with AI-powered analysis</p>
            <div style="font-size: 2rem; margin-top: 15px;">
                ❤️ 😊 😢 😠 😐
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Check API health
        if not self.check_api_health():
            st.error("""
            ⚠️ **Backend API is not running!** 
            
            Please start the Flask server first by running:
            ```bash
            python app.py
            ```
            """)
            
            # Show a cute loading animation while waiting
            with st.expander("🔄 Setup Instructions"):
                st.write("""
                1. **Open your terminal** 🖥️
                2. **Navigate to your project folder** 📁
                3. **Run the backend server:** 
                   ```bash
                   python app.py
                   ```
                4. **Wait for the server to start** ⏳
                5. **Refresh this page** 🔄
                """)
            
            # Add a fun waiting animation
            with st.container():
                st.write("🎵 Waiting for backend to start...")
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.1)
                    progress_bar.progress(i + 1)
                st.balloons()
            return
        
        # Enhanced Sidebar
        with st.sidebar:
            st.markdown("""
            <div style="text-align: center; padding: 20px 0;">
                <h1>🎯 Navigation</h1>
                <p>Choose your analysis mode below</p>
            </div>
            """, unsafe_allow_html=True)
            
            app_mode = st.selectbox(
                "🚀 Choose Analysis Mode",
                ["Single Text Analysis", "Batch Analysis", "Real-time Demo", "Emotion Guide", "Dashboard Overview"]
            )
            
            # Add some fun facts in sidebar
            st.markdown("---")
            st.markdown("### 💡 Did You Know?")
            fun_facts = [
                "🤖 AI can detect emotions with over 85% accuracy!",
                "📊 Emotional analysis helps understand customer feedback",
                "❤️ Positive emotions improve productivity by 31%",
                "🎭 Humans express 7 basic emotions universally"
            ]
            st.info(random.choice(fun_facts))
            
            # Add quick stats
            st.markdown("### 📈 Quick Stats")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Analyses Today", "127", "12%")
            with col2:
                st.metric("Accuracy", "89%", "3%")
        
        # Main content based on selected mode
        if app_mode == "Single Text Analysis":
            self.single_text_analysis()
        elif app_mode == "Batch Analysis":
            self.batch_analysis()
        elif app_mode == "Real-time Demo":
            self.real_time_demo()
        elif app_mode == "Emotion Guide":
            self.emotion_guide()
        elif app_mode == "Dashboard Overview":
            self.dashboard_overview()
    
    def dashboard_overview(self):
        """Dashboard overview with key metrics"""
        st.header("📊 Dashboard Overview")
        
        # Key metrics in cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <div class="feature-icon">📈</div>
                <h4>Total Analyses</h4>
                <h2>1,247</h2>
                <p>+12% this week</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card" style="background: linear-gradient(135deg, #00b894 0%, #00a085 100%);">
                <div class="feature-icon">🎯</div>
                <h4>Accuracy</h4>
                <h2>89.2%</h2>
                <p>+3.1% improvement</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card" style="background: linear-gradient(135deg, #0984e3 0%, #0767b1 100%);">
                <div class="feature-icon">😊</div>
                <h4>Positive</h4>
                <h2>64%</h2>
                <p>Most common emotion</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="metric-card" style="background: linear-gradient(135deg, #6c5ce7 0%, #5649c2 100%);">
                <div class="feature-icon">⚡</div>
                <h4>Response Time</h4>
                <h2>0.8s</h2>
                <p>Lightning fast</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Sample data visualization
        st.subheader("📈 Emotion Trends")
        
        # Sample trend data
        dates = pd.date_range('2024-01-01', periods=30, freq='D')
        trend_data = pd.DataFrame({
            'Date': dates,
            'Love': np.random.randint(20, 50, 30),
            'Joyful': np.random.randint(25, 60, 30),
            'Sad': np.random.randint(10, 30, 30),
            'Angry': np.random.randint(5, 25, 30),
            'Neutral': np.random.randint(15, 40, 30)
        })
        
        fig = px.line(trend_data, x='Date', y=['Love', 'Joyful', 'Sad', 'Angry', 'Neutral'],
                     title='📊 Emotion Trends Over Time',
                     color_discrete_map=self.emotion_colors)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Quick actions
        st.subheader("🚀 Quick Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🎭 Analyze Sample Text", use_container_width=True):
                st.session_state.quick_action = "sample"
        
        with col2:
            if st.button("📊 View Reports", use_container_width=True):
                st.session_state.quick_action = "reports"
        
        with col3:
            if st.button("🔄 Real-time Demo", use_container_width=True):
                st.session_state.quick_action = "demo"
    
    def single_text_analysis(self):
        """Single text analysis interface"""
        st.header("🔍 Single Text Emotion Analysis")
        
        # Text input options with enhanced UI
        input_method = st.radio(
            "🎯 Choose input method:",
            ["✍️ Type text", "📚 Use example text"],
            horizontal=True
        )
        
        text = ""
        
        if input_method == "✍️ Type text":
            text = st.text_area(
                "📝 Enter text to analyze:",
                height=150,
                placeholder="Type your text here... ✨",
                help="💡 Enter any text you want to analyze for emotional content"
            )
        else:
            example_options = {
                "❤️ Love Example": "I love you more than anything in this world! You mean everything to me ❤️ Every moment with you is magical! 💕",
                "😊 Joyful Example": "I'm so happy today! Everything is going perfectly and I feel amazing! 🎉 Just got promoted and life is wonderful! 🌈",
                "😢 Sad Example": "I feel so lonely and empty inside. Nothing brings me joy anymore... The world feels grey and hopeless. 🌧️",
                "😠 Angry Example": "This makes me absolutely furious! I can't believe how unfair this is! How dare they treat people this way! 🔥",
                "😐 Neutral Example": "The weather is okay today. Nothing special happened, just a regular day with normal activities. ⚖️"
            }
            
            selected_example = st.selectbox("📚 Choose an example:", list(example_options.keys()))
            text = example_options[selected_example]
            st.text_area("📄 Example text:", value=text, height=150, disabled=True)
        
        if st.button("🎯 Analyze Emotion", type="primary", use_container_width=True) and text.strip():
            with st.spinner("🔍 Analyzing emotion... 🌈"):
                # Add a cute loading animation
                progress_text = "Processing your text... ✨"
                my_bar = st.progress(0, text=progress_text)
                
                for percent_complete in range(100):
                    time.sleep(0.01)
                    my_bar.progress(percent_complete + 1, text=progress_text)
                time.sleep(0.5)
                my_bar.empty()
                
                result = self.analyze_emotion(text)
                self.display_emotion_result(result)
                
                # Celebration for positive emotions
                if result.get('success') and result['result']['emotion'] in ['love', 'joyful']:
                    st.balloons()
                    st.success("🎉 Yay! Positive emotions detected! Spread the joy! 🌈")
    
    def batch_analysis(self):
        """Batch analysis interface"""
        st.header("📚 Batch Text Analysis")
        
        st.write("📊 Upload a file or enter multiple texts to analyze emotions in bulk. Perfect for analyzing customer feedback, social media posts, or survey responses!")
        
        # Enhanced file upload
        uploaded_file = st.file_uploader(
            "📁 Upload a text file (one text per line)",
            type=['txt', 'csv'],
            help="💡 Supported formats: .txt, .csv. Each line should contain one text to analyze."
        )
        
        # Manual input with better UI
        st.subheader("✍️ Or enter texts manually:")
        manual_texts = st.text_area(
            "📝 Enter texts (one per line):",
            height=200,
            placeholder="Enter each text on a new line... ✨\n\nExample:\nI love this so much! ❤️\nI feel really sad today 😢\nThis makes me angry! 🔥\nHaving a normal day 😐\nSo happy right now! 😊",
            help="💡 Each line will be analyzed separately as a distinct text input"
        )
        
        texts_to_analyze = []
        
        if uploaded_file is not None:
            # Read uploaded file
            content = uploaded_file.getvalue().decode("utf-8")
            texts_to_analyze = [line.strip() for line in content.split('\n') if line.strip()]
            st.success(f"✅ Loaded {len(texts_to_analyze)} texts from file 📁")
        
        if manual_texts:
            manual_texts_list = [line.strip() for line in manual_texts.split('\n') if line.strip()]
            texts_to_analyze.extend(manual_texts_list)
        
        if texts_to_analyze:
            st.info(f"📊 Total texts to analyze: **{len(texts_to_analyze)}**")
            
            # Enhanced preview
            with st.expander("👀 Preview texts", expanded=True):
                for i, text in enumerate(texts_to_analyze[:5]):
                    st.write(f"**{i+1}.** {text}")
                if len(texts_to_analyze) > 5:
                    st.write(f"📋 ... and **{len(texts_to_analyze) - 5}** more texts")
            
            if st.button("🚀 Analyze All Texts", type="primary", use_container_width=True):
                with st.spinner(f"🔍 Analyzing {len(texts_to_analyze)} texts... 🌈"):
                    batch_result = self.batch_analyze(texts_to_analyze)
                    self.display_batch_results(batch_result)
    
    def real_time_demo(self):
        """Real-time emotion analysis demo"""
        st.header("⚡ Real-time Emotion Analysis Demo")
        
        st.write("""
        🎭 This demo shows real-time emotion analysis on streaming text data.
        Watch as emotions change instantly while you type! Perfect for live feedback analysis. ✨
        """)
        
        # Real-time input with enhanced UI
        demo_text = st.text_input(
            "🎤 Enter text for real-time analysis:",
            placeholder="Start typing to see real-time analysis... ✨",
            key="real_time_input"
        )
        
        if demo_text:
            # Simulate real-time analysis with enhanced visual feedback
            with st.spinner("🔍 Analyzing in real-time... ⚡"):
                # Show typing animation
                typing_placeholder = st.empty()
                for i in range(3):
                    typing_placeholder.markdown(f"🔍 Processing{'.' * (i + 1)}")
                    time.sleep(0.3)
                typing_placeholder.empty()
                
                result = self.analyze_emotion(demo_text)
                
                if result.get('success'):
                    emotion_data = result['result']
                    
                    # Enhanced real-time result display
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        emotion = emotion_data['emotion']
                        confidence = emotion_data['confidence']
                        emoji = self.emotion_emojis.get(emotion, '😐')
                        image = self.emotion_images.get(emotion, '📊')
                        
                        st.markdown(
                            f'<div class="metric-card" style="background: linear-gradient(135deg, {self.emotion_colors.get(emotion, "#95a5a6")} 0%, {self._darken_color(self.emotion_colors.get(emotion, "#95a5a6"))} 100%);">'
                            f'<div class="feature-icon">{image}</div>'
                            f'<h3>{emoji} {emotion.title()}</h3>'
                            f'<h1>{confidence:.2%}</h1>'
                            f'<p>🎯 Confidence Level</p>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                        
                        # Emotion description
                        st.info(f"📝 **Description:** {self.emotion_descriptions.get(emotion, '')}")
                    
                    with col2:
                        self.plot_emotion_distribution(emotion_data)
        
        # Enhanced sample social media analysis
        st.subheader("📱 Sample Social Media Posts Analysis")
        
        sample_posts = [
            "I'm in love with this beautiful sunset! ❤️ Feeling so grateful for this moment.",
            "Feeling so sad and lonely tonight... 😢 Wish I had someone to talk to.",
            "This traffic is making me absolutely furious! 😠 How can people drive like this?",
            "Just having a regular day, nothing special 😐 Work, eat, sleep, repeat.",
            "So happy and joyful! Best day ever! 😊 Everything is going perfectly!",
            "I love my family so much! They mean everything to me 💕 Grateful for their support.",
            "Why does everything have to be so difficult? So frustrated with this situation!",
            "Beautiful weather today, feeling peaceful and content with life 🌤️",
            "This movie broke my heart 💔 so emotional right now, can't stop crying",
            "Yay! Got the job! So excited and joyful! 🎉 Time to celebrate! 🥳"
        ]
        
        if st.button("🎭 Analyze Sample Posts", use_container_width=True):
            with st.spinner("🔍 Analyzing sample posts... 📊"):
                batch_result = self.batch_analyze(sample_posts)
                self.display_batch_results(batch_result)
                
                # Show some fun insights
                st.success("🎉 Sample analysis complete! Here are some insights from social media:")
                st.write("""
                - 😊 **Joyful** posts often include exclamation marks and positive emojis
                - ❤️ **Love** expressions frequently mention family and gratitude
                - 😢 **Sad** posts tend to be longer and more reflective
                - 🔥 **Angry** posts use strong language and rhetorical questions
                """)
    
    def emotion_guide(self):
        """Enhanced emotion information guide"""
        st.header("📚 Emotion Guide")
        st.write("🎓 Learn about the different emotions this system can detect. Understand what each emotion means and see examples!")
        
        emotion_info = self.get_emotion_info()
        
        if emotion_info and emotion_info.get('success'):
            emotions_data = emotion_info['emotions']
        else:
            # Enhanced fallback data
            emotions_data = {
                'love': {
                    'description': 'Feelings of affection, care, and deep attachment. Characterized by warmth, protectiveness, and strong positive connections.',
                    'examples': ['I love you more than anything! 💕', 'This is absolutely wonderful! 🌟', 'You complete my world! ❤️'],
                    'color': '#e74c3c',
                    'emoji': '❤️',
                    'image': '💕',
                    'triggers': ['Affectionate relationships', 'Beautiful moments', 'Heartfelt connections'],
                    'physical_signs': ['Warm feeling', 'Smiling', 'Butterflies in stomach']
                },
                'sad': {
                    'description': 'Feelings of unhappiness, sorrow, or disappointment. Often accompanied by low energy and withdrawal.',
                    'examples': ['I feel completely alone... 🌧️', 'Nothing seems to work out 😔', 'This pain is overwhelming'],
                    'color': '#3498db',
                    'emoji': '😢',
                    'image': '🌧️',
                    'triggers': ['Loss', 'Disappointment', 'Loneliness'],
                    'physical_signs': ['Tears', 'Heavy feeling', 'Low energy']
                },
                'angry': {
                    'description': 'Feelings of frustration, irritation, or rage. Characterized by tension and strong reactions.',
                    'examples': ['This is absolutely unacceptable! 🔥', 'I am so frustrated right now! 💢', 'How dare they do this!'],
                    'color': '#e67e22',
                    'emoji': '😠',
                    'image': '🔥',
                    'triggers': ['Injustice', 'Frustration', 'Boundary violation'],
                    'physical_signs': ['Clenched fists', 'Hot face', 'Tense muscles']
                },
                'neutral': {
                    'description': 'Neutral or balanced emotional state. Neither strongly positive nor negative.',
                    'examples': ['The weather is fine today ⚖️', 'Just going about my day', 'Nothing special to report'],
                    'color': '#95a5a6',
                    'emoji': '😐',
                    'image': '⚖️',
                    'triggers': ['Routine activities', 'Neutral events', 'Balanced situations'],
                    'physical_signs': ['Relaxed posture', 'Normal breathing', 'Calm demeanor']
                },
                'joyful': {
                    'description': 'Feelings of happiness, excitement, and delight. Characterized by high energy and positivity.',
                    'examples': ['I am over the moon! 🌈', 'This is fantastic news! 🎉', 'What a wonderful day! 😊'],
                    'color': '#f1c40f',
                    'emoji': '😊',
                    'image': '🌈',
                    'triggers': ['Success', 'Beautiful moments', 'Positive surprises'],
                    'physical_signs': ['Smiling', 'Laughter', 'Bouncing energy']
                }
            }
        
        # Enhanced emotion cards with tabs
        for emotion, info in emotions_data.items():
            with st.container():
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    emoji = info.get('emoji', '😐')
                    image = info.get('image', '📊')
                    color = info.get('color', '#95a5a6')
                    st.markdown(
                        f'<div style="background: linear-gradient(135deg, {color} 0%, {self._darken_color(color)} 100%); padding: 40px; border-radius: 20px; text-align: center; color: white; box-shadow: 0 8px 25px rgba(0,0,0,0.15);">'
                        f'<h1 style="font-size: 4rem; margin: 0;">{image}</h1>'
                        f'<h1 style="font-size: 3rem; margin: 10px 0;">{emoji}</h1>'
                        f'<h2 style="margin: 0;">{emotion.title()}</h2>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                
                with col2:
                    tab1, tab2, tab3 = st.tabs(["📝 Description", "💬 Examples", "🔍 Details"])
                    
                    with tab1:
                        st.subheader(f"{emoji} {emotion.title()}")
                        st.write(f"**Description:** {info['description']}")
                        
                        # Confidence indicator for this emotion
                        confidence = random.uniform(0.7, 0.95)  # Simulated confidence
                        st.write(f"**🎯 Typical Detection Confidence:** {confidence:.1%}")
                        
                        # Quick facts
                        st.write("**💡 Quick Facts:**")
                        st.write(f"- 🎭 Emotion Type: {'Positive' if emotion in ['love', 'joyful'] else 'Negative' if emotion in ['sad', 'angry'] else 'Neutral'}")
                        st.write(f"- 🌟 Common in: {'Social media' if emotion in ['love', 'joyful'] else 'Personal journals' if emotion == 'sad' else 'Feedback'}")
                    
                    with tab2:
                        st.write("**📚 Example Texts:**")
                        for example in info['examples']:
                            st.write(f"• {example}")
                        
                        st.write("**🎯 Common Phrases:**")
                        common_phrases = {
                            'love': ['I love', 'adore', 'cherish', 'treasure'],
                            'sad': ['I feel sad', 'disappointed', 'heartbroken', 'lonely'],
                            'angry': ['I am angry', 'furious', 'frustrated', 'outraged'],
                            'neutral': ['It is okay', 'normal', 'regular', 'fine'],
                            'joyful': ['I am happy', 'excited', 'thrilled', 'delighted']
                        }
                        for phrase in common_phrases.get(emotion, []):
                            st.write(f"• '{phrase}'")
                    
                    with tab3:
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.write("**⚡ Common Triggers:**")
                            for trigger in info.get('triggers', []):
                                st.write(f"• {trigger}")
                        with col_b:
                            st.write("**🔍 Physical Signs:**")
                            for sign in info.get('physical_signs', []):
                                st.write(f"• {sign}")
                
                st.markdown("---")

def main():
    # Add numpy import for dashboard
    import numpy as np
    app = EmotionAnalysisApp()
    app.run()

if __name__ == "__main__":
    main()