# -*- coding: utf-8 -*-
{
    'name': "Kwantify Employee Document migration",
    'summary': "This feature is used to migrate employee's document from V5 to V6.",
    'description': "Employee document migration module",
    'author': "CSM Technologies",
    'website': "https://www.csm.tech",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Kwantify/Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','kw_employee'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/kw_emp_update_doc_cron.xml',
        'views/res_config_Settings.xml',
        'views/kw_emp_update_doc.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
