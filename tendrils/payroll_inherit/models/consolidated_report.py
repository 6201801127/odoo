from odoo import fields, models, api, tools
from odoo.exceptions import ValidationError
import datetime,calendar
from datetime import date, datetime, time

class ConsolidateSalaryFilter(models.TransientModel):
    _name = 'monthly_salary_report_filter'
    _description = 'Consolidate Salary Filter'

    MONTH_LIST = [
        ('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'),
        ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'),
        ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')
    ]

    @api.model
    def _get_year_list(self):
        current_year = date.today().year
        return [(str(i), i) for i in range(current_year, 1998, -1)]

    year = fields.Selection(string='Year', selection='_get_year_list', default=str(date.today().year))
    month = fields.Selection(MONTH_LIST, string='Month', default=str(date.today().month))
    
    def action_submit(self):
        self.env['consolidate_report'].with_context(date_to = date(int(self.year),int(self.month),calendar.monthrange(int(self.year), int(self.month))[1])).init()
        view_id = self.env.ref('payroll_inherit.consolidate_report_view_tree').id
        action = {
            'name':f'Consolidated Report for {calendar.month_name[int(self.month)]}-{self.year}',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(view_id, 'tree')],
            'res_model': 'consolidate_report',
            # 'view_id': view_id,
            'target': 'current',
            # 'domain':[('state','=','done')]
        }
        return action
    def action_submit_hr(self):
        self.env['consolidate_report'].with_context(date_to = date(int(self.year),int(self.month),calendar.monthrange(int(self.year), int(self.month))[1])).init()
        view_id = self.env.ref('payroll_inherit.consolidate_report_view_tree').id
        action = {
            'name':f'Consolidated Report for {calendar.month_name[int(self.month)]}-{self.year}',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(view_id, 'tree')],
            'res_model': 'consolidate_report',
            # 'view_id': view_id,
            'target': 'current',
            'domain':[('state','in',['done'])]
        }
        return action

class ConsolidateReport(models.Model):
    _name = 'consolidate_report'
    _description = 'Consolidate Report'
    _auto = False
    
    name = fields.Char()
    amount = fields.Float()
    date_to = fields.Date()
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done'),('verify', 'Verify'),('cancel', 'Cancel')], string='State')
    
    @api.model_cr
    def init(self):
        dates = self.env.context.get('date_to')  if self.env.context.get('date_to') else date.today()
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
           SELECT
            ROW_NUMBER() OVER (order by l.sequence) AS id,
            l.name,sum(l.amount) as amount ,h.date_to,h.state from hr_payslip_line l
            join hr_payslip h on h.id = l.slip_id
            join res_company c on h.company_id = c.id
            where h.date_to = '{dates}' and
            c.parent_id is not null
            group by h.date_to,l.name,h.state,l.sequence
            order by l.sequence
        )"""
        self.env.cr.execute(query)
    