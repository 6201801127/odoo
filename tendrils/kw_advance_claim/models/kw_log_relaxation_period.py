from odoo import models, fields, api


class kw_log_relaxation_period(models.Model):
    _name = 'kw_advance_log_relaxation_period'
    _description = "Relaxation Period log"

    salary_adv_id = fields.Many2one('kw_advance_apply_salary_advance', string='Salary adv id', ondelete='cascade')
    approve_by = fields.Many2one('hr.employee', string="Approve By")
    approved_on = fields.Date(string="Approved on")
    relaxation_period = fields.Many2one('kw_advance_buffer_period_master', string='Relaxation Period')
    description = fields.Char(string="Description")
