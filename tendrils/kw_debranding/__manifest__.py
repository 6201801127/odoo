{
    'name': "Kwantify Debranding",
    'description': "Helps change the aesthetic look of Odoo software via customizing them with Logo and other branding changes.",
    'author': "CSM Technologies Pvt. Ltd.",
    'website': "www.csm.tech",
    'depends': [
        'base_setup',
        'web',
        'website',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/user_error_log.xml',
    ],
    'qweb' : ['static/src/xml/setting.xml'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
