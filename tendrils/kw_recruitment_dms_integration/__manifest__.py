# -*- coding: utf-8 -*-
{
    'name': "Kwantify Recruitment DMS Integration",
    'summary': """Store recruitment CV materials at Document""",
    'description': """
    Store recruitment CV materials at Document
    """,
    'author': "CSM Technologies",
    'website': "https://www.csm.tech",
    'category': 'Kwantify/Integration',
    'version': '0.1',
    'depends': ['base', 'kw_recruitment', 'kw_dms'],
    'data': [
        'security/ir.model.access.csv',
        'data/kw_recruitment_dms_integration_data.xml',
        'data/dms_scheduler_data.xml',
        'views/kw_recruitment_cv_material_view.xml',
        'views/res_config_setting.xml',
        'views/document_wizard.xml',
    ],
    "application": True,
    "installable": True,
    'auto_install': False,
}
