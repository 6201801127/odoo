# -*- coding: utf-8 -*-
{
    'name': "Kwantify Local Visit",
    'version': '0.1',
    'summary': """
       This shall be applicable to all employees (Regular & Onsite) at CSM.""",

    'description': """
       This shall be applicable to all employees (Regular & Onsite) at CSM, who are required 
       to travel locally on account of business/project needs/training/personal work during official timing.
    """,
    'category': 'Kwantify/Employee',
    'author': 'CSM Technologies',
    'company': 'CSM Technologies',
    'maintainer': 'CSM Technologies',
    'website': "https://www.csm.tech",

    'depends': ['base', 'hr', 'kw_branch_master', 'kw_dynamic_workflow', 'kw_web_notify', 'crm'],

    # always loaded
    'data': [
        'security/kw_lv_security.xml',
        'security/ir.model.access.csv',

        # data files
        'data/kw_lv_category.xml',
        'data/kw_lv_dynamic_workflow.xml',
        'data/kw_lv_activity_master.xml',
        'data/kw_lv_sub_category_master.xml',
        'data/kw_lv_vehicle_category_master.xml',
        'data/kw_lv_settlement_dynamic_workflow.xml',
        'data/kw_lv_stage_master.xml',
        'data/mail_activity_data.xml',
        'data/kw_lv_cron.xml',

        # Views
        'views/kw_lv_activity_master_view.xml',
        'views/kw_lv_category_master_view.xml',
        'views/kw_lv_sub_category_master_view.xml',
        'views/kw_lv_vehicle_category_master.xml',
        'views/kw_lv_vehicle_master.xml',
        'views/inherit_partner_view.xml',
        'views/kw_lv_meeting.xml',
        'views/kw_lv_apply.xml',
        'views/kw_lv_business.xml',
        'views/kw_lv_office_in.xml',
        'views/kw_lv_view_lv_view.xml',
        'views/kw_lv_take_action_view.xml',
        'views/kw_lv_approval_remark_views.xml',
        # 'views/res_config_setting.xml',
        'views/kw_lv_settlement_apply.xml',
        'views/kw_lv_settlement_take_action_view.xml',
        'views/kw_lv_settlement_approval_remark_views.xml',
        'views/kw_lv_settlement_payment.xml',
        'views/kw_lv_stage_master.xml',

        ## Wizard
        'wizard/kw_lv_settlement_payment.xml',

        ## Reports
        'report/kw_lv_apply_report.xml',
        'report/kw_lv_business_report.xml',
        'report/kw_lv_settlement_report.xml',
        'report/lv_claim_report.xml',

        ## Mails
        'views/Mail Templetes/kw_lv_office_out_mail.xml',
        'views/Mail Templetes/kw_lv_office_in_mail.xml',
        'views/Mail Templetes/kw_lv_settlement_apply_mail.xml',
        'views/Mail Templetes/kw_lv_settlement_take_action_mail.xml',
        'views/Mail Templetes/kw_lv_settlement_paid_mail.xml',
        'views/Mail Templetes/kw_lv_intimate_to_ofc_out_mail.xml',
        'views/Mail Templetes/kw_lv_ofc_out_group.xml',
        'views/Mail Templetes/kw_lv_ofc_out_other_applied.xml',
        'views/Mail Templetes/kw_lv_travel_desk_mail.xml',
        'views/Mail Templetes/kw_lv_auto_approve_mail.xml',
        'views/Mail Templetes/kw_lv_forward_to_upper_ra_mail.xml',
        'views/Mail Templetes/kw_lv_ra_or_upper_ra_approval_mail.xml',
        'views/Mail Templetes/kw_monthly_auto_approval_mail.xml',
        'views/Mail Templetes/kw_lv_reminder_mail.xml',

        'views/menuitem.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
