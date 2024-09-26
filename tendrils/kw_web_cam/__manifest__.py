# -*- coding: utf-8 -*-
{
    "name": " Tendrils Live WebCam ",
    "version": "12.0.1.3",

    "author": "CSM Technology",
    "website": "http://www.csm.co.in",
    'company': 'CSM Technology',

    "depends": ["web"],
    "license": "LGPL-3",
    "category": "web",

    "summary": """Allows to take image with WebCam[TAGS], web camera, web photo, web images, camera image,
     snapshot web, snapshot webcam, snapshot picture, web contact image,
     web product image, online mobile web image and product image.""",

    "data": [
        "views/assets.xml",
    ],
    "depends": [
        "web",
    ],
    "qweb": [
        "static/src/xml/web_widget_image_webcam.xml",
    ],


    'installable': True,
    'auto_install': False,
    'application': True,
    
    "images": ['static/description/banner.gif'],
    
}
