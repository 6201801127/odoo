# -*- coding: utf-8 -*-
{
    'name': "Work From Home",
    'summary': """Enable WFH features for employees""",
    'description': """Enable WFH features for employees""",
    'author': "CSM Technologies",
    'website': "https://www.csmpl.com",
    'category': 'Kwantify/Employee',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'kw_dynamic_workflow', 'kw_employee', 'kw_hr_attendance', 'kw_onboarding'],  # 'crm',

    # always loaded
    'data': [
        # security files
        'security/security.xml',
        'security/ir.model.access.csv',

        # data file
        'data/ir_sequence_data.xml',
        'data/ir_cron.xml',
        'views/res_config_settings.xml',
        'data/kw_wfh_type_data.xml',
        'data/kw_wfh_reason_data.xml',
        'data/kw_wfh_request_workflow.xml',
        'data/kw_wfh_mail_data.xml',
        # 'data/kw_wfh_deliverable_workflow.xml',
        'wizard/kw_wfh_request_remark_wizard.xml',
        'wizard/kw_wfh_deliverables_wizard.xml',
        'wizard/kw_wfh_report_wizard.xml',
        'views/email/kw_wfh_employee_request_mail.xml',
        'views/email/kw_wfh_mail_template.xml',
        'views/email/kw_wfh_emp_request_extension_mail.xml',
        'views/email/kw_wfh_extension_mail_template.xml',
        'views/email/kw_wfh_end_process_mail.xml',
        'views/reports/kw_wfh_reports.xml',
        'views/templates/kw_wfh_view_success_form.xml',

        # view files
        'views/kw_wfh_type_master.xml',
        'views/kw_wfh_request.xml',
        'wizard/kw_wfh_end_process_wizard.xml',
        'views/kw_wfh_reason_master.xml',
        'views/reports/reported_task.xml',
        'views/kw_wfh_request_takeaction.xml',
        'views/kw_wfh_initiative_by_csm.xml',
        'views/kw_wfh_extension.xml',
        'views/kw_wfh_deliverables_emp_action.xml',
        'views/kw_wfh_active_wfh.xml',
        'views/kw_wfh_inherit_hr_employee_form_view.xml',
        'views/kw_wfh_employee_system_inherit.xml',
        'views/kw_wfh_hr_employee_view.xml',
        'views/wfh_by_hr_process.xml',
        'views/employee_system_view.xml',
        'views/menuitem.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        
    ],
    'installable': True,
    'application': True,    
    'auto_install': False,
}
