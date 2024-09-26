{
    "name": "Execute Query",
    "version": "1.0.1",
    "author": "Kwantify",
    "website": "https://www.csm.tech",
    "category": "Kwantify / Extra Tools",
    "license": "LGPL-3",
    "support": "kwantify@csm.tech",
    "summary": "Execute query from database",
    "description": """
        Execute query without open postgres
Goto : Settings > Technical
    """,
    "depends": [
        "base",
        "mail",
    ],
    "data": [
        "views/ms_query_view.xml",
        "security/ir.model.access.csv",
        "wizards/ms_query_export_wizard.xml",
    ],
    "demo": [],
    "test": [],
    "images": [
        "static/description/images/main_screenshot.png",
        "static/description/images/main_1.png",
        "static/description/images/main_2.png",
        "static/description/images/main_3.png",
    ],
    "qweb": [],
    "css": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
