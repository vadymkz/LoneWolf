import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

EXCLUDE_FROM_TITLE = [
    'C#', 'Machine', 'AI', 'ML', 'LLM', 'Odoo', 'GCP', 'Angular', 'QA', 'Part-time', 'short-term', 'Cloud', 'Big Data',
    'Science', 'Head', 'Lead', 'Node', 'Java', 'drone', 'trainee', 'junior'
]
EXCLUDE_FROM_TITLE = {s.lower() for s in EXCLUDE_FROM_TITLE}
