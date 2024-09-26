# -*- coding: utf-8 -*-
{
    'name': "Kwantify Training DMS Integration",
    'summary': """Store training materials at dms""",
    'description': """Store training materials at dms""",
    'author': "CSM Technologies",
    'website': "https://www.csm.tech",
    'category': 'Kwantify/Integration',
    'version': '0.1',
    'depends': ['base', 'kw_training', 'kw_dms'],
    'data': [
        "views/kw_training_material_views.xml",
        "data/kw_training_dms_integration_data.xml",
        "views/res_config_settings.xml",
    ],
    "application": True,
    "installable": True,
    'auto_install': False,
}
