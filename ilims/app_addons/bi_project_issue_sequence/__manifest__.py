# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Project Issue Sequence',
    'version': '14.0.0.0',
    'author': 'BrowseInfo',
    'category':'Project',
    'website': 'https://www.browseinfo.in',
    'summary': 'This module allow to create automatic sequence of project issue',
    'description':""" This module allow to create automatic sequence of project issue.""", 
    'license':'OPL-1',
    'depends':['project', 'mail', 'base', 'hr_timesheet', 'gts_stakeholder', 'analytic', 'gts_project_stages'],
    'data':[
        'data/ir_sequence_data.xml',
        'data/email_template.xml',
        'views/project_issue.xml',
        'views/project_view.xml',
        ],
    'installable': True,
    'auto_install': False,
    "images":['static/description/Banner.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
