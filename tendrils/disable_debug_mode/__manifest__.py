{
    'name': 'Kwantify Disable Debug Mode',
    'category': 'Extra Tools',
    'sequence': 50,
    'summary': "Kwantify This module disables debug mode for users who do not have the "
               "'Enable debug mode' permission.",
    'version': '12.0.1.0',
    'depends': [
        'web', 'base', 'base_setup', 'kw_synchronization', 'kw_account_fiscal_year'
    ],
    'data': [
        'security/disable_debug_mode_security.xml',
        'security/ir.model.access.csv',
        'views/url_access_restriction.xml',
        'views/developer_menu.xml'
    ],
    'demo': [],
    'qweb': ['static/src/xml/warning_message_page.xml'],
    'installable': True,
    'application': False,
}
