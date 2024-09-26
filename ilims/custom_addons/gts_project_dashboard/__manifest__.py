{
    'name': "Project Dashboard",
    'version': '14.0.1.0.0',
    'summary': """Project Dashboard""",
    'description': """Project Dashboard""",
    'category': 'Dashboard',
    'author': '',
    'company': 'Geotechnosoft',
    'maintainer': 'http://www.geotechnosoft.com',
    'website': "www.geotechnosoft.com",
    'depends': ['project', 'base', 'gts_project_stages'],
    'data': [
        'views/dashboard_views.xml'
    ],
    'qweb': ["static/src/xml/project_dashboard.xml"],
    'images': [],
    'license': "AGPL-3",
    'installable': True,
    'application': False,
}