# -*- coding: utf-8 -*-
{
	'name': 'Employee Profile',
	'version': '12.0.1.0.0',
	'summary': 'Employee Profile',
	'category': 'Tools',
	'author': 'Dexciss Technologies Pvt Ltd(@ RGupta)',
	'maintainer': 'dexciss Techno Solutions',
	'company': 'dexciss Techno Solutions',
	'website': 'https://www.dexciss.com',
	'depends': ['base','hr','base_address_city','category_religion','hr_skills','hr_employee_stpi','stpi_contract_pr'],
	'data': [
		'security/ir.model.access.csv',
		# 'security/security.xml',
        'views/employee_profile.xml',
        'views/profile_report.xml',
	],
	'images': [],
	'license': 'AGPL-3',
	'installable': True,
	'application': False,
	'auto_install': False,
}