# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'HR Employee Chart',
    'category': 'Hidden',
    'version': '1.0',
    'description':
        """
Employee Chart Widget for HR
=======================

This module extend the employee form with a organizational chart.
(N+1, N+2, direct subordinates)
        """,
    'depends': ['hr', 'kw_employee'],
    'data': [
        'views/hr_templates.xml',
        'views/hr_views.xml'
    ],
    'qweb': [
        'static/src/xml/hr_employee_chart.xml',
    ]
}
