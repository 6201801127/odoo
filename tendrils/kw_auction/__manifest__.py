# -*- coding: utf-8 -*-
{
    'name': "Auction",

    'summary': """ 

    """,

    'description': """

    """,

    'author': "CSM Technologies",
    'website': "https://www.csm.tech",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': '',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr', 'base_address_city'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/kw_auction_date_master_view.xml',
        'views/kw_auction_it_declaration_view.xml',
        'views/kw_auction_view.xml',
        'views/kw_auction_report_view.xml',
        'views/kw_book_auction_wizard_view.xml',
        'views/menu.xml',
        'views/auction_ref_id_sequence.xml',
        'views/email/kw_auction_mail_templates.xml'

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'qweb': [
        "static/src/xml/*.xml",
    ]
}