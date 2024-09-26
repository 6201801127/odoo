from odoo import models, api, fields, tools

class AnnualRevenueDraftBudgetvsActual(models.Model):
    _name = "annual_revenue_draft_budget_vs_actual"
    _description = "Annual Budget For four year of expense Revenue budget"
    _auto = False
    _order = "account_code asc"

    account_id = fields.Many2one('account.account', 'Account Code')
    account_code = fields.Char(string='Account Code')
    account_name = fields.Char(related='account_id.name', string='Account Name')
    group_type_id = fields.Many2one('kw.group.type',string='Group Type')
    group_head_id = fields.Many2one('account.account.type', string='Group Head')
    group_id = fields.Many2one('account.group.name',string= 'Group Name')

    account_head_id = fields.Many2one('account.head',string= 'Account Head')
    account_sub_head_id = fields.Many2one('account.sub.head', string='Account Sub Head')
    fiscal_year_id = fields.Many2one('account.fiscalyear', string="Fiscal Year")
    department_id = fields.Many2one('hr.department', string="Department")
    division_id = fields.Many2one('hr.department', string="Division")
    section_id = fields.Many2one('hr.department', string="Section")

    budget_type = fields.Char(string="Budget Type")
    project_id = fields.Many2one('kw_project_budget_master_data', string="Project Name")
    project_name = fields.Char(string="Project Name")
    project_code = fields.Char(string="Project Code")
 
    year_1_budget = fields.Float('Budget 21-22')
    year_1_total_balance = fields.Float(string='Actual 21-22')
    year_2_budget = fields.Float(string='Budget 22-23')
    year_2_total_balance = fields.Float(string='Actual 22-23')
    year_3_budget = fields.Float(string='Budget 23-24')
    year_3_total_balance = fields.Float(string='Actual 23-24',compute="_compute_practical_amount")
    year_4_total_budget = fields.Float(string='Budget 24-25')


    @api.multi
    def _compute_practical_amount(self):
        for line in self:
            date_to = line.fiscal_year_id.date_stop
            date_from = line.fiscal_year_id.date_start
            aml_obj = self.env['account.move.line']
            domain = [('account_id', '=', line.account_id.id),
                     ('fiscalyear_id','=',4),
                        ('move_id.state', '=', 'posted'),
                      ]
                      
            if not line.department_id and not line.section_id and not line.division_id:
                domain.extend([('department_id', '=', False),
                           ('section_id', '=', False),
                           ('division_id', '=', False)])
            else:
                if line.section_id:
                    domain.append(('section_id', '=', line.section_id.id))
                elif line.division_id:
                    domain.append(('division_id', '=', line.division_id.id))
                elif line.department_id:
                    domain.append(('department_id', '=', line.department_id.id))
                    domain.append(('section_id', '=', False))
                    domain.append(('division_id', '=', False))
            if not line.project_id:
                domain.append(('project_wo_id', '=', False))
            else:
                domain.append(('project_wo_id', '=', line.project_id.id))

            where_query = aml_obj._where_calc(domain)
            aml_obj._apply_ir_rules(where_query, 'read')
            from_clause, where_clause, where_clause_params = where_query.get_sql()
            # print(where_clause)
            if line.account_id.group_type.code == '3':
                select = "SELECT sum(account_move_line.credit)-sum(account_move_line.debit) from" + from_clause + "left join account_move am on am.id = account_move_line.move_id and am.state = 'posted'"+"where" + where_clause
            else:
                select = "SELECT sum(account_move_line.debit)-sum(account_move_line.credit) from" + from_clause + "left join account_move am on am.id = account_move_line.move_id and am.state = 'posted'"+" where " + where_clause
            self.env.cr.execute(select, where_clause_params)
            result = self.env.cr.fetchone()
            line.year_3_total_balance = result[0] if result else 0.0
          
  
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
                    aml.fiscalyear_id,
					aml.project_wo_id as project_id,
                    aml.department_id,
                    aml.division_id,
                    aml.section_id,
                    aml.balance AS total_balance
                FROM 
                    account_move_line aml
                JOIN 
                    account_move am ON am.id = aml.move_id
                WHERE 
                    am.state = 'posted' 
                    and aml.fiscalyear_id != 5
            )
            select 
			null::char as budget_type,
            a.fiscal_year_id as fiscal_year_id,
                    a.account_id as account_id,
					b.project_id,
                	(select wo_name from kw_project_budget_master_data where id = b.project_id) as project_name,					  
                	(select wo_code from kw_project_budget_master_data where id = b.project_id) as project_code,
                    b.department_id,
                    b.division_id,
                    b.section_id,
                    0 as total_budget,
                    b.total_balance 
                    from a left join b on a.account_id = b.account_id and a.fiscal_year_id = b.fiscalyear_id
                    where b.total_balance IS NOT NULL
                
            union all

                    SELECT 
					'Treasury Budget' as budget_type,
                    b.fiscal_year_id AS fiscal_year_id,
                    a.account_code_id as account_id,
					null::int as project_id,
					null::char as project_name,
					null::char as project_code,
                    (SELECT department_id FROM kw_budget_dept_mapping WHERE id = b.budget_department) AS department_id,
                    (SELECT division_id FROM kw_budget_dept_mapping WHERE id = b.budget_department) AS division_id,
                    (SELECT section_id FROM kw_budget_dept_mapping WHERE id = b.budget_department) AS section_id,
                    sum(a.apr_budget + a.may_budget + a.jun_budget + a.jul_budget + a.aug_budget + a.sep_budget + a.oct_budget + a.nov_budget + a.dec_budget + a.jan_budget + a.feb_budget + a.mar_budget) AS total_budget,
                    0 as total_balance
                FROM 
                    kw_revenue_budget b
                LEFT JOIN 
                    kw_revenue_budget_line a ON a.revenue_budget_id = b.id
                WHERE 
                    a.account_code_id IS NOT NULL
                    AND (b.fiscal_year_id != 4 OR b.state = 'validate') 
                                
                GROUP BY 
                    b.fiscal_year_id, b.budget_department, a.account_code_id	
								  
			union all
								  
				SELECT 
				'Project Budget' as budget_type,
                ks.fiscal_year_id AS fiscal_year_id,
                kl.account_code_id AS account_id,
                kl.project_id as project_id,
                (select wo_name from kw_project_budget_master_data where id = kl.project_id) as project_name,
                STRING_AGG(DISTINCT kl.project_code, ', ') AS project_code,
				null::int as department_id,
				null::int as division_id,
				null::int as section_id,
                SUM(kl.apr_budget + kl.may_budget + kl.jun_budget + kl.jul_budget + kl.aug_budget + kl.sep_budget + kl.oct_budget + kl.nov_budget + kl.dec_budget + kl.jan_budget + kl.feb_budget + kl.mar_budget) AS total_budget,
                0 as total_balance
                from
            kw_sbu_project_budget_line kl
            left JOIN
                kw_sbu_project_budget ks ON kl.sbu_project_budget_id = ks.id
                where kl.account_code_id IS NOT NULL
            AND (ks.fiscal_year_id != 4 OR ks.state = 'validate') 
            GROUP BY
                kl.account_code_id,
                ks.fiscal_year_id,
                kl.project_id,
                ks.budget_department 		  
								  
                )
                SELECT MAX(budget_type) AS budget_type,
                fiscal_year_id,account_id,
			   project_id,
			   project_name,project_code,
			   department_id,division_id,section_id,
                sum(total_budget) as total_budget,
			   sum(total_balance) as total_balance
                    FROM  final_cte
                    group by 
                    final_cte.fiscal_year_id,
                    final_cte.account_id,
			   		final_cte.project_id,
			   		final_cte.project_name,
			   		final_cte.project_code,
                    final_cte.department_id,
                    final_cte.division_id,
                    final_cte.section_id
			   )

                    select ROW_NUMBER() OVER(order by account_id desc) AS id,MAX(budget_type) AS budget_type,account_id,
					project_id,
					department_id, division_id,section_id,
					MAX(project_code) AS project_code,
					MAX(project_name) AS project_name,
                    MAX(fiscal_year_id) AS fiscal_year_id,
					(select group_type from account_account where id = final.account_id) as group_type_id,
                    (select group_name from account_account where id = final.account_id) as group_id,
                    (select user_type_id from account_account where id = final.account_id) as group_head_id,
                    (select account_head_id from account_account where id = final.account_id) as account_head_id,
                    (select account_sub_head_id from account_account where id = final.account_id) as account_sub_head_id,
                    (select code from account_account where id = final.account_id) as account_code,
					max(case when fiscal_year_id = 2 then total_budget  end) as year_1_budget,
					max(case when fiscal_year_id = 2 then total_balance  end) as year_1_total_balance,
					max(case when fiscal_year_id = 3 then total_budget  end) as year_2_budget,
					max(case when fiscal_year_id = 3 then total_balance  end) as year_2_total_balance,
					max(case when fiscal_year_id = 4 then total_budget end) as year_3_budget,
					max(case when fiscal_year_id = 4 then total_balance  end) as year_3_total_balance,
                    max(case when fiscal_year_id = 5 then total_budget  end) as year_4_total_budget
					from final
					group by account_id,department_id,project_id,division_id,section_id	
            )""" % (self._table))

