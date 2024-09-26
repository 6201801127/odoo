# -*- coding: utf-8 -*-
###################################################################################
# Application By CSM Technologies
###################################################################################

{
    "name": "Web Responsive",
    "summary": "BSAP Responsive web client, community-supported",
    "version": "14.0.1",
    "category": "BSAP",
    "website": "https://www.csm.tech/in/",
    "author": "CSM Technologies",
    "license": "LGPL-3",
    "installable": True,
    "depends": ["web", "mail"],
    "development_status": "Production/Stable",
    "maintainers": "CSM Technologies",
    "data": ["views/assets.xml", "views/res_users.xml", "views/web.xml"],
    "qweb": [
        "static/src/xml/apps.xml",
        "static/src/xml/form_buttons.xml",
        "static/src/xml/menu.xml",
        "static/src/xml/navbar.xml",
        "static/src/xml/attachment_viewer.xml",
        "static/src/xml/discuss.xml",
        "static/src/xml/control_panel.xml",
        "static/src/xml/search_panel.xml",
    ],
    "sequence": 1,
}
