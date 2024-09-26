# -*- coding: utf-8 -*-
{
    'Module Name': "Change Request Management",

    'summary': """Kwantify Change Request Management""",

    'description': """
        This module provides functionality for managing change requests in Kwantify
    """,

    'author': 'CSM Technologies',
    'company': 'CSM Technologies',
    'maintainer': 'CSM Technologies',
    'website': "https://www.csm.tech",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'kw_employee', 'kw_project','kw_timesheets'],
    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'data/ir_sequence_data.xml',
        'data/cr_apply_mail.xml',
        'data/cr_uploaded_mail.xml',
        'data/cr_rollbacked_mail.xml',
        'data/cr_cancel_mail.xml',
        'data/cr_request_rollbacked_mail.xml',
        'data/sync_officer_access.xml',

        'views/cr_menu.xml',
        'views/kw_cr_management.xml',
        'views/environment_master.xml',
        'views/project_cr_configuration.xml',
        'views/environment_sequence.xml',
        'views/project_environment_management.xml',
        'views/cr_activity_master.xml',
        'views/cr_uploaded_wizard.xml',
        'views/cr_rollbacked_wizard.xml',
        'views/cr_cancel_wizard.xml',
        'views/cr_request_rollback_wizard.xml',
        'views/cr_incident_management.xml',
        'views/server_configuration.xml',
        'views/project_master_config.xml',
        'views/kw_domain_bills_details.xml',
        'views/domain_server_master.xml',
        'views/cr_sr_dashboard.xml',

        'reports/cr_management_report_view.xml',
        'reports/server_data_center_report.xml',
        'reports/project_config_pdf_report.xml',
        'reports/domain_billing_report.xml',
        'reports/domain_pdf_report_view.xml',
        'reports/project_wise_cr_sr_details.xml',
        'reports/time_wise_uploaded_cr_sr_report.xml',
        'reports/uploaded_cr_sr_by_adminstrative_report.xml',
        'reports/server_instance_report.xml',
        'reports/working_project_numbers.xml',
        'reports/cr_env_sequence_statictics.xml',

    ],
    'qweb': ["static/src/xml/sync_officer_access.xml",
             "static/src/xml/sync_config_manager.xml",
             "static/src/xml/cr_sr_dashboard_views.xml"],
             

    'application': True,
    'installable': True,
    'auto_install': False,

}
