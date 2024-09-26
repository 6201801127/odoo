{
    'name': "Gts Project Sale Purchase",
    'summary': """ """,
    'description': """  """,
    'author': "Geotechnosoft",
    'website': "https://www.geotechnosoft.com",
    'category': 'Contacts',
    'version': '0.0.0.14',
    'depends': ['sale', 'project', 'account', 'purchase', 'hr_timesheet', 'sale_timesheet', 'gts_ticket_management',
                'sales_team'],
    'data': [
        'security/ir.model.access.csv',
        'views/project_view.xml',
        'views/sale_view.xml',
        'views/purchase_view.xml',
        'views/account_view.xml',
    ],
}
