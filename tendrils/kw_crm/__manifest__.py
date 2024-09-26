# -*- coding: utf-8 -*-
{
    'name': "Kwantify CRM",
    'version': '0.1',
    'summary': """Organize and schedule your projects""",
    'description': """Organize and schedule your projects""",
    'category': 'Kwantify/Project',
    'author': 'CSM Technologies',
    'company': 'CSM Technologies',
    'maintainer': 'CSM Technologies',
    'website': "https://www.csm.tech",
    'depends': ['base','crm'],
    'data': [
        'security/project_security.xml',
        'security/ir.model.access.csv',

        'data/data_kw_crm_lead_type_master.xml',
        'data/data_kw_crm_lead_source_master.xml',
        'data/data_kw_crm_tender_type_master.xml',
        'data/data_kw_crm_tender_source_master.xml',
        'data/data_kw_crm_financial_evaluation_master.xml',

        'views/competitor_views.xml',
        'views/kw_project_crm_inherit.xml',
        'views/kw_lead_competitor_view.xml',
        'views/kw_lead_category_master_view.xml',
        'views/kw_crm_lead_source_master.xml',
        'views/kw_crm_tender_type_master.xml',
        'views/kw_crm_tender_source_master.xml',
        'views/kw_crm_financial_evaluation_master.xml',
        'views/kw_crm_lead_type_master.xml',
    ],
    'qweb': [

    ],
    'demo': [ ],
    'installable': True,
    'application': False,
}
