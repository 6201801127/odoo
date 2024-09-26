from odoo import models, fields, api, _
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
import datetime


class ResourceDashboard(models.Model):
    _name = 'employee_dashboard'
    _description = 'Employee Dashboard'

    @api.model
    def get_total_head_count(self,**kwargs):
        fy_value = kwargs.get('fy_value', 0)
        cr = self._cr
        fy_query = f" hr.active = true"
        fiscal_year = self.env['account.fiscalyear'].sudo().search([('id','=',fy_value)],limit=1)
        if  kwargs and fy_value and fiscal_year:
            date_start = fiscal_year.date_start.strftime('%Y-%m-%d')
            date_stop = fiscal_year.date_stop.strftime('%Y-%m-%d')
            where_clause = f"{fy_query} AND hr.date_of_joining BETWEEN TO_DATE('{date_start}', 'YYYY-MM-DD') AND TO_DATE('{date_stop}', 'YYYY-MM-DD')"
        else:
            where_clause = fy_query
            
        query = f"""SELECT count(*) FROM hr_employee hr WHERE {where_clause} """
        cr.execute(query)
        data = cr.fetchall()
        return data
    @api.model
    def get_total_male_head_count(self,**kwargs):
        fy_value = kwargs.get('fy_value', 0)
        cr = self._cr
        fy_query = f" hr.employement_type not in (SELECT id FROM kwemp_employment_type where code = 'O') AND hr.gender='male' AND hr.active=true"
        fiscal_year = self.env['account.fiscalyear'].sudo().search([('id','=',fy_value)],limit=1)
        if  kwargs and fy_value and fiscal_year:
            date_start = fiscal_year.date_start.strftime('%Y-%m-%d')
            date_stop = fiscal_year.date_stop.strftime('%Y-%m-%d')
            where_clause = f"{fy_query} AND hr.date_of_joining BETWEEN TO_DATE('{date_start}', 'YYYY-MM-DD') AND TO_DATE('{date_stop}', 'YYYY-MM-DD')"
        else:
            where_clause = fy_query
        query = f"""SELECT count(*) FROM hr_employee hr WHERE {where_clause} """
        cr.execute(query)
        data = cr.fetchall()
        return data
    
    @api.model
    def get_total_female_head_count(self,**kwargs):
        fy_value = kwargs.get('fy_value', 0)
        cr = self._cr
        fy_query = f"hr.employement_type not in (SELECT id FROM kwemp_employment_type where code = 'O') AND hr.gender='female' AND hr.active=true"
        fiscal_year = self.env['account.fiscalyear'].sudo().search([('id','=',fy_value)],limit=1)
        if  kwargs and fy_value and fiscal_year:
            date_start = fiscal_year.date_start.strftime('%Y-%m-%d')
            date_stop = fiscal_year.date_stop.strftime('%Y-%m-%d')
            where_clause = f"{fy_query} AND hr.date_of_joining BETWEEN TO_DATE('{date_start}', 'YYYY-MM-DD') AND TO_DATE('{date_stop}', 'YYYY-MM-DD')"
        else:
            where_clause = fy_query
        query = f"""SELECT count(*) FROM hr_employee hr WHERE {where_clause} """
        cr.execute(query)
        data = cr.fetchall()
        return data
    @api.model
    def get_csm_head_count(self,**kwargs):
        fy_value = kwargs.get('fy_value', 0)
        cr = self._cr
        fy_query = f"hr.employement_type not in (SELECT id FROM kwemp_employment_type where code = 'O') AND hr.active=true"
        fiscal_year = self.env['account.fiscalyear'].sudo().search([('id','=',fy_value)],limit=1)
        if  kwargs and fy_value and fiscal_year:
            date_start = fiscal_year.date_start.strftime('%Y-%m-%d')
            date_stop = fiscal_year.date_stop.strftime('%Y-%m-%d')
            where_clause = f"{fy_query} AND hr.date_of_joining BETWEEN TO_DATE('{date_start}', 'YYYY-MM-DD') AND TO_DATE('{date_stop}', 'YYYY-MM-DD')"
        else:
            where_clause = fy_query
        query = f"""SELECT count(*) FROM hr_employee hr WHERE {where_clause}  """
        cr.execute(query)
        data = cr.fetchall()
        return data
    @api.model
    def get_susidary_head_count(self,**kwargs):
        fy_value = kwargs.get('fy_value', 0)
        cr = self._cr
        fy_query = f"hr.company_id not in (1) AND hr.active=true"
        fiscal_year = self.env['account.fiscalyear'].sudo().search([('id','=',fy_value)],limit=1)
        if  kwargs and fy_value and fiscal_year:
            date_start = fiscal_year.date_start.strftime('%Y-%m-%d')
            date_stop = fiscal_year.date_stop.strftime('%Y-%m-%d')
            where_clause = f"{fy_query} AND hr.date_of_joining BETWEEN TO_DATE('{date_start}', 'YYYY-MM-DD') AND TO_DATE('{date_stop}', 'YYYY-MM-DD')"
        else:
            where_clause = fy_query
        query = f"""SELECT count(*) FROM hr_employee hr WHERE {where_clause}  """
        cr.execute(query)
        data = cr.fetchall()
        return data
    @api.model
    def get_offsite_head_count(self,**kwargs):
        fy_value = kwargs.get('fy_value', 0)
        cr = self._cr
        fy_query = f"hr.location='offsite' AND hr.employement_type not in (SELECT id FROM kwemp_employment_type WHERE code = 'O')AND hr.active=true"
        fiscal_year = self.env['account.fiscalyear'].sudo().search([('id','=',fy_value)],limit=1)
        if  kwargs and fy_value and fiscal_year:
            date_start = fiscal_year.date_start.strftime('%Y-%m-%d')
            date_stop = fiscal_year.date_stop.strftime('%Y-%m-%d')
            where_clause = f"{fy_query} AND hr.date_of_joining BETWEEN TO_DATE('{date_start}', 'YYYY-MM-DD') AND TO_DATE('{date_stop}', 'YYYY-MM-DD')"
        else:
            where_clause = fy_query
        query = f"""SELECT count(*) FROM hr_employee hr 
                           WHERE {where_clause}  """
        cr.execute(query)
        data = cr.fetchall()
        return data
    @api.model
    def get_outsource_head_count(self,**kwargs):
        fy_value = kwargs.get('fy_value', 0)
        cr = self._cr
        fy_query = f"hr.employement_type in (SELECT id FROM kwemp_employment_type WHERE code = 'O') AND hr.active=true"
        fiscal_year = self.env['account.fiscalyear'].sudo().search([('id','=',fy_value)],limit=1)
        if  kwargs and fy_value and fiscal_year:
            date_start = fiscal_year.date_start.strftime('%Y-%m-%d')
            date_stop = fiscal_year.date_stop.strftime('%Y-%m-%d')
            where_clause = f"{fy_query} AND hr.date_of_joining BETWEEN TO_DATE('{date_start}', 'YYYY-MM-DD') AND TO_DATE('{date_stop}', 'YYYY-MM-DD')"
        else:
            where_clause = fy_query
        query = f"""SELECT count(*) FROM hr_employee hr 
                           WHERE {where_clause} """
        cr.execute(query)
        data = cr.fetchall()
        return data
    @api.model
    def get_onsite_head_count(self,**kwargs):
        fy_value = kwargs.get('fy_value', 0)
        cr = self._cr
        fy_query = f" hr.location='onsite' AND hr.employement_type not in (SELECT id FROM kwemp_employment_type WHERE code = 'O') AND hr.active=true"
        fiscal_year = self.env['account.fiscalyear'].sudo().search([('id','=',fy_value)],limit=1)
        if  kwargs and fy_value and fiscal_year:
            date_start = fiscal_year.date_start.strftime('%Y-%m-%d')
            date_stop = fiscal_year.date_stop.strftime('%Y-%m-%d')
            where_clause = f"{fy_query} AND hr.date_of_joining BETWEEN TO_DATE('{date_start}', 'YYYY-MM-DD') AND TO_DATE('{date_stop}', 'YYYY-MM-DD')"
        else:
            where_clause = fy_query
        query = f"""SELECT count(*) FROM hr_employee hr 
                           WHERE {where_clause} """
        cr.execute(query)
        data = cr.fetchall()
        return data
    

    # @api.model
    # def employee_head_count(self):
    #     employee_head_count_data = []
    #     cr = self._cr
    #     query = """
    #         SELECT gender, COUNT(*) AS count
    #         FROM hr_employee
    #         GROUP BY gender;
    #     """
    #     cr.execute(query)
    #     data = cr.fetchall()

    #     for row in data:
    #         gender = row[0]
    #         count = row[1]
    #         employee_head_count_data.append({
    #             'gender': gender,
    #             'count': count,
    #         })
    #     return employee_head_count_data
      
    @api.model
    def level_wise_male_female_count(self,**kwargs):
        level_wise_gender_data = []
        fy_value = kwargs.get('fy_value', 0)
        cr = self._cr
        fy_query = f" hr.active = true AND hr.level is not null AND hr.gender is not null"
        fiscal_year = self.env['account.fiscalyear'].sudo().search([('id','=',fy_value)],limit=1)
        if  kwargs and fy_value and fiscal_year:
            date_start = fiscal_year.date_start.strftime('%Y-%m-%d')
            date_stop = fiscal_year.date_stop.strftime('%Y-%m-%d')
            where_clause = f"{fy_query} AND hr.date_of_joining BETWEEN TO_DATE('{date_start}', 'YYYY-MM-DD') AND TO_DATE('{date_stop}', 'YYYY-MM-DD')"
        else:
            where_clause = fy_query
            
        query = f"""SELECT 
                        level.name,
                        COUNT(CASE WHEN hr.gender = 'male' THEN hr.id END) AS male_count,
                        COUNT(CASE WHEN hr.gender = 'female' THEN hr.id END) AS female_count 
                    FROM 
                        hr_employee hr 
                    LEFT JOIN 
                        kw_grade_level level ON level.id = hr.level 
                    WHERE 
                       {where_clause}
                    GROUP BY 
					    level.name
					ORDER BY 
					    level.name ASC"""

        cr.execute(query)
        data = cr.fetchall()

        for row in data:
            level = row[0]
            male_count = row[1]
            female_count = row[2]
            level_wise_gender_data.append({
                'name': level,
                'male_count': male_count,
                'female_count': female_count
            })
        return level_wise_gender_data
    
    @api.model
    def department_wise_male_female_count(self,**kwargs):
        dept_wise_gender_data = []
        fy_value = kwargs.get('fy_value', 0)
        cr = self._cr
        fy_query = "hr.active = true AND hr.department_id is not null AND hr.gender is not null"
        fiscal_year = self.env['account.fiscalyear'].sudo().search([('id','=',fy_value)],limit=1)
        if  kwargs and fy_value and fiscal_year:
            date_start = fiscal_year.date_start.strftime('%Y-%m-%d')
            date_stop = fiscal_year.date_stop.strftime('%Y-%m-%d')
            where_clause = f"{fy_query} AND hr.date_of_joining BETWEEN TO_DATE('{date_start}', 'YYYY-MM-DD') AND TO_DATE('{date_stop}', 'YYYY-MM-DD')"
        else:
            where_clause = fy_query
            
        query = f"""	SELECT
                        COUNT(*) AS gender_count,
                        hr.gender AS gender,
                        dept.name
		            FROM
		                hr_employee hr
		            LEFT JOIN 
                        hr_department dept ON dept.id = hr.department_id 
                    WHERE 
                       {where_clause}
                    GROUP BY 
                        dept.name,hr.gender
                    ORDER BY 
					    dept.name ASC"""

        cr.execute(query)
        result = cr.fetchall()
        for row in result:
            gender_count = row[0]
            gender = row[1]
            department = row[2]
            dept_wise_gender_data.append({
                'name': gender.capitalize(),
                'category': department,
                'data': gender_count
            })
        return dept_wise_gender_data
    
    @api.model
    def designation_wise_male_female_count(self,**kwargs):
        desig_wise_gender_data = []
        cr = self._cr
        fy_value = kwargs.get('fy_value', 0)
        fy_query = "hr.active = true AND hr.job_id is not null AND hr.gender is not null"
        fiscal_year = self.env['account.fiscalyear'].sudo().search([('id','=',fy_value)],limit=1)
        if  kwargs and fy_value and fiscal_year:
            date_start = fiscal_year.date_start.strftime('%Y-%m-%d')
            date_stop = fiscal_year.date_stop.strftime('%Y-%m-%d')
            where_clause = f"{fy_query} AND hr.date_of_joining BETWEEN TO_DATE('{date_start}', 'YYYY-MM-DD') AND TO_DATE('{date_stop}', 'YYYY-MM-DD')"
        else:
            where_clause = fy_query
            
        query = f"""	SELECT
                        COUNT(*) AS gender_count,
                        hr.gender AS gender,
                        desig.name
		            FROM
		                hr_employee hr
		            LEFT JOIN 
                        hr_job desig ON desig.id = hr.job_id 
                    WHERE 
                       {where_clause}
                    GROUP BY 
                        desig.name,hr.gender
                    ORDER BY 
					    hr.gender,desig.name ASC"""

        cr.execute(query)
        result = cr.fetchall()
        for row in result:
            gender_count = row[0]
            gender = row[1]
            designation = row[2]
            desig_wise_gender_data.append({
                'name': gender.capitalize(),
                'category': designation,
                'data': gender_count
            })
        return desig_wise_gender_data
    
    
    @api.model
    def location_wise_male_female_count(self,**kwargs):
        location_wise_gender_data = []
        fy_value = kwargs.get('fy_value', 0)
        cr = self._cr
        fy_query = "hr.active = true AND hr.job_branch_id is not null AND hr.gender is not null"
        fiscal_year = self.env['account.fiscalyear'].sudo().search([('id','=',fy_value)],limit=1)
        if  kwargs and fy_value and fiscal_year:
            date_start = fiscal_year.date_start.strftime('%Y-%m-%d')
            date_stop = fiscal_year.date_stop.strftime('%Y-%m-%d')
            where_clause = f"{fy_query} AND hr.date_of_joining BETWEEN TO_DATE('{date_start}', 'YYYY-MM-DD') AND TO_DATE('{date_stop}', 'YYYY-MM-DD')"
        else:
            where_clause = fy_query
            
        query = f"""SELECT 
                        loc.alias,
                        COUNT(CASE WHEN hr.gender = 'male' THEN hr.id END) AS male_count,
                        COUNT(CASE WHEN hr.gender = 'female' THEN hr.id END) AS female_count 
                    FROM 
                        hr_employee hr 
                    LEFT JOIN 
                        kw_res_branch loc ON loc.id = hr.job_branch_id 
                    WHERE 
                        {where_clause}
                    GROUP BY 
                        loc.alias
                    ORDER BY 
					    loc.alias ASC"""

        cr.execute(query)
        data = cr.fetchall()

        for row in data:
            location = row[0]
            male_count = row[1]
            female_count = row[2]
            location_wise_gender_data.append({
                'name': location,
                'male_count': male_count,
                'female_count': female_count
            })
        return location_wise_gender_data
    @api.model
    def age_wise_male_female_count(self,**kwargs):
        age_wise_gender_data = []
        cr = self._cr
        fy_value = kwargs.get('fy_value', 0)
        fy_query = "hr.active = true AND hr.birthday is not null AND hr.gender is not null"
        fiscal_year = self.env['account.fiscalyear'].sudo().search([('id','=',fy_value)],limit=1)
        if  kwargs and fy_value and fiscal_year:
            date_start = fiscal_year.date_start.strftime('%Y-%m-%d')
            date_stop = fiscal_year.date_stop.strftime('%Y-%m-%d')
            where_clause = f"{fy_query} AND hr.date_of_joining BETWEEN TO_DATE('{date_start}', 'YYYY-MM-DD') AND TO_DATE('{date_stop}', 'YYYY-MM-DD')"
        else:
            where_clause = fy_query
            
        query = f"""SELECT 
            CASE
                WHEN EXTRACT(YEAR FROM age(current_date, hr.birthday)) BETWEEN 18 AND 24 THEN '18-24'
                WHEN EXTRACT(YEAR FROM age(current_date, hr.birthday)) BETWEEN 25 AND 30 THEN '25-30'
                WHEN EXTRACT(YEAR FROM age(current_date, hr.birthday)) BETWEEN 31 AND 35 THEN '31-35'
                WHEN EXTRACT(YEAR FROM age(current_date, hr.birthday)) BETWEEN 36 AND 40 THEN '36-40'
                WHEN EXTRACT(YEAR FROM age(current_date, hr.birthday)) BETWEEN 41 AND 45 THEN '41-45'
                WHEN EXTRACT(YEAR FROM age(current_date, hr.birthday)) BETWEEN 46 AND 50 THEN '46-50'
                ELSE '50+'
                END AS age_group,
                COUNT(CASE WHEN hr.gender = 'male' THEN hr.id END) AS male_count,
                COUNT(CASE WHEN hr.gender = 'female' THEN hr.id END) AS female_count 
            FROM 
                hr_employee hr 
            WHERE 
                {where_clause}
            GROUP BY 
                age_group
            ORDER BY 
                age_group
                            """

        cr.execute(query)
        data = cr.fetchall()

        for row in data:
            age_group = row[0]
            male_count = row[1]
            female_count = row[2]
            age_wise_gender_data.append({
                'age_group': age_group,
                'male_count': male_count,
                'female_count': female_count
            })
        return age_wise_gender_data

    @api.model
    def fy_wise_male_female_count(self,**kwargs):
        fy_wise_gender_data = []
        fy_value = kwargs.get('fy_value', 0)
        cr = self._cr
        fy_query = "hr.active = true AND hr.date_of_joining is not null AND hr.gender is not null"
        fiscal_year = self.env['account.fiscalyear'].sudo().search([('id','=',fy_value)],limit=1)
        if  kwargs and fy_value and fiscal_year:
            date_start = fiscal_year.date_start.strftime('%Y-%m-%d')
            date_stop = fiscal_year.date_stop.strftime('%Y-%m-%d')
            where_clause = f"{fy_query} AND hr.date_of_joining BETWEEN TO_DATE('{date_start}', 'YYYY-MM-DD') AND TO_DATE('{date_stop}', 'YYYY-MM-DD')"
        else:
            where_clause = fy_query
            
        query = f"""SELECT 
                        fy.name AS financial_year,
                        COUNT(CASE WHEN hr.gender = 'male' THEN hr.id END) AS male_count,
                        COUNT(CASE WHEN hr.gender = 'female' THEN hr.id END) AS female_count
                    FROM 
                        hr_employee hr
                    JOIN 
                        account_fiscalyear fy ON hr.date_of_joining BETWEEN fy.date_start AND fy.date_stop
                    WHERE 
                        {where_clause}
                    GROUP BY 
                        fy.name
                    ORDER BY 
                        fy.name ASC"""

        cr.execute(query)
        data = cr.fetchall()

        for row in data:
            fy_value = row[0]
            male_count = row[1]
            female_count = row[2]
            fy_wise_gender_data.append({
                'name': fy_value,
                'male_count': male_count,
                'female_count': female_count
            })
        return fy_wise_gender_data
    
    @api.model
    def headcount_by_tenure_range(self,**kwargs):
        fy_value = kwargs.get('fy_value', 0)
        cr = self._cr
        fy_query = "active = true AND gender is not null AND date_of_joining is not null"
        fiscal_year = self.env['account.fiscalyear'].sudo().search([('id','=',fy_value)],limit=1)
        if  kwargs and fy_value and fiscal_year:
            date_start = fiscal_year.date_start.strftime('%Y-%m-%d')
            date_stop = fiscal_year.date_stop.strftime('%Y-%m-%d')
            where_clause = f"{fy_query} AND date_of_joining BETWEEN TO_DATE('{date_start}', 'YYYY-MM-DD') AND TO_DATE('{date_stop}', 'YYYY-MM-DD')"
        else:
            where_clause = fy_query
            
        self.env.cr.execute(f"""
            SELECT
                CASE
                    WHEN EXTRACT(YEAR FROM AGE(date_of_joining)) < 1 THEN 'Less than 1 year'
                    WHEN EXTRACT(YEAR FROM AGE(date_of_joining)) BETWEEN 1 AND 5 THEN '1-5 years'
                    WHEN EXTRACT(YEAR FROM AGE(date_of_joining)) BETWEEN 6 AND 10 THEN '6-10 years'
                    ELSE 'More than 10 years'
                END AS tenure_group, gender, COUNT(id) AS employee_count
            FROM hr_employee
            WHERE {where_clause}
            GROUP BY tenure_group, gender
        """)
        result = self.env.cr.fetchall()
        data = {}
        for row in result:
            tenure_group = row[0]
            gender = row[1].capitalize()
            employee_count = row[2]
            if tenure_group not in data:
                data[tenure_group] = {'Male': 0, 'Female': 0}
            data[tenure_group][gender] = employee_count
        return data
    
    @api.model
    def get_sbu_wise_data(self,**kwargs):
        sbu_data = {}
        fy_value = kwargs.get('fy_value', 0)
        cr = self._cr
        fy_query = "hr.active = true AND hr.sbu_master_id is not null AND hr.gender is not null AND hr.sbu_type='sbu'"
        fiscal_year = self.env['account.fiscalyear'].sudo().search([('id','=',fy_value)],limit=1)
        if  kwargs and fy_value and fiscal_year:
            date_start = fiscal_year.date_start.strftime('%Y-%m-%d')
            date_stop = fiscal_year.date_stop.strftime('%Y-%m-%d')
            where_clause = f"{fy_query} AND hr.date_of_joining BETWEEN TO_DATE('{date_start}', 'YYYY-MM-DD') AND TO_DATE('{date_stop}', 'YYYY-MM-DD')"
        else:
            where_clause = fy_query
            
        cr.execute(f"""select sbm.name,count(*) 
                                from hr_employee hr
                                left join kw_sbu_master sbm on sbm.id = hr.sbu_master_id
                                where {where_clause}
                                group by sbm.name """)
        data = cr.fetchall()
        for row in data:
            sbu = row[0]
            value = row[1]
            if sbu in sbu_data:
                sbu_data[sbu] += value
            else:
                sbu_data[sbu] = value

        formatted_sbu_data = [[sbu, value] for sbu, value in sbu_data.items()]
        return [formatted_sbu_data]
    
    @api.model
    def get_role_wise_data(self,**kwargs):

        employee_role_data = {}
        fy_value = kwargs.get('fy_value', 0)
        cr = self._cr
        
        fy_query = "hr.active = true AND hr.emp_category is not null AND hr.gender is not null"
        fiscal_year = self.env['account.fiscalyear'].sudo().search([('id','=',fy_value)],limit=1)
        if  kwargs and fy_value and fiscal_year:
            date_start = fiscal_year.date_start.strftime('%Y-%m-%d')
            date_stop = fiscal_year.date_stop.strftime('%Y-%m-%d')
            where_clause = f"{fy_query} AND hr.date_of_joining BETWEEN TO_DATE('{date_start}', 'YYYY-MM-DD') AND TO_DATE('{date_stop}', 'YYYY-MM-DD')"
        else:
            where_clause = fy_query
            
        cr.execute(f"""select  
                        count(*),
			            kcn.name as role
                        from hr_employee hr
                        left join kwmaster_category_name kcn on kcn.id=hr.emp_category
                        where {where_clause}
                        group by kcn.name """)
        data = cr.fetchall()
        
        for row in data:
            value = row[0]
            role = row[1]
            if role in employee_role_data:
                employee_role_data[role] += value
            else:
                employee_role_data[role] = value

        formatted_data = [[role, value] for role, value in employee_role_data.items()]
        return [formatted_data]
    
    @api.model
    def quater_wise_resource_addition_count(self,**kwargs):
        fy_wise_gender_data = []
        fy_value = kwargs.get('fy_value', 0)
        cr = self._cr
        fy_query = "hr.active = true AND hr.date_of_joining is not null AND hr.gender is not null"
        fiscal_year = self.env['account.fiscalyear'].sudo().search([('id','=',fy_value)],limit=1)
        if  kwargs and fy_value and fiscal_year:
            date_start = fiscal_year.date_start.strftime('%Y-%m-%d')
            date_stop = fiscal_year.date_stop.strftime('%Y-%m-%d')
            where_clause = f"{fy_query} AND hr.date_of_joining BETWEEN TO_DATE('{date_start}', 'YYYY-MM-DD') AND TO_DATE('{date_stop}', 'YYYY-MM-DD')"
        else:
            where_clause = fy_query
            
        query = f"""SELECT 
                        fy.name AS financial_year,
                        COUNT(CASE WHEN hr.gender = 'male' THEN hr.id END) AS male_count,
                        COUNT(CASE WHEN hr.gender = 'female' THEN hr.id END) AS female_count
                    FROM 
                        hr_employee hr
                    JOIN 
                        account_fiscalyear fy ON hr.date_of_joining BETWEEN fy.date_start AND fy.date_stop
                    WHERE 
                        {where_clause}
                    GROUP BY 
                        fy.name
                    ORDER BY 
                        fy.name ASC"""

        cr.execute(query)
        data = cr.fetchall()

        for row in data:
            fy_value = row[0]
            male_count = row[1]
            female_count = row[2]
            fy_wise_gender_data.append({
                'name': fy_value,
                'male_count': male_count,
                'female_count': female_count
            })
        return fy_wise_gender_data
    
    @api.model
    def outsource_wise_male_female_count(self,**kwargs):
        outsource_wise_gender_data = []
        fy_value = kwargs.get('fy_value', 0)
        cr = self._cr
        fy_query = "hr.active = true AND hr.date_of_joining is not null AND hr.gender is not null AND hr.employement_type in (SELECT id FROM kwemp_employment_type WHERE code = 'O')"
        fiscal_year = self.env['account.fiscalyear'].sudo().search([('id','=',fy_value)],limit=1)
        if  kwargs and fy_value and fiscal_year:
            date_start = fiscal_year.date_start.strftime('%Y-%m-%d')
            date_stop = fiscal_year.date_stop.strftime('%Y-%m-%d')
            where_clause = f"{fy_query} AND hr.date_of_joining BETWEEN TO_DATE('{date_start}', 'YYYY-MM-DD') AND TO_DATE('{date_stop}', 'YYYY-MM-DD')"
        else:
            where_clause = fy_query
            
        query = f"""SELECT 
                        hr.gender AS gender,
                        COUNT(CASE WHEN hr.gender = 'male' THEN hr.id END) AS male_count,
                        COUNT(CASE WHEN hr.gender = 'female' THEN hr.id END) AS female_count
                    FROM 
                        hr_employee hr
                    WHERE 
                        {where_clause}
                    GROUP BY 
                        hr.gender
                    ORDER BY 
                        hr.gender ASC"""

        cr.execute(query)
        data = cr.fetchall()

        for row in data:
            gender = row[0]
            male_count = row[1]
            female_count = row[2]
            outsource_wise_gender_data.append({
                'name': gender.capitalize(),
                'male_count': male_count,
                'female_count': female_count
            })
        return outsource_wise_gender_data
    
    @api.model
    def day_status_wise_male_female_count(self,**kwargs):
        day_status_wise_gender_data = []
        fy_value = kwargs.get('fy_value', 0)
        cr = self._cr
        fy_query = """e.active = true 
                    AND e.gender is not null 
                    AND e.date_of_joining is not null
                    AND e.employement_type in (SELECT id FROM kwemp_employment_type WHERE code != 'O')"""
        fiscal_year = self.env['account.fiscalyear'].sudo().search([('id','=',fy_value)],limit=1)
        if  kwargs and fy_value and fiscal_year:
            date_start = fiscal_year.date_start.strftime('%Y-%m-%d')
            date_stop = fiscal_year.date_stop.strftime('%Y-%m-%d')
            where_clause = f"{fy_query} AND hr.date_of_joining BETWEEN TO_DATE('{date_start}', 'YYYY-MM-DD') AND TO_DATE('{date_stop}', 'YYYY-MM-DD')"
        else:
            where_clause = fy_query
            
        query = f"""
                SELECT
                    CASE
                        WHEN a.payroll_day_value = 0 THEN 'Absent'
                        WHEN a.day_status IN ('DAY_STATUS_RHOLIDAY', 'DAY_STATUS_WEEKOFF') THEN 'Week Off'
                        WHEN a.day_status IN ('DAY_STATUS_HOLIDAY') THEN 'Holiday'
                        WHEN a.day_status NOT IN ('DAY_STATUS_RHOLIDAY', 'DAY_STATUS_WEEKOFF', 'DAY_STATUS_HOLIDAY') AND a.check_in IS NOT NULL THEN 'Present'
                        WHEN a.is_on_tour = TRUE THEN 'On Tour'
                        WHEN a.leave_status IS NOT NULL THEN 'On Leave'
                    END AS day_status,
                    COUNT(CASE WHEN e.gender = 'male' THEN 1 END) AS male_count,
                    COUNT(CASE WHEN e.gender = 'female' THEN 1 END) AS female_count
                FROM
                    hr_employee e
                JOIN
                    kw_daily_employee_attendance a ON  a.employee_id = e.id
                WHERE e.active = true 
                    AND e.gender is not null 
                    AND e.date_of_joining is not null
                    AND e.employement_type in (SELECT id FROM kwemp_employment_type WHERE code != 'O')
                GROUP BY
                    CASE
                        WHEN a.payroll_day_value = 0 THEN 'Absent'
                        WHEN a.day_status IN ('DAY_STATUS_RHOLIDAY', 'DAY_STATUS_WEEKOFF') THEN 'Week Off'
                        WHEN a.day_status IN ('DAY_STATUS_HOLIDAY') THEN 'Holiday'
                        WHEN a.day_status NOT IN ('DAY_STATUS_RHOLIDAY', 'DAY_STATUS_WEEKOFF', 'DAY_STATUS_HOLIDAY') AND a.check_in IS NOT NULL THEN 'Present'
                        WHEN a.is_on_tour = TRUE THEN 'On Tour'
                        WHEN a.leave_status IS NOT NULL THEN 'On Leave'
                    END
                ORDER BY
                    day_status
                """
        cr.execute(query)
        data = cr.fetchall()

        for row in data:
            day_status_value = row[0]
            male_count = row[1]
            female_count = row[2]
            day_status_wise_gender_data.append({
                'name': day_status_value,
                'male_count': male_count,
                'female_count': female_count
            })
        # print("Day Status Value.......................",day_status_wise_gender_data)
        return day_status_wise_gender_data
    
    # @api.model
    # def get_resource_fy_filter_data(self):
    #     fy_data_dict = []
    #     cr = self._cr
    #     fy_query = """select id as id,name as name,* from account_fiscalyear ORDER BY name DESC"""
    #     cr.execute(fy_query)
    #     fy_data = cr.fetchall()

    #     for row in fy_data:
    #         fy_data_dict.append({'id': row[0], 'name': row[1]})
    #     return [fy_data_dict]
    
    
    # @api.model
    # def get_resource_dashboard_filter_data(self):
    #     resource_filter_data = {
    #         'resource_nexus_dashboard_filters': self.get_resource_fy_filter_data(),
    #     }
    #     return resource_filter_data
    
    
   