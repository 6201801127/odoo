from odoo import models,api,fields

class HrJob(models.Model):
    _inherit='hr.job'
    
    pay_level_id = fields.Many2one('hr.payslip.paylevel', string='Pay Level')
    # pay_level = fields.Many2one('payslip.pay.level', string='Pay Cell', track_visibility='onchange')