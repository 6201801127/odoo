# -*- coding: utf-8 -*-
{
    'name': "Kwantify Announcement",

    'summary': """
        Broadcasting organization announcements among internal users and posting comments""",

    'description': """
       Broadcasting organization announcements among internal users and posting comments
    """,

    'author': "CSM Technologies",
    'website': "https://www.csmpl.com",
    'category': 'Kwantify/Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','kw_employee','kw_utility_tools'],
    # always loaded
    'data': [
        'security/kwannounce_security.xml',
        'security/ir.model.access.csv',
        'views/assests.xml',
        'views/kw_announcement_menus.xml',

        'views/kw_announcement_groups.xml',

        'views/kw_announcement_category_view.xml',
        'views/kw_announcement_view.xml',
        'views/kw_announcement_comments_view.xml',
        'views/kw_announcement_template_view.xml',

        'data/kwannounce_category_data.xml',
        'data/kwannounce_new_joinee_template.xml',
        
        'views/email/kw_announcement_email_template.xml',
        'views/kw_announcement_search_panel.xml',
        'views/kw_announcement_contact.xml',
    ],
    'qweb': [
        'static/src/xml/kwannounce_comment_box.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        
    ],
    'installable': True,
    'application': True,    
    'auto_install': False,
}
