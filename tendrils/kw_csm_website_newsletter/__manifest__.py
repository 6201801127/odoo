# -*- coding: utf-8 -*-
{
    'name': "CSM Website Newsletter",
    'summary': """CSM Website Newsletter""",
    'description': """ CSM News letter
        
    """,

    'author': "CSM Technologies",
    'website': "https://www.csm.tech",

    'category': 'Kwantify/Extra Tools',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'mail', 'kw_usability'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/kw_news_letter_group.xml',
        # 'views/views.xml',
        'views/templates.xml',
        'views/kw_newsletter_scheduler.xml',
        # 'views/news_letter_mail_template.xml',
        'views/news_letter_mail_template_new.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
}
