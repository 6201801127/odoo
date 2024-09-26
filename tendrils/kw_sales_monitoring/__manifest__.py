{
    'name': "Sales Monitoring",
    'version': '0.1',
    'author': "Kwantify",
    'category': 'Kwantify/Sales',
    'description': 'Sales Monitoring',
    'website': "https://www.csm.tech",
    
    'depends': ['base', 'web', 'mail',"crm",'kw_budget','kw_eq'],
    
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        
        'data/sequence.xml',
        'data/stages.xml',

        'views/crm_stages.xml',
        'views/csg_sales_collection.xml',
        'views/cold_lead_view.xml',
        'views/masters.xml',
        'views/warm_lead_view.xml',
        'views/lac_view.xml',
        'views/qualified_leads_view.xml',
        'views/pac_view.xml',

        'views/question_master.xml',
        'views/value_master.xml',
        'views/criteria_master.xml',
        'views/hot_lead_view.xml',
        'views/opportunity_review.xml',
        'views/service_request.xml',
        'views/assets.xml',
        'workorder/views/workorder.xml',
        'workorder/views/sequence.xml',
        'views/project_milestone.xml',
        'views/change_order_wizard_view.xml',
        'views/menus.xml',
    ],
    
    'installable': True,
    'auto_install': True,
    'application': True,
}
