{
    "name": "Kwantify RESTFUL API",
    "version": "1.0.1",
    "category": "Kwantify / API",
    "author": "CSM",
    "website": "https://csm.tech",
    "summary": "Kwantify RESTFUL API",
    # "support": "",
    "description": """ RESTFUL API For Odoo
====================
With use of this module user can enable REST API in any Odoo applications/modules

For detailed example of REST API refer https://ajepe.github.io/restful-api-for-odoo
""",
    "depends": ["web"],
    "data": [
        "data/ir_config_param.xml",
        "views/ir_model.xml",
        "views/res_users.xml",
        "security/ir.model.access.csv",
    ],
    "images": ["static/description/main_screenshot.png"],
    "license": "LGPL-3",
    "installable": True,
    "auto_install": False,
    'application': True,
}
