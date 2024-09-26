from odoo import models, api, fields, tools

class RevenueExpenseReport(models.Model):
    _name = "revenue_budget_expense_report"
    _description = "Report For expense revenue budget"
    _auto = False
    _order = "account_code asc"

    account_id = fields.Many2one('account.account', 'Account Code')
    particular =fields.Char(string='Particulars')
    sequence_ref =fields.Char(string='ID')
    budget_type =fields.Char(string='Budget Type')
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
            # acc_ids = line.budgetary_position_id.account_ids.ids
            date_to = line.fiscal_year_id.date_stop
            date_from = line.fiscal_year_id.date_start
            aml_obj = self.env['account.move.line']
            domain = [('account_id', '=',
                       line.account_id.id),
                        ('date', '>=', date_from),
                        ('date', '<=', date_to),
                        ('move_id.state', '=', 'posted'),
                        # ('department_id', '=', line.department_id.id),
                        # ('budget_type','=','treasury'),
                        #  ('budget_update','=',False)
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

    def action_open_budget_entries(self):
        action = self.env['ir.actions.act_window'].for_xml_id('account', 'action_account_moves_all_a')
        domain = [('account_id', '=',
                             self.account_id.id),
                            ('date', '>=', self.fiscal_year_id.date_start),
                            ('date', '<=', self.fiscal_year_id.date_stop),
                            ('move_id.state', '=', 'posted'),
                            # ('department_id', '=', self.department_id.id),
                            # ('budget_type','=','treasury'),
                            # ('budget_update','=',False)
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


    @api.depends('april_budget', 'may_budget', 'june_budget', 'july_budget',
                 'august_budget', 'september_budget', 'october_budget', 
                 'november_budget', 'december_budget', 'january_budget', 
                 'february_budget', 'march_budget')
    def compute_total_planed_amount(self):
        for rec in self:
            rec.total_budget = rec.april_budget + rec.may_budget + rec.june_budget + \
                              rec.july_budget + rec.august_budget + rec.september_budget + \
                              rec.october_budget + rec.november_budget + rec.december_budget + \
                              rec.january_budget + rec.february_budget + rec.march_budget

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
)
select 
b.budget_type as budget_type,
null::char as particular,
a.fiscal_year_id as fiscal_year_id,
        a.account_id as account_id,
	  	b.department_id,
		b.division_id,
		b.section_id,
        null::char as sequence_ref,
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
		b.total_balance 
		from a left join b on a.account_id = b.account_id and a.fiscal_year_id = b.fiscalyear_id
		where b.total_balance IS NOT NULL
	
 union all

 		SELECT 
        'Treasury Budget' as budget_type,
        max(a.name_of_expenses) as particular,
        b.fiscal_year_id AS fiscal_year_id,
        a.account_code_id as account_id,
        (SELECT department_id FROM kw_budget_dept_mapping WHERE id = b.budget_department) AS department_id,
        (SELECT division_id FROM kw_budget_dept_mapping WHERE id = b.budget_department) AS division_id,
        (SELECT section_id FROM kw_budget_dept_mapping WHERE id = b.budget_department) AS section_id,
        max(a.sequence_ref) as sequence_ref,
        SUM(a.apr_budget) AS april_budget, 
        SUM(a.may_budget) AS may_budget,
        SUM(a.jun_budget) AS june_budget,
        SUM(a.jul_budget) AS july_budget,
        SUM(a.aug_budget) AS august_budget,
        SUM(a.sep_budget) AS september_budget,
        SUM(a.oct_budget) AS october_budget,
        SUM(a.nov_budget) AS november_budget,
        SUM(a.dec_budget) AS december_budget,
        SUM(a.jan_budget) AS january_budget,
        SUM(a.feb_budget) AS february_budget,
        SUM(a.mar_budget) AS march_budget,
		sum(a.apr_budget + a.may_budget + a.jun_budget + a.jul_budget + a.aug_budget + a.sep_budget + a.oct_budget + a.nov_budget + a.dec_budget + a.jan_budget + a.feb_budget + a.mar_budget) AS total_budget,
		0 as total_balance
    FROM 
        kw_revenue_budget b
    LEFT JOIN 
        kw_revenue_budget_line a ON a.revenue_budget_id = b.id
    WHERE 
        a.account_code_id IS NOT NULL and b.state = 'validate' and a.state = 'validate'
					
    GROUP BY 
        b.fiscal_year_id, b.budget_department, a.account_code_id				
	)
	SELECT 
    MAX(budget_type) AS budget_type,
    max(particular) as particular,
	fiscal_year_id,account_id,department_id,division_id,section_id,sum(total_budget) as total_budget,sum(total_balance) as balance,
    max(sequence_ref) as sequence_ref,
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
        SUM(march_budget) AS march_budget
	    FROM  final_cte
        group by 
        final_cte.fiscal_year_id,
        final_cte.account_id,
        final_cte.department_id,
        final_cte.division_id,
        final_cte.section_id)

select ROW_NUMBER() OVER(order by account_id desc) AS id,(select group_type from account_account where id = final.account_id) as group_type_id,
        (select group_name from account_account where id = final.account_id) as group_id,
        (select user_type_id from account_account where id = final.account_id) as group_head_id,
       	(select account_head_id from account_account where id = final.account_id) as account_head_id,
        (select account_sub_head_id from account_account where id = final.account_id) as account_sub_head_id,
        (select code from account_account where id = final.account_id) as account_code,* from final

)""" % (self._table))

#  WITH a AS (
#     SELECT 
#         af.id AS fiscal_year_id,
#         aa.id AS account_id,
#         aa.group_type AS group_type_id,
#         aa.group_name AS group_id,
#         aa.user_type_id AS group_head_id,
#         aa.account_head_id AS account_head_id,
#         aa.account_sub_head_id AS account_sub_head_id,
#         aa.code as account_code,
#         af.date_start,
#         af.date_stop
#     FROM 
#         account_account aa
#     CROSS JOIN 
#         account_fiscalyear af
# ),
# result2 AS (
#     SELECT 
#         b.fiscal_year_id AS fy_year,
#         (SELECT department_id FROM kw_budget_dept_mapping WHERE id = b.budget_department) AS department_id,
#         (SELECT division_id FROM kw_budget_dept_mapping WHERE id = b.budget_department) AS division_id,
#         (SELECT section_id FROM kw_budget_dept_mapping WHERE id = b.budget_department) AS section_id,
#         a.account_code_id,
#         SUM(a.apr_budget) AS april_budget, 
#         SUM(a.may_budget) AS may_budget,
#         SUM(a.jun_budget) AS june_budget,
#         SUM(a.jul_budget) AS july_budget,
#         SUM(a.aug_budget) AS august_budget,
#         SUM(a.sep_budget) AS september_budget,
#         SUM(a.oct_budget) AS october_budget,
#         SUM(a.nov_budget) AS november_budget,
#         SUM(a.dec_budget) AS december_budget,
#         SUM(a.jan_budget) AS january_budget,
#         SUM(a.feb_budget) AS february_budget,
#         SUM(a.mar_budget) AS march_budget
#     FROM 
#         kw_revenue_budget b
#     LEFT JOIN 
#         kw_revenue_budget_line a ON a.revenue_budget_id = b.id
#     WHERE 
#         a.account_code_id IS NOT NULL
#     GROUP BY 
#         b.fiscal_year_id, b.budget_department, a.account_code_id
# )
# SELECT 
#     ROW_NUMBER() OVER(order by a.fiscal_year_id desc) AS id,
#     a.fiscal_year_id,
#     a.account_id,
#     a.group_type_id,
#     a.group_id,
#     a.group_head_id,
#     a.account_head_id,
#     a.account_sub_head_id,
#     a.account_code,
#     result2.department_id,
#     result2.division_id,
#     result2.section_id,
#     result2.april_budget,
#     result2.may_budget,
#     result2.june_budget,
#     result2.july_budget,
#     result2.august_budget,
#     result2.september_budget,
#     result2.october_budget,
#     result2.november_budget,
#     result2.december_budget,
#     result2.january_budget,
#     result2.february_budget,
#     result2.march_budget,
#     COALESCE(aml.total_balance, 0) AS total_balance
# FROM 
#     a
# LEFT JOIN 
#     result2 ON a.account_id = result2.account_code_id 
#             AND a.fiscal_year_id = result2.fy_year
# LEFT JOIN (
#     SELECT 
#         aml.account_id,
#         aml.fiscalyear_id,
#         SUM(aml.balance) AS total_balance
#     FROM 
#         account_move_line aml
#     JOIN 
#         a ON a.account_id = aml.account_id
#     JOIN 
#         account_move am ON am.id = aml.move_id
#     WHERE 
#         aml.date >= a.date_start
#         AND aml.date <= a.date_stop
#         AND am.state = 'posted'
#     GROUP BY 
#         aml.account_id, aml.fiscalyear_id
# ) aml ON aml.account_id = a.account_id AND aml.fiscalyear_id = a.fiscal_year_id
# WHERE 
#     result2.april_budget IS NOT NULL OR
#     result2.may_budget IS NOT NULL OR
#     result2.june_budget IS NOT NULL OR
#     result2.july_budget IS NOT NULL OR
#     result2.august_budget IS NOT NULL OR
#     result2.september_budget IS NOT NULL OR
#     result2.october_budget IS NOT NULL OR
#     result2.november_budget IS NOT NULL OR
#     result2.december_budget IS NOT NULL OR
#     result2.january_budget IS NOT NULL OR
#     result2.february_budget IS NOT NULL OR
#     result2.march_budget IS NOT NULL OR
#     aml.total_balance IS NOT NULL


#  WITH move_line AS (
#         SELECT 
# 	    ROW_NUMBER() OVER(order by aml.account_id desc) AS id,
#         aml.fiscalyear_id as fiscal_year_id,
#         aml.account_id,
#         aml.department_id,
#         aa.group_type,
#         aa.group_name,
#         aa.user_type_id,
#         aa.account_head_id,
#         aa.account_sub_head_id,
#         SUM(CASE WHEN EXTRACT(MONTH FROM aml.date) = 4 THEN aml.balance ELSE 0 END) AS april_balance,
#         SUM(CASE WHEN EXTRACT(MONTH FROM aml.date) = 5 THEN aml.balance ELSE 0 END) AS may_balance,
#         SUM(CASE WHEN EXTRACT(MONTH FROM aml.date) = 6 THEN aml.balance ELSE 0 END) AS june_balance,
#         SUM(CASE WHEN EXTRACT(MONTH FROM aml.date) = 7 THEN aml.balance ELSE 0 END) AS july_balance,
#         SUM(CASE WHEN EXTRACT(MONTH FROM aml.date) = 8 THEN aml.balance ELSE 0 END) AS august_balance,
#         SUM(CASE WHEN EXTRACT(MONTH FROM aml.date) = 9 THEN aml.balance ELSE 0 END) AS september_balance,
#         SUM(CASE WHEN EXTRACT(MONTH FROM aml.date) = 10 THEN aml.balance ELSE 0 END) AS october_balance,
#         SUM(CASE WHEN EXTRACT(MONTH FROM aml.date) = 11 THEN aml.balance ELSE 0 END) AS november_balance,
#         SUM(CASE WHEN EXTRACT(MONTH FROM aml.date) = 12 THEN aml.balance ELSE 0 END) AS december_balance,
#         SUM(CASE WHEN EXTRACT(MONTH FROM aml.date) = 1 THEN aml.balance ELSE 0 END) AS january_balance,
#         SUM(CASE WHEN EXTRACT(MONTH FROM aml.date) = 2 THEN aml.balance ELSE 0 END) AS february_balance,
#         SUM(CASE WHEN EXTRACT(MONTH FROM aml.date) = 3 THEN aml.balance ELSE 0 END) AS march_balance,
#         SUM(aml.balance) AS total_balance
#     FROM 
#         account_move_line aml 
#     LEFT JOIN 
#         account_account aa ON aml.account_id = aa.id
#     GROUP BY 
#         aml.fiscalyear_id, aml.account_id, aml.department_id, aa.group_type, aa.group_name, aa.user_type_id, aa.account_head_id, aa.account_sub_head_id
# ),
# budget_line AS (
#     SELECT 
# 	 ROW_NUMBER() OVER(order by krbl.account_code_id desc) AS id,
#         krb.fiscal_year_id as fiscal_year_id,
#         kbdm.department_id as department_id,
#         aa.group_type,
#         aa.group_name,
#         aa.user_type_id,
#         aa.account_head_id,
#         aa.account_sub_head_id,
#         krbl.account_code_id as account_id,
#         SUM(krbl.apr_budget) AS april_budget, 
#         SUM(krbl.may_budget) AS may_budget,
#         SUM(krbl.jun_budget) AS june_budget,
#         SUM(krbl.jul_budget) AS july_budget,
#         SUM(krbl.aug_budget) AS august_budget,
#         SUM(krbl.sep_budget) AS september_budget,
#         SUM(krbl.oct_budget) AS october_budget,
#         SUM(krbl.nov_budget) AS november_budget,
#         SUM(krbl.dec_budget) AS december_budget,
#         SUM(krbl.jan_budget) AS january_budget,
#         SUM(krbl.feb_budget) AS february_budget,
#         SUM(krbl.mar_budget) AS march_budget,
#         SUM(krbl.total_amount) AS total_balance
#     FROM 
#         kw_revenue_budget_line krbl
#     LEFT JOIN 
#         kw_revenue_budget krb ON krb.id = krbl.revenue_budget_id
# 	left join kw_budget_dept_mapping kbdm on kbdm.id = krb.budget_department 
#     LEFT JOIN 
#         account_account aa ON krbl.account_code_id = aa.id 
#     GROUP BY 
#         krb.fiscal_year_id, kbdm.department_id, krbl.account_code_id, aa.group_type, aa.group_name, aa.user_type_id, aa.account_head_id, aa.account_sub_head_id
# )


# SELECT 
#  ROW_NUMBER() OVER(order by account_id desc) AS id,
#     fiscal_year_id,
#     account_id,
#     department_id as department_id, 
#     group_type as group_type_id,
#     group_name as group_id,
#     user_type_id as group_head_id,
#     account_head_id AS account_head_id,
#     account_sub_head_id AS account_sub_head_id,
#     april_balance AS april_actual,
#     may_balance AS may_actual,
#     june_balance AS june_actual,
#     july_balance AS july_actual,
#     august_balance AS august_actual,
#     september_balance AS september_actual,
#     october_balance AS october_actual,
#     november_balance AS november_actual,
#     december_balance AS december_actual,
#     january_balance AS january_actual,
#     february_balance AS february_actual,
#     march_balance AS march_actual,
#     total_balance AS actual_amount,
#     NULL AS april_budget,
#     NULL AS may_budget,
#     NULL AS june_budget,
#     NULL AS july_budget,
#     NULL AS august_budget,
#     NULL AS september_budget,
#     NULL AS october_budget,
#     NULL AS november_budget,
#     NULL AS december_budget,
#     NULL AS january_budget,
#     NULL AS february_budget,
#     NULL AS march_budget,
#     NULL AS total_budget
# FROM 
#     move_line

# UNION

# SELECT 
#  ROW_NUMBER() OVER(order by account_id desc) AS id,
#     fiscal_year_id,
#     account_id,
#     department_id as department_id,
#     group_type as group_type_id,
#     group_name  as group_id,
#     user_type_id as group_head_id,
#     account_head_id  AS account_head_id,
#     account_sub_head_id AS account_sub_head_id,
#     NULL AS april_actual,
#     NULL AS may_actual,
#     NULL AS june_actual,
#     NULL AS july_actual,
#     NULL AS august_actual,
#     NULL AS september_actual,
#     NULL AS october_actual,
#     NULL AS november_actual,
#     NULL AS december_actual,
#     NULL AS january_actual,
#     NULL AS february_actual,
#     NULL AS march_actual,
#     NULL AS actual_amount,
#     april_budget AS april_budget,
#     may_budget AS may_budget,
#     june_budget AS june_budget,
#     july_budget AS july_budget,
#     august_budget AS august_budget,
#     september_budget AS september_budget,
#     october_budget AS october_budget,
#     november_budget AS november_budget,
#     december_budget AS december_budget,
#     january_budget AS january_budget,
#     february_budget AS february_budget,
#     march_budget AS march_budget,
#     total_balance AS total_budget
# FROM 
#     budget_line