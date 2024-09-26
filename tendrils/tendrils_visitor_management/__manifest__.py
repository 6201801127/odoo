# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
#############################################################################
#
#       Module Name : Visitor Management System
#       Create By : Chandrasekhar Dash  
#       Created On : 10-Jun-2024
#       Assign By : Abhijit Swain
#
#############################################################################
{
    'name': "Tendrils Visitor Management",
    'summary': "Tendrils Visitor Management.",

    'description': "Tendrils Visitor Details Management",

    'author': "CSM Tech",
    'website': "https://www.csm.tech",

    # Categories can be used to filter modules in modules listing

    'category': 'Kwantify',
    'version': '0.1',

    # any module necessary for this one to work correctly

     'depends': [
        'base',
        'hr',
        'contacts',
        'mail',
    ],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/visitor_data.xml',
        'views/menu.xml',
        'data/visitors_email.xml',
        'data/system_parameter_mail.xml',

    ],

    'application': True,
    'installable': True,
    'auto_install': False,

}
