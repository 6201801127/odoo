# -*- encoding: utf-8 -*-
{
    "name": "Holiday Calendar",
    "summary": "Calendar",
    "description": "Calendar where we can see my all holidays battalion wise",
    "category": "Custom",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "web",
        "hr",
        "hr_holidays",
        "resource",
        "sandwich_rule",
        "base_branch_company",
        "hr_employee_in",
    ],
    "data": ["data/holiday_calendar.xml", "views/assets.xml"],
    "qweb": [
        "static/src/xml/*.xml",
    ],
}
