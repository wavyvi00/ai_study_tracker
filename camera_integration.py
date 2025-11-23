"""
Camera Integration Helper Module
Provides utilities for camera-based study tracking including:
- Attention score to XP multiplier conversion
- Posture monitoring and warnings
- Break reminders (20-20-20 rule)
- Camera analytics
"""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional


def calculate_attention_multiplier(attention_score: float) -> float:
    """
    Convert attention score (0-100) to XP multiplier (0.5-1.0)
    
    Args:
        attention_score: Attention score from camera detector (0-100)
        
    Returns:
        XP multiplier between 0.5 and 1.0
    """
    if attention_score >= 80:
        return 1.0  # Full XP
    elif attention_score >= 60:
        return 0.85
    elif attention_score >= 40:
        return 0.7
    elif attention_score >= 20:
        return 0.6
    else:
        return 0.5  # Minimum multiplier


class PostureMonitor:
    """Monitors posture quality and triggers warnings"""
    
    def __init__(self, warning_interval_minutes: int = 10):
        self.warning_interval = warning_interval_minutes * 60  # Convert to seconds
        self.bad_posture_start_time = None
        self.last_warning_time = None
        self.total_bad_posture_seconds = 0
        self.total_good_posture_seconds = 0
        
    def update(self, has_good_posture: bool):
        """
        Update posture tracking
        
        Args:
            has_good_posture: Whether user currently has good posture
            
        Returns:
            True if warning should be shown, False otherwise
        """
        current_time = time.time()
        
        if has_good_posture:
            # Good posture - reset bad posture timer
            if self.bad_posture_start_time is not None:
                self.total_bad_posture_seconds += (current_time - self.bad_posture_start_time)
                self.bad_posture_start_time = None
            self.total_good_posture_seconds += 1
            return False
        else:
            # Bad posture
            if self.bad_posture_start_time is None:
                self.bad_posture_start_time = current_time
            
            self.total_bad_posture_seconds += 1
            
            # Check if we should show warning
            bad_posture_duration = current_time - self.bad_posture_start_time
            
            if bad_posture_duration >= self.warning_interval:
                # Check if we haven't warned recently (don't spam warnings)
                if self.last_warning_time is None or \
                   (current_time - self.last_warning_time) >= self.warning_interval:
                    self.last_warning_time = current_time
                    return True
            
            return False
    
    def get_posture_quality_percentage(self) -> float:
        """
        Get percentage of time with good posture
        
        Returns:
            Percentage (0-100) of time with good posture
        """
        total_time = self.total_good_posture_seconds + self.total_bad_posture_seconds
        if total_time == 0:
            return 100.0
        return (self.total_good_posture_seconds / total_time) * 100
    
    def reset(self):
        """Reset posture tracking for new session"""
        self.bad_posture_start_time = None
        self.last_warning_time = None
        self.total_bad_posture_seconds = 0
        self.total_good_posture_seconds = 0


class BreakReminder:
    """Manages break reminders using 20-20-20 rule and general breaks"""
    
    def __init__(self, break_interval_minutes: int = 20):
        self.break_interval = break_interval_minutes * 60  # Convert to seconds
        self.session_start_time = None
        self.last_break_time = None
        self.breaks_taken = 0
        
    def start_session(self):
        """Start tracking for a new session"""
        self.session_start_time = time.time()
        self.last_break_time = time.time()
        self.breaks_taken = 0
    
    def check_break_needed(self) -> bool:
        """
        Check if break reminder should be shown
        
        Returns:
            True if break is needed, False otherwise
        """
        if self.last_break_time is None:
            return False
        
        current_time = time.time()
        time_since_break = current_time - self.last_break_time
        
        return time_since_break >= self.break_interval
    
    def mark_break_taken(self):
        """Mark that user took a break"""
        self.last_break_time = time.time()
        self.breaks_taken += 1
    
    def get_time_until_break(self) -> int:
        """
        Get seconds until next break
        
        Returns:
            Seconds until next break (0 if break is due)
        """
        if self.last_break_time is None:
            return 0
        
        current_time = time.time()
        time_since_break = current_time - self.last_break_time
        remaining = self.break_interval - time_since_break
        
        return max(0, int(remaining))
    
    def reset(self):
        """Reset for new session"""
        self.session_start_time = None
        self.last_break_time = None
        self.breaks_taken = 0


class CameraAnalytics:
    """Tracks and analyzes camera-based metrics"""
    
    def __init__(self):
        self.attention_scores: List[float] = []
        self.posture_readings: List[bool] = []
        self.time_away_seconds = 0
        self.time_present_seconds = 0
        
    def record_attention(self, score: float):
        """Record an attention score reading"""
        self.attention_scores.append(score)
    
    def record_posture(self, good_posture: bool):
        """Record a posture reading"""
        self.posture_readings.append(good_posture)
    
    def record_presence(self, is_present: bool):
        """Record user presence"""
        if is_present:
            self.time_present_seconds += 1
        else:
            self.time_away_seconds += 1
    
    def get_average_attention(self) -> float:
        """
        Get average attention score for session
        
        Returns:
            Average attention score (0-100)
        """
        if not self.attention_scores:
            return 0.0
        return sum(self.attention_scores) / len(self.attention_scores)
    
    def get_posture_quality(self) -> float:
        """
        Get percentage of time with good posture
        
        Returns:
            Percentage (0-100) of time with good posture
        """
        if not self.posture_readings:
            return 0.0
        good_count = sum(1 for p in self.posture_readings if p)
        return (good_count / len(self.posture_readings)) * 100
    
    def get_presence_percentage(self) -> float:
        """
        Get percentage of time user was present
        
        Returns:
            Percentage (0-100) of time present
        """
        total_time = self.time_present_seconds + self.time_away_seconds
        if total_time == 0:
            return 100.0
        return (self.time_present_seconds / total_time) * 100
    
    def get_session_summary(self) -> Dict:
        """
        Get complete session summary
        
        Returns:
            Dictionary with all analytics
        """
        return {
            'average_attention_score': round(self.get_average_attention(), 2),
            'posture_quality': round(self.get_posture_quality(), 2),
            'time_away_seconds': self.time_away_seconds,
            'time_present_seconds': self.time_present_seconds,
            'presence_percentage': round(self.get_presence_percentage(), 2),
            'total_attention_readings': len(self.attention_scores),
            'total_posture_readings': len(self.posture_readings)
        }
    
    def reset(self):
        """Reset analytics for new session"""
        self.attention_scores = []
        self.posture_readings = []
        self.time_away_seconds = 0
        self.time_present_seconds = 0
