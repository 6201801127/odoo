{
    'name': "Report docx",

    'summary': "Kwantify Module to create docx report",
    'author': 'CSM Technologies',
    'website': "https://csm.tech",
    'category': 'Reporting',
    'version': '0.1',
    'license': 'AGPL-3',
    'external_dependencies': {
        'python': [
            'docx',
        ],
    },
    'depends': [
        'base', 'web',
    ],
    'data': [
        'views/webclient_templates.xml',
    ],
    'demo': [
        # 'demo/report.xml',
    ],
    'installable': True,
}
