# -*- coding: utf-8 -*-
{
    'name': "bsscl grievance",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "CSM Technologies",
    'website': "http://www.csm.tech",

    'category': 'BSSCL',
    'version': '0.1',

    'depends': ['base','base_setup','base_branch_company','hr','contacts','employee_stages','hr_recruitment','resource'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        # 'views/hr_employee_view.xml',
        'wizards/reject_wizard.xml',

        # 'data/relative_type_data.xml',
        # 'report/employee_service_book.xml',
        'views/bsscl_grievance_type.xml',
        'views/bsscl_grievance.xml',
        'views/grievance_menu.xml',
        'data/bsscl_grievance_type.xml',
        'data/bsscl_ir_sequence.xml',
       
    ],
    
    'demo': [
        # 'data/hr_resume_demo.xml'
        ],
    
    # 'qweb': [
    #     'static/src/xml/resume_templates.xml',
    #     'static/src/xml/skills_templates.xml',
    # ],
}
