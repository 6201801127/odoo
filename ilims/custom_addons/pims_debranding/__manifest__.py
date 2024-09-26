{
    'name': "PIMS Debranding",
    'description': "PIMS Debranding",
    'depends': [
        'base_setup',
        'web',
        'website',
    ],
    'data': [
        'views/views.xml',
    ],
    'qweb' : ['static/src/xml/setting.xml'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
