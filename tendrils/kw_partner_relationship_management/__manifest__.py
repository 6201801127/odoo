# -*- coding: utf-8 -*-
{
    'name': "Partner Relationship Management",

    'summary': """
        Kwantify Partner relationship management solution
        """,

    'description': """
        Kwantify partner relationship management solution
    """,

    'author': "CSM Technologies",
    'website': "https://www.csm.tech",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Kwantify/Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'board', 'crm'],

    # always loaded
    'data': [
        'security/kw_partner_profiling_security.xml',
        'security/ir.model.access.csv',
        # 'views/template.xml',
        'views/kw_partner_type_master_views.xml',
        'views/kw_service_tech_master_views.xml',
        'views/res_partner_views.xml',
        'views/kw_certification_master_views.xml',
        'views/kw_client_master_views.xml',
        'views/kw_product_category_view.xml',
        'views/kw_product_master_views.xml',
        'views/kw_partner_master_rel_view.xml',
        'views/kw_partner_profiling.xml',
        'views/kw_partner_report_view.xml',
        'views/kw_res_partner_contact_view.xml',
        'views/menus.xml',

        'data/product_category_data.xml',
        'data/partner_type_data.xml',
        'data/product_master_data.xml'
    ],
    'installable': True,
    'application': True
}