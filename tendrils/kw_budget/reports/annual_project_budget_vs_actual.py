from odoo import models, api, fields, tools

class AnnualProjectBudgetvsActual(models.Model):
    _name = "annual_project_budget_vs_actual"
    _description = "Annual Budget For four year of expense Project budget"
    _auto = False
    _order = "account_code asc"

    account_id = fields.Many2one('account.account', 'Account Code')
    account_code = fields.Char(string='Account Code')
    budget_department=fields.Many2one('kw_sbu_project_mapping', string="Budget Departement")
    account_name = fields.Char(related='account_id.name', string='Account Name')
    group_type_id = fields.Many2one('kw.group.type',string='Group Type')
    group_head_id = fields.Many2one('account.account.type', string='Group Head')
    group_id = fields.Many2one('account.group.name',string= 'Group Name')
    account_head_id = fields.Many2one('account.head',string= 'Account Head')
    account_sub_head_id = fields.Many2one('account.sub.head', string='Account Sub Head')
    fiscal_year_id = fields.Many2one('account.fiscalyear', string="Fiscal Year")
    project_id = fields.Many2one('project.project', string="Project")
    project_name = fields.Char(string='Project Name')
    project_code = fields.Char(string='Project Code')
    sbu_name = fields.Char(string="SBU Name")
    department_id = fields.Many2one('hr.department', string="Department" )
    division_id = fields.Many2one('hr.department', string="Division")
    section_id = fields.Many2one('hr.department', string="Section")
    year_1_budget = fields.Float('Budget 22-23')
    year_1_total_balance = fields.Float(string='Actual 22-23')
    year_2_budget = fields.Float(string='Budget 23-24')
    year_2_total_balance = fields.Float(string='Actual 23-24',compute="_compute_practical_amount_23_24")
    year_3_budget = fields.Float(string='Budget 24-25')
    year_3_total_balance = fields.Float(string='Actual 24-25',compute="_compute_practical_amount_24_25")
   
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('report_action_annual_project_approved_budget'):
            data = self.env['kw_sbu_project_mapping'].sudo().search([('level_2_approver','in',[self.env.user.employee_ids.id])])
            # print(data, '============>>>')
            if self.env.user.has_group('kw_budget.group_finance_kw_budget') or self.env.user.has_group('kw_budget.group_approver_kw_budget') or self.env.user.has_group('kw_budget.group_manager_kw_budget'):
                args += []
            elif self.env.user.has_group('kw_budget.group_department_head_kw_budget'):
                args += [('budget_department', 'in', data.ids)]
        return super(AnnualProjectBudgetvsActual, self)._search(args, offset=offset, limit=limit, order=order, count=count,
                                                                access_rights_uid=access_rights_uid)
   
    @api.multi
    def _compute_practical_amount_24_25(self):
        for line in self:
            date_to = line.fiscal_year_id.date_stop
            date_from = line.fiscal_year_id.date_start
            aml_obj = self.env['account.move.line']
            domain = [('account_id', '=',line.account_id.id),
                       ('fiscalyear_id','=',5),
                        ('move_id.state', '=', 'posted'),
                      ]
            if not line.project_id:
                domain.extend([('project_wo_id', '=', False)])
            else:
                if line.project_id:
                    domain.append(('project_wo_id','=',line.project_id.id))
            where_query = aml_obj._where_calc(domain)
            aml_obj._apply_ir_rules(where_query, 'read')
            from_clause, where_clause, where_clause_params = where_query.get_sql()
            if line.account_id.group_type.code == '3':
                select = "SELECT sum(account_move_line.credit)-sum(account_move_line.debit) from" + from_clause + "left join account_move am on am.id = account_move_line.move_id and am.state = 'posted'"+"where" + where_clause
            else:
                select = "SELECT sum(account_move_line.debit)-sum(account_move_line.credit) from" + from_clause + "left join account_move am on am.id = account_move_line.move_id and am.state = 'posted'"+" where " + where_clause
            self.env.cr.execute(select, where_clause_params)
            line.year_3_total_balance = self.env.cr.fetchone()[0] or 0.0
           
    @api.multi
    def _compute_practical_amount_23_24(self):
        for line in self:
            date_to = line.fiscal_year_id.date_stop
            date_from = line.fiscal_year_id.date_start
            aml_obj = self.env['account.move.line']
            domain = [('account_id', '=',line.account_id.id),
                       ('fiscalyear_id','=',4),
                        ('move_id.state', '=', 'posted'),
                      ]
            if not line.project_id:
                domain.extend([('project_wo_id', '=', False)])
            else:
                if line.project_id:
                    domain.append(('project_wo_id','=',line.project_id.id))
            where_query = aml_obj._where_calc(domain)
            aml_obj._apply_ir_rules(where_query, 'read')
            from_clause, where_clause, where_clause_params = where_query.get_sql()
            if line.account_id.group_type.code == '3':
                select = "SELECT sum(account_move_line.credit)-sum(account_move_line.debit) from" + from_clause + "left join account_move am on am.id = account_move_line.move_id and am.state = 'posted'"+"where" + where_clause
            else:
                select = "SELECT sum(account_move_line.debit)-sum(account_move_line.credit) from" + from_clause + "left join account_move am on am.id = account_move_line.move_id and am.state = 'posted'"+" where " + where_clause
            self.env.cr.execute(select, where_clause_params)
            line.year_2_total_balance = self.env.cr.fetchone()[0] or 0.0
   
  
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
        
 with final as (With final_cte as (WITH a AS (
    SELECT 
        af.id AS fiscal_year_id,
        aa.id AS account_id
    FROM 
        account_account aa
    CROSS JOIN 
        account_fiscalyear af 
),
b as (
	 SELECT 
        aml.account_id,
        aml.fiscalyear_id as fiscal_year_id,
		aml.project_wo_id as project_id,
       aml.balance AS total_balance
    FROM 
        account_move_line aml
    JOIN 
        account_move am ON am.id = aml.move_id
    WHERE 
        am.state = 'posted' 
)

select 
a.fiscal_year_id as fiscal_year_id,
        a.account_id as account_id,
        null::int as budget_department,					   
		b.project_id,
        (select wo_name from kw_project_budget_master_data where id = b.project_id) as project_name,					  
		(select wo_code from kw_project_budget_master_data where id = b.project_id) as project_code,
        (SELECT name FROM kw_sbu_master WHERE id =(SELECT pb.sbu_id from kw_project_budget_master_data pb where
															pb.id = b.project_id)) AS sbu_name,
        (select id from hr_department where id =(SELECT department_id FROM hr_employee WHERE id =(select sbu.representative_id from kw_sbu_master sbu left join kw_project_budget_master_data pb
																	  on pb.id=b.project_id where sbu.id=pb.sbu_id)))as department_id,
		(select id from hr_department where id =(SELECT division FROM hr_employee WHERE id =(select sbu.representative_id from kw_sbu_master sbu left join kw_project_budget_master_data pb
																	  on pb.id=b.project_id where sbu.id=pb.sbu_id))) as division_id,		   
		(select id from hr_department where id =(SELECT section FROM hr_employee WHERE id =(select sbu.representative_id from kw_sbu_master sbu left join kw_project_budget_master_data pb
																	  on pb.id=b.project_id where sbu.id=pb.sbu_id))) as section_id,                                                  
		0 as total_budget,
		b.total_balance 
		from a left join b on a.account_id = b.account_id and a.fiscal_year_id = b.fiscal_year_id
		where b.total_balance IS NOT NULL
								   
 union all
 		 		SELECT 
				ks.fiscal_year_id AS fiscal_year_id,
                kl.account_code_id AS account_id,
                ks.budget_department as budget_department,
                kl.project_id as project_id,
                (select wo_name from kw_project_budget_master_data where id = kl.project_id) as project_name,
				STRING_AGG(DISTINCT kl.project_code, ', ') AS project_code,
                (SELECT name FROM kw_sbu_master WHERE id = (SELECT sbu_id FROM kw_sbu_project_mapping WHERE id = ks.budget_department)) AS sbu_name,
                (select id from hr_department where id =(SELECT department_id FROM hr_employee WHERE id =(select sbu.representative_id from kw_sbu_master sbu left join kw_sbu_project_mapping pb on
																	 pb.id=  ks.budget_department  where  sbu.id=pb.sbu_id)))as department_id,
				(select id from hr_department where id =(SELECT division FROM hr_employee WHERE id =(select sbu.representative_id from kw_sbu_master sbu left join kw_sbu_project_mapping pb on
																	 pb.id=  ks.budget_department  where  sbu.id=pb.sbu_id)))as division_id,
				(select id from hr_department where id =(SELECT section FROM hr_employee WHERE id =(select sbu.representative_id from kw_sbu_master sbu left join kw_sbu_project_mapping pb on
																	 pb.id=  ks.budget_department  where  sbu.id=pb.sbu_id)))as section_id,
                SUM(kl.apr_budget + kl.may_budget + kl.jun_budget + kl.jul_budget + kl.aug_budget + kl.sep_budget + kl.oct_budget + kl.nov_budget + kl.dec_budget + kl.jan_budget + kl.feb_budget + kl.mar_budget) AS total_budget,
				0 as total_balance
                from
            kw_sbu_project_budget_line kl
            left JOIN
                kw_sbu_project_budget ks ON kl.sbu_project_budget_id = ks.id
                where ks.state ='validate' and kl.state= 'validate'
            GROUP BY
                kl.account_code_id,
                ks.fiscal_year_id,
                kl.project_id,
                ks.budget_department              			
	)
	SELECT 
	fiscal_year_id,
	account_id,
    max(budget_department)as budget_department,
	project_id,
    project_name,
	MAX(project_code) AS project_code,
    max(sbu_name) as sbu_name,
    max(department_id) as department_id,
	max(division_id) as division_id,
	max(section_id) as section_id,
	sum(total_budget) as total_budget,
	sum(total_balance) as balance
	FROM  final_cte
	group by 
	final_cte.fiscal_year_id,
	final_cte.account_id,
	final_cte.project_id,
    final_cte.project_name
	)
select ROW_NUMBER() OVER(order by account_id desc) AS id,account_id,max(budget_department)as budget_department,project_id,
     MAX(project_name) AS project_name,
    COALESCE(MAX(sbu_name), 'NA') AS sbu_name,
    max(department_id) as department_id,
	max(division_id) as division_id,
	max(section_id) as section_id,
	  MAX(fiscal_year_id) AS fiscal_year_id,
	  MAX(project_code) AS project_code,
	(select group_type from account_account where id = final.account_id) as group_type_id,
        (select group_name from account_account where id = final.account_id) as group_id,
        (select user_type_id from account_account where id = final.account_id) as group_head_id,
       	(select account_head_id from account_account where id = final.account_id) as account_head_id,
        (select account_sub_head_id from account_account where id = final.account_id) as account_sub_head_id,
        (select code from account_account where id = final.account_id) as account_code,
		max(case when fiscal_year_id = 3 then total_budget  end) as year_1_budget,
		max(case when fiscal_year_id = 3 then balance  end) as year_1_total_balance,
		max(case when fiscal_year_id = 4 then total_budget  end) as year_2_budget,
		max(case when fiscal_year_id = 4 then balance  end) as year_2_total_balance,
		max(case when fiscal_year_id = 5 then total_budget end) as year_3_budget,
		max(case when fiscal_year_id = 5 then balance  end) as year_3_total_balance
		from final
		where fiscal_year_id !=6
		group by account_id,project_id
	
            )""" % (self._table))

