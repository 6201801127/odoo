# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2020-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

{
	'name': "BSSCL Employee Orientation & Training / बिहार सरिफ स्मार्ट सिटी लिमिटेड कर्मचारी अभिविन्यास और प्रशिक्षण",
	'version': '14.0.1.1.0',
	'category': "BSSCL",
	'summary': """Employee Orientation/Training Program / कर्मचारी उन्मुखीकरण/प्रशिक्षण कार्यक्रम""",
	'description':'Complete Employee Orientation/Training Program / पूर्ण कर्मचारी उन्मुखीकरण/प्रशिक्षण कार्यक्रम',
	'author': 'BSSCL / बिहार सरिफ स्मार्ट सिटी लिमिटेड',
	'company': 'BIHAR SARIF SMART CITY LIMITED / बिहार सरिफ स्मार्ट सिटी लिमिटेड',
	'website': 'https://www.cybrosys.com',
	'depends': ['base', 'hr'],
	'data': [
		# 'views/orientation_checklist_line.xml',
		# 'views/employee_orientation.xml',
		# 'views/orientation_checklist.xml',
		# 'views/orientation_checklists_request.xml',
		# 'views/orientation_checklist_sequence.xml',
		# 'views/orientation_request_mail_template.xml',
		'security/training_security.xml',
		'security/ir.model.access.csv',
		'views/print_pack_certificates_template.xml',
		'views/report.xml',
		'views/employee_training.xml',

	],
	'images': ['static/description/banner.png'],
	'license': 'AGPL-3',
	'installable': True,
	'auto_install': False,
	'application': False,
}
