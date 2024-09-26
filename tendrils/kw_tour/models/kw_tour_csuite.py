from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.fields import Datetime


class KWTourCSuite(models.Model):
    _name = 'kw_tour_c_suite'
    _description = "Tour C-Suite"

    company_id = fields.Many2one('res.company', string="Company", required=True)
    department_id = fields.Many2one('hr.department', string="Department", required=True)
    employee_ids =  fields.Many2many('hr.employee', string="CSuite", required=True)
    active = fields.Boolean(string="Active", default=True)

    @api.model
    def _update_group_users(self):
        dataa = []
        records = self.env['kw_tour_c_suite'].search([])
        for rec in records:
            dataa.extend(rec.employee_ids.mapped('user_id').ids)
        group_department_head_kw_budget = self.env.ref('kw_tour.group_kw_tour_c_suite_user').sudo()
        group_department_head_kw_budget.write({'users': [(6, 0, dataa)]})

    @api.model
    def create(self, vals):
        record = super(KWTourCSuite, self).create(vals)
        self._update_group_users()
        return record

    @api.multi
    def write(self, vals):
        res = super(KWTourCSuite, self).write(vals)
        self._update_group_users()
        return res

    @api.multi
    def unlink(self):
        res = super(KWTourCSuite, self).unlink()
        self._update_group_users()
        return res


