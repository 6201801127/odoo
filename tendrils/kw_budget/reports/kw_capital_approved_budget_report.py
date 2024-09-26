from odoo import models, api, fields, tools

class ApprovedCapitalReport(models.Model):
    _name = "kw_capital_approved_budget_report"
    _description = "Report For Approved Capital budget"
    _auto = False

    sequence_ref = fields.Char(string="ID")
    merged_expenses_remark = fields.Char(string='Name of Expenses')
    account_code_id = fields.Many2one('account.account', 'Account Code')
    account_code = fields.Char(related='account_code_id.code', string='Account Code')
    account_name = fields.Char(related='account_code_id.name', string='Account Name')
    fiscal_year_id = fields.Many2one('account.fiscalyear', string="Fiscal Year")
    department_id = fields.Many2one('hr.department', string="Department")
    remark =  fields.Text('Remark')
    date_from = fields.Date('Month Start')
    date_to = fields.Date('Month End')
    budget_department=fields.Many2one('kw_budget_dept_mapping', string="Budget Departement")
    name_of_expenses =  fields.Char(string='Narration')
    april_budget = fields.Float('Apr Budget')
    may_budget = fields.Float('May Budget')
    june_budget = fields.Float('Jun Budget')
    july_budget = fields.Float('Jul Budget')
    august_budget = fields.Float('Aug Budget')
    september_budget = fields.Float('Sep Budget')
    october_budget = fields.Float('Oct Budget')
    november_budget = fields.Float('Nov Budget')
    december_budget = fields.Float('Dec Budget')
    january_budget = fields.Float('Jan Budget')
    february_budget = fields.Float('Feb Budget')
    march_budget = fields.Float('Mar Budget')
    next_fy_budget = fields.Float('Next Fy Budget')
    total_budget = fields.Float('Total Budget Amount') 

    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('report_action_capital_budget'):
            # print('calllled')
            data = self.env['kw_budget_dept_mapping'].sudo().search(['|',('level_2_approver','in',[self.env.user.employee_ids.id]),('level_1_approver','in',[self.env.user.employee_ids.id])])
            # print('data calllled',data)
            if self.env.user.has_group('kw_budget.group_finance_kw_budget') or self.env.user.has_group('kw_budget.group_approver_kw_budget') or self.env.user.has_group('kw_budget.group_manager_kw_budget'):
                args += []
            elif self.env.user.has_group('kw_budget.group_department_head_kw_budget'):
                args += [('budget_department', 'in', data.ids)]
        return super(ApprovedCapitalReport, self)._search(args, offset=offset, limit=limit, order=order, count=count,
                                                            access_rights_uid=access_rights_uid)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
            SELECT 
                row_number() over(order by CASE 
                    WHEN cbl.sequence_ref ~ '^[0-9]+$' THEN cast(cbl.sequence_ref as int)
                    ELSE NULL 
                END) as id,
                dm.department_id as department_id,
                cb.budget_department,
                CONCAT(cbl.name_of_expenses, ' ; ', cbl.remark) as merged_expenses_remark,
                cb.fiscal_year_id as fiscal_year_id,cbl.remark as remark,
                cbl.name_of_expenses as name_of_expenses,
                cbl.date_from as date_from,
                cbl.date_to as date_to,
                COALESCE(NULLIF(TRIM(sequence_ref), ''), 'NA') AS sequence_ref,
                cbl.account_code_id as account_code_id,
                cbl.apr_budget AS april_budget,
                cbl.may_budget AS may_budget,
                cbl.jun_budget AS june_budget,
                cbl.jul_budget AS july_budget,
                cbl.aug_budget AS august_budget,
                cbl.sep_budget AS september_budget,
                cbl.oct_budget AS october_budget,
                cbl.nov_budget AS november_budget,
                cbl.dec_budget AS december_budget,
                cbl.jan_budget AS january_budget,
                cbl.feb_budget AS february_budget,
                cbl.mar_budget AS march_budget,
                cbl.next_fy_year AS next_fy_budget,
               cbl.total_amount AS total_budget
                from kw_budget_dept_mapping dm
                left join kw_capital_budget cb
                on dm.id =cb.budget_department
                left join kw_capital_budget_line cbl on cbl.capital_budget_id =cb.id 
                where cb.state in ('validate')
                ORDER BY
                CASE 
                    WHEN cbl.sequence_ref ~ '^[0-9]+$' THEN cast(cbl.sequence_ref as int)
                    ELSE NULL   
                END
                )""" % (self._table))

