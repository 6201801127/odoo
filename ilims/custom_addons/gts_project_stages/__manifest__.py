{
    'name': "Gts Project Stages",
    'summary': """ """,
    'description': """  """,
    'author': "Geotechnosoft",
    'website': "https://www.geotechnosoft.com",
    'category': 'Contacts',
    'version': '0.0.0.14',
    'depends': ['project', 'web', 'hr_timesheet', 'gts_stakeholder', 'analytic', 'sale_project'],
    'data': [
        'security/security_view.xml',
        'security/ir.model.access.csv',

        'data/activity_data.xml',
        'data/cron_schedular.xml',
        'data/email_template.xml',
        'views/project_stage_view.xml',
        #'views/project_view.xml'
    ],
}
