{

    'name': 'Password Security',
    "summary": "Allow admin to set password security requirements.",
    'version': '12.0.1.1.4',
    'author':
        "CSM Technology",
    'category': 'Base',
    'depends': [
        'auth_signup',
        'auth_password_policy_signup',
    ],
    'external_dependencies': {
        'python': ['zxcvbn'],
    },
    "license": "LGPL-3",
    "data": [
        'data/kw_password_security_parameter.xml',
        'views/password_security.xml',
        'views/res_config_settings_views.xml',
        'security/ir.model.access.csv',
        'security/res_users_pass_history.xml',
        'data/password_expiration_cron.xml',
    ],
    "demo": [
        'demo/res_users.xml',
    ],
    'installable': True,
}
