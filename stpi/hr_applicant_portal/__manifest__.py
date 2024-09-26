{
    'name': "HR Applicant Portal",
    'version': '1.0',
    'summary': """HR Applicant Portal """,
    'description': """
    HR Applicant Portal
""",
    'category': 'Human Resources',
    'author': '',
    'depends': ['hr_recruitment', 'hr_applicant','website'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/myportal_hr_applicant_templates.xml',
        'data/ir_sequence.xml',
        'views/hr_applicant.xml',
        'views/new_applicant_template.xml',
    ],
    'demo': [],
    'images': [],
    'installable': True,
    'application': True,
    'license': 'OPL-1',
}
