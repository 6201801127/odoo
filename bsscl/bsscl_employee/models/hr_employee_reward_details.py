import re, base64
from odoo import SUPERUSER_ID
from datetime import datetime, date
from odoo import api, fields, models,tools


class HrEmployeeRewards(models.Model):
    _name           = 'hr.employee.rewards_details'
    _inherit        = ['mail.thread','mail.activity.mixin']
    _description    = 'Employee Rewards'

    employee_id = fields.Many2one('hr.employee' , ondelete='cascade')
    order_no = fields.Char(string="Order No / आदेश संख्या")
    order_date = fields.Date(string="Order Date / आर्डर की तारीख")
    effective_from = fields.Date(string="Suspension Revoke with effect from / निलंबन वापस लिया गया")
    revok_desc = fields.Char(string="Order Suspension Revoke Description / आदेश निलंबन रद्द करने का विवरण")
    issuer_id = fields.Many2one('res.branch', string="Order Issuing Authority/Office / आदेश जारी करने वाला प्राधिकरण")
    reward_date = fields.Date(string="Reward Date / इनाम की तारीख")
    reward_type  = fields.Selection(selection=[('monetary', 'Monetary Rewards'),('non-monetary', 'Non-Monetary Rewards')], string='Reward Type / इनाम का प्रकार', tracking=True)
    curr_office = fields.Many2one('res.branch',string="Post and Office where posted at the time of Reward / पोस्ट और कार्यालय जहां इनाम के समय पोस्ट किया गया था ", help="Office were posted at the time of Reward(H.Q.Location)")
    details = fields.Text(string="Reward Details / इनाम विवरण")
    remarks = fields.Char(string="Remarks / टिप्पणियां")
    joining_order_no = fields.Char(string="joining Order No / सेवारंभ आदेश संख्या")
    joining_order_date = fields.Date(string="joining Order Date /  सेवारंभ आदेश की तारीख")
    joining_date = fields.Date(string="Joining Date / सेवारंभ तारीख")
    joining_office = fields.Date(string="Joining office / सेवारंभ कार्यालय")

class EmployeePunishment(models.Model):
    _name = 'employee.punishment'
    _description = 'Punishment'

    employee_id = fields.Many2one('hr.employee','Employee Id')
    given_by = fields.Many2one(comodel_name="hr.employee",string='Given by / दिया गया')
    given_date = fields.Date(string='Given Date / दी गई तारीख')
    approve_date = fields.Date(string='Approve Date / मंज़ूरी तिथि')
    reason = fields.Char(string='Reason / कारण')