"""
Tests for Camera Integration Module
"""

import pytest
from camera_integration import (
    calculate_attention_multiplier,
    PostureMonitor,
    BreakReminder,
    CameraAnalytics
)
import time


class TestAttentionMultiplier:
    """Test attention score to XP multiplier conversion"""
    
    def test_perfect_attention(self):
        """100 score should give 1.0x multiplier"""
        assert calculate_attention_multiplier(100) == 1.0
        assert calculate_attention_multiplier(90) == 1.0
        assert calculate_attention_multiplier(80) == 1.0
    
    def test_good_attention(self):
        """60-79 score should give 0.85x multiplier"""
        assert calculate_attention_multiplier(75) == 0.85
        assert calculate_attention_multiplier(60) == 0.85
    
    def test_moderate_attention(self):
        """40-59 score should give 0.7x multiplier"""
        assert calculate_attention_multiplier(50) == 0.7
        assert calculate_attention_multiplier(40) == 0.7
    
    def test_low_attention(self):
        """20-39 score should give 0.6x multiplier"""
        assert calculate_attention_multiplier(30) == 0.6
        assert calculate_attention_multiplier(20) == 0.6
    
    def test_very_low_attention(self):
        """0-19 score should give 0.5x multiplier (minimum)"""
        assert calculate_attention_multiplier(10) == 0.5
        assert calculate_attention_multiplier(0) == 0.5


class TestPostureMonitor:
    """Test posture monitoring and warnings"""
    
    def test_good_posture_no_warning(self):
        """Good posture should not trigger warnings"""
        monitor = PostureMonitor(warning_interval_minutes=1)
        
        for _ in range(70):  # 70 seconds of good posture
            assert monitor.update(has_good_posture=True) == False
    
    def test_bad_posture_triggers_warning(self):
        """Bad posture for interval should trigger warning"""
        monitor = PostureMonitor(warning_interval_minutes=1)  # 60 seconds
        
        # Start bad posture
        monitor.update(has_good_posture=False)
        
        # Manually set start time to 61 seconds ago to simulate time passing
        monitor.bad_posture_start_time = time.time() - 61
        
        # Now update should trigger warning
        result = monitor.update(has_good_posture=False)
        assert result == True
    
    def test_posture_quality_calculation(self):
        """Test posture quality percentage calculation"""
        monitor = PostureMonitor()
        
        # 70 seconds good, 30 seconds bad = 70% quality
        for _ in range(70):
            monitor.update(has_good_posture=True)
        for _ in range(30):
            monitor.update(has_good_posture=False)
        
        quality = monitor.get_posture_quality_percentage()
        assert 69 <= quality <= 71  # Allow small rounding error
    
    def test_reset(self):
        """Test that reset clears all data"""
        monitor = PostureMonitor()
        
        for _ in range(50):
            monitor.update(has_good_posture=False)
        
        monitor.reset()
        
        assert monitor.get_posture_quality_percentage() == 100.0


class TestBreakReminder:
    """Test break reminder functionality"""
    
    def test_no_break_needed_initially(self):
        """No break should be needed right after starting"""
        reminder = BreakReminder(break_interval_minutes=1)
        reminder.start_session()
        
        assert reminder.check_break_needed() == False
    
    def test_break_needed_after_interval(self):
        """Break should be needed after interval passes"""
        reminder = BreakReminder(break_interval_minutes=1)  # 60 seconds
        reminder.start_session()
        
        # Simulate time passing (we can't actually wait 60 seconds in test)
        # So we'll manually set the last_break_time
        reminder.last_break_time = time.time() - 61  # 61 seconds ago
        
        assert reminder.check_break_needed() == True
    
    def test_mark_break_taken(self):
        """Marking break taken should reset timer"""
        reminder = BreakReminder(break_interval_minutes=1)
        reminder.start_session()
        
        # Force break needed
        reminder.last_break_time = time.time() - 61
        assert reminder.check_break_needed() == True
        
        # Mark break taken
        reminder.mark_break_taken()
        assert reminder.breaks_taken == 1
        assert reminder.check_break_needed() == False


class TestCameraAnalytics:
    """Test camera analytics tracking"""
    
    def test_average_attention(self):
        """Test average attention score calculation"""
        analytics = CameraAnalytics()
        
        analytics.record_attention(100)
        analytics.record_attention(80)
        analytics.record_attention(60)
        
        avg = analytics.get_average_attention()
        assert avg == 80.0
    
    def test_posture_quality(self):
        """Test posture quality percentage"""
        analytics = CameraAnalytics()
        
        # 7 good, 3 bad = 70%
        for _ in range(7):
            analytics.record_posture(True)
        for _ in range(3):
            analytics.record_posture(False)
        
        quality = analytics.get_posture_quality()
        assert quality == 70.0
    
    def test_presence_tracking(self):
        """Test presence percentage calculation"""
        analytics = CameraAnalytics()
        
        # 80 present, 20 away = 80%
        for _ in range(80):
            analytics.record_presence(True)
        for _ in range(20):
            analytics.record_presence(False)
        
        presence = analytics.get_presence_percentage()
        assert presence == 80.0
    
    def test_session_summary(self):
        """Test complete session summary"""
        analytics = CameraAnalytics()
        
        analytics.record_attention(90)
        analytics.record_attention(70)
        analytics.record_posture(True)
        analytics.record_posture(False)
        analytics.record_presence(True)
        analytics.record_presence(True)
        
        summary = analytics.get_session_summary()
        
        assert summary['average_attention_score'] == 80.0
        assert summary['posture_quality'] == 50.0
        assert summary['presence_percentage'] == 100.0
        assert summary['total_attention_readings'] == 2
        assert summary['total_posture_readings'] == 2
    
    def test_reset(self):
        """Test that reset clears all data"""
        analytics = CameraAnalytics()
        
        analytics.record_attention(100)
        analytics.record_posture(True)
        analytics.record_presence(True)
        
        analytics.reset()
        
        assert analytics.get_average_attention() == 0.0
        assert analytics.get_posture_quality() == 0.0
        assert analytics.time_present_seconds == 0
        assert analytics.time_away_seconds == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
