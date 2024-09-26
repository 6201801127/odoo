# -*- coding: utf-8 -*-
{
    'name': 'GTS Change Request',
    'version': '14.0.0.1',
    'category': 'Project',
    'description': """
    This Module will show smart button for change request in Project form view.
    """,
    'depends': ['project', 'mail', 'gts_document_type', 'mail', 'quality_control_oca', 'web', 'gts_groups'],
    'data': [
        'security/security_view.xml',
        'security/ir.model.access.csv',

        'data/activity_data.xml',
        'wizard/close_cr_view.xml',
        'wizard/cr_reject_reason_view.xml',
        'wizard/project_task_wizard.xml',
        'wizard/submit_approval_view.xml',
        'wizard/cr_reject_view.xml',
        'views/change_request_view.xml',
        'views/change_request_menues.xml',
        'views/project_view.xml',
        'views/masters_view.xml',
        'data/email_template.xml',
        'data/cron_schedular.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
