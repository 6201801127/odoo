# -*- coding: utf-8 -*-
{
    'name': "Generate CV",

    'summary': """
        Kwantify: This module is used to generate cv of the employees""",

    'description': """
        This module is used to generate cv of the employees
    """,

    'author': "CSM Technologies",
    'website': "https://www.csm.tech",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Kwantify',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'kw_employee_info_system', 'report_docx','mail'],

    # always loaded
    'data': [
        'security/security.xml',
        'data/request_sequence.xml',
        'data/apply_approve_mail.xml',
        'security/ir.model.access.csv',
        'views/cv_tag_wizard.xml',
        'views/cv_approve_wizard.xml',
        'views/cv_reject_wizard.xml',
        'views/cv_cancel_wizard.xml',

        'views/generate_employee_cv_doc.xml',
        'views/hr_employee_generate_cv.xml',
        'views/hr_cv_mapping.xml',
        'views/cv_mapping_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'external_dependencies': {
        'python': [
            'docx',
            'htmldocx',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
