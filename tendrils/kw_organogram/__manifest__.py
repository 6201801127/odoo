# -*- coding: utf-8 -*-
{
    'name': "Kwantify Organogram",

    'summary': """ Organogram hierarchy representation of organization """,

    'description': """
        This module shows hierarchy of organization, i.e. starting from parent node
        to child nodes and siblings node too.
        """,

    'author': "CSM Technologies",
    'website': "https://www.csmpl.co.in",

    'category': 'Kwantify/Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'kw_employee'],

    # always loaded
    'data': [
        'views/menu.xml',
        'views/assets.xml',
        'views/hr_dept_hierarchy_client_action.xml',
        'views/hr_employee_hierarchy_client_action.xml',
        'views/hr_grade_level_hierarchy_client_action.xml',
        'views/project_resource_hierarchy.xml'
    ],
    'qweb': [
        'static/src/xml/*.xml'
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
