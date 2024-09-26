# -*- coding: utf-8 -*-
{
    'name': "Guest House",

    'summary': """Kwantify Guest House""",

    'description': """
        Independent guest accommodation with basic amenities""",

    'author': "CSM Technologies",
    'website': "https://www.csm.tech",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Kwantify/Tour',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'base_address_city', 'kw_tour'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/kw_facilities_master_view.xml',
        'views/kw_guest_house_master_view.xml',
        'views/kw_custom_view.xml',
        'views/kw_guest_house_booking_view.xml',
        'views/kw_house_master_feedback_view.xml',
        'views/kw_guest_house_report_view.xml',
        'data/kw_guest_house_data.xml',
        'views/menu.xml',
        'views/booking_sequence.xml',
        'views/email/kw_guesthouse_mail_templates.xml',
        'data/reminder_mail.xml',
        
    ],
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}