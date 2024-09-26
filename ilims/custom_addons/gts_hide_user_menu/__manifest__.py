# -*- coding: utf-8 -*-
{
    'name': "Hide User Menu",
    'summary': """""",
    'description': """
        Hide menus for user such as Documentation, Support, etc.
    """,

    'author': 'Geo Technosoft',
    'website': 'https://www.geotechnosoft.com',

    'category': 'web',
    'version': '0.1',
    # any module necessary for this one to work correctly
    'depends': ['web'],

    # always loaded
    'data': [

    ],
'qweb': [
        "static/src/xml/*.xml",
    ],

}
