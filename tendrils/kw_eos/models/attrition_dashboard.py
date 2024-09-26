from odoo import models, fields, api
from datetime import date, datetime,timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError

def _get_period_key(date, period):
    if period == 'monthly':
        return date.strftime('%b %Y')
    elif period == 'quarterly':
        quarter = (date.month - 1) // 3 + 1
        return f'Q{quarter} {date.year}'
    elif period == 'yearly':
        return str(date.year)
        
class AttritionDashboard(models.Model):
    _name = 'kw_attrition_dashboard'
    _description = 'Attrition Dashboard'

    employee_count = fields.Integer(string='Employee Count')
    employee_count_as_of_april = fields.Integer()
    attrition_count = fields.Integer(string='Attrition Count')
    active_employee_count = fields.Integer(string='Active Employee Count')
    attrition_rate = fields.Float(string='Attrition Rate')
    average_tenure = fields.Char(string='Average Tenure')
    attrition_by_job_role = fields.Float()
    attrition_by_gender = fields.Float()
    department_attrition = fields.Float()
    top_resignation_reasons = fields.Float()
    attrition_by_tenure = fields.Float()
    joiners_by_department = fields.Float(string='Joiners by Department')
    resignees_by_department = fields.Float(string='Resignees by Department')
    voluntary_involuntary_attrition = fields.Float(string='Voluntary and Involuntary Attrition')
    fy_wise_joining_exit = fields.Float(string='FY Wise Joining and Exit')

    def _get_period_key(self, date_obj, period='monthly'):
        if period == 'monthly':
            return date_obj.strftime('%b %Y')
        elif period == 'quarterly':
            fiscal_quarter_map = {
                1: 'Q4',  # Jan-Mar
                2: 'Q4',
                3: 'Q4',
                4: 'Q1',  # Apr-Jun
                5: 'Q1',
                6: 'Q1',
                7: 'Q2',  # Jul-Sep
                8: 'Q2',
                9: 'Q2',
                10: 'Q3',  # Oct-Dec
                11: 'Q3',
                12: 'Q3'
            }
            quarter = fiscal_quarter_map[date_obj.month]
            if quarter == 'Q4':
                return f'{quarter} {date_obj.year + 1}'
            else:
                return f'{quarter} {date_obj.year}'
        elif period == 'yearly':
            return str(date_obj.year)
        
    @api.model
    def get_dashboard_data(self):
        # self.env['hr.employee'].compute_tenure_months()
        employee_count = self.env['hr.employee'].search_count(['|', ('active', '=', False), ('active', '=', True)])
        attrition_count_main = self.env['hr.employee'].search_count([('active', '=', False)])
        active_employee_count = self.env['hr.employee'].search_count([('active', '=', True)])
        
        attrition_rate = round((attrition_count_main / employee_count) * 100, 3) if employee_count else 0

        # Calculate attrition by tenure and average tenure
        employee_data = self.env['hr.employee'].search([('active', '=', False)])
        tenure_counts = [0, 0, 0, 0, 0, 0]  # 0-3, 3-6, 6-12, 12-24, 24-36, 36+
        total_attrition_count = 0
        total_tenure_months = 0

        for employee in employee_data:
            tenure_months = employee.tenure_months
            if tenure_months:
                if tenure_months <= 3:
                    tenure_counts[0] += 1
                elif tenure_months <= 6:
                    tenure_counts[1] += 1
                elif tenure_months <= 12:
                    tenure_counts[2] += 1
                elif tenure_months <= 24:
                    tenure_counts[3] += 1
                elif tenure_months <= 36:
                    tenure_counts[4] += 1
                else:
                    tenure_counts[5] += 1
                
                total_attrition_count += 1
                total_tenure_months += tenure_months

        attrition_by_tenure = [(count / total_attrition_count) * 100 for count in tenure_counts] if total_attrition_count > 0 else [0] * 7
        average_tenure_months = total_tenure_months / total_attrition_count if total_attrition_count else 0
        average_tenure_years = int(average_tenure_months // 12)
        average_tenure_remaining_months = int(average_tenure_months % 12)
        average_tenure = f"{average_tenure_years}.{average_tenure_remaining_months} Yrs"

        # Other calculations
        male_count = self.env['hr.employee'].search_count([('gender', '=', 'male'), ('active', '=', False)])
        female_count = self.env['hr.employee'].search_count([('gender', '=', 'female'), ('active', '=', False)])
        total_attrition = male_count + female_count

        if total_attrition:
            male_percentage = round((male_count / total_attrition) * 100, 3)
            female_percentage = round((female_count / total_attrition) * 100, 3)
            attrition_by_gender = [
                {'name': 'Male', 'y': male_percentage},
                {'name': 'Female', 'y': female_percentage},
            ]
        else:
            attrition_by_gender = [
                {'name': 'Male', 'y': 0},
                {'name': 'Female', 'y': 0},
            ]
        
        attrition_by_job_role = []
        jobs = self.env['hr.job'].search([])
        reasons = self.env['kw_resignation_master'].search([])

        for job in jobs:
            total_count = self.env['hr.employee'].search_count([('job_id', '=', job.id)])
            attrition_count = self.env['hr.employee'].search_count([('job_id', '=', job.id), ('active', '=', False)])
            
            if total_count > 0:  # To avoid division by zero
                attrition_percentage = (attrition_count / total_count) * 100
            else:
                attrition_percentage = 0
            
            if attrition_count > 0:  # Only add job roles with attrition
                attrition_by_job_role.append({
                    'name': job.name,
                    'y': round(attrition_percentage, 3)  # rounding to 3 decimal places
                })

        # Fetch and format department attrition data
        department_attrition = []
        departments = self.env['hr.department'].search([])

        for department in departments:
            total_count = self.env['hr.employee'].search_count([('department_id', '=', department.id)])
            attrition_count = self.env['hr.employee'].search_count([('department_id', '=', department.id), ('active', '=', False)])
            
            if attrition_count > 0:  # Only add departments with attrition
                department_attrition.append({
                    'department': department.name,
                    'total_count': total_count,
                    'attrition_count': attrition_count,
                    'department_id': department.id
                })

        # Fetch and format job role attrition data
        top_resignation_reasons = []
        for reason in reasons:
            total_count = self.env['hr.employee'].search_count([('resignation_reason', '=', reason.id)])
            attrition_count = self.env['hr.employee'].search_count([('resignation_reason', '=', reason.id), ('active', '=', False)])
            top_resignation_reasons.append({
                'job_role': reason.name,
                'total_count': total_count,
                'attrition_count': attrition_count
            })

     
        # Voluntary and Involuntary Attrition Calculation
        # Count voluntary attrition
        voluntary_count = self.env['hr.employee'].search_count([
            ('active', '=', False), 
            ('attrition_type', '=', 'voluntary')
        ])

        # Count involuntary attrition for each reason
        involuntary_reasons = ['contract_closure', 'demise', 'retirement', 'performance_issue', 'termination']
        involuntary_counts = {reason: self.env['hr.employee'].search_count([
            ('active', '=', False), 
            ('attrition_type', '=', 'involuntary'), 
            ('involuntary_reason', '=', reason)
        ]) for reason in involuntary_reasons}

        involuntary_total = sum(involuntary_counts.values())
        voluntary_involuntary_attrition = {
            'voluntary': voluntary_count,
            'involuntary': involuntary_total,
            'involuntary_details': involuntary_counts
        }
        fy_wise_joining_exit = self._get_fy_wise_joining_exit_data()
        data = {
            'employee_count': employee_count,
            'attrition_count': attrition_count_main,
            'attrition_rate': attrition_rate,
            'average_tenure': average_tenure,  # Use the calculated average tenure
            'attrition_by_job_role': attrition_by_job_role,
            'attrition_by_gender': attrition_by_gender,
            'department_attrition': department_attrition,
            'top_resignation_reasons': top_resignation_reasons,
            'attrition_by_tenure': attrition_by_tenure,
            'voluntary_involuntary_attrition': voluntary_involuntary_attrition,
            'fy_wise_joining_exit': fy_wise_joining_exit,  # Add the new data here
        }
        return data

    def _get_fy_wise_joining_exit_data(self):
        query = """
        SELECT
            row_number() OVER () AS id,
            d.name AS department_name,
            d.id as department_id,
            COUNT(CASE WHEN e.date_of_joining >= '2022-04-01' AND e.date_of_joining <= '2023-03-31' AND e.employement_type NOT IN (SELECT id FROM kwemp_employment_type WHERE code IN ('O')) AND e.company_id = 1 THEN 1 END) AS fy_22_23_joining,
            COUNT(CASE WHEN e.last_working_day >= '2022-04-01' AND e.last_working_day <= '2023-03-31' AND e.employement_type NOT IN (SELECT id FROM kwemp_employment_type WHERE code IN ('O')) AND e.company_id = 1 THEN 1 END) AS fy_22_23_exit,
            COUNT(CASE WHEN e.date_of_joining >= '2023-04-01' AND e.date_of_joining <= '2024-03-31' AND e.employement_type NOT IN (SELECT id FROM kwemp_employment_type WHERE code IN ('O')) AND e.company_id = 1 THEN 1 END) AS fy_23_24_joining,
            COUNT(CASE WHEN e.last_working_day >= '2023-04-01' AND e.last_working_day <= '2024-03-31' AND e.employement_type NOT IN (SELECT id FROM kwemp_employment_type WHERE code IN ('O')) AND e.company_id = 1 THEN 1 END) AS fy_23_24_exit,
            COUNT(CASE WHEN e.date_of_joining >= '2024-04-01' AND e.date_of_joining <= '2025-03-31' AND e.employement_type NOT IN (SELECT id FROM kwemp_employment_type WHERE code IN ('O')) AND e.company_id = 1 THEN 1 END) AS fy_24_25_joining,
            COUNT(CASE WHEN e.last_working_day >= '2024-04-01' AND e.last_working_day <= '2025-03-31' AND e.employement_type NOT IN (SELECT id FROM kwemp_employment_type WHERE code IN ('O')) AND e.company_id = 1 THEN 1 END) AS fy_24_25_exit
        FROM
            hr_department d
        LEFT JOIN
            hr_employee e ON e.department_id = d.id
        LEFT JOIN
            kw_hr_department_type dt ON d.dept_type = dt.id
        WHERE
            dt.code = 'department' AND d.active = true
        GROUP BY
            d.id, d.name
        ORDER BY
            d.name ASC;

        """
        self.env.cr.execute(query)
        result = self.env.cr.dictfetchall()
        return result

    def _get_current_fiscal_quarter_dates(self):
        current_date = date.today()
        year = current_date.year
        if current_date.month < 4:
            fiscal_year_start = date(year - 1, 4, 1)
        else:
            fiscal_year_start = date(year, 4, 1)

        quarter_dates = {
            'Q1': (fiscal_year_start, fiscal_year_start + relativedelta(months=3) - timedelta(days=1)),
            'Q2': (fiscal_year_start + relativedelta(months=3), fiscal_year_start + relativedelta(months=6) - timedelta(days=1)),
            'Q3': (fiscal_year_start + relativedelta(months=6), fiscal_year_start + relativedelta(months=9) - timedelta(days=1)),
            'Q4': (fiscal_year_start + relativedelta(months=9), fiscal_year_start + relativedelta(months=12) - timedelta(days=1))
        }

        for quarter, dates in quarter_dates.items():
            if dates[0] <= current_date <= dates[1]:
                return dates

        return None

    def _is_date_within_current_fiscal_year(self, start_date, end_date):
        current_date = date.today()
        year = current_date.year
        if current_date.month < 4:
            fiscal_year_start = date(year - 1, 4, 1)
            fiscal_year_end = date(year, 3, 31)
        else:
            fiscal_year_start = date(year, 4, 1)
            fiscal_year_end = date(year + 1, 3, 31)

        return fiscal_year_start <= start_date <= fiscal_year_end and fiscal_year_start <= end_date <= fiscal_year_end

    def _get_joiners_by_department_data(self, start_date, end_date, period='quarterly'):
        if self._is_date_within_current_fiscal_year(start_date, end_date):
            start_date, end_date = self._get_current_fiscal_quarter_dates()

        joiners_data = []
        departments = self.env['hr.department'].search([])

        for department in departments:
            department_data = {}
            joiners = self.env['hr.employee'].search([
                ('department_id', '=', department.id),
                ('active', '=', True),
                ('date_of_joining', '>=', start_date),
                ('date_of_joining', '<=', end_date),
                ('employement_type.code', '!=', 'O'),
                ('company_id','=',1)
            ])

            for joiner in joiners:
                period_key = self._get_period_key(joiner.date_of_joining, period)
                if period_key not in department_data:
                    department_data[period_key] = 0
                department_data[period_key] += 1

            for key, count in department_data.items():
                joiners_data.append({
                    'department': department.name,
                    'period': key,
                    'count': count
                })

        return joiners_data

    def _get_resignees_by_department_data(self, start_date, end_date, period='quarterly'):
        if self._is_date_within_current_fiscal_year(start_date, end_date):
            start_date, end_date = self._get_current_fiscal_quarter_dates()

        resignees_data = []
        departments = self.env['hr.department'].search([])

        for department in departments:
            department_data = {}
            resignees = self.env['hr.employee'].search([
                ('department_id', '=', department.id),
                ('active', '=', False),
                ('last_working_day', '>=', start_date),
                ('last_working_day', '<=', end_date),
                ('employement_type.code', '!=', 'O'),
                ('company_id','=',1)
            ])

            for resignee in resignees:
                if resignee.last_working_day and isinstance(resignee.last_working_day, date):
                    period_key = self._get_period_key(resignee.last_working_day, period)
                    if period_key not in department_data:
                        department_data[period_key] = 0
                    department_data[period_key] += 1

            for key, count in department_data.items():
                resignees_data.append({
                    'department': department.name,
                    'period': key,
                    'count': count
                })

        return resignees_data


    @api.model
    def get_available_fiscal_years(self):
        employees = self.env['hr.employee'].search([('active', '=', False)])
        if not employees:
            return []
        min_date = min(emp.last_working_day for emp in employees if emp.last_working_day)
        max_date = max(emp.last_working_day for emp in employees if emp.last_working_day)
        if not min_date or not max_date:
            return []
        min_year = min_date.year
        max_year = max_date.year
        return [f"FY{year}" for year in range(min_year, max_year + 1)]
    
    @api.model
    def get_attrition_by_tenure_data(self, selected_year=None, selected_quarter=None):
        domain = [('active', '=', False)]
        start_date = None
        end_date = None
        
        if selected_year:
            fiscal_year = self.env['account.fiscalyear'].search([('name', '=', selected_year)], limit=1)
            if fiscal_year:
                domain += [('last_working_day', '>=', fiscal_year.date_start), ('last_working_day', '<=', fiscal_year.date_stop), ('employement_type.code', '!=', 'O'), ('company_id', '=', 1)]
                start_date = fiscal_year.date_start
                end_date = fiscal_year.date_stop
                if selected_quarter:
                    quarter_start_month = {
                        'Q1': 4,  # April
                        'Q2': 7,  # July
                        'Q3': 10, # October
                        'Q4': 1   # January of the next year
                    }
                    quarter_end_month = {
                        'Q1': 6,  # June
                        'Q2': 9,  # September
                        'Q3': 12, # December
                        'Q4': 3   # March
                    }
                    # Determine the correct year for the start and end dates of the quarter
                    if selected_quarter == 'Q4':
                        start_date = fiscal_year.date_stop.replace(month=quarter_start_month[selected_quarter], day=1)
                        end_date = fiscal_year.date_stop.replace(month=quarter_end_month[selected_quarter], day=31)
                    else:
                        start_date = fiscal_year.date_start.replace(month=quarter_start_month[selected_quarter], day=1)
                        end_date = fiscal_year.date_start.replace(month=quarter_end_month[selected_quarter], day=30)
                    domain += [('last_working_day', '>=', start_date), ('last_working_day', '<=', end_date)]

        employee_data = self.env['hr.employee'].search(domain)
        tenure_data = {
            '0-3': [],
            '3-6': [],
            '6-12': [],
            '12-24': [],
            '24-36': [],
            '36+': []
        }
        tenure_counts = [0, 0, 0, 0, 0, 0]
        total_attrition_count = 0
        total_tenure_months = 0

        for employee in employee_data:
            tenure_months = employee.tenure_months
            if tenure_months is not None:
                if tenure_months <= 3:
                    tenure_counts[0] += 1
                    tenure_data['0-3'].append(employee.id)
                elif tenure_months <= 6:
                    tenure_counts[1] += 1
                    tenure_data['3-6'].append(employee.id)
                elif tenure_months <= 12:
                    tenure_counts[2] += 1
                    tenure_data['6-12'].append(employee.id)
                elif tenure_months <= 24:
                    tenure_counts[3] += 1
                    tenure_data['12-24'].append(employee.id)
                elif tenure_months <= 36:
                    tenure_counts[4] += 1
                    tenure_data['24-36'].append(employee.id)
                else:
                    tenure_counts[5] += 1
                    tenure_data['36+'].append(employee.id)

                total_attrition_count += 1
                total_tenure_months += tenure_months

        attrition_by_tenure = [(count / total_attrition_count) * 100 for count in tenure_counts] if total_attrition_count > 0 else [0] * 6
        average_tenure_months = total_tenure_months / total_attrition_count if total_attrition_count else 0
        average_tenure_years = int(average_tenure_months // 12)
        average_tenure_remaining_months = int(average_tenure_months % 12)
        average_tenure = f"{average_tenure_years}.{average_tenure_remaining_months} Yrs"
        return {
            'attrition_by_tenure': attrition_by_tenure,
            'tenure_data': tenure_data,
            'average_tenure': average_tenure,
        }

 
    @api.model
    def get_joinee_resignee_attrition_data(self, selected_year=None, selected_quarter=None):
        joiners_by_department = []
        resignees_by_department = []

        if selected_year:
            start_year, end_year = map(int, selected_year.split('-'))
            fiscal_year_start_date = date(start_year, 4, 1)
            fiscal_year_end_date = date(end_year, 3, 31)

            if selected_quarter:
                fiscal_quarter_months = {
                    'Q1': (4, 6),  # April to June
                    'Q2': (7, 9),  # July to September
                    'Q3': (10, 12),  # October to December
                    'Q4': (1, 3)  # January to March
                }
                start_month, end_month = fiscal_quarter_months[selected_quarter]
                if selected_quarter == 'Q4':
                    quarter_start_date = date(end_year, start_month, 1)
                    quarter_end_date = date(end_year, end_month, 31)
                else:
                    quarter_start_date = date(start_year, start_month, 1)
                    quarter_end_date = date(start_year, end_month, 30)
                joiners_domain = [('active', '=', True), ('date_of_joining', '>=', quarter_start_date), ('date_of_joining', '<=', quarter_end_date), ('employement_type.code', '!=', 'O'), ('company_id', '=', 1)]
                resignees_domain = [('active', '=', False), ('last_working_day', '>=', quarter_start_date), ('last_working_day', '<=', quarter_end_date), ('employement_type.code', '!=', 'O'), ('company_id', '=', 1)]
            else:
                joiners_domain = [('active', '=', True), ('date_of_joining', '>=', fiscal_year_start_date), ('date_of_joining', '<=', fiscal_year_end_date), ('employement_type.code', '!=', 'O'), ('company_id', '=', 1)]
                resignees_domain = [('active', '=', False), ('last_working_day', '>=', fiscal_year_start_date), ('last_working_day', '<=', fiscal_year_end_date), ('employement_type.code', '!=', 'O'), ('company_id', '=', 1)]
        else:
            joiners_domain = [('active', '=', True), ('employement_type.code', '!=', 'O')]
            resignees_domain = [('active', '=', False), ('employement_type.code', '!=', 'O')]

        departments = self.env['hr.department'].search([])
        for department in departments:
            department_joiners_data = {}
            joiners = self.env['hr.employee'].search([('department_id', '=', department.id)] + joiners_domain)
            for joiner in joiners:
                period_key = self._get_period_key(joiner.date_of_joining, 'quarterly')
                if period_key not in department_joiners_data:
                    department_joiners_data[period_key] = 0
                department_joiners_data[period_key] += 1
            for key, count in department_joiners_data.items():
                joiners_by_department.append({
                    'department': department.name,
                    'period': key,
                    'count': count
                })
        for department in departments:
            department_resignees_data = {}
            resignees = self.env['hr.employee'].search([('department_id', '=', department.id)] + resignees_domain)
            for resignee in resignees:
                if resignee.last_working_day and isinstance(resignee.last_working_day, date):
                    period_key = self._get_period_key(resignee.last_working_day, 'quarterly')
                    if period_key not in department_resignees_data:
                        department_resignees_data[period_key] = 0
                    department_resignees_data[period_key] += 1
            for key, count in department_resignees_data.items():
                resignees_by_department.append({
                    'department': department.name,
                    'period': key,
                    'count': count
                })
        return {
            'joiners_by_department': joiners_by_department,
            'resignees_by_department': resignees_by_department
        }

    @api.model
    def get_current_fiscal_year_data(self):
        today = datetime.today().date()
        fiscal_year = self.env['account.fiscalyear'].search([
            ('date_start', '<=', today),
            ('date_stop', '>=', today)
        ], limit=1)
        
        if not fiscal_year:
            raise UserError('No fiscal year found for the current date.')
        
        fiscal_year_start_date = fiscal_year.date_start
        fiscal_year_end_date = fiscal_year.date_stop

        # Determine the April 1st date of the fiscal year
        start_year = fiscal_year_start_date.year
        if fiscal_year_start_date.month == 4:  # Fiscal year starts after April
            april_1st_date = date(start_year, 4, 1)  # April 1st of the current fiscal year

        return self._get_dashboard_data(fiscal_year_start_date, fiscal_year_end_date,april_1st_date)

    @api.model
    def get_selected_fiscal_year_data(self, selected_year=None):
        if selected_year:
            try:
                start_year, end_year = map(int, selected_year.split('-'))
            except ValueError:
                raise UserError('Invalid format for selected_year. Expected format: "YYYY-YYYY".')

            fiscal_year = self.env['account.fiscalyear'].search([
                ('date_start', '>=', f'{start_year}-01-01'),
                ('date_stop', '<=', f'{end_year}-12-31')
            ], limit=1)
            
            if not fiscal_year:
                raise UserError('No fiscal year found for the selected range.')

            fiscal_year_start_date = fiscal_year.date_start
            fiscal_year_end_date = fiscal_year.date_stop
            # Determine the April 1st date based on the fiscal year start date
            if fiscal_year_start_date.month == 4:  # Fiscal year starts after April
                april_1st_date = date(start_year, 4, 1)  # April 1st of the current fiscal year

            return self._get_dashboard_data(fiscal_year_start_date, fiscal_year_end_date, april_1st_date)


    def _get_dashboard_data(self, start_date, end_date,april_1st_date):
        employee_count = self.env['hr.employee'].search_count([
            '&','&','&',('date_of_joining','<=',end_date),('active', '=', True),('employement_type.code', '!=', 'O'),('company_id','=',1)])
        
        attrition_count_main = self.env['hr.employee'].search_count([('active', '=', False), ('last_working_day', '>=', start_date), ('last_working_day', '<=', end_date),('employement_type.code', '!=', 'O'),('company_id','=',1)])
        active_employee_count = self.env['hr.employee'].search_count([('active', '=', True)])
        attrition_rate = round((attrition_count_main / employee_count) * 100, 3) if employee_count else 0
        employee_count_as_of_april = self.env['hr.employee'].search_count([
        '&', '&', '&',
        ('date_of_joining', '<=', april_1st_date),
        ('active', '=', True),
        ('employement_type.code', '!=', 'O'),
        ('company_id', '=', 1)
        ])
        # Calculate attrition by tenure and average tenure
        employee_data = self.env['hr.employee'].search([('active', '=', False), ('last_working_day', '>=', start_date), ('last_working_day', '<=', end_date),('employement_type.code', '!=', 'O'),('company_id','=',1)])
        tenure_data = {
        '0-3': [],
        '3-6': [],
        '6-12': [],
        '12-24': [],
        '24-36': [],
        '36+': []
        }
        tenure_counts = [0, 0, 0, 0, 0, 0]
        total_attrition_count = 0
        total_tenure_months = 0

        for employee in employee_data:
            tenure_months = employee.tenure_months
            if tenure_months is not None:
                if tenure_months <= 3:
                    tenure_counts[0] += 1
                    tenure_data['0-3'].append(employee.id)
                elif tenure_months <= 6:
                    tenure_counts[1] += 1
                    tenure_data['3-6'].append(employee.id)
                elif tenure_months <= 12:
                    tenure_counts[2] += 1
                    tenure_data['6-12'].append(employee.id)
                elif tenure_months <= 24:
                    tenure_counts[3] += 1
                    tenure_data['12-24'].append(employee.id)
                elif tenure_months <= 36:
                    tenure_counts[4] += 1
                    tenure_data['24-36'].append(employee.id)
                else:
                    tenure_counts[5] += 1
                    tenure_data['36+'].append(employee.id)

                total_attrition_count += 1
                total_tenure_months += tenure_months

        attrition_by_tenure = [(count / total_attrition_count) * 100 for count in tenure_counts] if total_attrition_count > 0 else [0] * 7
        average_tenure_months = total_tenure_months / total_attrition_count if total_attrition_count else 0
        average_tenure_years = int(average_tenure_months // 12)
        average_tenure_remaining_months = int(average_tenure_months % 12)
        average_tenure = f"{average_tenure_years}.{average_tenure_remaining_months} Yrs"

        # Other calculations
        male_count = self.env['hr.employee'].search_count([('gender', '=', 'male'), ('active', '=', False), ('last_working_day', '>=', start_date), ('last_working_day', '<=', end_date),('employement_type.code', '!=', 'O'),('company_id','=',1)])
        female_count = self.env['hr.employee'].search_count([('gender', '=', 'female'), ('active', '=', False), ('last_working_day', '>=', start_date), ('last_working_day', '<=', end_date),('employement_type.code', '!=', 'O'),('company_id','=',1)])
        total_attrition = male_count + female_count

        if total_attrition:
            male_percentage = round((male_count / total_attrition) * 100, 3)
            female_percentage = round((female_count / total_attrition) * 100, 3)
            attrition_by_gender = [
                {'name': 'Male', 'y': male_percentage},
                {'name': 'Female', 'y': female_percentage},
            ]
        else:
            attrition_by_gender = [
                {'name': 'Male', 'y': 0},
                {'name': 'Female', 'y': 0},
            ]

        attrition_by_job_role = []
        jobs = self.env['hr.job'].search([])
        reasons = self.env['kw_resignation_master'].search([])

        for job in jobs:
            total_count = self.env['hr.employee'].search_count([('job_id', '=', job.id),])
            attrition_count = self.env['hr.employee'].search_count([('job_id', '=', job.id), ('active', '=', False), ('last_working_day', '>=', start_date), ('last_working_day', '<=', end_date),('employement_type.code', '!=', 'O'),('company_id','=',1)])

            if attrition_count > 0:  
                attrition_by_job_role.append({
                    'name': job.name,
                    'y': attrition_count  
                })

        # Fetch and format department attrition data
        department_attrition = []
        departments = self.env['hr.department'].search([])

        for department in departments:
            total_count = self.env['hr.employee'].search_count([('department_id', '=', department.id),('employement_type.code', '!=', 'O'),('company_id','=',1),('active','=',True)])
            attrition_count = self.env['hr.employee'].search_count([('department_id', '=', department.id), ('active', '=', False), ('last_working_day', '>=', start_date), ('last_working_day', '<=', end_date),('employement_type.code', '!=', 'O'),('company_id','=',1)])

            if attrition_count > 0:  
                department_attrition.append({
                    'department': department.name,
                    'total_count': total_count,
                    'attrition_count': attrition_count,
                    'department_id': department.id
                })

        # Fetch and format job role attrition data
        top_resignation_reasons = []
        for reason in reasons:
            total_count = self.env['hr.employee'].search_count([('resignation_reason', '=', reason.id)])
            attrition_count = self.env['hr.employee'].search_count([('resignation_reason', '=', reason.id), ('active', '=', False), ('last_working_day', '>=', start_date), ('last_working_day', '<=', end_date),('employement_type.code', '!=', 'O'),('company_id','=',1)])
            top_resignation_reasons.append({
                'job_role': reason.name,
                'total_count': total_count,
                'attrition_count': attrition_count
            })

        # Fetch and format data for joiners and resignee  by department
        joiners_by_department = self._get_joiners_by_department_data(start_date, end_date)
        resignees_by_department = self._get_resignees_by_department_data(start_date, end_date)

        # Voluntary and Involuntary Attrition Calculation
        voluntary_count = self.env['hr.employee'].search_count([
            ('active', '=', False), 
            ('attrition_type', '=', 'vountary'),
            ('last_working_day', '>=', start_date),
            ('last_working_day', '<=', end_date),
            ('employement_type.code', '!=', 'O'),
            ('company_id','=',1)
        ])
        involuntary_reasons = ['contract_closure', 'demise', 'retirement', 'performance_issue', 'termination']
        involuntary_counts = {reason: self.env['hr.employee'].search_count([
            ('active', '=', False), 
            ('attrition_type', '=', 'involuntary'), 
            ('involuntary_reason', '=', reason),
            ('last_working_day', '>=', start_date),
            ('last_working_day', '<=', end_date),
            ('employement_type.code', '!=', 'O'),
            ('company_id','=',1)
        ]) for reason in involuntary_reasons}
        total_involuntary_attrition = sum(involuntary_counts.values())
        voluntary_involuntary_attrition = {
            'voluntary': voluntary_count,
            'involuntary': total_involuntary_attrition,
            'involuntary_details': involuntary_counts
        }
        fy_wise_joining_exit = self._get_fy_wise_joining_exit_data()

        return {
            'fiscal_year_start_date': start_date,
            'fiscal_year_end_date': end_date,
            'employee_count': employee_count,
            'active_employee_count': active_employee_count,
            'attrition_count': attrition_count_main,
            'attrition_rate': attrition_rate,
            'attrition_by_tenure': attrition_by_tenure,
            'attrition_by_gender': attrition_by_gender,
            'attrition_by_job_role': attrition_by_job_role,
            'department_attrition': department_attrition,
            'top_resignation_reasons': top_resignation_reasons,
            'joiners_by_department': joiners_by_department,
            'resignees_by_department': resignees_by_department,
            'voluntary_attrition': voluntary_count,
            'involuntary_attrition': total_involuntary_attrition,
            'involuntary_counts': involuntary_counts,
            'average_tenure': average_tenure,
            'male_count': male_count,
            'female_count': female_count,
            'total_attrition': total_attrition,
            'fy_wise_joining_exit': fy_wise_joining_exit,  
            'voluntary_involuntary_attrition':voluntary_involuntary_attrition,
            'tenure_data':tenure_data,
            'employee_count_as_of_april':employee_count_as_of_april,

        }

