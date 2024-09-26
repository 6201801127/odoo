# -*- coding: utf-8 -*-
{
    'name': "Kwantify Meeting API Integration",
    'version': '12.0.1.0.0',
    'summary': """
       Meeting Room APIs """,

    'description': """
       This is used to fetch all meeting room information with the help of APIs.
    """,
    'category': 'Kwantify/API',
    'author': 'CSM Technologies',
    'company': 'CSM Technologies',
    'maintainer': 'CSM technologies',
    'website': "https://www.csm.tech",

    'depends': ['base','restful','kw_meeting_schedule'],

    # always loaded
    'data': [

    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    'installable': True,
    'application': False,
    'auto_install': False,
}