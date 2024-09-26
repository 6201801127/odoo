# -*- coding: utf-8 -*-
{
	'name': 'Multiple Approveal',
	'version': '12.0.1.0.0',
	'summary': 'Reimbursement Stpi',
	'category': 'Tools',
	'author': 'Dexciss Technologies Pvt Ltd(@ RGupta)',
	'maintainer': 'dexciss Techno Solutions',
	'company': 'dexciss Techno Solutions',
	'website': 'https://www.dexciss.com',
	'depends': ['base','tds','tour_request','reimbursement_stpi'],
	'data': [

		'wizard/reimbursement.xml',
		'wizard/tds.xml',
		'wizard/tour_request.xml',
		'wizard/tour_claim.xml',
		'wizard/vehicle_request.xml',
	],
	'images': [],
	'license': 'AGPL-3',
	'installable': True,
	'application': False,
	'auto_install': False,
}