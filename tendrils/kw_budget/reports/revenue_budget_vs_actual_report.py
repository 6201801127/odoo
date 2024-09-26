from odoo import models, api, fields, tools

class RevenueBudgetvsActualReport(models.Model):
    _name = "revenue_budget_vs_actual_report"
    _description = "Report For expense revenue budget"
    _auto = False
    _order = "account_code asc"


    budget_type= fields.Char(string='Budget Type')
    particular =fields.Char(string='Particulars')

    sbu_name =fields.Char(string='SBU Name')
    work_order_type =fields.Char(string='Work Order Type')
    opp_name =fields.Char(string='OPP Name')
    order_value =fields.Char(string='Order Value')
    client_name =fields.Char(string='Client Name')
    sequence_ref =fields.Char(string='ID')
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
    april_budget = fields.Float('Apr Budget')
    project_id = fields.Many2one('kw_project_budget_master_data', string="Project Name")
    project_name = fields.Char(string="Project Name")
    expense_type = fields.Char(string='Income/Exp.')
    project_code = fields.Char(string="Project Code")
    category_id =  fields.Many2one('kw_sbu_project_category_master', string='Category Name')
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
    project_budget_line =  fields.Many2one('kw_sbu_project_budget_line', string="Particulars")
    treasury_budget_line =  fields.Many2one('kw_revenue_budget_line', string="Particulars")
    april_actual = fields.Float('Apr Actual', compute='_compute_actual_amount')
    may_actual = fields.Float('May Actual', compute='_compute_actual_amount')
    june_actual = fields.Float('Jun Actual', compute='_compute_actual_amount')
    july_actual = fields.Float('Jul Actual', compute='_compute_actual_amount')
    august_actual = fields.Float('Aug Actual', compute='_compute_actual_amount')
    september_actual = fields.Float('Sep Actual', compute='_compute_actual_amount')
    october_actual = fields.Float('Oct Actual', compute='_compute_actual_amount')
    november_actual = fields.Float('Nov Actual', compute='_compute_actual_amount')
    december_actual = fields.Float('Dec Actual', compute='_compute_actual_amount')
    january_actual = fields.Float('Jan Actual', compute='_compute_actual_amount')
    february_actual = fields.Float('Feb Actual', compute='_compute_actual_amount')
    march_actual = fields.Float('Mar Actual', compute='_compute_actual_amount')
    total_budget = fields.Float('Total Budget Amount' )
    actual_amount = fields.Float('Total Actual Amount', compute="_compute_practical_amount")
    exceed_budget_amount = fields.Boolean(string='Exceed Budget Amount',compute='_compute_practical_amount')
    

    @api.multi
    def _compute_actual_amount(self):
        for line in self:
            date_to = line.fiscal_year_id.date_stop
            date_from = line.fiscal_year_id.date_start
            aml_obj = self.env['account.move.line']
            domain = [('account_id', '=', line.account_id.id),
                      ('date', '>=', date_from),
                      ('date', '<=', date_to),
                        ('move_id.state', '=', 'posted'), 
                        ('budget_line', '=', line.treasury_budget_line.id),
                        ('project_line', '=', line.project_budget_line.id),
                       
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

            month_conditions = [
                f"extract('month' from {aml_obj._table}.date) = {month}"
                for month in range(1, 13)
            ]
            where_clause += f" AND ({' OR '.join(month_conditions)})"
            if line.account_id.group_type.code == '3':
                select = "SELECT extract('month' from account_move_line.date) as month, sum(account_move_line.credit)-sum(account_move_line.debit) as balance " \
                         "from " + from_clause + "left join account_move am on am.id = account_move_line.move_id and am.state = 'posted'" + "where " + where_clause + " GROUP BY month"
            else:
                select = "SELECT extract('month' from account_move_line.date) as month, sum(account_move_line.debit)-sum(account_move_line.credit) as balance " \
                         "from " + from_clause +" left join account_move am on am.id = account_move_line.move_id and am.state = 'posted'"+" where " + where_clause + " GROUP BY month"

            self.env.cr.execute(select, where_clause_params)
            month_balances = dict(self.env.cr.fetchall())

            for month in range(1, 13):
                month_field = self._month_number_to_field_name(month)
                setattr(line, month_field, month_balances.get(month, 0.0))

    def _month_number_to_field_name(self, month):
        month_map = {4: 'april_actual',5: 'may_actual',6: 'june_actual',7: 'july_actual',8: 'august_actual',9: 'september_actual',10: 'october_actual',11: 'november_actual',12: 'december_actual',1: 'january_actual',2: 'february_actual',3: 'march_actual',}
        return month_map.get(month, 'january_actual')

    @api.multi
    def _compute_practical_amount(self):
        for line in self:
            date_to = line.fiscal_year_id.date_stop
            date_from = line.fiscal_year_id.date_start
            aml_obj = self.env['account.move.line']
            domain = [('account_id', '=',
                       line.account_id.id),
                        ('date', '>=', date_from),
                        ('date', '<=', date_to),
                        ('move_id.state', '=', 'posted'),
                     ('budget_line', '=', line.treasury_budget_line.id),
                    ('project_line', '=', line.project_budget_line.id),
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
            if line.account_id.group_type.code == '3':
                select = "SELECT sum(account_move_line.credit)-sum(account_move_line.debit) from" + from_clause + "left join account_move am on am.id = account_move_line.move_id and am.state = 'posted'"+"where" + where_clause
            else:
                select = "SELECT sum(account_move_line.debit)-sum(account_move_line.credit) from" + from_clause + "left join account_move am on am.id = account_move_line.move_id and am.state = 'posted'"+" where " + where_clause
            self.env.cr.execute(select, where_clause_params)
            line.actual_amount = self.env.cr.fetchone()[0] or 0.0
            if line.account_id.group_type.code == '3':
                line.exceed_budget_amount = False
            else:
                if line.total_budget < abs(line.actual_amount):
                    line.exceed_budget_amount = True
                else:
                    line.exceed_budget_amount = False
           

    def action_open_budget_entries(self):
        action = self.env['ir.actions.act_window'].for_xml_id('account', 'action_account_moves_all_a')
        domain = [('account_id', '=',
                             self.account_id.id),
                            ('date', '>=', self.fiscal_year_id.date_start),
                            ('date', '<=', self.fiscal_year_id.date_stop),
                            ('move_id.state', '=', 'posted'),
                        
                            ('budget_line', '=', self.treasury_budget_line.id),
                            ('project_line', '=', self.project_budget_line.id),
                         
                            ]
        if not self.department_id and not self.section_id and not self.division_id:
            domain.extend([('department_id', '=', False),
                           ('section_id', '=', False),
                           ('division_id', '=', False)])
        else:
            if self.section_id:
                domain.append(('section_id', '=', self.section_id.id))
            elif self.division_id:
                domain.append(('division_id', '=', self.division_id.id))
            elif self.department_id:
                domain.append(('department_id', '=', self.department_id.id))
                domain.append(('section_id', '=', False))
                domain.append(('division_id', '=', False))
        if not self.project_id:
            domain.append(('project_wo_id', '=', False))
        else:
            domain.append(('project_wo_id', '=', self.project_id.id))
        action['domain'] = domain
        return action


   
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
                    aml.budget_type,
                    aml.account_id,
					aml.budget_line as treasury_budget_line,
					aml.project_line as project_budget_line,
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
                    
            )
            select 
			b.budget_type as budget_type,
            null::char as particular,
            a.fiscal_year_id as fiscal_year_id,
                    a.account_id as account_id,
					b.project_id,
                	(select wo_name from kw_project_budget_master_data where id = b.project_id) as project_name,					  
                	(select wo_code from kw_project_budget_master_data where id = b.project_id) as project_code,
                   (SELECT name FROM kw_sbu_master WHERE id =(SELECT pb.sbu_id from kw_project_budget_master_data pb where
															pb.id = b.project_id)) AS sbu_name,
                    (SELECT name FROM kw_group_type WHERE id = (SELECT group_type FROM account_account WHERE id = b.account_id)) AS expense_type,
					null::char as work_order_type,
					null::char as opp_name,				
					null::char as order_value,				
					null::char as client_name,
                    null::int as category_id,
                    COALESCE((SELECT sequence_ref FROM kw_revenue_budget_line WHERE id = (SELECT budget_line FROM account_move_line WHERE id = b.treasury_budget_line)),
                    (SELECT sequence_ref FROM kw_sbu_project_budget_line WHERE id = (SELECT project_line FROM account_move_line WHERE id = b.project_budget_line))) AS sequence_ref,
                    b.department_id,
                    b.division_id,
                    b.section_id,
					0 AS april_budget, 
					0 AS may_budget,
					0 AS june_budget,
					0 AS july_budget,
					0 AS august_budget,
					0 AS september_budget,
					0 AS october_budget,
					0 AS november_budget,
					0 AS december_budget,
					0 AS january_budget,
					0 AS february_budget,
					0 AS march_budget,
                    0 as total_budget,
					b.treasury_budget_line,
					b.project_budget_line,
                    b.total_balance 
                    from a left join b on a.account_id = b.account_id and a.fiscal_year_id = b.fiscalyear_id
                    where b.total_balance IS NOT NULL
                
            union all

                    SELECT 
					'Treasury Budget' as budget_type,
                    max(a.name_of_expenses) as particular,
                    b.fiscal_year_id AS fiscal_year_id,
                    a.account_code_id as account_id,
					null::int as project_id,
					null::char as project_name,
					null::char as project_code,
                    'NA' as sbu_name,
                    a.expense_type as expense_type,
					null::char as work_order_type,
					null::char as opp_name,				
					null::char as order_value,				
					null::char as client_name,
                    null::int as category_id,
                    max(a.sequence_ref) as sequence_ref,			
                    (SELECT department_id FROM kw_budget_dept_mapping WHERE id = b.budget_department) AS department_id,
                    (SELECT division_id FROM kw_budget_dept_mapping WHERE id = b.budget_department) AS division_id,
                    (SELECT section_id FROM kw_budget_dept_mapping WHERE id = b.budget_department) AS section_id,
					SUM(a.apr_budget) AS apr_budget,
					SUM(a.may_budget) AS may_budget,
					SUM(a.jun_budget) AS jun_budget,
					SUM(a.jul_budget) AS jul_budget,
					SUM(a.aug_budget) AS aug_budget,
					SUM(a.sep_budget) AS sep_budget,
					SUM(a.oct_budget) AS oct_budget,
					SUM(a.nov_budget) AS nov_budget,
					SUM(a.dec_budget) AS dec_budget,
					SUM(a.jan_budget) AS jan_budget,
					SUM(a.feb_budget) AS feb_budget,
					SUM(a.mar_budget) AS mar_budget,
                    sum(a.apr_budget + a.may_budget + a.jun_budget + a.jul_budget + a.aug_budget + a.sep_budget + a.oct_budget + a.nov_budget + a.dec_budget + a.jan_budget + a.feb_budget + a.mar_budget) AS total_budget,
					a.id as treasury_budget_line,
					null::int as project_budget_line,	
                    0 as total_balance
                FROM 
                    kw_revenue_budget b
                LEFT JOIN 
                    kw_revenue_budget_line a ON a.revenue_budget_id = b.id
                WHERE 
                    a.account_code_id IS NOT NULL AND b.state = 'validate' AND a.state = 'validate'  
                                
                GROUP BY 
                    b.fiscal_year_id, b.budget_department, a.account_code_id,a.id
								  
			union all
								  
				SELECT 
				'Project Budget' as budget_type,
                max(kl.head_of_expense) as particular,
                ks.fiscal_year_id AS fiscal_year_id,
                kl.account_code_id AS account_id,
                kl.project_id as project_id,
                (select wo_name from kw_project_budget_master_data where id = kl.project_id) as project_name,
                STRING_AGG(DISTINCT kl.project_code, ', ') AS project_code,

                (SELECT name FROM kw_sbu_master WHERE id = (SELECT sbu_id FROM kw_sbu_project_mapping WHERE id = ks.budget_department)) AS sbu_name,
                STRING_AGG(DISTINCT kl.head_expense_type, ', ') AS expense_type,

                STRING_AGG(DISTINCT kl.work_order_type, ', ') AS work_order_type,
				STRING_AGG(DISTINCT kl.opportunity_name, ', ') AS opp_name,
				STRING_AGG(DISTINCT REPLACE(kl.order_value, ',', ''), ', ') AS order_value,
				STRING_AGG(DISTINCT kl.client, ', ') AS client_name,
                max(kl.category_id) as category_id,
                max(kl.sequence_ref) as sequence_ref,
				(select id from hr_department where id =(SELECT department_id FROM hr_employee WHERE id =(select sbu.representative_id from kw_sbu_master sbu left join kw_sbu_project_mapping kb on
																	 kb.id= ks.budget_department  where  sbu.id=kb.sbu_id)))as department_id,
				(select id from hr_department where id =(SELECT division FROM hr_employee WHERE id =(select sbu.representative_id from kw_sbu_master sbu left join kw_sbu_project_mapping kb on
																	 kb.id=  ks.budget_department  where  sbu.id=kb.sbu_id)))as division_id,
				(select id from hr_department where id =(SELECT section FROM hr_employee WHERE id =(select sbu.representative_id from kw_sbu_master sbu left join kw_sbu_project_mapping kb on
																	 kb.id=  ks.budget_department  where  sbu.id=kb.sbu_id)))as section_id,
				SUM(kl.apr_budget) AS apr_budget,
                SUM(kl.may_budget) AS may_budget,
                SUM(kl.jun_budget) AS jun_budget,
                SUM(kl.jul_budget) AS jul_budget,
                SUM(kl.aug_budget) AS aug_budget,
                SUM(kl.sep_budget) AS sep_budget,
                SUM(kl.oct_budget) AS oct_budget,
                SUM(kl.nov_budget) AS nov_budget,
                SUM(kl.dec_budget) AS dec_budget,
                SUM(kl.jan_budget) AS jan_budget,
                SUM(kl.feb_budget) AS feb_budget,
                SUM(kl.mar_budget) AS mar_budget,
                SUM(kl.apr_budget + kl.may_budget + kl.jun_budget + kl.jul_budget + kl.aug_budget + kl.sep_budget + kl.oct_budget + kl.nov_budget + kl.dec_budget + kl.jan_budget + kl.feb_budget + kl.mar_budget) AS total_budget,
				null::int as treasury_budget_line,	
				kl.id as project_budget_line,
                0 as total_balance
                from
            kw_sbu_project_budget_line kl
            left JOIN
                kw_sbu_project_budget ks ON kl.sbu_project_budget_id = ks.id
                where kl.account_code_id IS NOT NULL
            AND ks.state = 'validate' AND kl.state = 'validate'
            GROUP BY
                kl.account_code_id,
                ks.fiscal_year_id,
                kl.project_id,
                ks.budget_department,
				kl.id
                )				
	SELECT MAX(budget_type) AS budget_type,
    max(particular) as particular,
    project_id,
	    MAX(project_code) AS project_code,
		MAX(project_name) AS project_name,
        MAX(sbu_name) AS sbu_name,
        MAX(expense_type) AS expense_type,
		MAX(work_order_type) AS work_order_type,
		MAX(opp_name) AS opp_name,
		MAX(order_value) AS order_value,
		MAX(client_name) AS client_name,
        MAX(category_id) AS category_id,
        COALESCE(MAX(sequence_ref), 'NA') AS sequence_ref,
	    fiscal_year_id,account_id,department_id,division_id,section_id,
        sum(total_budget) as total_budget,
        sum(total_balance) as balance,
        SUM(april_budget) as april_budget, 
        SUM(may_budget) AS may_budget,
        SUM(june_budget) AS june_budget,
        SUM(july_budget) AS july_budget,
        SUM(august_budget) AS august_budget,
        SUM(september_budget) AS september_budget,
        SUM(october_budget) AS october_budget,
        SUM(november_budget) AS november_budget,
        SUM(december_budget) AS december_budget,
        SUM(january_budget) AS january_budget,
        SUM(february_budget) AS february_budget,
        SUM(march_budget) AS march_budget,
        treasury_budget_line,
		project_budget_line	 
	    FROM  final_cte
        group by 
        
        final_cte.fiscal_year_id,
        final_cte.account_id,
		 final_cte.treasury_budget_line,
		final_cte.project_budget_line,
		final_cte.project_id,	
        final_cte.department_id,
        final_cte.division_id,
        final_cte.section_id)
select ROW_NUMBER() OVER(order by account_id desc,fiscal_year_id desc,project_id desc,department_id desc,division_id desc,section_id desc) AS id,(select group_type from account_account where id = final.account_id) as group_type_id,
        (select group_name from account_account where id = final.account_id) as group_id,
        (select user_type_id from account_account where id = final.account_id) as group_head_id,
       	(select account_head_id from account_account where id = final.account_id) as account_head_id,
        (select account_sub_head_id from account_account where id = final.account_id) as account_sub_head_id,
        (select code from account_account where id = final.account_id) as account_code,* from final

)""" % (self._table))
