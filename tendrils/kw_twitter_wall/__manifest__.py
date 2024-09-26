# -*- coding: utf-8 -*-
{
    'name': "Kwantify Twitter Integration",

    'summary': """
        Twitter scroller from wall snippet in website""",

    'description': """
        Twitter scroller from wall snippet in website
    """,

    'author': "CSM Technologies",
    'website': "https://www.csm.tech",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Kwantify/Tools',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['website', 'website_twitter'],
    'data': [
        'security/ir.model.access.csv',
        'data/kw_website_twitter_cron_job_data.xml',
        'views/kw_website_twitter_snippet_templates.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
