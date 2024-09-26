# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Skills Management',
    'category': 'Hidden',
    'version': '1.3',
    'summary': 'Manage skills, knowledge and resume of your employees',
    'description':
        """
Skills and Resume for HR
========================
Last Updated by RGupta 06/09/2019 -> Type -> Required

This module introduces skills and resume management for employees.
    Last Updated by sangits 02/04/2019
        """,
    'depends': ['base','hr','groups_inherit'],
    'data': [
        'security/ir.model.access.csv',
        'security/hr_skills_security.xml',
        'views/hr_views.xml',
        'views/hr_templates.xml',
        'data/hr_resume_data.xml',
    ],
    'demo': ['data/hr_resume_demo.xml'],
    'qweb': [
        'static/src/xml/resume_templates.xml',
        'static/src/xml/skills_templates.xml',
    ],
    'installable': True,
    'application': True,
}
