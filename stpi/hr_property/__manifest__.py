# -*- coding: utf-8 -*-
{
	'name': 'HR - Property - STPI',
	'version': '12.0.1.0.0',
	'summary': 'HR - Property - STPI',
	'category': 'Tools',
	'author': 'Dexciss Technologies Pvt Ltd(@ RGupta)',
	'maintainer': 'dexciss Techno Solutions',
	'company': 'dexciss Techno Solutions',
	'website': 'https://www.dexciss.com',
	'depends': ['base','hr'],
	'data': [
		'security/ir.model.access.csv',
		'security/security.xml',
        'views/hr_property.xml',
	],
	'images': [],
	'license': 'AGPL-3',
	'installable': True,
	'application': False,
	'auto_install': False,
}