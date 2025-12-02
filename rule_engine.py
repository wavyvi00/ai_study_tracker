class RuleEngine:
    def __init__(self):
        self.study_keywords = [
            'code', 'terminal', 'docs', 'pdf', 'canvas', 'notion', 'obsidian', 
            'cursor', 'xcode', 'intellij', 'pycharm', 'calendar', 'electron',
            'student', 'profile', 'portal', 'login', 'sso', 'auth', 'dashboard', 'canvas', 'blackboard',
            'chatgpt', 'claude', 'gemini', 'copilot', 'perplexity', 'openai',
            'math', 'algebra', 'calculus', 'geometry', 'statistics', 'physics', 'chemistry', 'biology',
            'history', 'economics', 'programming', 'python', 'javascript', 'java', 'c++',
            'tutorial', 'course', 'lesson', 'lecture', 'learn', 'education', 'study'
        ]
        
        self.distraction_keywords = [
            'youtube', 'twitter', 'x.com', 'twitter.com', ' / x', 'reddit', 'facebook', 
            'instagram', 'netflix', 'game', 'tiktok', 'twitch', 'hulu', 'disney', 'prime video'
        ]
        
        self.search_keywords = [
            'search', 'results', 'query', 'find', 'looking for', 'google search', 'bing search'
        ]
        
        self.educational_channels = [
            'crash course', 'ted-ed', 'veritasium', '3blue1brown', 'khan academy', 
            'mit opencourseware', 'stanford', 'harvard', 'coursera', 'udemy'
        ]
        
        # Explicit educational context indicators (for overriding distraction sites)
        self.explicit_learning = [
            'tutorial', 'course', 'lecture', 'lesson', 'how to build', 'how to make',
            'learn', 'education', 'teaching', 'instructor', 'professor',
            'onnx', 'machine learning', 'deep learning', 'neural network', 'ai model',
            'algorithm', 'data science', 'research', 'paper', 'documentation',
            'ai', 'ml', 'engine', 'framework', 'library', 'api', 'sdk'
        ]

    def analyze(self, app_name, window_title):
        """
        Analyze the window using rule-based logic.
        Returns: (state, confidence, reason)
        state: "focused", "distracted", "searching", or "unknown"
        """
        text = f"{app_name} {window_title}".lower()
        
        # 1. Check for Search/Research context
        for keyword in self.search_keywords:
            if keyword in text:
                return "searching", 0.9, f"Detected search keyword: {keyword}"
                
        # 2. Check for Distraction Sites (STRICT MODE)
        for dist in self.distraction_keywords:
            if dist in text:
                # Distraction site detected - ONLY allow override if EXPLICIT learning context
                for edu in self.explicit_learning + self.educational_channels:
                    if edu in text:
                        return "focused", 0.8, f"Educational content on {dist}: {edu}"
                
                # No explicit learning context found - mark as distracted
                return "distracted", 0.95, f"Detected distraction app/site: {dist}"

        # 3. Check for Study Keywords
        for keyword in self.study_keywords:
            if keyword in text:
                return "focused", 0.8, f"Detected study keyword: {keyword}"
                
        return "unknown", 0.0, "No rules matched"
