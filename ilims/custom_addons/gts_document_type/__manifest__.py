# -*- coding: utf-8 -*-
{
    'name': 'GTS Document Type',
    'version': '14.0',
    'category': 'Project',
    'description': """
    """,
    'depends': ['project', 'base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/document_type.xml',
        'views/attachmment.xml',
        'views/project_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}