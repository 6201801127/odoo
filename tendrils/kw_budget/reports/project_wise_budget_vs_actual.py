from odoo import models, api, fields, tools

class ProjectWiseBudgetReport(models.Model):
    _name = "project_wise_budget_report"
    _description = "Project wise Treasury Report"
    _auto = False
    _order = "fiscal_year_id asc"

    # head_of_expense = fields.Char(string='Name of Expenses')
    budget_type =fields.Char(string='Budget Type')
    account_id = fields.Many2one('account.account', 'Account Name')
    account_name = fields.Char(related='account_id.name', string='Account Name')
    account_code = fields.Char(related='account_id.code',string='Account Code')
    group_type_id = fields.Many2one('kw.group.type',string='Group Type')
    group_head_id = fields.Many2one('account.account.type', string='Group Head')
    group_id = fields.Many2one('account.group.name',string= 'Group Name')
    account_head_id = fields.Many2one('account.head',string= 'Account Head')
    account_sub_head_id = fields.Many2one('account.sub.head', string='Account Sub Head')
    project_line =  fields.Many2one('kw_sbu_project_budget_line', string="Particulars")
    fiscal_year_id = fields.Many2one('account.fiscalyear', string="Fiscal Year")
    # sbu_id = fields.Many2one('kw_sbu_master', string="SBU Name")
    department_id = fields.Many2one('hr.department', string="Department")
    division_id = fields.Many2one('hr.department', string="Division")
    section_id = fields.Many2one('hr.department', string="Section")
    sbu_name = fields.Char(string="SBU Name")
    project_id = fields.Many2one('kw_project_budget_master_data', string="Project Name")
    project_name = fields.Char(string="Project Name")
    budget_department=fields.Many2one('kw_sbu_project_mapping', string="SBU ID")
    # sbu_name=fields.Many2one(related='budget_department.name', string="SBU Name")
    order_value = fields.Char(string="Order Value")
    client_name = fields.Char(string="Client Name")
    # order_code = fields.Char(string="Project Code")
    expense_type = fields.Char(string='Income/Exp.')
    sequence_ref = fields.Char(string="ID")
    project_code = fields.Char(string="Project Code")
    work_order_type = fields.Char(string="Work Order Type")
    opp_name = fields.Char(string="OPP Name")
    category_id =  fields.Many2one('kw_sbu_project_category_master', string='Category Name')
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
   

    @api.multi
    def _compute_actual_amount(self):
        for line in self:
            date_to = line.fiscal_year_id.date_stop
            date_from = line.fiscal_year_id.date_start
            aml_obj = self.env['account.move.line']
            domain = [('account_id', '=', line.account_id.id),
                    ('project_line', '=', line.project_line.id),
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
            if line.sudo().account_id.group_type.code == '3':
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
                        ('project_line', '=', line.project_line.id),
                        ('date', '>=', date_from),
                        ('date', '<=', date_to),
                        ('move_id.state', '=', 'posted')
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
                domain.extend([('project_wo_id', '=', False)])
            else:
                if line.project_id:
                    domain.append(('project_wo_id','=',line.project_id.id))
            where_query = aml_obj._where_calc(domain)
            aml_obj._apply_ir_rules(where_query, 'read')
            from_clause, where_clause, where_clause_params = where_query.get_sql()
            if line.sudo().account_id.group_type.code == '3':
                select = "SELECT sum(account_move_line.credit)-sum(account_move_line.debit) from" + from_clause + "left join account_move am on am.id = account_move_line.move_id and am.state = 'posted'"+"where" + where_clause
            else:
                select = "SELECT sum(account_move_line.debit)-sum(account_move_line.credit) from" + from_clause + "left join account_move am on am.id = account_move_line.move_id and am.state = 'posted'"+" where " + where_clause
            self.env.cr.execute(select, where_clause_params)
            line.actual_amount = self.env.cr.fetchone()[0] or 0.0
           

    def action_open_budget_entries(self):
        action = self.env['ir.actions.act_window'].for_xml_id('account', 'action_account_moves_all_a')
        domain = [('account_id', '=',
                             self.account_id.id),
                    ('project_line', '=', self.project_line.id),
                            ('date', '>=', self.fiscal_year_id.date_start),
                            ('date', '<=', self.fiscal_year_id.date_stop),
                            ('move_id.state', '=', 'posted'),
                    
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
                domain.extend([('project_wo_id', '=', False)])
        else:
            if self.project_id:
                domain.append(('project_wo_id','=',self.project_id.id))
        action['domain'] = domain
        return action


    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('report_action_project_budget'):
            data = self.env['kw_sbu_project_mapping'].sudo().search(['|',('level_2_approver','in',[self.env.user.employee_ids.id]),('level_1_approver','in',[self.env.user.employee_ids.id])])
            # print(data, '============>>>')
            if self.env.user.has_group('kw_budget.group_finance_kw_budget') or self.env.user.has_group('kw_budget.group_approver_kw_budget') or self.env.user.has_group('kw_budget.group_manager_kw_budget'):
                args += []
            elif self.env.user.has_group('kw_budget.group_manager_report'):
                args += []
            elif self.env.user.has_group('kw_budget.group_department_head_kw_budget'):
                args += [('budget_department', 'in', data.ids)]
        return super(ProjectWiseBudgetReport, self)._search(args, offset=offset, limit=limit, order=order, count=count,
                                                        access_rights_uid=access_rights_uid)


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
                aml.project_line,
                aml.department_id,
                aml.division_id,
                aml.section_id,
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
                b.project_line,
                (SELECT s.id AS budget_department FROM kw_project_budget_master_data pb LEFT JOIN kw_sbu_master s ON s.id = pb.sbu_id WHERE pb.id = b.project_id) as budget_department,
        		(SELECT name FROM kw_sbu_master WHERE id =(SELECT pb.sbu_id from kw_project_budget_master_data pb where
															pb.id = b.project_id)) AS sbu_name,
                b.department_id,
                b.division_id,
                b.section_id,
                (select wo_name from kw_project_budget_master_data where id = b.project_id) as project_name,					  
                (select wo_code from kw_project_budget_master_data where id = b.project_id) as project_code,
                (SELECT name FROM kw_group_type WHERE id = (SELECT group_type FROM account_account WHERE id = b.account_id)) AS expense_type,
                ''::char as order_code,
                ''::char as work_order_type,
                ''::char as opp_name,
                ''::char as order_value,
                ''::char as client_name,
                null::int as category_id,
                (SELECT sequence_ref FROM kw_sbu_project_budget_line WHERE id = (SELECT project_line FROM account_move_line WHERE id = b.project_line)) AS sequence_ref,
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
                    kl.id as project_line,
                    ks.budget_department,
                    (SELECT name FROM kw_sbu_master WHERE id = (SELECT sbu_id FROM kw_sbu_project_mapping WHERE id = ks.budget_department)) AS sbu_name,
                    (select id from hr_department where id =(SELECT department_id FROM hr_employee WHERE id =(select sbu.representative_id from kw_sbu_master sbu left join kw_sbu_project_mapping pb on
																	 pb.id=  ks.budget_department  where  sbu.id=pb.sbu_id)))as department_id,
					(select id from hr_department where id =(SELECT division FROM hr_employee WHERE id =(select sbu.representative_id from kw_sbu_master sbu left join kw_sbu_project_mapping pb on
																	 pb.id=  ks.budget_department  where  sbu.id=pb.sbu_id)))as division_id,
					(select id from hr_department where id =(SELECT section FROM hr_employee WHERE id =(select sbu.representative_id from kw_sbu_master sbu left join kw_sbu_project_mapping pb on
																	 pb.id=  ks.budget_department  where  sbu.id=pb.sbu_id)))as section_id,
                    (select wo_name from kw_project_budget_master_data where id = kl.project_id) as project_name,
                    STRING_AGG(DISTINCT kl.project_code, ', ') AS project_code,
                    STRING_AGG(DISTINCT kl.head_expense_type, ', ') AS expense_type,
                    STRING_AGG(DISTINCT kl.order_code, ', ') AS order_code,
                    STRING_AGG(DISTINCT kl.work_order_type, ', ') AS work_order_type,
                    STRING_AGG(DISTINCT kl.opportunity_name, ', ') AS opp_name,
                    STRING_AGG(DISTINCT REPLACE(kl.order_value, ',', ''), ', ') AS order_value,
                    STRING_AGG(DISTINCT kl.client, ', ') AS client_name,
                    max(kl.category_id) as category_id,
                    kl.sequence_ref as sequence_ref,
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
                    where ks.state ='validate' and kl.state ='validate'
                GROUP BY
                    kl.account_code_id,
                    ks.fiscal_year_id,
                    kl.project_id,
                    kl.id,
                    ks.budget_department              			
        )
                SELECT
              
                fiscal_year_id,
                account_id,
                project_id,
                project_line,
                MAX(budget_department) AS budget_department,
                COALESCE(MAX(sbu_name), 'NA') AS sbu_name,
                department_id,
				division_id,
	            section_id,
                project_name,
                MAX(project_code) AS project_code,
                MAX(expense_type) AS expense_type,
                MAX(order_code) AS order_code,
                MAX(work_order_type) AS work_order_type,
                MAX(opp_name) AS opp_name,
                MAX(order_value) AS order_value,
                MAX(client_name) AS client_name,
                max(category_id) as category_id,
                COALESCE(NULLIF(TRIM(MAX(sequence_ref)), ''), 'NA') AS sequence_ref,
                MAX(budget_type) as budget_type,
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
                final_cte.project_line,
                final_cte.project_name,
                final_cte.department_id,
                final_cte.division_id,
                final_cte.section_id)
            select ROW_NUMBER() OVER(order by account_id desc,fiscal_year_id desc,project_id desc) AS id,
                (select group_type from account_account where id = final.account_id) as group_type_id,
                    (select group_name from account_account where id = final.account_id) as group_id,
                    (select user_type_id from account_account where id = final.account_id) as group_head_id,
                    (select code from account_account where id = final.account_id) as account_code,
                    (select account_head_id from account_account where id = final.account_id) as account_head_id,
                    (select account_sub_head_id from account_account where id = final.account_id) as account_sub_head_id,
                    * 
                    from final
        )""" % (self._table))

