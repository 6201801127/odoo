# -*- coding: utf-8 -*-
{
    'name': 'Recruitment Customisation',
    'version': '12.0.1.0.0',
    'summary': """Changes in Job Position and Requisition""",
    'description': """Advertisement Created""",
    'category': 'Module for STPI',
    'author': 'Dexciss Technology @RGupta',
    'company': 'Dexciss Technology ',
    'maintainer': 'Dexciss Technology ',
    'website': "https://www.dexciss.com",
    'version': '12.0.4',
    'depends': ['base','hr_employee_requisition','stpi_contract_pr','recruitment_up_stpi','hr_applicant'],
    'data': [
        'security/ir.model.access.csv',
        'security/employee_job_position.xml',
        'security/recruitment_advertisement.xml',
        'data/hr_advertisement_cron.xml',
        'data/emp_rec_type.xml',
        'security/recruitment_advertisement.xml',
        'wizard/update_advertisement.xml',
        'wizard/create_job_pos.xml',
        'views/hr_app_in.xml',
        'views/hr_requisition_application.xml',
        'views/hr_job_inherit.xml',
        'views/hr_recruitment_stage_inherit_view.xml',
        # 'views/hr_applicant_view.xml',
        'wizard/advertisement_publish_wizard_views.xml'

    ],

    # 'demo': [
    #     'data/previous_occupation_organisation_type_demo.xml',
    #
    # ],


    'installable': True,
    'application': True,
    'auto_install': False,
    'demo': True

}