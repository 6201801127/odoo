
{
    'name': 'Employee Requisition',
    'version': '12.0.3',
    'sequence':1,
    'category': '',
    'description': """
                Last update 16/Jule/19 by SMehata
                Last update 10/Jule/19 by SMehata
                Transititon By SMehata
                Last Updated by Sangita 08/01/2020
                Last Updated by sangita 21/01/2020
    """,
    'author': 'Dexciss Technology Pvt. Ltd. (Sangita)',
    'summary': '',
    'website': 'http://www.dexciss.com/',
    'images': [],
    'depends': ['hr','hr_recruitment','base',
                ],
    'data': [
            'data/hr_employee_requisition.xml',
            'security/ir.model.access.csv',
            'security/employee_requisition.xml',
            'data/hr_employee_requisition.xml',
            'wizard/reason_wizard.xml',
            'view/hr_employee_requisition_view.xml',

            ],
                        
    'installable': True,
    'application': True,
    'auto_install': False,
}

