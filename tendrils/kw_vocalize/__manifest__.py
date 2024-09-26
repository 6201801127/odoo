# -*- coding: utf-8 -*-
{
    'name': 'Kwantify Vocalize Form',
    'summary': """Kwantify vocalize Form""",
    'description': """Kwantify vocalize Form""",
    'category': 'Kwantify/Human Resources',
    'author': 'kwantify@csm.tech',
    'company': 'CSM Technologies',
    'maintainer': 'CSM Technologies ',
    'website': "https://www.csm.tech",
    'version': '1.0.1',
    'depends': ['base',],
    'data': [
        'security/ir.model.access.csv',

        'views/menu.xml',
        'views/res_config_setting_view.xml',
        # 'views/kw_auth_inherited.xml',
        'views/qweb/vocalize_voting.xml',
        'data/system_param_data.xml',   
        'views/assets.xml',
    ],

    # 'demo': [
    #     'data/previous_occupation_organisation_type_demo.xml',
    #
    # ],
    'qweb': [ 'views/qweb/menu_inherit.xml',],
    'installable': True,
    'application': True,
    'auto_install': False,

}
