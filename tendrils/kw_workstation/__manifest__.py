{
    'name': "Kwantify Workstation",

    'summary': """
       Kwantify Workstation Management System
    """,

    'description': """
       Manage the Workstations
    """,

    'author': "CSM Technologies",
    'website': "https://www.csm.tech",

    'category': 'Kwantify/Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'kw_employee'],

    # always loaded
    'data': [
        'security/kw_workstation_security.xml',
        'security/ir.model.access.csv',

        'data/cron_ws_assign.xml',
        'data/mail_ws_assignment_schedule.xml',

        # 'views/kw_workstation_employee.xml',
        # 'views/kw_workstation_emp_tagging.xml',
        'views/kw_workstation_master.xml',
        'views/kw_infrastructure_master.xml',
        'views/kw_workstation_type_master.xml',
        # 'views/kw_workstation_config.xml',
        'views/kw_workstation_seatmap.xml',
        'views/kw_workstation_menu.xml',
        'views/employee_system_view.xml',
        'views/kw_workstation_assign.xml',

        'static/src/layouts/seat_map_sixth_floor_c_block.xml',
        'static/src/layouts/seat_map_sixth_floor_s_block.xml',
        'static/src/layouts/seat_map_sixth_floor_m_block.xml',
        'static/src/layouts/seat_map_fifth_floor.xml',
        'static/src/layouts/patia_ground_floor.xml',
        'static/src/layouts/patia_first_floor.xml',
        'static/src/layouts/patia_security_block.xml',
        'static/src/layouts/patia_admin_and_it_block.xml',
        'static/src/layouts/ihub_ground_floor.xml',
        'static/src/layouts/delhi_office_layout.xml',
        'static/src/layouts/jaipur_office_layout.xml',
        'static/src/layouts/noida_office_layout.xml',
        'static/src/layouts/patna_office_layout.xml',
        'static/src/layouts/ranchi_office_layout.xml',

        'views/kw_shift_workstation_request.xml',
        'views/template_of_shift_attendance.xml',
        'views/workstation_cc_notify.xml',

        'reports/employee_workstation_mis_report.xml',
        'reports/kw_employee_hybrid_report.xml',
        'reports/employee_workstation_attendance_report.xml',
        'reports/kw_emp_monthly_hybrid_report.xml',

    ],
    "qweb": [

    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
# -*- coding: utf-8 -*-
