{
    'name': 'Odoo Php Intergation for data synch',
    'version': '1.0',
    'category': 'Extra Tools',
    'sequence': 90,
    'summary': 'Track your data',
    'description': "",
    'website': '',
    'depends': [
        'mail', 'base'
    ],
    'data': [

		'security/ir.model.access.csv',
		'views/floor_view.xml',
		'views/res_partner_view.xml',
		'views/payment_view.xml',
		'views/url_conf.xml',
    ],
    'demo': [
        
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}
