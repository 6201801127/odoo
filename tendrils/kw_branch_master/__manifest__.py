# -*- coding: utf-8 -*-
{
    'name': "Kwantify Branch",
    'summary': "Kwantify Branch Master",
    'description': "Kwantify Branch Master",
    'author': "CSM Technologies",
    'website': "https://www.csm.tech",
    'category': 'Kwantify/Tools',
    'depends': ['base', 'hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/location_master_data.xml',
        'data/branch_master_data.xml',
        'data/kw_branch_unit_data.xml',
        'views/kw_location_master.xml',
        'views/kw_res_branch.xml',
        'views/res_company.xml',
        'views/res_users.xml',
        'views/kw_res_branch_unit_view.xml',
        'views/kw_branch_guest_house.xml',
    ],
    # only loaded in demonstration mode
    'installable': True,
    'application': False,
    'auto_install': False,
}
