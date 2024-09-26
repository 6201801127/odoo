# -*- coding: utf-8 -*-
{
    'name': "Exit / Transfer Management",
    'summary': """ Manage employee exit transfer data""",
    'description': "Group Category 'Exit or Transfer'",
    'category': 'STPI',
    'author': 'CSM Technologies',
    'company' : 'CSM Technologies',
    'website': "http://www.csm.tech",
    'maintainer' : 'CSM Technologies',
    'version': '14.0.1',
    'depends' : ['base',"mail",'hr'],
    'data': [
        # 'security/security.xml',
        'security/ir.model.access.csv',
        'data/exit_master_data.xml',
        'views/print_template.xml',
        'views/exit_transfer_views.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}