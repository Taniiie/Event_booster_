"""
Live Event Interaction Components
Handles real-time polling, Q&A, engagement tracking, and heatmaps
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import json

class LiveInteractionManager:
    def __init__(self):
        self.active_polls = {}
        self.qa_queue = []
        self.engagement_data = []
        self.chat_messages = []
        
    def create_poll(self, question, options, poll_type='multiple_choice'):
        """Create a new poll"""
        poll_id = f"poll_{len(self.active_polls) + 1}_{int(datetime.now().timestamp())}"
        
        poll = {
            'id': poll_id,
            'question': question,
            'options': options,
            'type': poll_type,
            'responses': {option: 0 for option in options},
            'total_responses': 0,
            'created_at': datetime.now(),
            'is_active': True,
            'segment_data': {}  # For segmented responses
        }
        
        self.active_polls[poll_id] = poll
        return poll_id
    
    def submit_poll_response(self, poll_id, response, user_segment=None):
        """Submit a response to a poll"""
        if poll_id in self.active_polls and self.active_polls[poll_id]['is_active']:
            poll = self.active_polls[poll_id]
            
            if response in poll['options']:
                poll['responses'][response] += 1
                poll['total_responses'] += 1
                
                # Track segmented data
                if user_segment:
                    if user_segment not in poll['segment_data']:
                        poll['segment_data'][user_segment] = {option: 0 for option in poll['options']}
                    poll['segment_data'][user_segment][response] += 1
                
                return True
        return False
    
    def get_poll_results(self, poll_id, show_segments=False):
        """Get poll results with optional segmentation"""
        if poll_id not in self.active_polls:
            return None
        
        poll = self.active_polls[poll_id]
        results = {
            'question': poll['question'],
            'responses': poll['responses'],
            'total_responses': poll['total_responses'],
            'percentages': {}
        }
        
        # Calculate percentages
        if poll['total_responses'] > 0:
            for option, count in poll['responses'].items():
                results['percentages'][option] = (count / poll['total_responses']) * 100
        
        if show_segments and poll['segment_data']:
            results['segments'] = poll['segment_data']
        
        return results
    
    def add_qa_question(self, question, user_name, user_segment=None, priority='normal'):
        """Add a question to the Q&A queue"""
        qa_item = {
            'id': f"qa_{len(self.qa_queue) + 1}",
            'question': question,
            'user_name': user_name,
            'user_segment': user_segment,
            'priority': priority,
            'timestamp': datetime.now(),
            'status': 'pending',  # pending, answered, dismissed
            'answer': None,
            'votes': 0
        }
        
        self.qa_queue.append(qa_item)
        return qa_item['id']
    
    def vote_qa_question(self, qa_id):
        """Vote for a Q&A question"""
        for qa in self.qa_queue:
            if qa['id'] == qa_id:
                qa['votes'] += 1
                return True
        return False
    
    def answer_qa_question(self, qa_id, answer):
        """Answer a Q&A question"""
        for qa in self.qa_queue:
            if qa['id'] == qa_id:
                qa['answer'] = answer
                qa['status'] = 'answered'
                return True
        return False
    
    def get_qa_queue(self, sort_by='votes'):
        """Get Q&A queue sorted by criteria"""
        if sort_by == 'votes':
            return sorted(self.qa_queue, key=lambda x: x['votes'], reverse=True)
        elif sort_by == 'time':
            return sorted(self.qa_queue, key=lambda x: x['timestamp'])
        elif sort_by == 'priority':
            priority_order = {'high': 3, 'normal': 2, 'low': 1}
            return sorted(self.qa_queue, key=lambda x: priority_order.get(x['priority'], 2), reverse=True)
        
        return self.qa_queue
    
    def track_engagement_event(self, user_id, event_type, event_data=None):
        """Track an engagement event"""
        engagement_event = {
            'user_id': user_id,
            'event_type': event_type,  # click, poll_response, question, chat, etc.
            'timestamp': datetime.now(),
            'data': event_data or {}
        }
        
        self.engagement_data.append(engagement_event)
    
    def calculate_engagement_score(self, time_window_minutes=5):
        """Calculate real-time engagement score"""
        cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
        recent_events = [e for e in self.engagement_data if e['timestamp'] > cutoff_time]
        
        if not recent_events:
            return 0
        
        # Weight different event types
        event_weights = {
            'poll_response': 3,
            'question': 5,
            'chat': 2,
            'click': 1,
            'reaction': 2,
            'share': 4
        }
        
        total_score = sum(event_weights.get(event['event_type'], 1) for event in recent_events)
        unique_users = len(set(event['user_id'] for event in recent_events))
        
        # Normalize by number of active users
        return total_score / max(unique_users, 1)
    
    def generate_engagement_heatmap(self, time_intervals=12):
        """Generate engagement heatmap data"""
        if not self.engagement_data:
            return None
        
        # Create time intervals
        now = datetime.now()
        interval_duration = timedelta(minutes=60 / time_intervals)  # 5-minute intervals for 12 intervals = 1 hour
        
        heatmap_data = []
        
        for i in range(time_intervals):
            start_time = now - timedelta(hours=1) + (i * interval_duration)
            end_time = start_time + interval_duration
            
            interval_events = [
                e for e in self.engagement_data 
                if start_time <= e['timestamp'] < end_time
            ]
            
            # Count events by type
            event_counts = {}
            for event in interval_events:
                event_type = event['event_type']
                event_counts[event_type] = event_counts.get(event_type, 0) + 1
            
            heatmap_data.append({
                'time_slot': start_time.strftime('%H:%M'),
                'total_events': len(interval_events),
                'unique_users': len(set(e['user_id'] for e in interval_events)),
                'event_breakdown': event_counts
            })
        
        return heatmap_data
    
    def get_live_insights(self):
        """Get real-time insights about the event"""
        current_engagement = self.calculate_engagement_score()
        total_polls = len(self.active_polls)
        total_questions = len(self.qa_queue)
        pending_questions = len([q for q in self.qa_queue if q['status'] == 'pending'])
        
        # Calculate participation rate
        unique_participants = len(set(e['user_id'] for e in self.engagement_data))
        
        insights = {
            'current_engagement_score': current_engagement,
            'total_active_polls': total_polls,
            'total_questions': total_questions,
            'pending_questions': pending_questions,
            'unique_participants': unique_participants,
            'engagement_trend': self._calculate_engagement_trend(),
            'top_question': self._get_top_question(),
            'most_active_segment': self._get_most_active_segment()
        }
        
        return insights
    
    def _calculate_engagement_trend(self):
        """Calculate engagement trend (increasing/decreasing)"""
        if len(self.engagement_data) < 10:
            return 'stable'
        
        # Compare last 5 minutes with previous 5 minutes
        now = datetime.now()
        recent_events = [e for e in self.engagement_data if e['timestamp'] > now - timedelta(minutes=5)]
        previous_events = [e for e in self.engagement_data if now - timedelta(minutes=10) <= e['timestamp'] <= now - timedelta(minutes=5)]
        
        recent_score = len(recent_events)
        previous_score = len(previous_events)
        
        if recent_score > previous_score * 1.2:
            return 'increasing'
        elif recent_score < previous_score * 0.8:
            return 'decreasing'
        else:
            return 'stable'
    
    def _get_top_question(self):
        """Get the most voted question"""
        if not self.qa_queue:
            return None
        
        return max(self.qa_queue, key=lambda x: x['votes'])
    
    def _get_most_active_segment(self):
        """Get the most active user segment"""
        segment_activity = {}
        
        for event in self.engagement_data:
            segment = event.get('data', {}).get('user_segment', 'Unknown')
            segment_activity[segment] = segment_activity.get(segment, 0) + 1
        
        if not segment_activity:
            return None
        
        return max(segment_activity.items(), key=lambda x: x[1])
    
    def add_chat_message(self, user_name, message, user_segment=None):
        """Add a chat message"""
        chat_message = {
            'id': f"chat_{len(self.chat_messages) + 1}",
            'user_name': user_name,
            'message': message,
            'user_segment': user_segment,
            'timestamp': datetime.now(),
            'reactions': {}
        }
        
        self.chat_messages.append(chat_message)
        self.track_engagement_event(user_name, 'chat', {'message_length': len(message)})
        
        return chat_message['id']
    
    def add_reaction_to_message(self, message_id, reaction, user_name):
        """Add a reaction to a chat message"""
        for message in self.chat_messages:
            if message['id'] == message_id:
                if reaction not in message['reactions']:
                    message['reactions'][reaction] = []
                if user_name not in message['reactions'][reaction]:
                    message['reactions'][reaction].append(user_name)
                    self.track_engagement_event(user_name, 'reaction', {'reaction_type': reaction})
                return True
        return False
    
    def get_chat_messages(self, limit=50):
        """Get recent chat messages"""
        return sorted(self.chat_messages, key=lambda x: x['timestamp'], reverse=True)[:limit]
    
    def generate_word_cloud_data(self):
        """Generate word cloud data from chat messages and Q&A"""
        text_data = []
        
        # Collect chat messages
        for message in self.chat_messages:
            text_data.append(message['message'])
        
        # Collect Q&A questions
        for qa in self.qa_queue:
            text_data.append(qa['question'])
        
        return ' '.join(text_data)
    
    def export_session_data(self):
        """Export all session data for analysis"""
        session_data = {
            'polls': self.active_polls,
            'qa_queue': self.qa_queue,
            'engagement_data': self.engagement_data,
            'chat_messages': self.chat_messages,
            'session_summary': self.get_live_insights()
        }
        
        return session_data
