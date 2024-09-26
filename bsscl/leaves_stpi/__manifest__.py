{
    'name': 'STPI Leave Management',
    'version': '12.0.2.0',
    'summary': 'Manage Leave Requests',
    'description': """
        Helps you to manage Leave Requests of your company's staff.
        """,
    'category': 'STPI',
    'author': 'CSM Technologies',
    'company' : 'CSM Technologies',
    'website': "http://www.csm.tech",
    'maintainer' : 'CSM Technologies',
    'depends': [
        # 'hr_holidays','hr','sandwich_rule','hr_branch_company','hr_payroll','hr_employee_stpi','resource','web','groups_inherit'],
        'hr_holidays','hr','sandwich_rule','hr_branch_company', 'web', 'resource','bsscl_employee'],
    'data': [

        'security/ir.model.access.csv',
        'security/security.xml',
        'views/hr_leave_type_extended.xml',
        'views/leave_type_view.xml',
        'views/employee_stages.xml',
        'views/leave_employee_type_view.xml',
        'views/hr_employee_view.xml',
        'views/hr_leave_view.xml',
        # 'views/hr_payslip_view.xml',
        'views/hr_leave_allocation_view.xml',
        'views/resource_calendar_view.xml',
        'views/leave_summary_report.xml',
        # 'views/report_leave_report.xml'
        # start : merged from hr_employee_stpi
        'data/hr_leave_cron.xml',
        # end : merged from hr_employee_stpi
        'data/holidays_type_data.xml',
        'data/hr_leave_type_data.xml',
        'data/allocate_leave_cron_job.xml',
        'data/expire_leave_cron_job.xml',
        'data/holiday_calendar.xml',
    ],
    'qweb': ['static/src/xml/*.xml', ],
    'demo': [],
    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
