# -*- coding: utf-8 -*-
{
    'name': "Kwantify Leave And Attendance Integration",

    'summary': """
        Integration with attendance module for Comp off""",

    'description': """
        Integration with attendance module for Comp off leave type and misc
    """,

    'author': "CSM Technologies",
    'website': "https://www.csm.tech",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category'  : 'Kwantify/HR+',
    'version'   : '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','kw_hr_attendance','kw_hr_leaves','kw_tour'],                                                                                                            

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'data/leave_types_data.xml',
        'views/hr_comp_off_leave_allocation_views.xml',
        'views/kw_off_day_entry_views.xml',
        'views/menus.xml',

        'data/kw_comp_off_apply_mail.xml',
        'data/kw_comp_off_approval_mail.xml',
        'data/kw_comp_off_reject_mail.xml',
        'data/kw_comp_off_forward_mail.xml',
        'data/kw_leave_on_tour_cron.xml',
        
    ],
    'installable': True,
    'application': False,
}