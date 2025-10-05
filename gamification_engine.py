"""
Gamification Engine for Event Booster
Handles points, badges, leaderboards, and engagement mechanics
"""

import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import random
import json

class GamificationEngine:
    def __init__(self):
        self.points_config = {
            'event_registration': 10,
            'pre_event_quiz': 15,
            'poll_participation': 5,
            'question_asked': 20,
            'event_attendance': 50,
            'post_event_feedback': 15,
            'social_share': 10,
            'referral': 25,
            'streak_bonus': 5
        }
        
        self.badges = {
            'early_bird': {'name': '🐦 Early Bird', 'description': 'Registered 7+ days before event', 'points': 25},
            'quiz_master': {'name': '🧠 Quiz Master', 'description': 'Completed 5+ pre-event quizzes', 'points': 50},
            'social_butterfly': {'name': '🦋 Social Butterfly', 'description': 'Shared 3+ events on social media', 'points': 30},
            'perfect_attendee': {'name': '⭐ Perfect Attendee', 'description': 'Attended 5+ events', 'points': 100},
            'question_champion': {'name': '❓ Question Champion', 'description': 'Asked 10+ questions', 'points': 75},
            'feedback_hero': {'name': '📝 Feedback Hero', 'description': 'Provided feedback for 10+ events', 'points': 60},
            'networking_pro': {'name': '🤝 Networking Pro', 'description': 'Connected with 20+ attendees', 'points': 80}
        }
    
    def calculate_user_points(self, user_data):
        """Calculate total points for a user based on their activities"""
        points = 0
        activities = user_data.get('activities', {})
        
        for activity, count in activities.items():
            if activity in self.points_config:
                points += self.points_config[activity] * count
        
        return points
    
    def check_badges(self, user_data):
        """Check which badges a user has earned"""
        earned_badges = []
        activities = user_data.get('activities', {})
        
        # Early Bird Badge
        if user_data.get('days_before_registration', 0) >= 7:
            earned_badges.append('early_bird')
        
        # Quiz Master Badge
        if activities.get('pre_event_quiz', 0) >= 5:
            earned_badges.append('quiz_master')
        
        # Social Butterfly Badge
        if activities.get('social_share', 0) >= 3:
            earned_badges.append('social_butterfly')
        
        # Perfect Attendee Badge
        if activities.get('event_attendance', 0) >= 5:
            earned_badges.append('perfect_attendee')
        
        # Question Champion Badge
        if activities.get('question_asked', 0) >= 10:
            earned_badges.append('question_champion')
        
        # Feedback Hero Badge
        if activities.get('post_event_feedback', 0) >= 10:
            earned_badges.append('feedback_hero')
        
        # Networking Pro Badge
        if activities.get('connections_made', 0) >= 20:
            earned_badges.append('networking_pro')
        
        return earned_badges
    
    def generate_quiz_questions(self, topic, difficulty='medium'):
        """Generate quiz questions based on topic and difficulty"""
        quiz_bank = {
            'AI': {
                'easy': [
                    {'question': 'What does AI stand for?', 'options': ['Artificial Intelligence', 'Automated Information', 'Advanced Integration'], 'correct': 0},
                    {'question': 'Which is a popular AI programming language?', 'options': ['Python', 'HTML', 'CSS'], 'correct': 0}
                ],
                'medium': [
                    {'question': 'What is machine learning?', 'options': ['A subset of AI', 'A type of computer', 'A programming language'], 'correct': 0},
                    {'question': 'What is neural network inspired by?', 'options': ['Human brain', 'Computer circuits', 'Internet'], 'correct': 0}
                ],
                'hard': [
                    {'question': 'What is the vanishing gradient problem?', 'options': ['Gradients become too small', 'Gradients become too large', 'No gradients'], 'correct': 0}
                ]
            },
            'SaaS': {
                'easy': [
                    {'question': 'What does SaaS stand for?', 'options': ['Software as a Service', 'System as a Service', 'Security as a Service'], 'correct': 0}
                ],
                'medium': [
                    {'question': 'What is a key benefit of SaaS?', 'options': ['Scalability', 'Hardware ownership', 'Local storage'], 'correct': 0}
                ]
            }
        }
        
        topic_questions = quiz_bank.get(topic, quiz_bank['AI'])
        return topic_questions.get(difficulty, topic_questions['medium'])
    
    def create_leaderboard(self, users_data):
        """Create a leaderboard based on user points"""
        leaderboard = []
        
        for user, data in users_data.items():
            points = self.calculate_user_points(data)
            badges = self.check_badges(data)
            leaderboard.append({
                'name': user,
                'points': points,
                'badges_count': len(badges),
                'badges': badges
            })
        
        return sorted(leaderboard, key=lambda x: x['points'], reverse=True)
    
    def suggest_connections(self, user_interests, all_users_data):
        """Suggest connections based on shared interests"""
        suggestions = []
        user_interests_set = set(user_interests.split(';'))
        
        for user, data in all_users_data.items():
            if 'interests' in data:
                other_interests = set(data['interests'].split(';'))
                common_interests = user_interests_set.intersection(other_interests)
                
                if len(common_interests) > 0:
                    suggestions.append({
                        'name': user,
                        'common_interests': list(common_interests),
                        'match_score': len(common_interests) / len(user_interests_set.union(other_interests))
                    })
        
        return sorted(suggestions, key=lambda x: x['match_score'], reverse=True)[:5]
    
    def generate_personalized_teaser(self, user_data, event_info):
        """Generate personalized teaser content"""
        interests = user_data.get('interests', '').split(';')
        primary_interest = interests[0] if interests else 'technology'
        
        teasers = {
            'AI': [
                f"🤖 Did you know? AI can now predict event engagement with 95% accuracy!",
                f"🧠 Fun fact: The human brain has 86 billion neurons - similar to some AI models!",
                f"⚡ AI processes data 1000x faster than humans. Ready to learn how?"
            ],
            'SaaS': [
                f"☁️ SaaS companies grow 5x faster than traditional software companies!",
                f"💼 95% of businesses use at least one SaaS application. What's your favorite?",
                f"🚀 SaaS market is expected to reach $623 billion by 2023!"
            ],
            'Marketing': [
                f"📈 Personalized marketing can increase revenue by up to 15%!",
                f"🎯 Email marketing has an average ROI of $42 for every $1 spent!",
                f"📱 Mobile marketing drives 40% more engagement than desktop!"
            ]
        }
        
        topic_teasers = teasers.get(primary_interest, teasers['AI'])
        return random.choice(topic_teasers)
    
    def create_countdown_content(self, event_date, user_data):
        """Create engaging countdown content"""
        days_left = (event_date - datetime.now()).days
        
        if days_left > 7:
            return {
                'message': f"🗓️ {days_left} days to go! Time to prepare!",
                'action': 'Take a pre-event quiz to earn points!',
                'urgency': 'low'
            }
        elif days_left > 3:
            return {
                'message': f"⏰ Only {days_left} days left! Getting excited?",
                'action': 'Connect with other attendees now!',
                'urgency': 'medium'
            }
        elif days_left > 0:
            return {
                'message': f"🔥 {days_left} days to go! Final preparations!",
                'action': 'Last chance to complete challenges!',
                'urgency': 'high'
            }
        else:
            return {
                'message': "🎉 Event day is here! Let's go!",
                'action': 'Join the event now!',
                'urgency': 'critical'
            }
