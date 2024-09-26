# -*- coding: utf-8 -*-
{
    'name': "Kwantify Advance Claim",

    'summary': """Salary Advance, Petty Cash & Claim features for employee""",

    'author': "CSM Technologies",
    'website': "https://www.csmpl.com",
    'category': 'Kwantify/Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','kw_dynamic_workflow','kw_employee'],
    # always loaded
    'data': [
      # security files
      'security/security.xml',
      'security/ir.model.access.csv',
      # data files
      'data/kw_advance_groups.xml',
      'data/kw_advance_type.xml',
      'data/ir_sequence_data.xml',
      'data/kw_advance_purpose.xml',
      # 'data/kw_claim_category.xml',
      # 'data/kw_claim_type.xml',
      'data/kw_adv_buffer_period_data.xml',
      'data/kw_salary_advance_workflow.xml',
      'data/kw_petty_cash_workflow.xml',
      'data/kw_claim_settlement_workflow.xml',
      'data/cron_salary_advance_update_paid_status_scheduler.xml',
      'wizard/kw_advance_salary_remarks_wizard.xml',
      'wizard/kw_apply_petty_cash_remark_wizard.xml',
      'wizard/kw_claim_settlement_remark_wizard.xml',
      'wizard/kw_advance_claim_report_wizard.xml',
      'wizard/kw_adv_pre_closer_wizard.xml',
      'wizard/kw_adv_relaxation_wiz.xml',
      'views/res_config_Settings.xml',
      'views/email/kw_salary_advance_mail.xml',
      'views/email/kw_petty_cash_mail.xml',
      'views/email/kw_claim_mail.xml',
      # view files
      'views/kw_adv_ret_config.xml',
      'views/kw_advance_purpose.xml',
      'views/kw_allow_for_another_loan.xml',
      'views/kw_advance_allow_restricted_loan.xml',
      'views/kw_advance_type.xml',
      'views/kw_adv_buffer_period_master.xml',
      'views/kw_amount_eligibility_conf.xml',
      'views/kw_claim_category.xml',
      'views/kw_claim_type_master.xml',
      'views/kw_eligibility_amnt_exec.xml',
      'views/kw_interest_exec.xml',
      'views/kw_advance_claim_groups.xml',
      'wizard/kw_apply_salary_advance_wizard.xml',
      'views/kw_apply_salary_advance.xml',
      'views/kw_apply_salary_advance_takeaction.xml',
      'views/kw_apply_salary_advance_takeaction_account.xml',
      'wizard/kw_apply_claim_wizard.xml',
      'wizard/kw_apply_petty_cash_wizard.xml',
      'views/kw_apply_petty_cash.xml',
      'views/kw_apply_petty_cash_takeaction.xml',
      'views/kw_apply_petty_cash_takeaction_account.xml',
      'views/kw_group.xml',
      'views/kw_claim_settlement.xml',
      'views/kw_claim_settlement_takeaction.xml',
      'views/kw_claim_settlement_takeaction_account.xml',
      'views/kw_advance_claim_report.xml',
      'views/reports/report_action.xml',
      'views/reports/report_advance_claim_settlement.xml',
      'views/menuitem.xml',
      
    ],
    # only loaded in demonstration mode
    'demo': [
        
    ],
    'installable': True,
    'application': True,    
    'auto_install': False,
}
