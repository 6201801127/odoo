{
    'name': 'Employee Stages',
    'version': '12.0.2',
    'summary': """Manages Employee Stages""",
    'description': """  Updated by SMehata 26/08/19 
                        This module is used to tracking the employee's different stages.""",
    'category': "Generic Modules/Human Resources",
    'author': 'Priyanka Patil(Dexciss Technology)',
    'company': 'Dexciss Technology',
    'website': "https://www.dexciss.com",
    'depends': ['base', 'hr','groups_inherit','hr_branch_company'],
    'data': [
        'security/employee_retirement_rules.xml',
        'security/ir.model.access.csv',
        'views/employee_stages_view.xml',
        # 'views/document_master.xml',
        'data/data_cron.xml'
    ],
    'demo': [],
    'images': ['static/description/DexLogo.png'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}


