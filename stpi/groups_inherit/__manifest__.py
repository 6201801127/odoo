# -*- coding: utf-8 -*-
###################################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Nilmar Shereef (<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################
{
    'name': 'Create User, Edit Group',
    'version': '12.0.1.0.0',
    'summary': """Create User from Employee.""",
    'description': """Create User from Employee""",
    'category': 'Module for STPI',
    'author': 'Dexciss Technology @RGupta',
    'company': 'Dexciss Technology ',
    'maintainer': 'Dexciss Technology ',
    'website': "https://www.dexciss.com",
    'depends': ['base', 'hr'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/hr_views.xml',
        # 'views/res_users_views.xml',
        'views/employee_b_view.xml',
        'wizard/create_user_wizard.xml',
        'wizard/employee_action_select.xml',
        'views/hr_employee_main.xml',
        'views/res_groups_inherit.xml',
        'views/job_post_master_views.xml',
        'views/group_master_views.xml'
    ],
    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
