# -*- coding: utf-8 -*-
{
    'name': "Kwantify Employee DMS Integration",

    'summary': """
        Store employee documents at DMS""",

    'description': """
        Store employee documents at DMS
    """,

    'author': "CSM Technologies",
    'website': "https://www.csm.tech",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Kwantify/Integration',
    'version': '1.0',

    # any module necessary for this one to work correctly  ,'hr','kw_employee'
    'depends': ['base', 'kw_employee', 'kw_dms'],

    # always loaded
    # default integration storages and groups
    'data': [
        "views/hr_employees_views.xml",
        "data/kwdms_integration_data.xml",
    ],
    "application": True,
    "installable": True,
    'auto_install': False,
}
