{
    'name': 'Job Offer Letter',
    'version': "1.0.0",
    "author": "Odoo Bangladesh",
    "website": "",
    'category': 'Human Resources',
    'depends': ['hr_recruitment'],
    'data': [
        'data/mail_data.xml',
        'views/he_application_view.xml',
    ],
    'installable': True,
    'application': False,
}
