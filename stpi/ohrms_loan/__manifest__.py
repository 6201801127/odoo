# -*- coding: utf-8 -*-
###################################################################################
#    A part of OpenHRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Anusha P P (<https://www.cybrosys.com>)
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
    'name': 'Open HRMS Loan Management',
    'version': '12.0.1.0.7',
    'summary': 'Manage Loan Requests',
    'description': """
         'updated by Rgupta 10/10/2019' -> Added one field 'approval_d' in hr.loan.line, py and xml both
         'updated by Maithili 01/10/2019'
        'updated by Maithili 30/Aug/2019'
        
        'Manage Loan request and loan type for the employees
         last updated by Maithili 28/08/2019'
         
        Helps you to manage Loan Requests of your company's staff.
        last updated by sangita 07/03/2019
        last updated by sangita 29/04/2019 read only loan lines
        Last updated by sangita 20/05/2019 balance amount get zero every time issue
        """,
    'category': 'Generic Modules/Human Resources',
    'author': "Cybrosys Techno Solutions",
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.openhrms.com",
    'depends': [
        'base', 'hr_payroll', 'hr','stpi_contract_pr','groups_inherit','category_religion'
    ],
    'data': [
        'security/security.xml',
        'data/foreclosure_amt_cron.xml',
        # 'security/pf_withdrawal_security.xml',
        'security/ir.model.access.csv',
        'views/hr_loan_seq.xml',
        'data/salary_rule_loan.xml',
        'report/report.xml',
        'wizard/reason_wizard.xml',
        'wizard/multi_approve.xml',
        'views/hr_loan.xml',
        # 'views/hr_payroll.xml',
        'views/loan_view.xml',
        'views/maximum_allowed.xml',
        'views/payment_advice.xml',
        'views/payment_advice_report.xml',

    ],
    'demo': [],
    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
