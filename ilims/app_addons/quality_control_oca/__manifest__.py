# Copyright 2010 NaN Projectes de Programari Lliure, S.L.
# Copyright 2014-2021 Tecnativa Pedro M. Baeza
# Copyright 2014 Oihane Crucelaegui - AvanzOSC
# Copyright 2017-2020 ForgeFlow S.L.
# Copyright 2017 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Quality Control OCA",
    "version": "13.0.1.1.0",
    "category": "Quality Control",
    "license": "AGPL-3",
    "summary": "Generic infrastructure for quality tests.",
    "author": "AvanzOSC, Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "depends": ["product", "project", "base", "web", "gts_acceptance_management"],
    "data": [
        "data/quality_control_data.xml",
        "security/quality_control_security.xml",
        "security/ir.model.access.csv",
        "data/activity_data.xml",
        "data/email_template.xml",
        "data/reminder_cron.xml",
        "wizard/qc_test_wizard_view.xml",
        "wizard/qc_ask_approval_wiz_view.xml",
        "wizard/rejection_reason.xml",
        "views/qc_menus.xml",
        "views/qc_inspection_view.xml",
        "views/qc_test_category_view.xml",
        "views/qc_test_view.xml",
        "views/qc_inspection_team_view.xml",
        "views/qc_trigger_view.xml",
        "views/product_template_view.xml",
        "views/product_category_view.xml",
        "views/project_view.xml",
        "report/test_report_template.xml"
    ],
    "demo": ["demo/quality_control_demo.xml"],
    "installable": True,
}
