import re

with open("streamlit_app.py", "r") as f:
    content = f.read()

missing_functions = """
def get_learning_time(skill):
    skill_lower = skill.lower()
    if any(k in skill_lower for k in ['python', 'java', 'c++', 'javascript', 'react', 'node', 'angular', 'php', 'ruby', 'go']):
        return "2-3 months"
    if any(k in skill_lower for k in ['machine learning', 'deep learning', 'data science', 'ai', 'artificial intelligence']):
        return "3-4 months"
    if any(k in skill_lower for k in ['sql', 'database', 'mysql', 'postgresql']):
        return "1-2 months"
    if any(k in skill_lower for k in ['excel', 'word', 'powerpoint']):
        return "1-2 months"
    if any(k in skill_lower for k in ['aws', 'azure', 'cloud', 'docker', 'kubernetes', 'devops']):
        return "2-3 months"
    return "1-2 months"

def get_practical_steps(skill):
    skill_lower = skill.lower()
    if any(k in skill_lower for k in ['python', 'java', 'c++', 'javascript', 'react', 'node', 'angular', 'php', 'ruby', 'go']):
        return ["Start with a beginner syntax course (e.g., freeCodeCamp, Codecademy).", "Build 2-3 small interactive projects to apply your knowledge.", "Push your code to GitHub and add the link to your resume."]
    if any(k in skill_lower for k in ['machine learning', 'deep learning', 'data science', 'ai', 'artificial intelligence']):
        return ["Take an introductory course (e.g., Andrew Ng's Coursera class).", "Practice analyzing free datasets on Kaggle.", "Create a simple portfolio project showing your insights."]
    if any(k in skill_lower for k in ['sql', 'database', 'mysql', 'postgresql']):
        return ["Learn basic SELECT, JOIN, and GROUP BY statements online.", "Practice querying a sample database.", "Solve beginner SQL challenges on HackerRank."]
    if any(k in skill_lower for k in ['excel', 'word', 'powerpoint']):
        return ["Watch a crash course on YouTube.", "Practice standard formulas (e.g., VLOOKUP) or formatting.", "Use it to organize your own personal data or budget."]
    if any(k in skill_lower for k in ['aws', 'azure', 'cloud', 'devops', 'docker', 'kubernetes']):
        return ["Familiarize yourself with the core services (Compute, Storage).", "Follow a tutorial to deploy a basic app.", "Consider studying for a foundational certification."]
    if any(k in skill_lower for k in ['communication', 'leadership', 'management', 'sales']):
        return ["Read industry-standard books or articles on the topic.", "Practice the skills in your current role or personal projects.", "Highlight relevant experiences where you used this skill on your resume."]
    return ["Start with a highly-rated beginner online course.", "Practice with small, real-world exercises.", "Add the skill to your resume once you master the basics."]

"""

# Insert these functions right before get_roadmap_content
content = content.replace("def get_roadmap_content(", missing_functions + "\ndef get_roadmap_content(")

with open("streamlit_app.py", "w") as f:
    f.write(content)
