# -*- coding: utf-8 -*-
{
    'name': 'GTS Contacts',
    'version': '14.0.0.1',
    'category': 'Contacts',
    'description': """
    """,
    'depends': ['base', 'contacts', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_states.xml',
        'views/masters_view.xml',
        'views/res_partner.xml',
        'views/hr_employee_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
