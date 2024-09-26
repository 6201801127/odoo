# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
	'name': 'Recruitment',
	'version': '1.0',
	'category': 'Human Resources/Recruitment',
	'sequence': 90,
	'summary': 'Track your recruitment pipeline',
	'description': "",
	'website': 'https://www.odoo.com/page/recruitment',
	'depends': [
		'hr','mail','hr_recruitment','website'
	],
	'data': [

		'views/hr_department_views_inherited.xml',
		# 'data/emp_rec_type.xml',
	],
	'demo': [

	],
	'qweb': [
		"static/src/xml/template.xml",

	],
	'installable': True,
	'auto_install': False,
	'application': True,
	'license': 'LGPL-3',
}
