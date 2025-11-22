import json
import os

class CourseManager:
    def __init__(self):
        self.courses_file = "courses.json"
        self.courses = self.load_courses()
    
    def load_courses(self):
        """Load courses from JSON file"""
        if os.path.exists(self.courses_file):
            try:
                with open(self.courses_file, 'r') as f:
                    data = json.load(f)
                    return data.get("courses", [])
            except Exception as e:
                print(f"Error loading courses: {e}")
                return []
        return []
    
    def save_courses(self):
        """Save courses to JSON file"""
        try:
            with open(self.courses_file, 'w') as f:
                json.dump({"courses": self.courses}, f, indent=2)
        except Exception as e:
            print(f"Error saving courses: {e}")
    
    def add_course(self, course_name):
        """Add a course if it doesn't exist"""
        if not course_name or course_name.strip() == "":
            return False
        
        course_name = course_name.strip()
        
        # Check if course already exists (case-insensitive)
        if not any(c.lower() == course_name.lower() for c in self.courses):
            self.courses.append(course_name)
            self.save_courses()
            print(f"Added new course: {course_name}")
            return True
        return False
    
    def get_courses(self):
        """Get list of all courses"""
        return self.courses
