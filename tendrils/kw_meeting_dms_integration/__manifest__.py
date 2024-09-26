# -*- coding: utf-8 -*-
{
    'name': "Kwantify Meeting DMS Integration",
    'summary': """Store meeting materials & MOMs at DMS""",
    'description': """
            Store meeting materials & MOMs at DMS
        """,
    'author': "CSM Technologies",
    'website': "https://www.csm.tech",
    'category': 'Kwantify/Integration',
    'version': '0.1',
    'depends': ['base', 'kw_dms', 'kw_meeting_schedule','kw_recruitment' ],
    'data': [
        'data/data_kw_meeting_dms_integration.xml',
        'data/dms_scheduler_data.xml',
        'views/res_config_setting.xml',
    ],
    "application": True,
    "installable": True,
    'auto_install': False,
}
