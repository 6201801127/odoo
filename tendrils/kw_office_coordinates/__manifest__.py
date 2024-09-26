# -*- coding: utf-8 -*-
{
    'name': "Kwantify Office Co-ordinates",
    'summary': "A module to store details of an organisation",
    'description': "Used to maintain Office details",
    'author': "CSM Technologies",
    'website': "https://www.csm.tech",
    'category': 'Kwantify/Tools',
    'version': '0.1',
    
    # any module necessary for this one to work correctly
    'depends': ['base','kw_employee','kw_announcement','hr'],

    # always loaded
    'data': [
        'security/security_office_manager_group.xml',
        'security/ir.model.access.csv',
        'views/kw_office_coordinate.xml',
        'views/kw_office_city_master.xml',
        'views/kw_office_contacts.xml',
        # 'views/kw_office_menu_item.xml',
        'views/office_address.xml',
        # 'views/kw_office_contact_details.xml',
        # 'views/api.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}