# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Create Issue from Lead',
    'category': 'CRM',
    'version': '14.0.0.0',
    'description': """
    Issue on Lead, Add Issue from lead, Issue Lead, Create Project Issue from Lead
""",
    'license':'OPL-1',
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.in',
    'depends': ['base', 'crm', 'sale','project'],
    
    'data': [ 'security/ir.model.access.csv',
             'views/crm_lead_view.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    "images":["static/description/Banner.png"],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
