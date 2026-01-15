import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

EXCLUDE_FROM_TITLE = [
    'c#', 'с#', 'Machine', 'AI', 'ML', 'LLM', 'Odoo', 'GCP', 'Angular', 'QA', 'Part-time', 'short-term', 'Cloud',
    'Science', 'Head', 'Lead', 'Node', 'Java', 'drone', 'trainee', 'junior', 'Leader', 'Principal', 'test', 'DevOps',
    'c++', 'с++', 'math', 'Platform', 'Algorithms', 'Kubernetes', 'Architect', 'Intern', 'NumPy', 'Vision',
    'UAE', 'Yii', 'Embedded', 'Big Data', 'office', 'Vue.JS', 'Azure', 'freelance', 'analyst', 'Go', 'Robotics', 'rust',
    'Airflow', 'Golang', 'React', 'PySpark', 'Databricks', 'AQA', 'Front end'
]
EXCLUDE_FROM_TITLE = {s.lower() for s in EXCLUDE_FROM_TITLE}

EXCLUDE_FROM_COMPANY_NAME = ['ajax', 'моу', 'Defence', 'Камера', 'ЗАЗМІК', 'Warbirds']
EXCLUDE_FROM_COMPANY_NAME = {s.lower() for s in EXCLUDE_FROM_COMPANY_NAME}

MINIMAL_SALARY = 3000
MAX_SALARY = 4500

DJINNI_LOGIN = os.getenv('DJINNI_LOGIN')
DJINNI_PASSWORD = os.getenv('DJINNI_PASSWORD')
