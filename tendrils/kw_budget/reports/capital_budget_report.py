from odoo import models, api, fields, tools


class CapitalBudgetReport(models.Model):
    _name = "capital_budget_report"
    _description = "Report For capital budget"
    _auto = False

    account_id = fields.Many2one('account.account', 'Account Code')
    account_code = fields.Char(related='account_id.code', string='Account Code')
    account_name = fields.Char(related='account_id.name', string='Account Name')
    group_type_id = fields.Many2one('kw.group.type', string='Group Type')
    group_head_id = fields.Many2one('account.account.type', string='Group Head')
    group_id = fields.Many2one('account.group.name', string='Group Name')
    account_head_id = fields.Many2one('account.head', string='Account Head')
    account_sub_head_id = fields.Many2one('account.sub.head', string='Account Sub Head')
    fiscal_year_id = fields.Many2one('account.fiscalyear', string="Fiscal Year")
    department_id = fields.Many2one('hr.department', string="Department")
    date_from = fields.Date(string="Month Start Date")
    date_to = fields.Date(string="Month End Date")
    total_amount = fields.Float(string="Total Amount")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
             		SELECT 
					row_number() OVER (order by account_code_id desc) AS id,
                    b.fiscal_year_id AS fiscal_year_id,
                    (SELECT department_id FROM kw_budget_dept_mapping WHERE id = b.budget_department) AS department_id, 
                    a.account_code_id as account_id,
                    b.date_from AS date_from,
                    b.date_to AS date_to,
					ac.group_type as group_type_id,
    				ac.group_name as group_id,
    				ac.user_type_id as group_head_id,
    				ac.account_head_id as account_head_id,
                    ac.account_sub_head_id as account_sub_head_id,
                    SUM(a.total_amount) AS total_amount
                FROM 
                    kw_capital_budget b
                LEFT JOIN 
                    kw_capital_budget_line a ON a.capital_budget_id = b.id
				left JOIN account_account ac on ac.id = a.account_code_id
                WHERE 
                    a.account_code_id IS NOT NULL
					
                GROUP BY 
                    b.fiscal_year_id, b.budget_department, a.account_code_id, b.date_from, b.date_to,ac.group_type,
					ac.group_name,ac.user_type_id,ac.account_head_id,ac.account_sub_head_id
                    )""" % (self._table))


    def open_capital_report_view(self):
        record = []
        data = self.env['kw_capital_budget_line'].search([])
        for rec in data:
            if rec.account_code_id == self.account_id and rec.capital_budget_id.fiscal_year_id == self.fiscal_year_id and rec.capital_budget_id.budget_department.department_id == self.department_id:
                record.append(rec.id)
        action = {
            'name': 'Capital Budget Report',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'view_type': 'form',
            'res_model': 'kw_capital_budget_line',
            'domain': [('id', 'in', record)],
            'target': 'self',
            'context': {'no_create_edit': False, 'delete': False}
        }
        return action