# -*- coding: utf-8 -*-
{
    'name': "EQ",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','kw_accounting','kw_skill_assessment'],

    # always loaded
    'data': [
        'security/kw_eq_security.xml',
        'security/ir.model.access.csv',
        'data/kw_eq_master_date.xml',
        'data/eq_css_data.xml',
        'views/kw_eq_email_template.xml',
        'views/kw_eq_revision_mail_templete.xml',
        'views/kw_eq_access_configuration.xml',
        'views/kw_eq_acc_head_sub_head.xml',
        'views/kw_eq_overhead_percentage_master.xml',
        'views/kw_eq_estimation.xml',
        'views/kw_eq_software_master.xml',
        'views/kw_eq_paticulars_master.xml',
        'views/kw_eq_ancillary_master.xml',
        'views/kw_eq_it_infra_master.xml',
        'views/kw_eq_designation_master.xml',
        'views/kw_eq_avg_rate_calculation.xml',
        'views/kw_eq_pbg_master.xml',
        'views/kw_eq_approval_configuration.xml',
        'views/kw_eq_report.xml',
        'views/kw_eq_replica.xml',
        'views/kw_eq_update_records.xml',
        'views/kw_eq_page_access.xml',
        'views/advance_for_eq.xml',
        'views/advance_eq_email_template.xml',
        'views/kw_eq_revision.xml',
        'views/menu.xml',
        'views/resource_qty_update_wiz.xml',
        'views/kw_eq_resource_report.xml',
    ],
    # only loaded in demonstration mode
    'application': True,
    'installable': True,
    'auto_install': False,
}