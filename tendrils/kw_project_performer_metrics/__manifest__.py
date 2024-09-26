# -*- coding: utf-8 -*-
{
    'name': "Project Performance Metrics",
    'summary': """
        To reduce defects and maintain the quality of products and services to achieve the business objectives. """,

    'description': """
        Project Performer Metrices
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base','kw_project','kw_resource_management'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/metrics_mail_template.xml',
        'views/kw_project_performer.xml',
        'wizard/metric_remark.xml',
        'views/menu.xml',
        
    ],
    'installable': True,
    'application': True,
}