# -*- coding: utf-8 -*-
{
    'name': "Kwantify Corporate Gifting",
    'summary': "",
    'description': "",
    'author': "CSM Technologies",
    'website': "https://www.csmpl.com",
    'category': 'Kwantify/Admin',
    'version': '0.1',
    'depends': ['base', 'crm', 'contacts'],
    'data': [
        'security/kw_corporate_security.xml',
        'security/ir.model.access.csv',
        'data/data_masters.xml',
        'views/menuitems.xml',
        'views/kw_occasion_master.xml',
        'views/res_partner_views.xml',
        'views/kw_corporate_gifting.xml',
        'views/gift_details.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
