# -*- coding: utf-8 -*-
{
    'name': "kw_certification",

    'summary': """
        """,

    'description': """
        
    """,

    'author': "CSM Technology",
    'website': "https://www.csm.tech",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'kw_resource_management','kw_employee_info_system'],

    # always loaded
    'data': [
        'security/group_security.xml',
        'security/ir.model.access.csv',
        'wizards/certification_nominate_employee.xml',
        'views/kw_certification.xml',
        'views/manual_certification_entry.xml',
        'views/kw_certification_config.xml',
        'reports/kw_certification_report.xml',
        'views/menus.xml',
        'views/mail_to_nominate_employee.xml',
        'data/sequence.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}