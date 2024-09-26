{
    "name"          : "Execute Query",
    "version"       : "1.0",
    "author"        : "Deepak Yadav",
    "website"       : "kulsys.com",
    "category"      : "Extra Tools",
    "license"       : "LGPL-3",
    "support"       : "info@kulsys.com",
    "summary"       : "Execute query from database",
    "description"   : """
        Execute query without open postgres
Goto : Settings > Technical
    """,
    "depends"       : [
        "base",
        "mail",
    ],
    "data"          : [
        "views/ms_query_view.xml",
        "security/ir.model.access.csv",
    ],
    "demo"          : [],
    "test"          : [],
    "images"        : [
        "static/description/images/main_screenshot.png",
    ],
    "qweb"          : [],
    "css"           : [],
    "application"   : True,
    "installable"   : True,
    "auto_install"  : False,
}