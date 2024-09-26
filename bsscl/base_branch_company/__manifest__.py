# -*- coding: utf-8 -*-
{
    'name': 'Branch & Company Mixin',
    'version': '1.7',
    'category': 'STPI',
    'author': 'CSM Technologies',
    'company' : 'CSM Technologies',
    'website': "http://www.csm.tech",
    'maintainer' : 'CSM Technologies',
    'sequence': 25,
    'summary': 'Include Branch & Company support',
    'description': "",
    'depends': ['base', 'base_setup'],
    'data': [
            'demo/branch_data.xml',
            'wizard/branch_config_view.xml',
            'security/branch_security.xml',
            'security/ir.model.access.csv',
            'views/res_branch_view.xml',
            'views/res_branch_config_view.xml',
            # 'views/account_config_setting.xml',
            'views/location_type_views.xml',
    ],
    'demo': [
        'demo/branch_demo.xml',
    ],
    'installable': True,
    'auto_install': True
}