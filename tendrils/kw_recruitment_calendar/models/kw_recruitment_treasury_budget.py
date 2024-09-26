from pickletools import read_uint1
from traceback import print_tb
from odoo import api, fields, models, _
from odoo import tools
import datetime
from datetime import date, timedelta
from odoo.exceptions import UserError, ValidationError
from datetime import date, timedelta
import calendar


class RecruitmenTreasuryBudgetLines(models.Model):
    _name = 'kw_recruitment_treasury_budget_line'
    _description = "Recruitment treasury Budget Lines"
    _rec_name = "name"
    _auto = False

    name = fields.Char('Name', default='Treasury Budget')
    total_planned = fields.Integer('Total Planned')
    total_incurred = fields.Integer('Total [Incurred]')
    total_remaining = fields.Integer('Total [Remaining]')

    department_id = fields.Many2one('hr.department', string="Department")
    fiscalyr = fields.Many2one('account.fiscalyear', string="Fiscal Year")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
            SELECT  row_number() over() AS id,
            a.name,
            a.id AS department_id,
            b.fiscalyr,
            SUM(b.total_budget) AS total_planned,
            SUM(b.total_incurred) AS total_incurred,
            SUM(b.total_remaining) AS total_remaining 
            FROM hr_department a
            join kw_recruitment_budget_lines b on a.id = b.dept_id 
            group by a.name,b.fiscalyr,a.id

         )""" % (self._table))

    def get_fiscal_year(self):
        current_date = date.today()
        current_fiscal_year_id = self.env['account.fiscalyear'].sudo().search(
            [('date_start', '<=', current_date), ('date_stop', '>=', current_date)], limit=1)
        return current_fiscal_year_id

    def get_budget_calculations(self, ids=False):
        if ids:
            query = f''' select SUM(total_budget) as total,
            SUM(total_remaining) as remaining, 
            SUM(total_incurred) as incurred 
            FROM kw_recruitment_budget_lines
                    WHERE id in ({str(ids)[1:-1]}) '''
            self._cr.execute(query)
            # print("query===",query)
            query_result = self._cr.fetchall()
            # print("query_result====",query_result)
            return query_result[0][0], query_result[0][1], query_result[0][2]

    @api.multi
    def action_view_department_budgets(self):
        tree_view_id = self.env.ref('kw_recruitment_calendar.kw_recruitment_budget_lines_tree').id
        current_fiscal_year_id = self.env['kw_recruitment_treasury_budget_line'].get_fiscal_year()
        treasury_budget_id = self.env['kw_recruitment_budget_lines'].sudo().search(
            [('fiscalyr', '=', self.fiscalyr.id), ('dept_id', '=', self.department_id.id)])
        action = {
            'name': f'{self.fiscalyr.name} Year Budget',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_recruitment_budget_lines',
            'view_mode': 'form',
            'views': [(tree_view_id, 'tree')],
            'target': 'self',
            'domain': [('id', 'in', treasury_budget_id.ids)],
            'search_view_ref': 'kw_recruitment_calendar.kw_recruitment_budget_lines_search'
        }
        if self.fiscalyr.id == current_fiscal_year_id.id:
            action['context'] = {'create': False, 'edit': True, 'delete': False, 'search_default_fiscalyr_filter': 1}
        else:
            action['context'] = {'create': False, 'edit': True, 'delete': False}

        return action

    @api.multi
    def redirect_department_budget(self):
        kanban_view_id = self.env.ref('kw_recruitment_calendar.department_budget_kanban').id
        action = {
            'name': 'Treasury Budget',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.department',
            'view_mode': 'kanban',
            'view_id': kanban_view_id,
            'target': 'self',
            'context': {'create': False, 'delete': False, 'edit': False}
        }
        return action
