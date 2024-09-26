# -*- coding: utf-8 -*-
{
    'name': "Kwantify KT Meeting Integration",
    'summary': """This module is used to integrate KT module with meeting schedule module.""",
    'author': "CSM Technologies",
    'website': "https://www.csm.tech",
    'category': 'Kwantify/Integration',
    'version': '0.1',
    'depends': ['base', 'kw_kt', 'kw_meeting_schedule', 'kw_meeting_zoom_integration'],
    'data': [
            'views/kw_kt_schedule_view.xml',
            ],
    "application": False,
    "installable": True,
    "auto_install": False,
}
