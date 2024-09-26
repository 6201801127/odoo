{
    'name': "kw_cpd",

    'summary': """Certified Professional Drive""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.csmpl.com",

    'category': 'Uncategorized',
    'version': '0.1',


    'depends': ['base','mail'],



    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'views/emails/kw_cpd_emails.xml',

        'views/kw_institute_master_views.xml',
        'views/kw_course_master_views.xml',
        'views/kw_cpd_percentage_config.xml',
        'views/kw_cpd_applications_views.xml',
        'views/kw_cpd_approval_log_views.xml',
        'views/kw_cpd_certification_views.xml',
        'views/kw_cpd_cert_log_views.xml',
        
        'data/kw_cpd_crons.xml',

        'reports/kw_cpd_applicants_report.xml'

        
    ],



    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}