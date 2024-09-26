from odoo import models, api, fields, tools

class TreasuryApprovedBudgetReport(models.Model):
    _name = "kw_treasury_approved_budget_report"
    _description = "Report For Approved Treasury budget"
    _auto = False
    # _order = "sequence_ref desc"

    account_code_id = fields.Many2one('account.account', 'Account Code')

    group_type_id = fields.Many2one(related='account_code_id.group_type',string='Group Type')
    group_head_id = fields.Many2one(related='account_code_id.user_type_id', string='Group Head')
    group_id = fields.Many2one(related='account_code_id.group_name',string= 'Group Name')
    account_head_id = fields.Many2one(related='account_code_id.account_head_id',string= 'Account Head')
    account_sub_head_id = fields.Many2one(related='account_code_id.account_sub_head_id', string='Account Sub Head')
    account_code = fields.Char( string='Account Code')
    sequence_ref = fields.Char( string='ID')
    account_name = fields.Char(related='account_code_id.name', string='Account Name')
    fiscal_year_id = fields.Many2one('account.fiscalyear', string="Fiscal Year")
    department_id = fields.Many2one('hr.department', string="Department")
    division_id = fields.Many2one('hr.department', string="Division")
    section_id = fields.Many2one('hr.department', string="Section")
    budget_department=fields.Many2one('kw_budget_dept_mapping', string="Budget Department")
    # state = fields.Char(string='Pending At')
    remark =  fields.Text('Remark')
    expense_type = fields.Char(string='Income/Exp.')
    name_of_expenses = fields.Char(string='Name of Expenses')
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
    total_budget = fields.Float('Total Budget Amount')

    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('report_action_treasury_approved_budget'):
            data = self.env['kw_budget_dept_mapping'].sudo().search(['|',('level_2_approver','in',[self.env.user.employee_ids.id]),('level_1_approver','in',[self.env.user.employee_ids.id])])
            # print(data, '============>>>')
            if self.env.user.has_group('kw_budget.group_finance_kw_budget') or self.env.user.has_group('kw_budget.group_approver_kw_budget') or self.env.user.has_group('kw_budget.group_manager_kw_budget'):
                args += []
            elif self.env.user.has_group('kw_budget.group_department_head_kw_budget'):
                args += [('budget_department', 'in', data.ids)]
        return super(TreasuryApprovedBudgetReport, self)._search(args, offset=offset, limit=limit, order=order, count=count,
                                                                access_rights_uid=access_rights_uid)


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
            select row_number() over(order by CASE 
            WHEN rbl.sequence_ref ~ '^[0-9]+$' THEN cast(rbl.sequence_ref as int)
            ELSE NULL 
        END) as id,dm.department_id as department_id,dm.division_id as division_id,
                dm.section_id as section_id,rb.fiscal_year_id as fiscal_year_id,rbl.expense_type as expense_type,rbl.remark as remark,
                (SELECT code FROM account_account WHERE id = rbl.account_code_id) AS account_code,   
                rbl.name_of_expenses as name_of_expenses,
                rbl.account_code_id as account_code_id,
                COALESCE(NULLIF(TRIM(rbl.sequence_ref), ''), 'NA') AS sequence_ref,
                rb.budget_department as budget_department,
                rbl.apr_budget AS april_budget,
                rbl.may_budget AS may_budget,
                rbl.jun_budget AS june_budget,
                rbl.jul_budget AS july_budget,
                rbl.aug_budget AS august_budget,
                rbl.sep_budget AS september_budget,
                rbl.oct_budget AS october_budget,
                rbl.nov_budget AS november_budget,
                rbl.dec_budget AS december_budget,
                rbl.jan_budget AS january_budget,
                rbl.feb_budget AS february_budget,
                rbl.mar_budget AS march_budget,
                (rbl.apr_budget + rbl.may_budget + rbl.jun_budget + rbl.jul_budget + rbl.aug_budget + rbl.sep_budget + rbl.oct_budget + rbl.nov_budget + rbl.dec_budget + rbl.jan_budget + rbl.feb_budget + rbl.mar_budget) AS total_budget
                from kw_budget_dept_mapping dm
                left join kw_revenue_budget rb
                on dm.id =rb.budget_department
                left join kw_revenue_budget_line rbl on rbl.revenue_budget_id =rb.id
                where rbl.revenue_budget_id is not null and rb.state in ('validate') and rbl.state in ('validate') 
				and  rbl.account_code_id is not null
                ORDER BY
                CASE 
                    WHEN rbl.sequence_ref ~ '^[0-9]+$' THEN cast(rbl.sequence_ref as int)
                    ELSE NULL 
                END

               
                )""" % (self._table))



