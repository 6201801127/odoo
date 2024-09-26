from odoo import models, api, fields, tools


class CapitalBudgetExpenseReport(models.Model):
    _name = "capital_budget_expense_report"
    _description = "Report For capital budget expense"
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
    division_id = fields.Many2one('hr.department', string="Division")
    section_id = fields.Many2one('hr.department', string="Section")
    # date_from = fields.Date(string="Month Start Date")
    # date_to = fields.Date(string="Month End Date")
    total_budget = fields.Float(string="Total Budget Amount")
    actual_amount = fields.Float(string='Actual Amount',compute='_compute_practical_amount', readonly=True)
    exceed_budget_amount = fields.Boolean(string='Exceed Budget Amount', compute='_compute_practical_amount')
    april_actual = fields.Float('April Actual', compute='_compute_actual_amount')
    may_actual = fields.Float('May Actual', compute='_compute_actual_amount')
    june_actual = fields.Float('June Actual', compute='_compute_actual_amount')
    july_actual = fields.Float('July Actual', compute='_compute_actual_amount')
    august_actual = fields.Float('Aug Actual', compute='_compute_actual_amount')
    september_actual = fields.Float('Sept Actual', compute='_compute_actual_amount')
    october_actual = fields.Float('Oct Actual', compute='_compute_actual_amount')
    november_actual = fields.Float('Nov Actual', compute='_compute_actual_amount')
    december_actual = fields.Float('Dec Actual', compute='_compute_actual_amount')
    january_actual = fields.Float('Jan Actual', compute='_compute_actual_amount')
    february_actual = fields.Float('Feb Actual', compute='_compute_actual_amount')
    march_actual = fields.Float('March Actual', compute='_compute_actual_amount')
    # total_budget = fields.Float('Total Budget Amount', compute='compute_total_planed_amount')

    @api.multi
    def _compute_actual_amount(self):
        for line in self:
            date_to = line.fiscal_year_id.date_stop
            date_from = line.fiscal_year_id.date_start
            aml_obj = self.env['account.move.line']
            domain = [('account_id', '=', line.account_id.id),
                      ('date', '>=', date_from),
                      ('date', '<=', date_to),
                    #    ('department_id', '=', line.department_id.id),
                       ('move_id.state', '=', 'posted'),
                       ('budget_update','=',True),
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
            month_conditions = [
                f"extract('month' from {aml_obj._table}.date) = {month}"
                for month in range(1, 13)
                ]
            where_clause += f" AND ({' OR '.join(month_conditions)})"
            # select = "SELECT extract('month' from date) as month, sum(debit)-sum(credit) as balance " \
            #          "from " + from_clause + " where " + where_clause + " GROUP BY month"
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

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        # budget_code = self.env['budget_report_group_mapping'].sudo().search([('code','=','cp')])
        # query_string = ''
        # if budget_code:
        #     if budget_code.group_type_id or budget_code.group_head_id or budget_code.group_id:
        #         query_string += 'where'
        #         if budget_code.group_type_id:
        #             query_string = f'aa.group_type = {}'
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
        account_move am ON am.id = aml.move_id and aml.budget_update=true
    WHERE 
        am.state = 'posted' 
)
select 
a.fiscal_year_id as fiscal_year_id,
        a.account_id as account_id,
	  	b.department_id,
		b.division_id,
		b.section_id,
		null::date as date_from,
		null::date as date_to,
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
				b.date_from AS date_from,
				b.date_to AS date_to,
				SUM(a.total_amount) AS total_budget,
				0 as total_balance
			FROM 
				kw_capital_budget b
			LEFT JOIN 
				kw_capital_budget_line a ON a.capital_budget_id = b.id
			WHERE 
				a.account_code_id IS NOT NULL and b.state = 'validate'
			GROUP BY 
				b.fiscal_year_id, b.budget_department, a.account_code_id, b.date_from, b.date_to			
	)
	SELECT 
	fiscal_year_id,
   account_id,
   department_id,
   division_id,
  section_id,
	sum(total_budget) as total_budget,
  sum(total_balance) as balance,
   date_from,
   date_to
   
	    FROM  final_cte
        group by 
        final_cte.fiscal_year_id,
        final_cte.account_id,
		final_cte.date_from,
		final_cte.date_to,
        final_cte.department_id,
        final_cte.division_id,
        final_cte.section_id,
		 final_cte.total_budget
			  )
select ROW_NUMBER() OVER(order by account_id desc) AS id,
(select group_type from account_account where id = final.account_id) as group_type_id,
        (select group_name from account_account where id = final.account_id) as group_id,
        (select user_type_id from account_account where id = final.account_id) as group_head_id,
       	(select account_head_id from account_account where id = final.account_id) as account_head_id,
        (select account_sub_head_id from account_account where id = final.account_id) as account_sub_head_id,
        (select code from account_account where id = final.account_id) as account_code,		 
        department_id,
		division_id,
		section_id,
		fiscal_year_id,
    account_id,
    SUM(total_budget) AS total_budget,
    SUM(balance) AS balance
FROM 
    final
GROUP BY 
    department_id,
    division_id,
	section_id,
	fiscal_year_id,
    account_id
                    )""" % (self._table))

    def action_open_budget_entries(self):
        action = self.env['ir.actions.act_window'].for_xml_id('account', 'action_account_moves_all_a')
        domain = [('account_id', '=',
                             self.account_id.id),
                            ('date', '>=', self.fiscal_year_id.date_start),
                            ('date', '<=', self.fiscal_year_id.date_stop),
                            # ('department_id', '=', self.department_id.id),
                            ('move_id.state', '=', 'posted'),
                            ('budget_update','=',True),
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
        action['domain'] = domain
        return action


    def _compute_practical_amount(self):
        for line in self:
            date_to = line.fiscal_year_id.date_stop
            date_from = line.fiscal_year_id.date_start
            aml_obj = self.env['account.move.line']
            domain = [('account_id', '=',
                       line.account_id.id),
                      ('date', '>=', date_from),
                      ('date', '<=', date_to),
                    #   ('department_id', '=', line.department_id.id),
                        ('move_id.state', '=', 'posted'),
                        ('budget_update','=',True),
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
 # ('department_id', '=', line.department_id.id)
#   where aa.group_type = 
                            # coalesce({budget_code.group_type_id.id if budget_code and budget_code.group_type_id else 'null'},aa.group_type)
                             