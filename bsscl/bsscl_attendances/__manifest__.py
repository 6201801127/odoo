{
    'name': "bsscl_attendances",

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

    'depends': ['base','hr', 'hr_attendance','hr_attendance_autoclose','hr_attendance_reason'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/remark_wizard.xml',
        'views/attendance_view.xml',
        'views/report.xml',
        'views/kw_employee_apply_attendance.xml',
        
    ]
}