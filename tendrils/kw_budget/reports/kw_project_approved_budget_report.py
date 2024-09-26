from odoo import models, api, fields, tools

class ApprovedSBUProjectReport(models.Model):
    _name = "kw_project_approved_budget_report"
    _description = "Report Approved SBU budget"
    _auto = False

    sequence_ref = fields.Char( string='ID')
    account_code_id = fields.Many2one('account.account', 'Account Code')
    account_code = fields.Char(related='account_code_id.code', string='Account Code')
    account_name = fields.Char(related='account_code_id.name', string='Account Name')
    fiscal_year_id = fields.Many2one('account.fiscalyear', string="Fiscal Year")
    sbu_id = fields.Many2one('kw_sbu_master', string="SBU Name")
    department_id = fields.Many2one('hr.department', string="Department" )
    division_id = fields.Many2one('hr.department', string="Division")
    section_id = fields.Many2one('hr.department', string="Section")
    budget_department=fields.Many2one('kw_sbu_project_mapping', string="SBU ID")
    sbu_name = fields.Char(string="SBU Name")
    project_id = fields.Many2one('project.project', string="Project Name")
    project_name_id = fields.Many2one('kw_project_budget_master_data', string="Project Name")
    expenses_type = fields.Char(string='Income/Exp.')
    project_name_code = fields.Char(string="Project Code")
    head_of_expense =  fields.Char(string='Head Of Expenses/Income')
    work_order_type =  fields.Char(string='Workorder Type')
    opp_name =  fields.Char(string='OPP Name')
    project_code =  fields.Char(string='Project Code')
    client =  fields.Char(string='Client')
    order_value =  fields.Char(string='Order value')
    category_id =  fields.Many2one('kw_sbu_project_category_master', string='Category Name')
    
    group_type_id = fields.Many2one(related='account_code_id.group_type',string='Group Type')
    group_head_id = fields.Many2one(related='account_code_id.user_type_id', string='Group Head')
    group_id = fields.Many2one(related='account_code_id.group_name',string= 'Group Name')
    account_head_id = fields.Many2one(related='account_code_id.account_head_id',string= 'Account Head')
    account_sub_head_id = fields.Many2one(related='account_code_id.account_sub_head_id', string='Account Sub Head')
    
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
        if self._context.get('report_action_project_budget'):
            data = self.env['kw_sbu_project_mapping'].sudo().search(['|',('level_2_approver','in',[self.env.user.employee_ids.id]),('level_1_approver','in',[self.env.user.employee_ids.id])])
            # print(data, '============>>>')
            if self.env.user.has_group('kw_budget.group_finance_kw_budget') or self.env.user.has_group('kw_budget.group_approver_kw_budget') or self.env.user.has_group('kw_budget.group_manager_kw_budget'):
                args += []
            elif self.env.user.has_group('kw_budget.group_department_head_kw_budget'):
                args += [('budget_department', 'in', data.ids)]
        return super(ApprovedSBUProjectReport, self)._search(args, offset=offset, limit=limit, order=order, count=count,
                                                        access_rights_uid=access_rights_uid)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
                SELECT 
                    ROW_NUMBER() OVER (
                        ORDER BY 
                            REGEXP_REPLACE(pbl.sequence_ref, '\d', '', 'g') ASC,
                            COALESCE(NULLIF(REGEXP_REPLACE(pbl.sequence_ref, '\D', '', 'g'), ''), '0')::INT ASC 
                    ) AS id,pm.sbu_id as sbu_id,
                (SELECT name FROM kw_sbu_master WHERE id = pm.sbu_id) AS sbu_name,             
                pb.fiscal_year_id as fiscal_year_id,
                pb.budget_department as budget_department,
                (select id from hr_department where id =(SELECT department_id FROM hr_employee WHERE id =(select sbu.representative_id from kw_sbu_master sbu left join kw_sbu_project_mapping kb on
																	 kb.id=  pb.budget_department  where  sbu.id=kb.sbu_id)))as department_id,
				(select id from hr_department where id =(SELECT division FROM hr_employee WHERE id =(select sbu.representative_id from kw_sbu_master sbu left join kw_sbu_project_mapping kb on
																	 kb.id=  pb.budget_department  where  sbu.id=kb.sbu_id)))as division_id,
				(select id from hr_department where id =(SELECT section FROM hr_employee WHERE id =(select sbu.representative_id from kw_sbu_master sbu left join kw_sbu_project_mapping kb on
																	 kb.id=  pb.budget_department  where  sbu.id=kb.sbu_id)))as section_id,
                pbl.head_expense_type as expenses_type,
                pbl.head_of_expense as head_of_expense,
                pbl.work_order_type as work_order_type,
                pbl.opportunity_name as opp_name,
                COALESCE(NULLIF(TRIM(pbl.sequence_ref), ''), 'NA') AS sequence_ref,
                pbl.order_code as project_code,
                pbl.client as client,
                pbl.order_id as project_id,
                pbl.project_id as project_name_id,
                pbl.project_code as project_name_code,
                REPLACE(pbl.order_value, ',', '') AS order_value,
                pbl.category_id as category_id,
                pbl.account_code_id as account_code_id,
                pbl.apr_budget AS april_budget,
                pbl.may_budget AS may_budget,
                pbl.jun_budget AS june_budget,
                pbl.jul_budget AS july_budget,
                pbl.aug_budget AS august_budget,
                pbl.sep_budget AS september_budget,
                pbl.oct_budget AS october_budget,
                pbl.nov_budget AS november_budget,
                pbl.dec_budget AS december_budget,
                pbl.jan_budget AS january_budget,
                pbl.feb_budget AS february_budget,
                pbl.mar_budget AS march_budget,
                (pbl.apr_budget + pbl.may_budget + pbl.jun_budget + pbl.jul_budget + pbl.aug_budget + pbl.sep_budget + pbl.oct_budget + pbl.nov_budget + pbl.dec_budget + pbl.jan_budget + pbl.feb_budget + pbl.mar_budget) AS total_budget
                from kw_sbu_project_mapping pm
                left join kw_sbu_project_budget pb
                on pm.id =pb.budget_department
                left join kw_sbu_project_budget_line pbl on pbl.sbu_project_budget_id =pb.id
                where pb.state in ('validate')
                ORDER BY
                    REGEXP_REPLACE(pbl.sequence_ref, '\d', '', 'g') ASC,
                    COALESCE(NULLIF(REGEXP_REPLACE(pbl.sequence_ref, '\D', '', 'g'), ''), '0')::INT ASC
                )""" % (self._table))



