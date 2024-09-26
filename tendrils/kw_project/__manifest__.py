# -*- coding: utf-8 -*-
{
    'name': 'Kwantify Project',
    'version': '0.1',
    'summary': '''Organize and schedule your projects''',
    'description': '''Organize and schedule your projects''',
    'category': 'Kwantify/Project',
    'author': 'CSM Technologies',
    'company': 'CSM Technologies',
    'maintainer': 'CSM Technologies',
    'website': 'https://www.csm.tech',
    'depends': ['base', 'project', 'crm', 'kw_employee'],  # , 'kw_kwantify_integration'
    'data': [
        'security/project_security.xml',
        'security/ir.model.access.csv',
        'views/kw_project_inherit.xml',
        'views/kw_employee_inherits.xml',
        'views/kw_project_tagging.xml',
        'views/kw_project_crm_inherit.xml',
        'data/data_cron.xml',
        'data/opportunity_data.xml',
        'views/res_config_settings_views.xml',
        # Email Templates
        'views/email/project_mail_template.xml',
        'views/kw_project_module.xml',
        'views/kw_debtor_list.xml',
        'views/opportunity_dashboard_port.xml',
        'views/kw_billing_dashboard_port.xml',
        'views/kw_sync_sales_portlet_data.xml',
    ],
    'qweb': [

    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
}