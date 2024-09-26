# -*- coding: utf-8 -*-
{
    'name': "Kwantify Training Meeting Integration",
    'summary': """This module is used to integrate training module with meeting schedule module.""",
    'author': "CSM Technologies",
    'website': "https://www.csm.tech",
    'category': 'Kwantify/Integration',
    'version': '0.1',
    'depends': ['base', 'kw_training', 'kw_meeting_schedule', 'kw_meeting_zoom_integration'],
    'data': [
            'views/kw_training_schedule_view.xml',
            'views/kw_training_meeting_view.xml',
            'views/kw_meeting_schedule_zoom_inherited_view.xml',
            'views/kw_training_schedule_action_forms.xml',
            'views/kw_my_training_view.xml',
            ],
    "application": False,
    "installable": True,
    "auto_install": False,
}
