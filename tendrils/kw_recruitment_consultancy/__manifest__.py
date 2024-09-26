{
    'name': "Recruitment Consultancy Web Page",
    'summary': "New Recruitment Consultancy",
    'description': "Recruitment Consultancy process",
    'author': "CSM Technologies",
    'website': "https://www.csm.tech",
    'category': 'Kwantify/Human Resources',
    'version': '0.1',
    
    'depends': ['base', 'kw_recruitment','web'],

    'data': [
        'views/web_menu.xml',
        
        'views/jobs.xml',
        'views/applicants.xml',
        'views/add_applicant.xml',
        'views/interviews.xml',
        'views/assets.xml',
    ],

    'demo': [],
    'installable': True,
    'application': True,
}
