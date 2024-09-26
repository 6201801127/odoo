# -*- coding: utf-8 -*-
{
    'name': 'Kwantify EOF Form',
    'summary': """Kwantify EOF Form""",
    'description': """Kwantify EOF Form""",
    'category': 'Kwantify/Human Resources',
    'author': 'kwantify@csm.tech',
    'company': 'CSM Technologies',
    'maintainer': 'CSM Technologies ',
    'website': "https://www.csm.tech",
    'version': '1.0.1',
    'depends': ['base','tds'],
    'data': [
        'security/ir.model.access.csv',
        'views/kw_epf_report.xml',
        'views/qweb/kw_epf_form.xml',
        'views/res_config_settings.xml',
        
    ],

    # 'demo': [
    #     'data/previous_occupation_organisation_type_demo.xml',
    #
    # ],

    'installable': True,
    'application': True,
    'auto_install': False,

}
