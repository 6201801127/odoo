# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Onboarding Process',
    'version': '1.0',
    'category': 'Human Resources/Recruitment',
    'sequence': 90,
    'summary': 'Track your recruitment pipeline',
    'description': "",
    'website': 'https://www.odoo.com/page/recruitment',
    'depends': [
        'hr','mail','hr_recruitment','website'
    ],
    'data': [
        'security/ir.model.access.csv',
		'views/kwonboard_onboarding_template.xml',
        'views/kwonboard_assets_frontend.xml',
        'views/kwonboard_educational_details_template.xml',
        'views/kw_resource_mapping.xml',
        'views/kw_onboarding_resource_mapping.xml',
        'views/kwonboard_message_view.xml',
       'views/kwonboard_personal_details_template.xml',
        'views/kwonboard_work_experience_template.xml',
        'views/kwonboard_identification_details_template.xml',
        'views/kwonboard_enrollment_views.xml',
		'views/email/kw_email_template.xml',
        'views/email/kw_email_otp_template.xml',
        'views/email/candidate_submit_template.xml',
        'views/email/config_email_template.xml',
        'views/email/config_completion_email_template.xml',
    ],
    'demo': [
        
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}
