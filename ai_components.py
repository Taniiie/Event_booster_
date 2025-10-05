"""
AI Components for Event Booster
Handles NLP, predictions, recommendations, and intelligent features
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from textblob import TextBlob
import streamlit as st
import random
import re

class AIComponents:
    def __init__(self):
        self.engagement_model = None
        self.churn_model = None
        self.vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        
    def predict_engagement(self, user_features):
        """Predict user engagement likelihood"""
        # Simulate engagement prediction based on user features
        features = [
            user_features.get('days_since_registration', 0),
            user_features.get('previous_events_attended', 0),
            user_features.get('quiz_completion_rate', 0),
            user_features.get('social_shares', 0),
            len(user_features.get('interests', '').split(';'))
        ]
        
        # Simple scoring algorithm (in production, use trained ML model)
        engagement_score = (
            min(features[0] / 30, 1) * 0.2 +  # Registration timing
            min(features[1] / 10, 1) * 0.3 +  # Previous attendance
            features[2] * 0.25 +               # Quiz completion
            min(features[3] / 5, 1) * 0.15 +  # Social engagement
            min(features[4] / 5, 1) * 0.1     # Interest diversity
        )
        
        return min(engagement_score, 1.0)
    
    def predict_churn_risk(self, user_data):
        """Predict if a user is at risk of churning"""
        # Calculate churn risk based on engagement patterns
        last_activity_days = user_data.get('days_since_last_activity', 30)
        attendance_rate = user_data.get('attendance_rate', 0.5)
        engagement_score = user_data.get('engagement_score', 0.5)
        
        # Simple churn risk calculation
        churn_risk = (
            min(last_activity_days / 60, 1) * 0.4 +
            (1 - attendance_rate) * 0.35 +
            (1 - engagement_score) * 0.25
        )
        
        risk_level = 'Low'
        if churn_risk > 0.7:
            risk_level = 'High'
        elif churn_risk > 0.4:
            risk_level = 'Medium'
        
        return {
            'risk_score': churn_risk,
            'risk_level': risk_level,
            'recommendations': self._get_churn_recommendations(risk_level)
        }
    
    def _get_churn_recommendations(self, risk_level):
        """Get recommendations based on churn risk level"""
        recommendations = {
            'High': [
                'Send personalized re-engagement email',
                'Offer exclusive content or early access',
                'Schedule one-on-one check-in call',
                'Provide special discount for next event'
            ],
            'Medium': [
                'Send targeted content based on interests',
                'Invite to upcoming relevant events',
                'Engage through social media',
                'Send event highlights and recordings'
            ],
            'Low': [
                'Continue regular communication',
                'Share upcoming event calendar',
                'Encourage social sharing',
                'Request feedback and testimonials'
            ]
        }
        return recommendations.get(risk_level, recommendations['Low'])
    
    def analyze_sentiment(self, text):
        """Analyze sentiment of text using TextBlob"""
        blob = TextBlob(text)
        sentiment = blob.sentiment
        
        if sentiment.polarity > 0.1:
            return {'sentiment': 'Positive', 'score': sentiment.polarity, 'subjectivity': sentiment.subjectivity}
        elif sentiment.polarity < -0.1:
            return {'sentiment': 'Negative', 'score': sentiment.polarity, 'subjectivity': sentiment.subjectivity}
        else:
            return {'sentiment': 'Neutral', 'score': sentiment.polarity, 'subjectivity': sentiment.subjectivity}
    
    def extract_key_topics(self, text_data):
        """Extract key topics from text using TF-IDF"""
        try:
            tfidf_matrix = self.vectorizer.fit_transform(text_data)
            feature_names = self.vectorizer.get_feature_names_out()
            
            # Get top terms
            mean_scores = np.mean(tfidf_matrix.toarray(), axis=0)
            top_indices = mean_scores.argsort()[-10:][::-1]
            
            return [feature_names[i] for i in top_indices]
        except:
            return ['AI', 'technology', 'innovation', 'digital', 'future']
    
    def recommend_content(self, user_interests, available_content):
        """Recommend content based on user interests"""
        user_interest_list = user_interests.lower().split(';')
        recommendations = []
        
        for content in available_content:
            content_text = content.get('title', '') + ' ' + content.get('description', '')
            content_text = content_text.lower()
            
            # Calculate relevance score
            relevance_score = 0
            for interest in user_interest_list:
                if interest.strip() in content_text:
                    relevance_score += 1
            
            if relevance_score > 0:
                recommendations.append({
                    'content': content,
                    'relevance_score': relevance_score,
                    'match_reasons': [interest for interest in user_interest_list if interest.strip() in content_text]
                })
        
        return sorted(recommendations, key=lambda x: x['relevance_score'], reverse=True)[:5]
    
    def cluster_attendees(self, attendee_data):
        """Cluster attendees based on their characteristics"""
        # Prepare features for clustering
        features = []
        attendee_names = []
        
        for name, data in attendee_data.items():
            feature_vector = [
                data.get('events_attended', 0),
                data.get('engagement_score', 0),
                len(data.get('interests', '').split(';')),
                data.get('social_shares', 0),
                data.get('quiz_scores', 0)
            ]
            features.append(feature_vector)
            attendee_names.append(name)
        
        if len(features) < 3:
            return {'clusters': {}, 'labels': []}
        
        # Perform clustering
        kmeans = KMeans(n_clusters=min(3, len(features)), random_state=42)
        cluster_labels = kmeans.fit_predict(features)
        
        # Group attendees by cluster
        clusters = {}
        for i, label in enumerate(cluster_labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(attendee_names[i])
        
        # Name clusters based on characteristics
        cluster_names = {
            0: 'Highly Engaged',
            1: 'Moderately Active',
            2: 'New/Passive'
        }
        
        return {
            'clusters': {cluster_names.get(k, f'Cluster {k}'): v for k, v in clusters.items()},
            'labels': cluster_labels
        }
    
    def generate_smart_qa_response(self, question):
        """Generate smart Q&A responses (simplified version)"""
        # Common FAQ patterns and responses
        faq_patterns = {
            r'.*when.*start.*': "The event starts at the scheduled time mentioned in your invitation. Please check your email for specific timing.",
            r'.*how.*join.*': "You can join the event using the link provided in your registration email or through the event platform.",
            r'.*recording.*available.*': "Yes, event recordings will be available to all registered participants within 24 hours after the event.",
            r'.*certificate.*': "Certificates of attendance will be provided to all attendees who complete the full session.",
            r'.*technical.*issue.*': "For technical issues, please contact our support team or use the chat function during the event.",
            r'.*slides.*presentation.*': "Presentation slides will be shared with all attendees after the event concludes.",
            r'.*networking.*': "Networking opportunities are available through our platform's networking feature and breakout rooms.",
            r'.*follow.*up.*': "Follow-up materials and resources will be sent to all participants within 48 hours."
        }
        
        question_lower = question.lower()
        
        for pattern, response in faq_patterns.items():
            if re.search(pattern, question_lower):
                return {
                    'response': response,
                    'confidence': 0.8,
                    'needs_human': False
                }
        
        # If no pattern matches, suggest human intervention
        return {
            'response': "Thank you for your question. This seems to require specific information. Our team will get back to you shortly, or you can ask this during the live Q&A session.",
            'confidence': 0.3,
            'needs_human': True
        }
    
    def calculate_roi_prediction(self, event_data):
        """Calculate ROI prediction for events"""
        # Simple ROI calculation based on engagement metrics
        total_registrations = event_data.get('total_registrations', 0)
        attendance_rate = event_data.get('attendance_rate', 0)
        engagement_score = event_data.get('avg_engagement_score', 0)
        conversion_rate = event_data.get('conversion_rate', 0.05)  # Default 5%
        
        # Estimated value per engaged attendee
        value_per_attendee = 100  # This would be customizable
        
        engaged_attendees = total_registrations * attendance_rate * engagement_score
        estimated_conversions = engaged_attendees * conversion_rate
        estimated_revenue = estimated_conversions * value_per_attendee
        
        # Calculate costs (simplified)
        estimated_costs = event_data.get('event_costs', total_registrations * 10)
        
        roi = ((estimated_revenue - estimated_costs) / estimated_costs) * 100 if estimated_costs > 0 else 0
        
        return {
            'estimated_revenue': estimated_revenue,
            'estimated_costs': estimated_costs,
            'roi_percentage': roi,
            'engaged_attendees': engaged_attendees,
            'estimated_conversions': estimated_conversions
        }
    
    def generate_event_summary(self, event_data, attendee_feedback):
        """Generate AI-powered event summary"""
        # Analyze feedback sentiment
        feedback_sentiments = [self.analyze_sentiment(feedback) for feedback in attendee_feedback if feedback]
        
        positive_feedback = sum(1 for s in feedback_sentiments if s['sentiment'] == 'Positive')
        total_feedback = len(feedback_sentiments)
        
        # Extract key topics from feedback
        key_topics = self.extract_key_topics(attendee_feedback) if attendee_feedback else []
        
        summary = {
            'overall_sentiment': 'Positive' if positive_feedback > total_feedback * 0.6 else 'Mixed' if positive_feedback > total_feedback * 0.3 else 'Needs Improvement',
            'sentiment_score': positive_feedback / total_feedback if total_feedback > 0 else 0,
            'key_topics_discussed': key_topics[:5],
            'attendance_rate': event_data.get('attendance_rate', 0),
            'engagement_highlights': [
                f"Average engagement score: {event_data.get('avg_engagement_score', 0):.2f}",
                f"Questions asked: {event_data.get('questions_count', 0)}",
                f"Poll participation: {event_data.get('poll_participation', 0)}%"
            ],
            'recommendations': self._generate_improvement_recommendations(event_data, feedback_sentiments)
        }
        
        return summary
    
    def _generate_improvement_recommendations(self, event_data, feedback_sentiments):
        """Generate recommendations for future events"""
        recommendations = []
        
        attendance_rate = event_data.get('attendance_rate', 0)
        engagement_score = event_data.get('avg_engagement_score', 0)
        
        if attendance_rate < 0.7:
            recommendations.append("Improve pre-event engagement and reminders to boost attendance")
        
        if engagement_score < 0.6:
            recommendations.append("Add more interactive elements like polls and Q&A sessions")
        
        negative_feedback = sum(1 for s in feedback_sentiments if s['sentiment'] == 'Negative')
        if negative_feedback > len(feedback_sentiments) * 0.3:
            recommendations.append("Address common concerns mentioned in feedback")
        
        if event_data.get('questions_count', 0) < 5:
            recommendations.append("Encourage more audience participation and questions")
        
        return recommendations[:3]  # Return top 3 recommendations
