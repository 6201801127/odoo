{
    'name': "bsscl_employee",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "CSM Technologies",
    'website': "http://www.csm.tech",

    'category': 'BSSCL',
    'version': '0.1',

    'depends': ['hr', 'base_branch_company','hr_recruitment','employee_stages','hr_contract','portal','contacts',
	    'hr_holidays','base_address_city','kw_handbook'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        # 'data/relative_type_data.xml',
        'data/administrative_task_type_demo.xml',
        'data/discipline_category.xml',
        'views/administrative_task_master.xml',

        'views/employee_category_views.xml',
        'views/employee_religion_views.xml',
        'views/relative_type_views.xml',
        'views/employee_relative.xml',
        'views/employee_document_view.xml',

        'views/disciplinary_action.xml',
        'views/vrs.xml',
        'wizards/create_wizard.xml',
        'views/change_request.xml',

        'views/hr_employee_views.xml',
        'views/employee_directory_view.xml',
        'views/hr_recruitment_view.xml',
        'views/inherit_hindi_view.xml',
        'views/hr_employee_reward.xml',
        'views/hr_contract_inherit.xml',
        'views/employee_type.xml',

        'views/hr_resume_views.xml',
        'views/helpdesk_view.xml',
        'views/helpdesk_calltype_master.xml',
        'views/helpdesk_category.xml',
        'views/helpdesk_sub_category.xml',
        'views/manage_helpdesk_view.xml',


        'wizards/employee_action_select.xml',
        'wizards/employee_administrative_task_wiz.xml',
        'views/hr_employee_document_master_views.xml',
        'views/inherited_hr_employee_view.xml',
        'report/employee_service_book.xml',
        'report/print_template_transfer.xml'
    ],

    'demo': [
        # 'data/hr_resume_demo.xml'
        ],

    # 'qweb': [
    #     'static/src/xml/resume_templates.xml',
    #     'static/src/xml/skills_templates.xml',
    # ],
}

