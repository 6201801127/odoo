from odoo import models, api, fields, tools

class AnnualTreasuryDraftBudgetvsActual(models.Model):
    _name = "annual_treasury_draft_budget_vs_actual"
    _description = "Annual Budget For four year of expense Treasury budget"
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
            a.fiscal_year_id as fiscal_year_id,
                    a.account_id as account_id,
                    b.department_id,
                    b.division_id,
                    b.section_id,
                    0 as total_budget,
                    b.total_balance 
                    from a left join b on a.account_id = b.account_id and a.fiscal_year_id = b.fiscalyear_id
                    where b.total_balance IS NOT NULL
                
            union all

                    SELECT 
                    b.fiscal_year_id AS fiscal_year_id,
                    a.account_code_id as account_id,
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
                )
                SELECT 
                fiscal_year_id,account_id,department_id,division_id,section_id,
                sum(total_budget) as total_budget,sum(total_balance) as total_balance
                    FROM  final_cte
                    group by 
                    final_cte.fiscal_year_id,
                    final_cte.account_id,
                    final_cte.department_id,
                    final_cte.division_id,
                    final_cte.section_id
			   )

                    select ROW_NUMBER() OVER(order by account_id desc) AS id,account_id,
					department_id, division_id,section_id,
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
					group by account_id,department_id, division_id,section_id				

            )""" % (self._table))

