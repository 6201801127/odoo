from odoo import api, fields, models, _
from odoo import tools
import datetime
from datetime import date, timedelta
from odoo.exceptions import UserError, ValidationError
from datetime import date, timedelta
import calendar


class KwDepartmetnInherit(models.Model):
    _inherit = 'hr.department'

    total_planned = fields.Integer('Total Planned', compute='get_department_budget')
    total_incurred = fields.Integer('Total [Incurred]', compute='get_department_budget')
    total_remaining = fields.Integer('Total [Remaining]', compute='get_department_budget')

    def get_department_budget(self):
        current_fiscal_year_id = self.env['kw_recruitment_treasury_budget_line'].get_fiscal_year()
        for rec in self:
            treasury_budget_id = self.env['kw_recruitment_budget_lines'].sudo().search(
                [('fiscalyr', '=', current_fiscal_year_id.id), ('dept_id', '=', rec.id)])
            if treasury_budget_id:
                total_planned, total_incurred, total_remaining = self.env[
                    'kw_recruitment_treasury_budget_line'].get_budget_calculations(treasury_budget_id.ids)
                rec.total_planned = total_planned
                rec.total_incurred = total_incurred
                rec.total_remaining = total_remaining
            else:
                rec.total_planned = 0
                rec.total_incurred = 0
                rec.total_remaining = 0

    @api.multi
    def view_department_buget(self):
        if self._context.get('budget_dept_id'):
            tree_view_id = self.env.ref('kw_recruitment_calendar.kw_recruitment_treasury_budget_line_view_tree').id
            last_config_ids = self.env['kw_recruitment_treasury_budget_line'].sudo().search(
                [('department_id', '=', int(self._context.get('budget_dept_id')))], order='id desc')
            treasury_budget_id = False
            action = {
                'name': f'{self.name} Treasury Budget',
                'type': 'ir.actions.act_window',
                'res_model': 'kw_recruitment_treasury_budget_line',
                'view_mode': 'form',
                'views': [(tree_view_id, 'tree')],
                'target': 'self',
                'domain': [('id', 'in', last_config_ids.ids)]
            }

            return action
