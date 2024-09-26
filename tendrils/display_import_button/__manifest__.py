# -*- coding: utf-8 -*-
{
	'name': "Remove Import Button",
	'sequence': 0,
	'summary': """Use To Display or Not Import Button on Your Tree and Kanban Views""",
	'description': """
		This module is used to manage the display of the "import" button on your
		list, form, kanban view, according to your needs.
	""",
	'author': "",
	"website": "",
	'category': 'Kwantify/Tools',
	'version': '1.0',
	'license': 'AGPL-3',
	'depends': ['web'],
	'data': [
		'views/import_template.xml',
	],
	'qweb': ['static/src/xml/template.xml'],
	'installable': True,
	'auto_install': False,
}
