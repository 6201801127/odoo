from odoo import fields, models, _, api
from odoo import tools
from datetime import date, datetime, time
import calendar

class kw_employee_bonus_report(models.Model):
    _name = 'kw_employee_bonus_report'
    _description = 'Bonus Allocation Report'
    _auto = False

    employee_id = fields.Many2one('hr.employee')
    april = fields.Float(string="April")
    may = fields.Float(string="May")
    june = fields.Float(string="June")
    july = fields.Float(string="July")
    august = fields.Float(string="August")
    september = fields.Float(string="September")
    october = fields.Float(string="October")
    november = fields.Float(string="November")
    december = fields.Float(string="December")
    january = fields.Float(string="January")
    february = fields.Float(string="February")
    march = fields.Float(string="March")
    fy_id = fields.Many2one('account.fiscalyear')


#     @api.model_cr
#     def init(self):
#         date_from = self.env.context.get('date_from') if self.env.context.get('date_from') else date.today()
#         date_to = self.env.context.get('date_to') if self.env.context.get('date_to') else date.today()
#         tools.drop_view_if_exists(self.env.cr, self._table)
#         self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
# with a as 
# (
# select p.employee_id,EXTRACT(MONTH FROM p.date_to) AS month,pl.amount as basic,
# case 
# when (select amount from hr_payslip_line where code = 'HRAMN' and slip_id = p.id ) > 0 then 1
# else 0 
# end as consolidated
# from hr_payslip p join hr_payslip_line pl on p.id = pl.slip_id
# where pl.code = 'BASIC' and p.date_from > '{date_from}' and p.date_to < '{date_to}' 
# 	and p.state = 'done'
# )
# SELECT 
#      row_number() over(order by employee_id asc) as id,
#     employee_id,
#     MAX(CASE WHEN month = 4 THEN basic ELSE NULL END) AS April,
#     MAX(CASE WHEN month = 5 THEN basic ELSE NULL END) AS May,
#     MAX(CASE WHEN month = 6 THEN basic ELSE NULL END) AS June,
#     MAX(CASE WHEN month = 7 THEN basic ELSE NULL END) AS July,
#     MAX(CASE WHEN month = 8 THEN basic ELSE NULL END) AS August,
#     MAX(CASE WHEN month = 9 THEN basic ELSE NULL END) AS September,
#     MAX(CASE WHEN month = 10 THEN basic ELSE NULL END) AS October,
#     MAX(CASE WHEN month = 11 THEN basic ELSE NULL END) AS November,
#     MAX(CASE WHEN month = 12 THEN basic ELSE NULL END) AS December,
# MAX(CASE WHEN month = 1 THEN basic ELSE NULL END) AS January,
#     MAX(CASE WHEN month = 2 THEN basic ELSE NULL END) AS February,
#     MAX(CASE WHEN month = 3 THEN basic ELSE NULL END) AS March
# FROM 
#     a where consolidated = 1
# GROUP BY
#     employee_id
#             )""" % (self._table))
        




    @api.model_cr
    def fetch_bonus_report(self):
        date_from = self.env.context.get('date_from') if self.env.context.get('date_from') else date.today()
        date_to = self.env.context.get('date_to') if self.env.context.get('date_to') else date.today()
        employee_id_from = self.env.context.get('employee_id_from') if self.env.context.get('employee_id_from') else 0
        employee_id_to = self.env.context.get('employee_id_to') if self.env.context.get('employee_id_to') else 0
        fy_id =  self.env.context.get('fy_id') if self.env.context.get('fy_id') else 1

        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
               WITH a AS (
    SELECT 
        p.employee_id,
        EXTRACT(MONTH FROM p.date_to) AS month,
        pl.amount AS basic,
        CASE 
            WHEN (SELECT amount FROM hr_payslip_line WHERE code = 'HRAMN' AND slip_id = p.id ) > 0 THEN 1 
            ELSE 0 
        END AS consolidated
    FROM 
        hr_payslip p 
    JOIN 
        hr_payslip_line pl ON p.id = pl.slip_id 
    WHERE 
        pl.code = 'BASIC' 
        AND p.date_from >= '{date_from}' 
        AND p.date_to <= '{date_to}' 
        AND p.state = 'done' 
        AND p.employee_id BETWEEN {employee_id_from} AND {employee_id_to}
)
SELECT
    (select {fy_id} ) as fy_id,
    employee_id,
    MAX(CASE WHEN month = 4 THEN basic ELSE NULL END) AS April,
    MAX(CASE WHEN month = 5 THEN basic ELSE NULL END) AS May,
    MAX(CASE WHEN month = 6 THEN basic ELSE NULL END) AS June,
    MAX(CASE WHEN month = 7 THEN basic ELSE NULL END) AS July,
    MAX(CASE WHEN month = 8 THEN basic ELSE NULL END) AS August,
    MAX(CASE WHEN month = 9 THEN basic ELSE NULL END) AS September,
    MAX(CASE WHEN month = 10 THEN basic ELSE NULL END) AS October,
    MAX(CASE WHEN month = 11 THEN basic ELSE NULL END) AS November,
    MAX(CASE WHEN month = 12 THEN basic ELSE NULL END) AS December,
    MAX(CASE WHEN month = 1 THEN basic ELSE NULL END) AS January,
    MAX(CASE WHEN month = 2 THEN basic ELSE NULL END) AS February,
    MAX(CASE WHEN month = 3 THEN basic ELSE NULL END) AS March
FROM 
    a 
WHERE 
    consolidated = 1 
GROUP BY 
    employee_id
)""" % (self._table))

        self.env.cr.execute("SELECT * FROM %s" % (self._table,))
        results = self.env.cr.dictfetchall()

        return results
    


class BonusFYFilter(models.TransientModel):
    _name = 'bonus_fy_filter'
    
    def _default_financial_yr(self):
            current_fiscal = self.env['account.fiscalyear'].search(
                [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
            return current_fiscal
    fy_id = fields.Many2one('account.fiscalyear',default=_default_financial_yr,required=True)

    @api.model
    def _get_year_list(self):
        current_year = date.today().year
        return [(str(i), i) for i in range(current_year, 1998, -1)]

    year = fields.Selection(string='Year', selection='_get_year_list', default=str(date.today().year))
    company_id = fields.Many2one('res.company')
    month = fields.Selection([(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'),(6, 'June'), (7, 'July'), (8, 'August'), (9, 'September'),(10, 'October'), (11, 'November'), (12, 'December')])
    grade_ids = fields.Many2many('kwemp_grade_master',string='Grades')
    budget_type = fields.Selection([('treasury','Treasury'),('project','Project')],string="Budget Type")


    
    def action_fetch_basic(self):
        if self.fy_id:
            domain = []
            domain.append(('fy_id', '=', self.fy_id.id))

            view_id = self.env.ref('payroll_integration.kw_employee_bonus_physical_report_view_tree').id
            return {
                'name':'Bonus Report',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree',
                'views': [(view_id, 'tree')],
                'res_model': 'employee_bonus_report_physical',
                'view_id': view_id,
                'target': 'current',
                'domain': domain,
            }
        
    def action_fetch_ctc(self):
        if self.fy_id:
            self.env['payroll_level_wise_report'].with_context(date_stop=self.fy_id.date_stop,date_start= self.fy_id.date_start,company_id=self.company_id.id).init()
            view_id = self.env.ref('payroll_integration.payroll_level_wise_report_view_tree').id
            return {
                'name':f'Report for FY- {self.fy_id.name}',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree',
                'views': [(view_id, 'tree')],
                'res_model': 'payroll_level_wise_report',
                'view_id': view_id,
                'target': 'current',
            }
        
    def action_fetch_ctc2(self):
        if self.fy_id:
            self.env['category_role_level_wise_report'].with_context(date_stop=self.fy_id.date_stop,date_start= self.fy_id.date_start,company_id=self.company_id.id).init()
            view_id = self.env.ref('payroll_integration.category_role_level_wise_report_view_tree').id
            return {
                'name':f'Report for FY- {self.fy_id.name}',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree',
                'views': [(view_id, 'tree')],
                'res_model': 'category_role_level_wise_report',
                'view_id': view_id,
                'target': 'current',
            }
    def action_fetch_ctc_role(self):
        if self.fy_id:
            self.env['payroll_role_wise_report'].with_context(date_stop=self.fy_id.date_stop,date_start= self.fy_id.date_start,company_id=self.company_id.id).init()
            view_id = self.env.ref('payroll_integration.payroll_role_wise_report_view_tree').id
            return {
                'name':f'Report for FY- {self.fy_id.name}',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree',
                'views': [(view_id, 'tree')],
                'res_model': 'payroll_role_wise_report',
                'view_id': view_id,
                'target': 'current',
            }
        
    def action_get_ctc(self):
        if self.fy_id:
            self.env['payroll_customised_report'].with_context(year=self.year,month=self.month,grade_ids=tuple(self.grade_ids.ids),budget_type=self.budget_type).init()
            view_id = self.env.ref('payroll_integration.payroll_customised_report_view_tree').id
            return {
                'name':f'Report for FY- {self.year}',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree',
                'views': [(view_id, 'tree')],
                'res_model': 'payroll_customised_report',
                'view_id': view_id,
                'target': 'current',
            }

class LevelWiseReport(models.Model):
    _name = 'payroll_level_wise_report'
    _auto = False
    
    MONTH_LIST = [
        ('1', 'January'), ('2', 'February'),
        ('3', 'March'), ('4', 'April'),
        ('5', 'May'), ('6', 'June'),
        ('7', 'July'), ('8', 'August'),
        ('9', 'September'), ('10', 'October'),
        ('11', 'November'), ('12', 'December')
    ]
    department_id = fields.Many2one('hr.department')
    level = fields.Many2one('kw_grade_level')
    ctc = fields.Float()
    emp_count =  fields.Integer()
    date_to = fields.Date()
    year = fields.Char(string='Year',size=4)
    month = fields.Selection(MONTH_LIST, string='Month')
    join_in_same_month_year =  fields.Integer()
    left_in_same_month_year =  fields.Integer()
    emp_role= fields.Many2one('kwmaster_role_name',string="Employee Role")
    emp_category= fields.Many2one('kwmaster_category_name',string="Employee Category")
    
    @api.model_cr
    def init(self):
        date_stop = self.env.context.get('date_stop') if self.env.context.get('date_stop') else date((date.today().year)+1,3,31)
        date_start = self.env.context.get('date_start') if self.env.context.get('date_start') else date((date.today().year),4,1)        
        company_id = self.env.context.get('company_id') if self.env.context.get('company_id') else 1
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
        select row_number() over() as id,
        sum(l.amount) as ctc,count(h.id) as emp_count,e.department_id,e.level,h.date_to,e.emp_category AS emp_category,e.emp_role AS emp_role,
        CAST(MAX(date_part('year', h.date_to)) AS VARCHAR(10)) AS year,
        CAST(MAX(date_part('month', h.date_to)) AS VARCHAR(10)) AS month,
        SUM(CASE 
        WHEN EXTRACT(MONTH FROM e.date_of_joining) = EXTRACT(MONTH FROM h.date_to)
             AND EXTRACT(YEAR FROM e.date_of_joining) = EXTRACT(YEAR FROM h.date_to)
        THEN 1
        ELSE 0
        END) AS join_in_same_month_year,
        SUM(CASE 
            WHEN EXTRACT(MONTH FROM e.last_working_day) = EXTRACT(MONTH FROM h.date_to)
                AND EXTRACT(YEAR FROM e.last_working_day) = EXTRACT(YEAR FROM h.date_to)
            THEN 1
            ELSE 0
        END) AS left_in_same_month_year
        from hr_payslip_line l
        join hr_payslip h on h.id=l.slip_id
        join hr_employee e on e.id = h.employee_id
        JOIN account_fiscalyear fy ON h.date_to BETWEEN fy.date_start AND fy.date_stop AND fy.date_start = '{date_start}' AND fy.date_stop = '{date_stop}'
        where l.code = 'CTC' and h.state='done' and e.company_id = {company_id}
        group by e.department_id,e.level,h.date_to,e.emp_category,e.emp_role
		)""" % (self._table))


class CategoryRoleLevelWiseReport(models.Model):
    _name = 'category_role_level_wise_report'
    _auto = False
    
    MONTH_LIST = [
        ('1', 'January'), ('2', 'February'),
        ('3', 'March'), ('4', 'April'),
        ('5', 'May'), ('6', 'June'),
        ('7', 'July'), ('8', 'August'),
        ('9', 'September'), ('10', 'October'),
        ('11', 'November'), ('12', 'December')
    ]
    department_id = fields.Many2one('hr.department')
    level = fields.Many2one('kw_grade_level')
    ctc = fields.Float()
    emp_count =  fields.Integer()
    date_to = fields.Date()
    year = fields.Char(string='Year',size=4)
    month = fields.Selection(MONTH_LIST, string='Month')
    join_in_same_month_year =  fields.Integer()
    left_in_same_month_year =  fields.Integer()
    # emp_role= fields.Many2one('kwmaster_role_name',string="Employee Role")
    # emp_category= fields.Many2one('kwmaster_category_name',string="Employee Category")
    
    @api.model_cr
    def init(self):
        date_stop = self.env.context.get('date_stop') if self.env.context.get('date_stop') else date((date.today().year)+1,3,31)
        date_start = self.env.context.get('date_start') if self.env.context.get('date_start') else date((date.today().year),4,1)        
        company_id = self.env.context.get('company_id') if self.env.context.get('company_id') else 1
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
        select row_number() over() as id,
        sum(l.amount) as ctc,count(h.id) as emp_count,e.department_id,e.level,h.date_to,
        CAST(MAX(date_part('year', h.date_to)) AS VARCHAR(10)) AS year,
        CAST(MAX(date_part('month', h.date_to)) AS VARCHAR(10)) AS month,
        SUM(CASE 
        WHEN EXTRACT(MONTH FROM e.date_of_joining) = EXTRACT(MONTH FROM h.date_to)
             AND EXTRACT(YEAR FROM e.date_of_joining) = EXTRACT(YEAR FROM h.date_to)
        THEN 1
        ELSE 0
        END) AS join_in_same_month_year,
        SUM(CASE 
            WHEN EXTRACT(MONTH FROM e.last_working_day) = EXTRACT(MONTH FROM h.date_to)
                AND EXTRACT(YEAR FROM e.last_working_day) = EXTRACT(YEAR FROM h.date_to)
            THEN 1
            ELSE 0
        END) AS left_in_same_month_year
        from hr_payslip_line l
        join hr_payslip h on h.id=l.slip_id
        join hr_employee e on e.id = h.employee_id
        JOIN account_fiscalyear fy ON h.date_to BETWEEN fy.date_start AND fy.date_stop AND fy.date_start = '{date_start}' AND fy.date_stop = '{date_stop}'
        where l.code = 'CTC' and h.state='done' and e.company_id = {company_id}
        group by e.department_id,e.level,h.date_to
		)""" % (self._table))
        
class RoleDeptWiseReport(models.Model):
    _name = 'payroll_role_wise_report'
    _auto = False
    
    MONTH_LIST = [
        ('1', 'January'), ('2', 'February'),
        ('3', 'March'), ('4', 'April'),
        ('5', 'May'), ('6', 'June'),
        ('7', 'July'), ('8', 'August'),
        ('9', 'September'), ('10', 'October'),
        ('11', 'November'), ('12', 'December')
    ]
    department_id = fields.Many2one('hr.department')
    emp_role = fields.Many2one('kwmaster_role_name')
    ctc = fields.Float()
    date_to = fields.Date()
    year = fields.Char(string='Year',size=4)
    month = fields.Selection(MONTH_LIST, string='Month')
    # emp_count =  fields.Integer()
    
    @api.model_cr
    def init(self):
        date_stop = self.env.context.get('date_stop') if self.env.context.get('date_stop') else date((date.today().year)+1,3,31)
        date_start = self.env.context.get('date_start') if self.env.context.get('date_start') else date((date.today().year),4,1)        
        company_id = self.env.context.get('company_id') if self.env.context.get('company_id') else 1
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
        select row_number() over() as id,
        sum(l.amount) as ctc,count(h.id) as emp_count,e.department_id,e.emp_role,h.date_to,
        CAST(MAX(date_part('year', h.date_to)) AS VARCHAR(10)) AS year,
        CAST(MAX(date_part('month', h.date_to)) AS VARCHAR(10)) AS month
        from hr_payslip_line l
        join hr_payslip h on h.id=l.slip_id
        join hr_employee e on e.id = h.employee_id
        JOIN account_fiscalyear fy ON h.date_to BETWEEN fy.date_start AND fy.date_stop AND fy.date_start = '{date_start}' AND fy.date_stop = '{date_stop}'
        where l.code = 'CTC' and h.state='done' and e.company_id = {company_id} and e.emp_role in (4,1)
        group by e.emp_role,e.department_id,h.date_to
		)""" % (self._table))
class BonusReportSync(models.TransientModel):
    _name = 'bonus_report_sync'
    
    def _default_financial_yr(self):
        current_fiscal = self.env['account.fiscalyear'].search([('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
        return current_fiscal
    
    fy_id = fields.Many2one('account.fiscalyear',default=_default_financial_yr,required=True)
    employee_id_from = fields.Integer('From Employee ID',required=True)
    employee_id_to = fields.Integer('To Employee ID',required=True)

    
    def action_create_record(self):
        if self.fy_id:
            physical_ids = self.env['employee_bonus_report_physical'].sudo().search([]).mapped('employee_id.id')
            results = self.env['kw_employee_bonus_report'].with_context(date_from = self.fy_id.date_start,date_to = self.fy_id.date_stop,employee_id_from=self.employee_id_from,employee_id_to=self.employee_id_to,fy_id=self.fy_id.id).fetch_bonus_report()
            query = "INSERT INTO employee_bonus_report_physical(employee_id, april,may, june, july, august, september, october, november, december,january,february,march,fy_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
            params = []
            
            if results:
                for rec in results:
                    if rec['employee_id'] not in physical_ids:
                        params.append((rec['employee_id'], rec['april'], rec['may'], rec['june'], rec['july'], rec['august'], rec['september'], rec['october'], rec['november'], rec['december'], rec['january'], rec['february'], rec['march'], rec['fy_id']))
            if params:
                self.env.cr.executemany(query, params)
                self.env.user.notify_success("Records Created Successfully.")

        

    def action_delete_record(self):
        if self.fy_id:
            employee_id_from = self.employee_id_from if self.employee_id_from else 0
            employee_id_to = self.employee_id_to if self.employee_id_to else 0
            fy_date_start = self.fy_id.id
            query = """DELETE FROM employee_bonus_report_physical WHERE employee_id >= %s  and employee_id <= %s AND fy_id = %s"""
            self.env.cr.execute(query,(employee_id_from,employee_id_to,fy_date_start))
            self.env.user.notify_danger("Records Deleted Successfully.")

class CustomisedReport(models.Model):
    _name = 'payroll_customised_report'
    _auto = False
    
    MONTH_LIST = [
        ('1', 'January'), ('2', 'February'),
        ('3', 'March'), ('4', 'April'),
        ('5', 'May'), ('6', 'June'),
        ('7', 'July'), ('8', 'August'),
        ('9', 'September'), ('10', 'October'),
        ('11', 'November'), ('12', 'December')
    ]
    ctc = fields.Float()
    net= fields.Float()
    date_to = fields.Date()
    year = fields.Char(string='Year',size=4)
    month = fields.Selection(MONTH_LIST, string='Month')
    grade_id = fields.Many2one('kwemp_grade_master',string='Grades')
    budget_type = fields.Selection([('treasury','Treasury'),('project','Project')],string="Budget Type")
    emp_count =  fields.Integer(compute='compute_count')

    # @api.depends('date_to')
    # def compute_count(self):
    #     for rec in self:
    #         payslip =  self.env['hr.payslip'].search([('date_to','=',rec.date_to)]).mapped('employee_id')
    #         employee = payslip.filtered(lambda x:x.grade.id == rec.grade_id.id and x.budget_type == rec.budget_type)
    #         rec.emp_count= len(employee)
            
            
    @api.depends('date_to')
    def compute_count(self):
        for rec in self:
            query = """
                SELECT COUNT(DISTINCT e.id) 
                FROM hr_payslip h
                JOIN hr_employee e ON e.id = h.employee_id
                WHERE h.date_to = %s 
                AND e.grade = %s 
                AND e.budget_type = %s
                AND h.state = 'done'
            """
            # Execute the query with parameters
            self.env.cr.execute(query, (rec.date_to, rec.grade_id.id, rec.budget_type))
            result = self.env.cr.fetchone()

            # Set the employee count from the query result
            rec.emp_count = result[0] if result else 0


    @api.model_cr
    def init(self):
        year = self.env.context.get('year', date.today().year)
        month = self.env.context.get('month', date.today().month)
        grade_ids = self.env.context.get('grade_ids', [])
        
        # Handle single or multiple grade_ids correctly
        if len(grade_ids) ==  1 :
            single_element_tuple = (grade_ids[0],)
            grade = str(single_element_tuple).replace(",", "")        
        else:
            grade = tuple(grade_ids)
        if not grade:
            grade = (1,2)
        
        # Default to (1, 2) if no grade_ids are provided
        if not grade_ids:
            grade = (14, 15)
        
        
        budget_type = self.env.context.get('budget_type', 'project')

        tools.drop_view_if_exists(self.env.cr, self._table)
        
        # Create the SQL query, using the correctly formatted tuple for grade
        query = f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                SELECT 
                    row_number() OVER() AS id,
                    sum(l.amount) filter (WHERE l.code = 'CTC') as ctc,
                    sum(l.amount) filter (WHERE l.code = 'NET') as net,
                    h.date_to,
                    CAST(EXTRACT(YEAR FROM h.date_to) AS VARCHAR(10)) AS year,
                    CAST(EXTRACT(MONTH FROM h.date_to) AS VARCHAR(2)) AS month,
                    '{budget_type}' AS budget_type,
                    e.grade as grade_id
                FROM 
                    hr_payslip_line l
                JOIN 
                    hr_payslip h ON h.id = l.slip_id
                JOIN 
                    hr_employee e ON e.id = h.employee_id
                WHERE 
                    h.state = 'done'
                    AND e.budget_type = '{budget_type}'
                    AND EXTRACT(MONTH FROM h.date_to) = {month}
                    AND EXTRACT(YEAR FROM h.date_to) = {year}
                    AND e.grade IN {grade}
                GROUP BY 
                    e.grade, h.date_to
            )
        """
        
        # Execute the SQL query
        self.env.cr.execute(query)
