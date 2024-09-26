{
    'name': "Kwantify Auth",
    'summary': """
    Authenticate user entry time.
    """,
    'description': """ 
    Authenticate user entry with Kwantify v5 and accept late entry reason if any 
    """,
    'author': "CSM Technologies",
    'website': "https://portal.csm.tech/",
    'category': 'Kwantify/Security',
    'data': [
        # 'data/system_config_parameter_data.xml',
        'security/ir.model.access.csv',
        'data/allowed_urls.xml',
        'views/res_config_settings_view.xml',
        'views/kw_user_status.xml',
        'views/assets.xml',
        'data/session_clear_cron.xml',
        'views/after_login_activity_config.xml',
    ],
    'version': '0.1',
    'depends': ['base'],
    'installable': True,
    'application': False,
    'auto_install': False
}