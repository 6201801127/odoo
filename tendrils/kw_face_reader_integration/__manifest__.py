# -*- coding: utf-8 -*-
{
    'name': "kw_face_reader_integration",

    'summary': """
        Employee face reader""",

    'description': """
        Long description of module's purpose
    """,

    'author': "CSM Technologies",
    'website': "https://www.csm.tech",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Kwantify/Extra Tools',
    'version': '1.0',
    # any module necessary for this one to work correctly
    'depends': ['base','hr','kw_employee'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/kw_face_reader_security.xml',

        # 'views/menu.xml',
        'data/system_param_data.xml',
        # 'views/assets.xml',
        'views/employee_face_capture_view.xml',
        'views/synced_kwantify_solutions_employee_view.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     # 'demo/demo.xml',
    # ],
    # 'qweb': [ 'views/qweb/menu_inherit.xml',],
    'application': True,
    'installable': True,
    'auto_install': False,
}