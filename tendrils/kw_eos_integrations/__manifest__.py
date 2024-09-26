# -*- coding: utf-8 -*-
{
    'name': "kw_eos_integrations",

    'summary': """
        EOS Integration """,

    'description': """
        EOS Integration Module
    """,

    'author': "CSM",
    'website': "https://www.csm.tech",

    'category': 'Kwantify/Integration',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','kw_tour','kw_advance_claim','kw_visiting_card','kw_onboarding','kw_hr_leaves','hr_holidays','kw_eos'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/mail_end_of_service.xml',
        'views/remark_form.xml',
        'views/views.xml',
        'views/eos_report_views.xml',
        'data/eos_remainder_mail.xml',
        'views/mail_before_last_working_day.xml',
        'views/kw_eos_report_wiz.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}