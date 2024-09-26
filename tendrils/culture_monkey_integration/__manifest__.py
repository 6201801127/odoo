# -*- coding: utf-8 -*-
{
    'name': "Kwantify culture monkey integration",

    'summary': """Kwantify culture monkey integration""",

    'description': """
        Kwantify culture monkey integration
    """,

    'author': 'CSM Technologies',
    'company': 'CSM Technologies',
    'maintainer': 'CSM Technologies',
    'website': "https://www.csm.tech",

    'category': 'Employee',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'kw_surveys'],

    # always loaded
    'data': [

        'security/ir.model.access.csv',
        'views/views.xml',
        'data/culture_monkey_update_cron.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
