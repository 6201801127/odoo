# -*- coding: utf-8 -*-
{
	'name': 'Appraisal - STPI',
	'version': '12.0.1.0.0',
	'summary': 'Appraisal Stpi',
	'category': 'Tools',
	'author': 'Dexciss Technologies Pvt Ltd(@ RGupta)',
	'maintainer': 'dexciss Techno Solutions',
	'company': 'Dexciss Techno Solutions',
	'website': 'https://www.dexciss.com',
	'depends': ['base','hr','hr_payroll','date_range','stpi_contract_pr','hr_employee_stpi','groups_inherit'],
	'data': [
		'security/ir.model.access.csv',
		'security/security.xml',
        'views/hr_employee.xml',
        'views/appraisal_forms.xml',
        'views/appraisal_template.xml',
        'views/overall_rate.xml',
        'views/template_mto_payroll.xml',
		'views/print_template.xml',
		'views/annex_template.xml',
		'wizard/create_appraisal.xml'
	],
	'images': [],
	'license': 'AGPL-3',
	'installable': True,
	'application': False,
	'auto_install': False,
}