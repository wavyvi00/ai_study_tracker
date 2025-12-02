import time
from window_provider import get_window_provider
from rule_engine import RuleEngine
from ai_engine import AIInferenceEngine

class FocusDetector:
    def __init__(self):
        self.window_provider = get_window_provider()
        self.rule_engine = RuleEngine()
        self.ai_engine = AIInferenceEngine()
        
        # Grace Period State
        self.last_state = "focused"
        self.grace_period_start = None
        self.grace_period_duration = 15.0 # seconds
        self.in_grace_period = False
        
        # Caching
        self.last_window_title = ""
        self.last_app_name = ""
        self.last_result = None

    def get_focus_state(self):
        """
        Main entry point. Returns dict with state, confidence, reason, and metadata.
        """
        try:
            app_name, window_title, has_permissions = self.window_provider.get_active_window()
        except Exception as e:
            print(f"❌ Error getting active window: {e}")
            return {
                "state": "unknown",
                "confidence": 0.0,
                "reason": f"Window provider error: {str(e)}",
                "source": "error",
                "app_name": "Error",
                "window_title": "",
                "has_permissions": False
            }
        
        # Optimization: If window hasn't changed, return cached result (but update grace period)
        if app_name == self.last_app_name and window_title == self.last_window_title and self.last_result:
             # We still need to check grace period expiry even if window is same
             # e.g. User stays on YouTube Home for > 15s
             pass 
        else:
            self.last_app_name = app_name
            self.last_window_title = window_title
        
        # 1. Rule-Based Check (Fast)
        try:
            rule_state, rule_conf, rule_reason = self.rule_engine.analyze(app_name, window_title)
        except Exception as e:
            print(f"❌ Error in rule engine: {e}")
            rule_state = "unknown"
            rule_conf = 0.0
            rule_reason = f"Rule engine error: {str(e)}"
        
        final_state = "unknown"
        confidence = 0.0
        reason = ""
        source = "rules"

        if rule_state != "unknown":
            final_state = rule_state
            confidence = rule_conf
            reason = rule_reason
        else:
            # 2. AI Check (Slow/Fallback)
            try:
                ai_state, ai_conf = self.ai_engine.predict(f"{app_name} {window_title}")
                if ai_state != "unknown" and ai_conf > 0.6:  # Lowered from 0.7 to 0.6
                    final_state = ai_state
                    confidence = ai_conf
                    reason = f"AI classified as {ai_state} ({int(ai_conf*100)}%)"
                    source = "ai"
                else:
                    # Default fallback
                    final_state = "distracted" # Assume distracted if unknown? Or focused?
                    confidence = 0.5
                    reason = "Unknown activity"
                    source = "default"
            except Exception as e:
                print(f"❌ Error in AI engine: {e}")
                # Default fallback
                final_state = "distracted"
                confidence = 0.5
                reason = f"AI error: {str(e)}"
                source = "error"

        # 3. Grace Period Logic
        # If we switch FROM focused TO distracted, start grace period
        if final_state == "distracted" and self.last_state == "focused":
            if not self.in_grace_period:
                print(f"🛡️ Entering Grace Period for {self.grace_period_duration}s")
                self.in_grace_period = True
                self.grace_period_start = time.time()
        
        # If we are IN grace period
        if self.in_grace_period:
            elapsed = time.time() - self.grace_period_start
            if elapsed < self.grace_period_duration:
                # Still in grace period - override to "searching" or "focused"
                # "searching" is a good neutral state that doesn't penalize but warns
                if final_state == "distracted":
                    final_state = "searching" # Neutral state
                    reason = f"Grace Period ({int(self.grace_period_duration - elapsed)}s left)"
            else:
                # Grace period expired
                self.in_grace_period = False
                print("⚠️ Grace Period Expired!")

        # If we switch back to focused, reset grace period
        if final_state == "focused":
            self.in_grace_period = False
            self.grace_period_start = None

        self.last_state = final_state
        
        return {
            "state": final_state,
            "confidence": confidence,
            "reason": reason,
            "source": source,
            "app_name": app_name,
            "window_title": window_title,
            "has_permissions": has_permissions
        }
