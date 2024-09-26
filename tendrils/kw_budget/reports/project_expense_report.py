from odoo import models, api, fields, tools
from datetime import date,datetime

def get_current_financial_dates():
    current_date = date.today()
    current_year = date.today().year
    if current_date < date(current_year, 4, 1):
        start_date = date(current_year - 1, 4, 1)
        end_date = date(current_year, 3, 31)
    else:
        start_date = date(current_year, 4, 1)
        end_date = date(current_year + 1, 3, 31)
    return start_date, end_date
start_date, end_date = get_current_financial_dates()

class ProjectExpenseReport(models.Model):
    _name = "project_budget_expense_report"
    _description = "Report For expense project budget"
    _auto = False
    _order = "account_code asc"

    account_id = fields.Many2one('account.account', 'Account Code')
    # particular =fields.Char(string='Particulars')
    budget_type =fields.Char(string='Budget Type')
    account_code = fields.Char(string='Account Code')
    account_name = fields.Char(related='account_id.name', string='Account Name')
    group_type_id = fields.Many2one('kw.group.type',string='Group Type')
    group_head_id = fields.Many2one('account.account.type', string='Group Head')
    group_id = fields.Many2one('account.group.name',string= 'Group Name')
    account_head_id = fields.Many2one('account.head',string= 'Account Head')
    account_sub_head_id = fields.Many2one('account.sub.head', string='Account Sub Head')
    fiscal_year_id = fields.Many2one('account.fiscalyear', string="Fiscal Year")
    # sbu_id = fields.Many2one('kw_sbu_master', string="SBU Name")
    sbu_name = fields.Char(string="SBU Name")
    # project_id = fields.Many2one('project.project', string="Project Name")
    project_id = fields.Many2one('kw_project_budget_master_data', string="Project Name")
    project_name = fields.Char(string="Project Name")
    project_code = fields.Char(string="Project Code")
    order_code = fields.Char(string="Project Code")
    work_order_type = fields.Char(string="Work Order Type")
    opp_name = fields.Char(string="OPP Name")
    order_value = fields.Char(string="Order Value")
    client_name = fields.Char(string="Client Name")
    sequence_ref = fields.Char(string="ID")
    # category_id =  fields.Many2one('kw_sbu_project_category_master', string='Category Name')
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
    total_budget = fields.Float('Total Budget Amount')
    actual_amount = fields.Float('Total Actual Amount', compute="_compute_practical_amount")
    exceed_budget_amount = fields.Boolean(string='Exceed Budget Amount',compute='_compute_practical_amount')
    current_financial_year = fields.Boolean("current Financial Year", compute='_compute_actual_amount',
                                            search="_search_current_financial_year")

    @api.multi
    def _search_current_financial_year(self, operator, value):
        # print('current year',start_date,end_date)
        return ['&', ('fiscal_year_id.date_start', '>=', start_date), ('fiscal_year_id.date_stop', '<=', end_date)]


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
                    #    ('project_wo_id','=',line.project_id.id)
                        # ('budget_type','=','project')
                      ]
            if not line.project_id:
                domain.extend([('project_wo_id', '=', False)])
            else:
                if line.project_id:
                    domain.append(('project_wo_id','=',line.project_id.id))
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
                        #   ('project_wo_id','=',line.project_id.id)
                        # ('budget_type','=','project')
                       
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
                            # ('project_wo_id','=',self.project_id.id),
                             ('move_id.state', '=', 'posted'),
                            #  ('budget_type','=','project')
                            ]
        if not self.project_id:
                domain.extend([('project_wo_id', '=', False)])
        else:
            if self.project_id:
                domain.append(('project_wo_id','=',self.project_id.id))
        action['domain'] = domain
        return action


    # @api.depends('april_budget', 'may_budget', 'june_budget', 'july_budget',
    #              'august_budget', 'september_budget', 'october_budget', 
    #              'november_budget', 'december_budget', 'january_budget', 
    #              'february_budget', 'march_budget')
    # def compute_total_planed_amount(self):
    #     for rec in self:
    #         rec.total_budget = rec.april_budget + rec.may_budget + rec.june_budget + \
    #                           rec.july_budget + rec.august_budget + rec.september_budget + \
    #                           rec.october_budget + rec.november_budget + rec.december_budget + \
    #                           rec.january_budget + rec.february_budget + rec.march_budget

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
        aml.balance AS total_balance,
        aml.budget_type
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

	   
		b.project_id,
        (select wo_name from kw_project_budget_master_data where id = b.project_id) as project_name,
        ''::char as sbu_name,				  
		(select wo_code from kw_project_budget_master_data where id = b.project_id) as project_code,
		''::char as expense_type,
		''::char as order_code,
 		''::char as work_order_type,
 		''::char as opp_name,
 		''::char as order_value,
 		''::char as client_name,
        ''::char as sequence_ref,
        b.budget_type as budget_type,
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
		from a left join b on a.account_id = b.account_id and a.fiscal_year_id = b.fiscal_year_id
		where b.total_balance IS NOT NULL
								   
 union all
 		 		SELECT
                ks.fiscal_year_id AS fiscal_year_id,
                kl.account_code_id AS account_id,
               

                kl.project_id as project_id,
                (select wo_name from kw_project_budget_master_data where id = kl.project_id) as project_name,
                (SELECT name FROM kw_sbu_master WHERE id = (SELECT sbu_id FROM kw_sbu_project_mapping WHERE id = ks.budget_department)) AS sbu_name,
				STRING_AGG(DISTINCT kl.project_code, ', ') AS project_code,
                STRING_AGG(DISTINCT kl.head_expense_type, ', ') AS expense_type,
				STRING_AGG(DISTINCT kl.order_code, ', ') AS order_code,
				STRING_AGG(DISTINCT kl.work_order_type, ', ') AS work_order_type,
				STRING_AGG(DISTINCT kl.opportunity_name, ', ') AS opp_name,
				STRING_AGG(DISTINCT REPLACE(kl.order_value, ',', ''), ', ') AS order_value,
				STRING_AGG(DISTINCT kl.client, ', ') AS client_name,								   
                MAX(kl.sequence_ref) as sequence_ref,
                'Project Budget' as budget_type,								   
                SUM(kl.apr_budget) AS april_budget,
                SUM(kl.may_budget) AS may_budget,
                SUM(kl.jun_budget) AS june_budget,
                SUM(kl.jul_budget) AS july_budget,
                SUM(kl.aug_budget) AS august_budget,
                SUM(kl.sep_budget) AS september_budget,
                SUM(kl.oct_budget) AS october_budget,
                SUM(kl.nov_budget) AS november_budget,
                SUM(kl.dec_budget) AS december_budget,
                SUM(kl.jan_budget) AS january_budget,
                SUM(kl.feb_budget) AS february_budget,
                SUM(kl.mar_budget) AS march_budget,
                SUM(kl.apr_budget + kl.may_budget + kl.jun_budget + kl.jul_budget + kl.aug_budget + kl.sep_budget + kl.oct_budget + kl.nov_budget + kl.dec_budget + kl.jan_budget + kl.feb_budget + kl.mar_budget) AS total_budget,
				0 as total_balance
                from
            kw_sbu_project_budget_line kl
            left JOIN
                kw_sbu_project_budget ks ON kl.sbu_project_budget_id = ks.id
                where ks.state ='validate'
            GROUP BY
                kl.account_code_id,
                ks.fiscal_year_id,
                kl.project_id,
                ks.budget_department              			
	)
	SELECT
    fiscal_year_id,
	account_id,
   

	project_id,
    max(project_name) as project_name,
    MAX(sbu_name) as sbu_name,
	MAX(project_code) AS project_code,
    MAX(expense_type) AS expense_type,
	MAX(order_code) AS order_code,
	MAX(work_order_type) AS work_order_type,
	MAX(opp_name) AS opp_name,
	MAX(order_value) AS order_value,
	MAX(client_name) AS client_name,
    MAX(sequence_ref) as sequence_ref,
    MAX(budget_type) AS budget_type,
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
	SUM(march_budget) AS march_budget
	FROM  final_cte
	group by 
	final_cte.fiscal_year_id,
	final_cte.account_id,
	final_cte.project_id,
    final_cte.project_name
	)
select ROW_NUMBER() OVER(order by account_id desc,fiscal_year_id desc) AS id,
	(select group_type from account_account where id = final.account_id) as group_type_id,
        (select group_name from account_account where id = final.account_id) as group_id,
        (select user_type_id from account_account where id = final.account_id) as group_head_id,
       	(select account_head_id from account_account where id = final.account_id) as account_head_id,
        (select account_sub_head_id from account_account where id = final.account_id) as account_sub_head_id,
        (select code from account_account where id = final.account_id) as account_code,
		* 
		from final
		
                )""" % (self._table))

            # select row_number() over() as id,
            #     kl.account_code_id AS account_id,
            #     ac.group_type as group_type_id,
			# 	ac.group_name as group_id,
            #     ac.code as account_code,
			# 	ac.user_type_id as group_head_id,
			# 	ac.account_head_id as account_head_id,
            #     ac.account_sub_head_id as account_sub_head_id,
            #     ks.fiscal_year_id AS fiscal_year_id,
            #     kbm.sbu_id AS sbu_id,
            #     (SELECT name FROM kw_sbu_master WHERE id = kbm.sbu_id) AS sbu_name,
			# 	kl.order_id as project_id,
            #     kl.project_id as project_name_id,
            #     kl.project_code as project_code,
			# 	kl.order_code as order_code,
            #     kl.work_order_type as work_order_type,
            #     kl.opportunity_name as opp_name,
            #     kl.order_value as order_value,
            #     kl.client as client_name,
            #     kl.category_id as category_id,
            #     SUM(kl.apr_budget) AS april_budget,
            #     SUM(kl.may_budget) AS may_budget,
            #     SUM(kl.jun_budget) AS june_budget,
            #     SUM(kl.jul_budget) AS july_budget,
            #     SUM(kl.aug_budget) AS august_budget,
            #     SUM(kl.sep_budget) AS september_budget,
            #     SUM(kl.oct_budget) AS october_budget,
            #     SUM(kl.nov_budget) AS november_budget,
            #     SUM(kl.dec_budget) AS december_budget,
            #     SUM(kl.jan_budget) AS january_budget,
            #     SUM(kl.feb_budget) AS february_budget,
            #     SUM(kl.mar_budget) AS march_budget
			# 	from
            #  kw_sbu_project_budget_line kl
            # JOIN
            #     kw_sbu_project_budget ks ON kl.sbu_project_budget_id = ks.id
            # JOIN
            #     kw_sbu_project_mapping kbm ON ks.budget_department = kbm.id
            # JOIN account_account ac on ac.id = kl.account_code_id
            # GROUP BY
            #     kl.account_code_id,
            #     ks.fiscal_year_id,
			# 	kl.order_id,
			# 	kl.order_code,
            #     kl.project_id,
            #     kl.project_code,
            #     kl.work_order_type,
            #     kl.client,
            #     ac.code,
            #     kl.opportunity_name,
            #     kl.order_value,
            #     kl.category_id,
            #     kbm.sbu_id,
            #     ac.group_name,
			# 	ac.group_type,
			# 	ac.user_type_id,
			# 	ac.account_head_id,
            #     ac.account_sub_head_id