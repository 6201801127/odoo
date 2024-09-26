# -*- coding: utf-8 -*-
{
    'name': "Kwantify Handbook DMS Integration",

    'summary': """
        Store policy documents at DMS""",

    'description': """
        Store policy documents at DMS
    """,

    'author': "CSM Technologies",
    'website': "http://www.csmpl.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Kwantify/Integration',
    'version': '1.0',

    # any module necessary for this one to work correctly ,'hr','kw_employee'
    'depends': ['base', 'kw_handbook', 'kw_dms'],

    # always loaded
    # default integration storages and groups
    'data': [
        "views/kw_handbook_views.xml",
        "data/dms_integration_data.xml",
    ],
    "application": True,
    "installable": True,
    'auto_install': False,
}
