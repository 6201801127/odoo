{
    'name': 'Kwantify HR Holidays Public',
    'description': 'Manage Public Holidays',
    'summary': "Manage Public Holidays",
    'category'  : 'Kwantify/HR+',
    'depends': [
        'base','kw_branch_master','resource'
    ],
    'data': [
        # 'data/data.xml',
        'security/ir.model.access.csv',
        'views/hr_holidays_public_view.xml',
        'views/hr_holidays_shift_view.xml',
        # 'views/hr_holidays_greetings.xml',
        # 'views/hr_leave_type.xml',
        # 'views/resource_calendar_views.xml',
        'wizards/holidays_public_next_year_wizard.xml',
    ],
    'installable': True,
}
