# -*- coding: utf-8 -*-
{
    "name": "Kwantify Claim",
    "summary": "Claim",
    "description": "Claim details module",
    "author": "CSM Technologies",
    "website": "https://www.csm.tech",

    "category": "Kwantify/Human Resources",
    "version": "0.1",

    "depends": ["base", "kw_employee", "hr",'kw_advance_claim'],
    "data": [
        "security/ir.model.access.csv",
        # "security/security.xml",
        'report/claim_report.xml',

        
        'report/cancel_reject_claim_report.xml',
        'report/settlement_claim_report.xml',
        'views/claim_notification_approver.xml',
        'views/claim_notification_mail_template.xml',
        # 'data/claim_category.xml',
        # 'data/claim_sub_category.xml',
        'report/category_sub_category_report.xml',
        'report/approval_non_approval_report.xml',
        "views/category_masters.xml",
        "views/claim.xml",

    ],
   
    "application": True,
    "installable": True,
    "auto_install": False,
}
