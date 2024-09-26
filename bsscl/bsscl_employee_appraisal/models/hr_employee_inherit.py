# *******************************************************************************************************************
#  File Name             :   hr_employee_inherit.py
#  Description           :   This is a model which is used to inherit employee module
#  Created by            :   Ajay Kumar Ravidas
#  Created On            :   10-02-2023
#  Modified by           :
#  Modified On           :
#  Modification History  :
# *******************************************************************************************************************

from odoo import fields, models, api, _
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

class InheritEmployee(models.Model):
    _inherit = 'hr.employee'

    appraisal_reporting_officer = fields.Many2one('hr.employee', string='Appraisal Reporting Officer / मूल्यांकन रिपोर्टिंग अधिकारी')
    appraisal_reviewing_officer = fields.Many2one('hr.employee', string='Appraisal Reviewing Officer / मूल्यांकन समीक्षा अधिकारी')