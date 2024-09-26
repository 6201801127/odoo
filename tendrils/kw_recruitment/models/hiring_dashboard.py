from odoo import models, fields, api, _
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta

class Employee(models.Model):
    _name = 'recruitment_data_dashboard'
    _description = 'recruitment_data_dashboard'

    @api.model
    def get_level_ageing_to_join_ratio_count(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        ageing_to_jion_ratio = {}
        cr = self._cr
        cr.execute("""with a as
            (SELECT e.id,e.level, e.name AS name,e.active, e.mrf_id AS mrf,e.date_of_joining,cfy.name as fy,rr.write_date::date AS mrf_app_date,
            CASE WHEN (e.date_of_joining - rr.write_date::date) > 0 THEN (e.date_of_joining - rr.write_date::date)
                    ELSE 0 END AS individual_aging_days
            FROM hr_employee e join kw_recruitment_requisition rr ON rr.id = e.mrf_id
            
                JOIN account_fiscalyear cfy ON e.date_of_joining >= cfy.date_start AND e.date_of_joining <= cfy.date_stop
            where mrf_id is not null and rr.state = 'approve' and cfy.id=%s and e.employement_type not in 
            (SELECT id FROM kwemp_employment_type where code = 'O'))

            
            select (SELECT name FROM kw_grade_level WHERE id = a.level) || '(' || COUNT(a.level) || ')' AS level,
                CASE WHEN COUNT(a.level) > 0 THEN SUM(a.individual_aging_days) / COUNT(a.level) END AS aging_join
            from a WHERE a.level IS NOT NULL GROUP BY a.level 
            ORDER BY level ASC """, (fiscal_year_id,))
      
        data = cr.fetchall()
        for row in data:
            level_name = row[0]
            value = row[1]
            if level_name in ageing_to_jion_ratio:
                ageing_to_jion_ratio[level_name] += value
            else:
                ageing_to_jion_ratio[level_name] = value

        formatted_ageing_to_join = [[level_name, value] for level_name, value in ageing_to_jion_ratio.items()]
        return [formatted_ageing_to_join]
    
    @api.model
    def get_grade_ageing_to_join_ratio_count(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        ageing_to_jion_grade_ratio = {}
        cr = self._cr
        cr.execute("""with a as
            (SELECT e.id,e.grade, e.name AS name,e.active, e.mrf_id AS mrf,e.date_of_joining,cfy.name as fy,rr.write_date::date AS mrf_app_date,
            CASE WHEN (e.date_of_joining - rr.write_date::date) > 0 THEN (e.date_of_joining - rr.write_date::date)
                    ELSE 0 END AS individual_aging_days
            FROM hr_employee e join kw_recruitment_requisition rr ON rr.id = e.mrf_id
            
                JOIN account_fiscalyear cfy ON e.date_of_joining >= cfy.date_start AND e.date_of_joining <= cfy.date_stop
            where mrf_id is not null and rr.state = 'approve' and cfy.id=%s and e.employement_type not in 
            (SELECT id FROM kwemp_employment_type where code = 'O'))

            
            select (SELECT name FROM kwemp_grade_master WHERE id = a.grade) || '(' || COUNT(a.grade) || ')' AS grade,
                CASE WHEN COUNT(a.grade) > 0 THEN SUM(a.individual_aging_days) / COUNT(a.grade) END AS aging_join
            from a WHERE a.grade IS NOT NULL GROUP BY a.grade 
            ORDER BY grade ASC""", (fiscal_year_id,))
        data = cr.fetchall()
        for row in data:
            grade_name = row[0]
            value = row[1]
            if grade_name in ageing_to_jion_grade_ratio:
                ageing_to_jion_grade_ratio[grade_name] += value
            else:
                ageing_to_jion_grade_ratio[grade_name] = value

        formatted_ageing_to_join_grade = [[grade_name, value] for grade_name, value in ageing_to_jion_grade_ratio.items()]
        return [formatted_ageing_to_join_grade]
    
    @api.model
    def get_dept_ageing_to_join_ratio_count(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        ageing_to_jion_dept_ratio = {}
        cr = self._cr
        cr.execute("""with a as
            (SELECT e.department_id,e.id, e.name AS name,rr.write_date::date AS mrf_app_date,
            CASE WHEN (e.date_of_joining - rr.write_date::date) > 0 THEN (e.date_of_joining - rr.write_date::date)
                    ELSE 0 END AS individual_aging_days
            FROM hr_employee e join kw_recruitment_requisition rr ON rr.id = e.mrf_id 
            JOIN account_fiscalyear cfy ON e.date_of_joining >= cfy.date_start AND e.date_of_joining <= cfy.date_stop
            where e.mrf_id is not null and rr.state = 'approve' and cfy.id=%s and e.employement_type not in 
            (SELECT id FROM kwemp_employment_type where code = 'O'))
            SELECT (SELECT name FROM hr_department WHERE id=a.department_id) || '(' || COUNT(a.department_id) || ')' as department, 
            CASE WHEN COUNT(a.department_id) > 0 THEN SUM(a.individual_aging_days) / COUNT(a.department_id) END AS aging_join
            from a WHERE a.department_id IS NOT NULL GROUP BY a.department_id  """,(fiscal_year_id,))
        data = cr.fetchall()
        for row in data:
            dept_name = row[0]
            value = row[1]
            if dept_name in ageing_to_jion_dept_ratio:
                ageing_to_jion_dept_ratio[dept_name] += value
            else:
                ageing_to_jion_dept_ratio[dept_name] = value

        formatted_ageing_to_join_dept = [[dept_name, value] for dept_name, value in ageing_to_jion_dept_ratio.items()]
        return [formatted_ageing_to_join_dept]
    
    @api.model
    def get_loc_ageing_to_join_ratio_count(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        ageing_to_jion_loc_ratio = {}
        cr = self._cr
        cr.execute("""with a as
            (SELECT e.id,e.base_branch_id, e.name AS name, e.mrf_id AS mrf,e.date_of_joining,cfy.name as fy,rr.write_date::date AS mrf_app_date,
            CASE WHEN (e.date_of_joining - rr.write_date::date) > 0 THEN (e.date_of_joining - rr.write_date::date)
                    ELSE 0 END AS individual_aging_days
            FROM hr_employee e join kw_recruitment_requisition rr ON rr.id = e.mrf_id
            
                JOIN account_fiscalyear cfy ON e.date_of_joining >= cfy.date_start AND e.date_of_joining <= cfy.date_stop
            where mrf_id is not null and rr.state = 'approve' and cfy.id=%s and e.employement_type not in 
            (SELECT id FROM kwemp_employment_type where code = 'O'))

            
            select (SELECT alias FROM kw_res_branch WHERE id = a.base_branch_id) || '(' || COUNT(a.base_branch_id) || ')' AS location,
                CASE WHEN COUNT(a.base_branch_id) > 0 THEN SUM(a.individual_aging_days) / COUNT(a.base_branch_id) END AS aging_join
            from a WHERE a.base_branch_id IS NOT NULL GROUP BY a.base_branch_id  """,(fiscal_year_id,))
        data = cr.fetchall()
        for row in data:
            loc_name = row[0]
            value = row[1]
            if loc_name in ageing_to_jion_loc_ratio:
                ageing_to_jion_loc_ratio[loc_name] += value
            else:
                ageing_to_jion_loc_ratio[loc_name] = value

        formatted_ageing_to_join_loc = [[loc_name, value] for loc_name, value in ageing_to_jion_loc_ratio.items()]
        return [formatted_ageing_to_join_loc]
    
    @api.model
    def get_budget_ageing_to_join_ratio_count(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        ageing_to_jion_budg_ratio = {}
        cr = self._cr
        cr.execute("""with a as
            (SELECT e.id,e.budget_type, e.name AS name, e.mrf_id AS mrf,e.date_of_joining,cfy.name as fy,rr.write_date::date AS mrf_app_date,
            CASE WHEN (e.date_of_joining - rr.write_date::date) > 0 THEN (e.date_of_joining - rr.write_date::date)
                    ELSE 0 END AS individual_aging_days
            FROM hr_employee e join kw_recruitment_requisition rr ON rr.id = e.mrf_id
            
                JOIN account_fiscalyear cfy ON e.date_of_joining >= cfy.date_start AND e.date_of_joining <= cfy.date_stop
            where mrf_id is not null and rr.state = 'approve' and cfy.id=%s and e.employement_type not in 
            (SELECT id FROM kwemp_employment_type where code = 'O'))

            
            select a.budget_type || '(' || COUNT(a.budget_type) || ')' AS budget_type,
                CASE WHEN COUNT(a.budget_type) > 0 THEN SUM(a.individual_aging_days) / COUNT(a.budget_type) END AS aging_join
            from a WHERE a.budget_type IS NOT NULL GROUP BY a.budget_type""",(fiscal_year_id,))
        data = cr.fetchall()
        for row in data:
            budg_data = row[0]
            value = row[1]
            if budg_data in ageing_to_jion_budg_ratio:
                ageing_to_jion_budg_ratio[budg_data] += value
            else:
                ageing_to_jion_budg_ratio[budg_data] = value

        formatted_ageing_to_join_budg = [[budg_data, value] for budg_data, value in ageing_to_jion_budg_ratio.items()]
        return [formatted_ageing_to_join_budg]
    
    @api.model
    def get_resource_ageing_to_join_ratio_count(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        ageing_to_jion_resource_ratio = {}
        cr = self._cr
        cr.execute("""with a as
                (SELECT(select MAX(hr_applicant_offer.offer_type) from hr_applicant_offer inner 
                        join hr_applicant on hr_applicant_offer.applicant_id = hr_applicant.id
                            where hr_applicant.mrf_id = e.mrf_id) AS resource,e.id,e.budget_type, e.name AS name, e.mrf_id AS mrf,e.date_of_joining,cfy.name as fy,rr.write_date::date AS mrf_app_date,
                CASE WHEN (e.date_of_joining - rr.write_date::date) > 0 THEN (e.date_of_joining - rr.write_date::date)
                        ELSE 0 END AS individual_aging_days
                FROM hr_employee e join kw_recruitment_requisition rr ON rr.id = e.mrf_id
                
                    JOIN account_fiscalyear cfy ON e.date_of_joining >= cfy.date_start AND e.date_of_joining <= cfy.date_stop
                where mrf_id is not null and rr.state = 'approve' and cfy.id=%s and e.employement_type not in 
                (SELECT id FROM kwemp_employment_type where code = 'O'))

                
                select resource || '(' || COUNT(a.resource) || ')' AS resource,
                    CASE WHEN COUNT(a.resource) > 0 THEN SUM(a.individual_aging_days) / COUNT(a.resource) END AS aging_join
                from a WHERE a.resource IS NOT NULL and resource in ('Intern','Lateral') GROUP BY a.resource 
                """,(fiscal_year_id,))
        data = cr.fetchall()
        for row in data:
            resou_data = row[0]
            value = row[1]
            if resou_data in ageing_to_jion_resource_ratio:
                ageing_to_jion_resource_ratio[resou_data] += value
            else:
                ageing_to_jion_resource_ratio[resou_data] = value

        formatted_ageing_to_join_resource = [[resou_data, value] for resou_data, value in ageing_to_jion_resource_ratio.items()]
        return [formatted_ageing_to_join_resource]
    
    @api.model
    def get_hiring_ageing_to_join_ratio_count(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        ageing_to_jion_hiri_resource_ratio = {}
        cr = self._cr
        cr.execute("""with a as
                (SELECT rr.resource as hiring_resource,e.id,e.budget_type, e.name AS name,rr.write_date::date AS mrf_app_date,
                CASE WHEN (e.date_of_joining - rr.write_date::date) > 0 THEN (e.date_of_joining - rr.write_date::date)
                        ELSE 0 END AS individual_aging_days
                FROM hr_employee e join kw_recruitment_requisition rr ON rr.id = e.mrf_id
                
                    JOIN account_fiscalyear cfy ON e.date_of_joining >= cfy.date_start AND e.date_of_joining <= cfy.date_stop
                where mrf_id is not null and rr.state = 'approve' and cfy.id=%s and e.employement_type not in 
                (SELECT id FROM kwemp_employment_type where code = 'O'))
                select a.hiring_resource || '(' || COUNT(a.hiring_resource) || ')' AS hiring_resource,
                    CASE WHEN COUNT(a.hiring_resource) > 0 THEN SUM(a.individual_aging_days) / COUNT(a.hiring_resource) END AS aging_join
                from a WHERE a.hiring_resource IS NOT NULL GROUP BY a.hiring_resource """,(fiscal_year_id,))
        data = cr.fetchall()
        for row in data:
            hiri_res = row[0]
            value = row[1]
            if hiri_res in ageing_to_jion_hiri_resource_ratio:
                ageing_to_jion_hiri_resource_ratio[hiri_res] += value
            else:
                ageing_to_jion_hiri_resource_ratio[hiri_res] = value

        formatted_ageing_to_join_hir_resource = [[hiri_res, value] for hiri_res, value in ageing_to_jion_hiri_resource_ratio.items()]
        return [formatted_ageing_to_join_hir_resource]
    
    @api.model
    def get_skill_ageing_to_join_ratio_count(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        ageing_to_jion_skill_resource_ratio = {}
        cr = self._cr
        cr.execute("""with a as
            (SELECT (select name from kw_skill_master where id= e.primary_skill_id) as primary_skill_id,e.id,e.budget_type, e.name AS name,rr.write_date::date AS mrf_app_date,
            CASE WHEN (e.date_of_joining - rr.write_date::date) > 0 THEN (e.date_of_joining - rr.write_date::date)
                    ELSE 0 END AS individual_aging_days
            FROM hr_employee e join kw_recruitment_requisition rr ON rr.id = e.mrf_id
            
                JOIN account_fiscalyear cfy ON e.date_of_joining >= cfy.date_start AND e.date_of_joining <= cfy.date_stop
            where mrf_id is not null and rr.state = 'approve' and cfy.id=%s and e.employement_type not in 
            (SELECT id FROM kwemp_employment_type where code = 'O'))
            select a.primary_skill_id || '(' || COUNT(a.primary_skill_id) || ')' AS prim_skill,
                CASE WHEN COUNT(a.primary_skill_id) > 0 THEN SUM(a.individual_aging_days) / COUNT(a.primary_skill_id) END AS aging_join
            from a WHERE a.primary_skill_id IS NOT NULL GROUP BY a.primary_skill_id """,(fiscal_year_id,))
        data = cr.fetchall()
        for row in data:
            skill_data = row[0]
            value = row[1]
            if skill_data in ageing_to_jion_skill_resource_ratio:
                ageing_to_jion_skill_resource_ratio[skill_data] += value
            else:
                ageing_to_jion_skill_resource_ratio[skill_data] = value

        formatted_ageing_to_join_skill = [[skill_data, value] for skill_data, value in ageing_to_jion_skill_resource_ratio.items()]
        return [formatted_ageing_to_join_skill]
    
    @api.model
    def get_company_ageing_to_join_ratio_count(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        ageing_to_jion_company_ratio = {}
        cr = self._cr
        cr.execute("""with a as
            (SELECT (select name from res_company where id=e.company_id) as company_id,e.id,e.budget_type, e.name AS name,rr.write_date::date AS mrf_app_date,
            CASE WHEN (e.date_of_joining - rr.write_date::date) > 0 THEN (e.date_of_joining - rr.write_date::date)
                    ELSE 0 END AS individual_aging_days
            FROM hr_employee e join kw_recruitment_requisition rr ON rr.id = e.mrf_id
            
            JOIN account_fiscalyear cfy ON e.date_of_joining >= cfy.date_start AND e.date_of_joining <= cfy.date_stop
            where mrf_id is not null and rr.state = 'approve' and cfy.id=%s and e.employement_type not in 
            (SELECT id FROM kwemp_employment_type where code = 'O'))
            
            select a.company_id || '(' || COUNT(a.company_id) || ')' AS company,
                CASE WHEN COUNT(a.company_id) > 0 THEN SUM(a.individual_aging_days) / COUNT(a.company_id) END AS aging_join
            from a WHERE a.company_id IS NOT NULL GROUP BY a.company_id""",(fiscal_year_id,))
        data = cr.fetchall()
        for row in data:
            comp_data = row[0]
            value = row[1]
            if comp_data in ageing_to_jion_company_ratio:
                ageing_to_jion_company_ratio[comp_data] += value
            else:
                ageing_to_jion_company_ratio[comp_data] = value

        formatted_ageing_to_join_company = [[comp_data, value] for comp_data, value in ageing_to_jion_company_ratio.items()]
        return [formatted_ageing_to_join_company]
        
    @api.model
    def get_designation_ageing_to_join_ratio_count(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        ageing_to_jion_desg_ratio = {}
        cr = self._cr
        cr.execute("""with a as
            (SELECT (select name from hr_job where id=e.job_id) as position,e.id,e.budget_type, e.name AS name,rr.write_date::date AS mrf_app_date,
            CASE WHEN (e.date_of_joining - rr.write_date::date) > 0 THEN (e.date_of_joining - rr.write_date::date)
                    ELSE 0 END AS individual_aging_days
            FROM hr_employee e join kw_recruitment_requisition rr ON rr.id = e.mrf_id
            
                JOIN account_fiscalyear cfy ON e.date_of_joining >= cfy.date_start AND e.date_of_joining <= cfy.date_stop
            where mrf_id is not null and rr.state = 'approve' and cfy.id=%s and e.employement_type not in 
            (SELECT id FROM kwemp_employment_type where code = 'O'))
            
            select a.position || '(' || COUNT(a.position) || ')' AS position,
                CASE WHEN COUNT(a.position) > 0 THEN SUM(a.individual_aging_days) / COUNT(a.position) END AS aging_join
            from a WHERE a.position IS NOT NULL GROUP BY a.position""",(fiscal_year_id,))
        data = cr.fetchall()
        for row in data:
            desg_data = row[0]
            value = row[1]
            if desg_data in ageing_to_jion_desg_ratio:
                ageing_to_jion_desg_ratio[desg_data] += value
            else:
                ageing_to_jion_desg_ratio[desg_data] = value

        formatted_ageing_to_join_desg = [[desg_data, value] for desg_data, value in ageing_to_jion_desg_ratio.items()]
        return [formatted_ageing_to_join_desg]
    
    @api.model
    def get_recruiter_ageing_to_join_ratio_count(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        ageing_to_jion_recru_ratio = {}
        cr = self._cr
        cr.execute("""with a as
            (SELECT(select MAX(user_id) from kw_hr_job_positions where id = (select max(job_position) from hr_applicant where mrf_id=e.mrf_id)) AS recruiter,
            e.id, e.name AS name,rr.write_date::date AS mrf_app_date,
            CASE WHEN (e.date_of_joining - rr.write_date::date) > 0 THEN (e.date_of_joining - rr.write_date::date)
            ELSE 0 END AS individual_aging_days
            FROM hr_employee e join kw_recruitment_requisition rr ON rr.id = e.mrf_id
            JOIN account_fiscalyear cfy ON e.date_of_joining >= cfy.date_start AND e.date_of_joining <= cfy.date_stop
            where mrf_id is not null and rr.state = 'approve' and cfy.id=%s and e.employement_type not in 
            (SELECT id FROM kwemp_employment_type where code = 'O'))
            
            select (select name from hr_employee where user_id=recruiter)|| '(' || COUNT(a.recruiter) || ')' AS recruiter,
                CASE WHEN COUNT(a.recruiter) > 0 THEN SUM(a.individual_aging_days) / COUNT(a.recruiter) END AS aging_join
            from a WHERE a.recruiter IS NOT NULL GROUP BY a.recruiter """,(fiscal_year_id,))
        data = cr.fetchall()
        for row in data:
            recru_data = row[0]
            value = row[1]
            if recru_data in ageing_to_jion_recru_ratio:
                ageing_to_jion_recru_ratio[recru_data] += value
            else:
                ageing_to_jion_recru_ratio[recru_data] = value

        formatted_ageing_to_join_company = [[recru_data, value] for recru_data, value in ageing_to_jion_recru_ratio.items()]
        return [formatted_ageing_to_join_company]
    
    
    @api.model
    def get_aging_offer_grade_ratio_count(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        ageing_to_offer_grade = {}
        cr = self._cr
        cr.execute("""with b as (
                with a as (select distinct(rr.id) as mrf_id,rl.write_date::date as mrf_app_date from kw_recruitment_requisition rr 
						   join kw_recruitment_requisition_log rl on 
                rr.id = rl.mrf_id where to_status = 'approve')
                select ho.grade, CASE WHEN (ho.current_date - a.mrf_app_date) > 0 THEN (ho.current_date - a.mrf_app_date)
                ELSE 0 END AS individual_aging_days from hr_applicant_offer ho
                JOIN account_fiscalyear cfy ON ho.create_date BETWEEN cfy.date_start AND cfy.date_stop
                join hr_applicant ha ON ha.id=ho.applicant_id
                JOIN a on a.mrf_id = ha.mrf_id where ha.mrf_id is not null and ho.active=True and cfy.id=%s)

                select (select name from kwemp_grade_master where id = grade) || '(' || COUNT(grade) || ')' as grade,
                case when count(grade) > 0 then 
                sum(individual_aging_days)/count(grade)  end as total_days from b where grade is not null group by grade 
				HAVING SUM(individual_aging_days) / COUNT(grade) > 0""",(fiscal_year_id,))
        data = cr.fetchall()
        for row in data:
            grade_data = row[0]
            value = row[1]
            if grade_data in ageing_to_offer_grade:
                ageing_to_offer_grade[grade_data] += value
            else:
                ageing_to_offer_grade[grade_data] = value

        formatted_ageing_to_offer_grade = [[grade_data, value] for grade_data, value in ageing_to_offer_grade.items()]
        return [formatted_ageing_to_offer_grade]
    
    @api.model
    def get_aging_offer_dept_ratio_count(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        ageing_to_offer_dept = {}
        cr = self._cr
        cr.execute("""with b as (
                with a as (select distinct(rr.id) as mrf_id,rl.write_date::date as mrf_app_date from kw_recruitment_requisition rr join kw_recruitment_requisition_log rl on 
                rr.id = rl.mrf_id where to_status = 'approve')
                
               	select ho.department,CASE WHEN (ho.current_date - a.mrf_app_date) > 0 THEN (ho.current_date - a.mrf_app_date)
                ELSE 0 END AS individual_aging_days from hr_applicant_offer ho
				JOIN account_fiscalyear cfy ON ho.create_date BETWEEN cfy.date_start AND cfy.date_stop
				join hr_applicant ha ON ha.id=ho.applicant_id JOIN a on a.mrf_id = ha.mrf_id 
                where ha.mrf_id is not null and ho.active=True and cfy.id=%s)

                select (select name from hr_department where id=department) || '(' || COUNT(department) || ')' as department,
                case when count(department) > 0 then
                sum(individual_aging_days)/count(department)  end as total_days from b where department is not null group by department
                HAVING SUM(individual_aging_days) / COUNT(department) > 0""",(fiscal_year_id,))
        data = cr.fetchall()
        for row in data:
            dept_data = row[0]
            value = row[1]
            if dept_data in ageing_to_offer_dept:
                ageing_to_offer_dept[dept_data] += value
            else:
                ageing_to_offer_dept[dept_data] = value

        formatted_ageing_to_offer_dept = [[dept_data, value] for dept_data, value in ageing_to_offer_dept.items()]
        return [formatted_ageing_to_offer_dept]
   
    @api.model
    def get_aging_offer_loc_ratio_count(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        ageing_to_offer_location = {}
        cr = self._cr
        cr.execute("""with b as (
                with a as (select distinct(rr.id) as mrf_id,rl.write_date::date as mrf_app_date from kw_recruitment_requisition rr join kw_recruitment_requisition_log rl on 
                rr.id = rl.mrf_id where to_status = 'approve')
                select ho.job_location_id,CASE WHEN (ho.current_date - a.mrf_app_date) > 0 THEN (ho.current_date - a.mrf_app_date)
                ELSE 0 END AS individual_aging_days from hr_applicant_offer ho
                JOIN account_fiscalyear cfy ON ho.create_date BETWEEN cfy.date_start AND cfy.date_stop JOIN hr_applicant ha ON ha.id=ho.applicant_id
                JOIN a on a.mrf_id = ha.mrf_id where ha.mrf_id is not null and ho.active=True and cfy.id=%s )

                SELECT (SELECT alias FROM kw_res_branch WHERE id = (SELECT kw_branch_id FROM kw_recruitment_location WHERE id = job_location_id)) || '(' || COUNT(job_location_id) || ')' AS location,
                CASE WHEN COUNT(job_location_id) > 0 THEN SUM(individual_aging_days) / COUNT(job_location_id)  
                END AS total_days FROM b WHERE job_location_id IS NOT NULL GROUP BY job_location_id HAVING SUM(individual_aging_days) / COUNT(job_location_id) > 0""",(fiscal_year_id,))
        data = cr.fetchall()
        for row in data:
            loc_data = row[0]
            value = row[1]
            if loc_data in ageing_to_offer_location:
                ageing_to_offer_location[loc_data] += value
            else:
                ageing_to_offer_location[loc_data] = value
        formatted_ageing_to_offer_loc = [[loc_data, value] for loc_data, value in ageing_to_offer_location.items()]
        return [formatted_ageing_to_offer_loc]
    
    @api.model
    def get_aging_offer_budget_ratio_count(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        ageing_to_offer_budget = {}
        cr = self._cr
        cr.execute("""with b as (
                with a as (select distinct(rr.id) as mrf_id,rl.write_date::date as mrf_app_date from kw_recruitment_requisition rr join kw_recruitment_requisition_log rl on 
                rr.id = rl.mrf_id where to_status = 'approve')
                
                select (select requisition_type from kw_recruitment_requisition where id= ha.mrf_id) AS budget,CASE WHEN (ho.current_date - a.mrf_app_date) > 0 THEN (ho.current_date - a.mrf_app_date)
                ELSE 0 END AS individual_aging_days from hr_applicant_offer ho
                JOIN account_fiscalyear cfy ON ho.create_date BETWEEN cfy.date_start AND cfy.date_stop
                JOIN hr_applicant ha ON ha.id=ho.applicant_id JOIN a on a.mrf_id = ha.mrf_id where ha.mrf_id is not null and ho.active=True and cfy.id=%s)

                select  budget || '(' || COUNT(budget) || ')' as budget,case when count(budget) > 0 then sum(individual_aging_days)/count(budget)  end as total_days 
                from b where budget is not null group by budget HAVING SUM(individual_aging_days) / COUNT(budget) > 0 """,(fiscal_year_id,))
        data = cr.fetchall()
        for row in data:
            bud_data = row[0]
            value = row[1]
            if bud_data in ageing_to_offer_budget:
                ageing_to_offer_budget[bud_data] += value
            else:
                ageing_to_offer_budget[bud_data] = value
        formatted_ageing_to_offer_budg = [[bud_data, value] for bud_data, value in ageing_to_offer_budget.items()]
        return [formatted_ageing_to_offer_budg]
    
    @api.model
    def get_aging_offer_resource_ratio_count(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        ageing_to_offer_resource = {}
        cr = self._cr
        cr.execute("""with b as (
                    with a as (select distinct(rr.id) as mrf_id,rl.write_date::date as mrf_app_date from kw_recruitment_requisition rr join kw_recruitment_requisition_log rl on 
                    rr.id = rl.mrf_id where to_status = 'approve')
                    select ho.offer_type AS resource,CASE WHEN (ho.current_date - a.mrf_app_date) > 0 THEN (ho.current_date - a.mrf_app_date)
                    ELSE 0 END AS individual_aging_days  from hr_applicant_offer ho 
                    JOIN account_fiscalyear cfy ON ho.create_date BETWEEN cfy.date_start AND cfy.date_stop
                    join hr_applicant ha ON ha.id= ho.applicant_id
                    join a on a.mrf_id = ha.mrf_id where cfy.id=%s )
                    select resource || '(' || COUNT(resource) || ')' as resource,case when count(resource) > 0 then sum(individual_aging_days)/count(resource)   end as total_days from b where resource in ('Intern','Lateral') 
                    and resource is not null
                    group by resource HAVING SUM(individual_aging_days) / COUNT(resource) > 0""",(fiscal_year_id,))
        data = cr.fetchall()
        for row in data:
            reso_data = row[0]
            value = row[1]
            if reso_data in ageing_to_offer_resource:
                ageing_to_offer_resource[reso_data] += value
            else:
                ageing_to_offer_resource[reso_data] = value
        formatted_ageing_to_offer_resource = [[reso_data, value] for reso_data, value in ageing_to_offer_resource.items()]
        return [formatted_ageing_to_offer_resource]
    
    @api.model
    def get_aging_offer_hire_ratio_count(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        ageing_to_offer_hire = {}
        cr = self._cr
        cr.execute("""with b as (
                with a as (select distinct(rr.id) as mrf_id,rl.write_date::date as mrf_app_date from kw_recruitment_requisition rr join kw_recruitment_requisition_log rl on 
                rr.id = rl.mrf_id where to_status = 'approve')
                select (select resource from kw_recruitment_requisition where id=ha.mrf_id) as hiring_resource,
                CASE WHEN (ho.current_date - a.mrf_app_date) > 0 THEN (ho.current_date - a.mrf_app_date)
                ELSE 0 END AS individual_aging_days ,cfy.name as fy from hr_applicant_offer ho
                JOIN account_fiscalyear cfy ON ho.create_date BETWEEN cfy.date_start AND cfy.date_stop 
                join hr_applicant ha ON ha.id=ho.applicant_id
                join a on a.mrf_id = ha.mrf_id where cfy.id=%s)
                select hiring_resource || '(' || COUNT(hiring_resource) || ')' as hire_type,
                case when count(hiring_resource) > 0 then
                sum(individual_aging_days)/count(hiring_resource) end as total_days from b where hiring_resource is not null group by hiring_resource
                HAVING SUM(individual_aging_days) / COUNT(hiring_resource) > 0""",(fiscal_year_id,))
        data = cr.fetchall()
        for row in data:
            hire_data = row[0]
            value = row[1]
            if hire_data in ageing_to_offer_hire:
                ageing_to_offer_hire[hire_data] += value
            else:
                ageing_to_offer_hire[hire_data] = value
        formatted_ageing_to_offer_hire = [[hire_data, value] for hire_data, value in ageing_to_offer_hire.items()]
        return [formatted_ageing_to_offer_hire]
    
    @api.model
    def get_aging_offer_skill_ratio_count(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        ageing_to_offer_skill = {}
        cr = self._cr
        cr.execute("""with b as (
                    WITH a AS (
                    SELECT DISTINCT rr.id AS mrf_id,rl.write_date::date AS mrf_app_date FROM kw_recruitment_requisition rr
                    JOIN kw_recruitment_requisition_log rl ON rr.id = rl.mrf_id WHERE to_status = 'approve')
                    SELECT (SELECT name FROM kw_skill_master WHERE id = has.kw_skill_master_id) AS skill,
                    CASE WHEN (ho.current_date - a.mrf_app_date) > 0 THEN (ho.current_date - a.mrf_app_date)
                        ELSE 0 END AS individual_aging_days
                    FROM hr_applicant_offer ho JOIN account_fiscalyear cfy ON ho.create_date BETWEEN cfy.date_start AND cfy.date_stop
                    JOIN hr_applicant ha ON ha.id = ho.applicant_id JOIN hr_applicant_kw_skill_master_rel has ON has.hr_applicant_id = ha.id 
                    JOIN a ON a.mrf_id = ha.mrf_id where has.kw_skill_master_id is not null and cfy.id=%s)
                    
                    select skill || '(' || COUNT(skill) || ')' as skill,case when count(skill) > 0 then sum(individual_aging_days)/count(skill) end as total_days from b where skill is not null  
                    group by skill HAVING SUM(individual_aging_days) / COUNT(skill) > 0
		            """,(fiscal_year_id,))
        data = cr.fetchall()
        for row in data:
            skill_data = row[0]
            value = row[1]
            if skill_data in ageing_to_offer_skill:
                ageing_to_offer_skill[skill_data] += value
            else:
                ageing_to_offer_skill[skill_data] = value
        formatted_ageing_to_offer_skill = [[skill_data, value] for skill_data, value in ageing_to_offer_skill.items()]
        return [formatted_ageing_to_offer_skill]
    
    @api.model
    def get_aging_offer_company_ratio_count(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        ageing_to_offer_company = {}
        cr = self._cr
        cr.execute("""with b as (
                    with a as (select distinct(rr.id) as mrf_id,rl.write_date::date as mrf_app_date from kw_recruitment_requisition rr join kw_recruitment_requisition_log rl on 
                    rr.id = rl.mrf_id where to_status = 'approve')
                    select (select name from res_company where id=(select company_id from kw_res_branch where id=ho.job_location)) as company_id,
                    CASE WHEN (ho.current_date - a.mrf_app_date) > 0 THEN (ho.current_date - a.mrf_app_date)
                        ELSE 0 END AS individual_aging_days from hr_applicant_offer ho 
                    JOIN account_fiscalyear cfy ON ho.create_date BETWEEN cfy.date_start AND cfy.date_stop
                    join hr_applicant ha ON ha.id= ho.applicant_id
                    join a on a.mrf_id = ha.mrf_id where cfy.id=%s)
                
                    select company_id || '(' || COUNT(company_id) || ')' as company_id,
                    case when count(company_id) > 0 then 
                    sum(individual_aging_days)/count(company_id)   end as total_days from b where company_id is not null 
                    group by company_id HAVING SUM(individual_aging_days) / COUNT(company_id) > 0""",(fiscal_year_id,))
        data = cr.fetchall()
        for row in data:
            comp_data = row[0]
            value = row[1]
            if comp_data in ageing_to_offer_company:
                ageing_to_offer_company[comp_data] += value
            else:
                ageing_to_offer_company[comp_data] = value
        formatted_ageing_to_offer_comp = [[comp_data, value] for comp_data, value in ageing_to_offer_company.items()]
        return [formatted_ageing_to_offer_comp]
    
    @api.model
    def get_aging_offer_desgination_ratio_count(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        ageing_to_offer_desg = {}
        cr = self._cr
        cr.execute("""with b as (
                    with a as (select distinct(rr.id) as mrf_id,rl.write_date::date as mrf_app_date from kw_recruitment_requisition rr join kw_recruitment_requisition_log rl on 
                    rr.id = rl.mrf_id where to_status = 'approve')
                    select (select name from hr_job where id=ho.designation) as position,CASE WHEN (ho.current_date - a.mrf_app_date) > 0 THEN (ho.current_date - a.mrf_app_date)
                        ELSE 0 END AS individual_aging_days
                    from hr_applicant_offer ho JOIN account_fiscalyear cfy ON ho.create_date BETWEEN cfy.date_start AND cfy.date_stop
                    join hr_applicant ha ON ha.id=ho.applicant_id
                    join a on a.mrf_id = ha.mrf_id where cfy.id=%s)

                    select position || '(' || COUNT(position) || ')' as position,
                    case when count(position) > 0 then 
                    sum(individual_aging_days)/count(position)  end  as total_days from b where position is not null
                    group by position HAVING SUM(individual_aging_days) / COUNT(position) > 0""",(fiscal_year_id,))
        data = cr.fetchall()
        for row in data:
            desg_data = row[0]
            value = row[1]
            if desg_data in ageing_to_offer_desg:
                ageing_to_offer_desg[desg_data] += value
            else:
                ageing_to_offer_desg[desg_data] = value
        formatted_ageing_to_offer_desg = [[desg_data, value] for desg_data, value in ageing_to_offer_desg.items()]
        return [formatted_ageing_to_offer_desg]
    
    @api.model
    def get_aging_offer_recruiter_ratio_count(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        ageing_to_offer_recruiter = {}
        cr = self._cr
        cr.execute("""with b as (
                with a as (select distinct(rr.id) as mrf_id,rl.write_date::date as mrf_app_date from kw_recruitment_requisition rr join kw_recruitment_requisition_log rl on 
                rr.id = rl.mrf_id where to_status = 'approve')
                select (select user_id from kw_hr_job_positions where id =ha.job_position ) AS recruiter,
                CASE WHEN (ho.current_date - a.mrf_app_date) > 0 THEN (ho.current_date - a.mrf_app_date)
                ELSE 0 END AS individual_aging_days from hr_applicant_offer ho
                JOIN account_fiscalyear cfy ON ho.create_date BETWEEN cfy.date_start AND cfy.date_stop
                join hr_applicant ha ON ha.id=ho.applicant_id
                join a on a.mrf_id = ha.mrf_id where cfy.id=%s)
                select (select name from hr_employee where user_id=recruiter)|| '(' || COUNT(recruiter) || ')' as recruiter,
                case when count(recruiter) > 0 then 
                sum(individual_aging_days)/count(recruiter)  end as total_days from b where recruiter is not null
                group by recruiter HAVING SUM(individual_aging_days) / COUNT(recruiter) > 0 """,(fiscal_year_id,))
       
        data = cr.fetchall()
        for row in data:
            rec_data = row[0]
            value = row[1]
            if rec_data in ageing_to_offer_recruiter:
                ageing_to_offer_recruiter[rec_data] += value
            else:
                ageing_to_offer_recruiter[rec_data] = value
        formatted_ageing_to_offer_recr = [[rec_data, value] for rec_data, value in ageing_to_offer_recruiter.items()]
        return [formatted_ageing_to_offer_recr]
    
    @api.model
    def get_source_hire_success_level_rate(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        success_rate_level = []
        cr = self._cr
        cr.execute("""with b as (
                    with a as (select count(*),us.name from utm_source us join hr_employee he ON he.emp_refered=us.id 
			JOIN kwonboard_enrollment k ON k.id=he.onboarding_id join hr_applicant h ON h.id=k.applicant_id
			where us.active=true and he.active=true  group by us.name)
            select a.count as source,count(level),(select name from utm_source where he.emp_refered=id) as emp_refered, he.level as level from hr_employee he 
            join kwonboard_enrollment k ON k.id=he.onboarding_id join hr_applicant h ON h.id=k.applicant_id 
            JOIN account_fiscalyear cfy ON he.create_date BETWEEN cfy.date_start AND cfy.date_stop
            join utm_source us ON us.id=he.emp_refered
            join a on a.name = us.name
            where he.active=true and cfy.id=%s and he.emp_refered is not null and he.level is not null group by level,emp_refered,source)

            select emp_refered,(select name from kw_grade_level where id = level)  as level,
            Round((count * 100.0 / source))  AS hire_success_rate
            from b group by level,source,count,emp_refered order by level asc """,(fiscal_year_id,))
       
        data = cr.fetchall()
        for row in data:
            rec_data = row[0]
            value = row[1]
            rate = row[2]
            success_rate_level.append({
                'name':  value,
                'category':rec_data ,
                'data': rate
            })
        return success_rate_level
    
    @api.model
    def get_source_hire_success_grade_rate(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        success_rate_grade = []
        cr = self._cr
        cr.execute("""with b as (
		    with a as (select count(*),us.name from utm_source us join hr_employee he ON he.emp_refered=us.id 
			JOIN kwonboard_enrollment k ON k.id=he.onboarding_id join hr_applicant h ON h.id=k.applicant_id
			where us.active=true and he.active=true  group by us.name)
            select a.count as source,count(grade),(select name from utm_source where he.emp_refered=id) as emp_refered, he.grade as grade from hr_employee he 
            join kwonboard_enrollment k ON k.id=he.onboarding_id join hr_applicant h ON h.id=k.applicant_id 
            JOIN account_fiscalyear cfy ON he.create_date BETWEEN cfy.date_start AND cfy.date_stop
            join utm_source us ON us.id=he.emp_refered
            join a on a.name = us.name
            where he.active=true and cfy.id=%s and he.emp_refered is not null and he.grade is not null group by grade,emp_refered,source)

            select emp_refered,(select name from kwemp_grade_master where id = grade)  as grade,
            Round((count * 100.0 / source))  AS hire_success_rate
            from b group by grade,source,count,emp_refered order by grade asc """,(fiscal_year_id,))
       
        data = cr.fetchall()
        for row in data:
            rec_data = row[0]
            value = row[1]
            rate = row[2]
            success_rate_grade.append({
                'name':  value,
                'category': rec_data,
                'data': rate
            })
        return success_rate_grade
    
    @api.model
    def get_source_hire_success_depart_rate(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        success_rate_department = []
        cr = self._cr
        cr.execute("""with b as (
		    with a as (select count(*),us.name from utm_source us join hr_employee he ON he.emp_refered=us.id 
			JOIN kwonboard_enrollment k ON k.id=he.onboarding_id join hr_applicant h ON h.id=k.applicant_id
			where us.active=true and he.active=true  group by us.name)
            select a.count as source,count(he.department_id),(select name from utm_source where he.emp_refered=id) as emp_refered, he.department_id as department from hr_employee he 
            join kwonboard_enrollment k ON k.id=he.onboarding_id join hr_applicant h ON h.id=k.applicant_id 
            JOIN account_fiscalyear cfy ON he.create_date BETWEEN cfy.date_start AND cfy.date_stop
            join utm_source us ON us.id=he.emp_refered
            join a on a.name = us.name
            where he.active=true and cfy.id=%s and he.emp_refered is not null and he.department_id is not null group by department,emp_refered,source)

            select emp_refered,(select name from hr_department where id = department)  as department,
            Round((count * 100.0 / source))  AS hire_success_rate
            from b group by department,source,count,emp_refered order by department asc """,(fiscal_year_id,))
       
        data = cr.fetchall()
        for row in data:
            rec_data = row[0]
            value = row[1]
            rate = row[2]
            success_rate_department.append({
                'name':  value,
                'category': rec_data,
                'data': rate
            })
        return success_rate_department
    
    
    @api.model
    def get_source_hire_success_location_rate(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        success_rate_location = []
        cr = self._cr
        cr.execute("""WITH a AS (
                SELECT COUNT(*) AS source_count,us.name AS source_name 
                FROM utm_source us JOIN hr_employee he ON he.emp_refered = us.id 
                JOIN kwonboard_enrollment k ON k.id = he.onboarding_id 
                JOIN hr_applicant h ON h.id = k.applicant_id
                WHERE us.active = true AND he.active = true 
                GROUP BY us.name),
            b AS (SELECT a.source_count AS source,COUNT(he.base_branch_id) AS count,
                us.name AS emp_refered, he.base_branch_id AS location FROM hr_employee he 
                JOIN kwonboard_enrollment k ON k.id = he.onboarding_id 
                JOIN hr_applicant h ON h.id = k.applicant_id 
            JOIN account_fiscalyear cfy ON he.create_date BETWEEN cfy.date_start AND cfy.date_stop
                JOIN utm_source us ON us.id = he.emp_refered JOIN a ON a.source_name = us.name
                WHERE he.active = true AND cfy.id=%s AND he.emp_refered IS NOT NULL AND he.base_branch_id IS NOT NULL 
                GROUP BY he.base_branch_id, emp_refered, source, us.name)
            SELECT emp_refered,(SELECT name FROM kw_res_branch WHERE id = b.location) AS location,
                ROUND((b.count * 100.0 / b.source)) AS hire_success_rate
            FROM b GROUP BY emp_refered, location, b.count, b.source ORDER BY location ASC""",(fiscal_year_id,))
       
        data = cr.fetchall()
        for row in data:
            rec_data = row[0]
            value = row[1]
            rate = row[2]
            success_rate_location.append({
                'name': value,
                'category': rec_data ,
                'data': rate
            })
        return success_rate_location
    
    @api.model
    def get_source_hire_success_budget_rate(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        success_rate_budg_type = []
        cr = self._cr
        cr.execute("""with b as (
		    with a as (select count(*),us.name from utm_source us join hr_employee he ON he.emp_refered=us.id 
			JOIN kwonboard_enrollment k ON k.id=he.onboarding_id join hr_applicant h ON h.id=k.applicant_id
			where us.active=true and he.active=true  group by us.name)
            select a.count as source,count(he.budget_type),(select name from utm_source where he.emp_refered=id) as emp_refered, he.budget_type as budget from hr_employee he 
            join kwonboard_enrollment k ON k.id=he.onboarding_id join hr_applicant h ON h.id=k.applicant_id 
            JOIN account_fiscalyear cfy ON he.create_date BETWEEN cfy.date_start AND cfy.date_stop
            join utm_source us ON us.id=he.emp_refered
            join a on a.name = us.name
            where he.active=true and cfy.id=%s and he.emp_refered is not null and he.budget_type is not null group by he.budget_type,emp_refered,source)

            select emp_refered,budget  as budget,
            Round((count * 100.0 / source))  AS hire_success_rate
            from b group by budget,source,count,emp_refered """,(fiscal_year_id,))
       
        data = cr.fetchall()
        for row in data:
            rec_data = row[0]
            value = row[1]
            rate = row[2]
            success_rate_budg_type.append({
                'name':  value,
                'category': rec_data,
                'data': rate
            })
        return success_rate_budg_type
    
    @api.model
    def get_source_hire_success_resource_rate(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        success_rate_resource = []
        cr = self._cr
        cr.execute("""WITH b as (
            WITH a AS (SELECT COUNT(*) AS count, us.name FROM utm_source us JOIN hr_employee he ON he.emp_refered = us.id
            JOIN kwonboard_enrollment k ON k.id = he.onboarding_id JOIN hr_applicant h ON h.id = k.applicant_id 
            WHERE us.active = true AND he.active = true GROUP BY us.name)
            SELECT a.count AS source_count, a.name AS source, COUNT(hao.offer_type),hao.offer_type as resource
            FROM hr_applicant_offer hao JOIN hr_applicant ha ON hao.applicant_id = ha.id JOIN kwonboard_enrollment k ON k.applicant_id = ha.id
            JOIN hr_employee he1 ON he1.onboarding_id = k.id
            JOIN account_fiscalyear cfy ON he1.create_date BETWEEN cfy.date_start AND cfy.date_stop
            JOIN utm_source us ON us.id = he1.emp_refered JOIN a ON a.name = us.name 
            where hao.offer_type in ('Intern','Lateral') and he1.active=True and cfy.id=%s group by a.count,a.name,hao.offer_type)
			
            select source,resource  as resource,  Round((count * 100.0 / source_count))  AS hire_success_rate
			from b group by resource,source_count,source,count""",(fiscal_year_id,))
       
        data = cr.fetchall()
        for row in data:
            rec_data = row[0]
            value = row[1]
            rate = row[2]
            success_rate_resource.append({
                'name':  value,
                'category': rec_data,
                'data': rate
            })
        return success_rate_resource
    
    @api.model
    def get_source_hire_success_hiring_res_rate(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        success_rate_hireres = []
        cr = self._cr
        cr.execute("""with b as (
		with a as (SELECT COUNT(*) AS count, us.name FROM utm_source us JOIN hr_employee he ON he.emp_refered = us.id
        JOIN kwonboard_enrollment k ON k.id = he.onboarding_id JOIN hr_applicant h ON h.id = k.applicant_id 
        WHERE us.active = true AND he.active = true GROUP BY us.name)
		select a.count as sc, a.name as source, count(resource),resource from kw_recruitment_requisition krr join hr_employee e on e.mrf_id=krr.id 
		JOIN account_fiscalyear cfy ON e.create_date BETWEEN cfy.date_start AND cfy.date_stop
		JOIN utm_source us ON us.id=e.emp_refered
		JOIN a on a.name = us.name where e.active=True and cfy.id=%s group by a.count, a.name,resource)
		select source,resource as hire_resource,
		 Round((count * 100.0 / sc))  AS hire_success_rate from b group by count,resource,source,sc""",(fiscal_year_id,))
       
        data = cr.fetchall()
        for row in data:
            rec_data = row[0]
            value = row[1]
            rate = row[2]
            success_rate_hireres.append({
                'name':  value,
                'category': rec_data,
                'data': rate
            })
        return success_rate_hireres
    
    @api.model
    def get_source_hire_success_skill_rate(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        success_rate_skill = []
        cr = self._cr
        cr.execute("""with b as (
	            with a as (SELECT COUNT(*) AS count, us.name FROM utm_source us JOIN hr_employee he ON he.emp_refered = us.id
                JOIN kwonboard_enrollment k ON k.id = he.onboarding_id JOIN hr_applicant h ON h.id = k.applicant_id 
                WHERE us.active = true AND he.active = true GROUP BY us.name)
            select a.count as sc,a.name as source,count(ksm.name),ksm.name from kw_skill_master ksm join hr_employee e on ksm.id= e.primary_skill_id join kwonboard_enrollment k ON k.id = e.onboarding_id 
            JOIN hr_applicant h ON h.id = k.applicant_id JOIN account_fiscalyear cfy ON e.create_date BETWEEN cfy.date_start AND cfy.date_stop
            join utm_source us ON us.id=e.emp_refered
            JOIN a on a.name = us.name where e.active=True and us.active = true and cfy.id=%s group by ksm.name,a.count,a.name)
            select source,name  as skill,
            Round((count * 100.0 / sc))  AS hire_success_rate from b group by count,name,sc,source""",(fiscal_year_id,))
       
        data = cr.fetchall()
        for row in data:
            rec_data = row[0]
            value = row[1]
            rate = row[2]
            success_rate_skill.append({
                'name':  value,
                'category': rec_data,
                'data': rate
            })
        return success_rate_skill
    
    @api.model
    def get_source_hire_success_company_rate(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        success_rate_company = []
        cr = self._cr
        cr.execute("""with b as (
            with a as (SELECT COUNT(*) AS count, us.name FROM utm_source us JOIN hr_employee he ON he.emp_refered = us.id
            JOIN kwonboard_enrollment k ON k.id = he.onboarding_id JOIN hr_applicant h ON h.id = k.applicant_id 
            WHERE us.active = true AND he.active = true GROUP BY us.name)
            
            select a.count as sc, a.name as source, count(rc.id),rc.name from res_company rc join hr_employee e on e.company_id=rc.id join kwonboard_enrollment k ON k.id = e.onboarding_id JOIN hr_applicant h ON h.id = k.applicant_id 
            JOIN account_fiscalyear cfy ON e.create_date BETWEEN cfy.date_start AND cfy.date_stop
            JOIN utm_source us on us.id=e.emp_refered JOIN a on a.name = us.name where e.active=True and us.active=True and cfy.id=%s group by a.count,a.name,rc.name )
            
            select source,name  as company_id,
            Round((count * 100.0 / sc))  AS hire_success_rate from b group by count,sc,source,name""",(fiscal_year_id,))
       
        data = cr.fetchall()
        for row in data:
            rec_data = row[0]
            value = row[1]
            rate = row[2]
            success_rate_company.append({
                'name':  value,
                'category': rec_data,
                'data': rate
            })
        return success_rate_company
    
    @api.model
    def get_source_hire_success_designation_rate(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        success_rate_desg = []
        cr = self._cr
        cr.execute("""with b as (
           with a as (SELECT COUNT(*) AS count, us.name FROM utm_source us JOIN hr_employee he ON he.emp_refered = us.id
        JOIN kwonboard_enrollment k ON k.id = he.onboarding_id JOIN hr_applicant h ON h.id = k.applicant_id 
        WHERE us.active = true AND he.active = true GROUP BY us.name)
		select a.count as sc,a.name as source, count(e.job_id),(select name from hr_job where id=e.job_id) as position from hr_employee e  JOIN kwonboard_enrollment k ON k.id = e.onboarding_id JOIN hr_applicant h ON h.id = k.applicant_id 
		JOIN account_fiscalyear cfy ON e.create_date BETWEEN cfy.date_start AND cfy.date_stop join utm_source us on us.id=e.emp_refered
		JOIN a on a.name = us.name where cfy.id=%s and e.active=True and us.active=True and e.emp_refered is not null group by a.count,a.name,e.job_id)

        select source,position as position,
        Round((count * 100.0 / sc))  AS hire_success_rate from b group by position,count,sc,source""",(fiscal_year_id,))
       
        data = cr.fetchall()
        for row in data:
            rec_data = row[0]
            value = row[1]
            rate = row[2]
            success_rate_desg.append({
                'name':  value,
                'category': rec_data,
                'data': rate
            })
        return success_rate_desg
    
    @api.model
    def get_source_hire_success_recruiter_rate(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        success_rate_recu = []
        cr = self._cr
        cr.execute("""with b as (
		with a as (SELECT COUNT(*) AS count, us.name FROM utm_source us JOIN hr_employee he ON he.emp_refered = us.id
        JOIN kwonboard_enrollment k ON k.id = he.onboarding_id JOIN hr_applicant h ON h.id = k.applicant_id 
        WHERE us.active = true AND he.active = true GROUP BY us.name)
		
		select a.count as sc,a.name as source, count(kjp.user_id),(select name from hr_employee where user_id=kjp.user_id) as recu from kw_hr_job_positions kjp join hr_applicant ha ON ha.job_position=kjp.id
		join kwonboard_enrollment k ON k.applicant_id=ha.id join hr_employee e on e.onboarding_id=k.id 
		JOIN account_fiscalyear cfy ON e.create_date BETWEEN cfy.date_start AND cfy.date_stop join utm_source us on us.id=e.emp_refered
		JOIN a on a.name = us.name where cfy.id=%s and e.active=True and kjp.is_published=true and e.emp_refered is not null group by a.count,a.name,kjp.user_id)
		select source,recu  as recruiter,
		 Round((count * 100.0 / sc))  AS hire_success_rate from b group by count,sc,source,recu""",(fiscal_year_id,))
       
        data = cr.fetchall()
        for row in data:
            rec_data = row[0]
            value = row[1]
            rate = row[2]
            success_rate_recu.append({
                'name':  value,
                'category': rec_data,
                'data': rate
            })
        return success_rate_recu
    
    @api.model
    def get_offer_to_join_grade_ratio(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        offer_join_ratio_grade = []
        cr = self._cr
        cr.execute("""WITH offer_counts AS (
                SELECT hao.grade AS grade,
                    COUNT(*) AS offer_count FROM hr_applicant_offer hao 
                JOIN hr_applicant ha ON hao.applicant_id = ha.id 
                JOIN hr_recruitment_stage hs ON ha.stage_id = hs.id
                JOIN account_fiscalyear cfy ON ha.create_date BETWEEN cfy.date_start AND cfy.date_stop 
                WHERE hs.code = 'OR' and cfy.id=%s
                GROUP BY hao.grade),
            joined_counts AS (
                SELECT hao.grade AS grade,COUNT(*) AS joined_count FROM 
                hr_applicant_offer hao JOIN hr_applicant ha ON hao.applicant_id = ha.id JOIN kwonboard_enrollment k ON ha.id = k.applicant_id
                JOIN hr_employee he ON k.id = he.onboarding_id JOIN hr_recruitment_stage hs ON ha.stage_id = hs.id JOIN account_fiscalyear cfy ON ha.create_date BETWEEN cfy.date_start AND cfy.date_stop 
                WHERE cfy.id=%s and hs.code = 'OA' and he.active=True and hao.grade = he.grade GROUP BY hao.grade)
            SELECT 
                (SELECT name FROM kwemp_grade_master WHERE id = COALESCE(oc.grade, jc.grade)) AS grade,
                COALESCE(oc.offer_count, 0) + COALESCE(jc.joined_count, 0) AS released_count,
                COALESCE(jc.joined_count, 0) AS joined_count
            FROM 
                offer_counts oc
            FULL OUTER JOIN 
                joined_counts jc ON oc.grade = jc.grade
                """,(fiscal_year_id, fiscal_year_id))
       
        data = cr.fetchall()
        for row in data:
            rec_data = row[0]
            value = row[1]
            rate = row[2]
            offer_join_ratio_grade.append({
                'name': rec_data,
                'category': value,
                'data': rate
            })
        return offer_join_ratio_grade
    
    @api.model
    def get_offer_to_join_dept_ratio(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        offer_join_ratio_dept = []
        cr = self._cr
        cr.execute("""WITH offer_counts AS (
                SELECT ha.department_id AS department,
                    COUNT(*) AS offer_count FROM hr_applicant ha JOIN hr_recruitment_stage hs ON ha.stage_id = hs.id
                JOIN account_fiscalyear cfy ON ha.create_date BETWEEN cfy.date_start AND cfy.date_stop WHERE hs.code = 'OR' and cfy.id=%s GROUP BY ha.department_id),
            joined_counts AS (
                SELECT ha.department_id as department,COUNT(*) AS joined_count FROM 
                hr_applicant ha JOIN kwonboard_enrollment k ON ha.id = k.applicant_id
                JOIN hr_employee he ON k.id = he.onboarding_id JOIN hr_recruitment_stage hs ON ha.stage_id = hs.id JOIN account_fiscalyear cfy ON ha.create_date BETWEEN cfy.date_start AND cfy.date_stop 
                WHERE cfy.id=%s and hs.code = 'OA' and ha.department_id = he.department_id  and he.active=True GROUP BY ha.department_id)
            SELECT 
                (SELECT name FROM hr_department WHERE id = COALESCE(oc.department, jc.department)) AS department,
                COALESCE(oc.offer_count, 0) + COALESCE(jc.joined_count, 0) AS released_count,
                COALESCE(jc.joined_count, 0) AS joined_count
            FROM offer_counts oc FULL OUTER JOIN joined_counts jc ON oc.department = jc.department
            """,(fiscal_year_id,fiscal_year_id))
       
        data = cr.fetchall()
        for row in data:
            rec_data = row[0]
            value = row[1]
            rate = row[2]
            offer_join_ratio_dept.append({
                'name': rec_data,
                'category': value,
                'data': rate
            })
        return offer_join_ratio_dept
    
    @api.model
    def get_offer_to_join_loc_ratio(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        off_join_loc_ratio = []
        cr = self._cr
        cr.execute("""WITH offer_counts AS (
                SELECT ha.job_location_id AS location,
                    COUNT(*) AS offer_count FROM hr_applicant ha 
                JOIN hr_recruitment_stage hs ON ha.stage_id = hs.id
                JOIN account_fiscalyear cfy ON ha.create_date BETWEEN cfy.date_start AND cfy.date_stop 
                WHERE hs.code = 'OR' and cfy.id=%s
                GROUP BY ha.job_location_id),
            joined_counts AS (
                SELECT ha.job_location_id as location,COUNT(*) AS joined_count FROM 
                hr_applicant ha JOIN kwonboard_enrollment k ON ha.id = k.applicant_id
                JOIN hr_employee he ON k.id = he.onboarding_id JOIN hr_recruitment_stage hs ON ha.stage_id = hs.id JOIN account_fiscalyear cfy ON ha.create_date BETWEEN cfy.date_start AND cfy.date_stop 
                WHERE cfy.id=%s and hs.code = 'OA' and he.active=True GROUP BY ha.job_location_id)
            SELECT 
                (SELECT name FROM kw_recruitment_location WHERE id = COALESCE(oc.location, jc.location)) AS location,
                COALESCE(oc.offer_count, 0) + COALESCE(jc.joined_count, 0) AS released_count,
                COALESCE(jc.joined_count, 0) AS joined_count
            FROM offer_counts oc FULL OUTER JOIN joined_counts jc ON oc.location = jc.location
	        """,(fiscal_year_id,fiscal_year_id))
        # and he.job_branch_id=(select kw_branch_id from kw_recruitment_location where id=ha.job_location_id) 
        data = cr.fetchall()
        for row in data:
            rec_data = row[0]
            value = row[1]
            rate = row[2]
            off_join_loc_ratio.append({
                'name': rec_data,
                'category': value,
                'data': rate
            })
        return off_join_loc_ratio
    
    @api.model
    def get_offer_to_join_budget_ratio(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        off_join_budget_ratio = []
        cr = self._cr
        cr.execute("""WITH offer_counts AS (
                SELECT kr.requisition_type as requisition_type,
                    COUNT(*) AS offer_count FROM kw_recruitment_requisition kr Join hr_applicant ha ON ha.mrf_id=kr.id
                JOIN hr_recruitment_stage hs ON ha.stage_id = hs.id
                JOIN account_fiscalyear cfy ON ha.create_date BETWEEN cfy.date_start AND cfy.date_stop 
                WHERE hs.code = 'OR' and cfy.id=%s GROUP BY  kr.requisition_type ),
            joined_counts AS (
                SELECT kr.requisition_type as requisition_type,COUNT(*) AS joined_count  FROM kw_recruitment_requisition kr Join hr_applicant ha ON ha.mrf_id=kr.id
                JOIN kwonboard_enrollment k ON ha.id = k.applicant_id JOIN hr_employee he ON k.id = he.onboarding_id 
                JOIN hr_recruitment_stage hs ON ha.stage_id = hs.id JOIN account_fiscalyear cfy ON ha.create_date BETWEEN cfy.date_start AND cfy.date_stop 
                WHERE hs.code = 'OA' and he.active=True and cfy.id=%s GROUP BY kr.requisition_type)
            SELECT 
                COALESCE(oc.requisition_type, jc.requisition_type) AS requisition_type,
                COALESCE(oc.offer_count, 0) + COALESCE(jc.joined_count, 0) AS released_count,
                COALESCE(jc.joined_count, 0) AS joined_count
            FROM 
                offer_counts oc 
            FULL OUTER JOIN 
                joined_counts jc ON oc.requisition_type = jc.requisition_type 
	        """,(fiscal_year_id,fiscal_year_id))
       
        data = cr.fetchall()
        for row in data:
            rec_data = row[0]
            value = row[1]
            rate = row[2]
            off_join_budget_ratio.append({
                'name': rec_data,
                'category': value,
                'data': rate
            })
        return off_join_budget_ratio
    
    @api.model
    def get_offer_to_join_resource_ratio(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        off_join_resource_ratio = []
        cr = self._cr
        cr.execute("""WITH offer_counts AS (
                SELECT hao.offer_type AS resource,
                    COUNT(*) AS offer_count FROM hr_applicant_offer hao 
                JOIN hr_applicant ha ON hao.applicant_id = ha.id 
                JOIN hr_recruitment_stage hs ON ha.stage_id = hs.id
                JOIN account_fiscalyear cfy ON ha.create_date BETWEEN cfy.date_start AND cfy.date_stop 
                WHERE hs.code = 'OR' and cfy.id=%s
                GROUP BY hao.offer_type),
            joined_counts AS (
                SELECT hao.offer_type AS resource,COUNT(*) AS joined_count FROM 
                hr_applicant_offer hao JOIN hr_applicant ha ON hao.applicant_id = ha.id JOIN kwonboard_enrollment k ON ha.id = k.applicant_id
                JOIN hr_employee he ON k.id = he.onboarding_id JOIN hr_recruitment_stage hs ON ha.stage_id = hs.id JOIN account_fiscalyear cfy ON ha.create_date BETWEEN cfy.date_start AND cfy.date_stop 
                WHERE  hs.code = 'OA' and cfy.id=%s  and he.active=True GROUP BY hao.offer_type)
            SELECT 
                COALESCE(oc.resource, jc.resource) AS resource,
                COALESCE(oc.offer_count, 0) + COALESCE(jc.joined_count, 0) AS released_count,
                COALESCE(jc.joined_count, 0) AS joined_count
            FROM 
                offer_counts oc 
            FULL OUTER JOIN 
                joined_counts jc ON oc.resource = jc.resource where oc.resource in ('Intern','Lateral') and jc.resource in ('Intern','Lateral')
	        """,(fiscal_year_id,fiscal_year_id))
       
        data = cr.fetchall()
        for row in data:
            rec_data = row[0]
            value = row[1]
            rate = row[2]
            off_join_resource_ratio.append({
                'name': rec_data,
                'category': value,
                'data': rate
            })
        return off_join_resource_ratio
    
    @api.model
    def get_offer_to_join_hire_res_ratio(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        off_join_hire_resource_ratio = []
        cr = self._cr
        cr.execute("""WITH offer_counts AS (
                SELECT kr.resource as resource,
                    COUNT(*) AS offer_count FROM kw_recruitment_requisition kr Join hr_applicant ha ON ha.mrf_id=kr.id
                JOIN hr_recruitment_stage hs ON ha.stage_id = hs.id
                JOIN account_fiscalyear cfy ON ha.create_date BETWEEN cfy.date_start AND cfy.date_stop 
                WHERE hs.code = 'OR' and cfy.id=%s GROUP BY  kr.resource ),
            joined_counts AS (
                SELECT kr.resource as resource,COUNT(*) AS joined_count  FROM kw_recruitment_requisition kr Join hr_applicant ha ON ha.mrf_id=kr.id
                JOIN kwonboard_enrollment k ON ha.id = k.applicant_id JOIN hr_employee he ON k.id = he.onboarding_id 
                JOIN hr_recruitment_stage hs ON ha.stage_id = hs.id JOIN account_fiscalyear cfy ON ha.create_date BETWEEN cfy.date_start AND cfy.date_stop 
                WHERE hs.code = 'OA' and cfy.id=%s  and he.active=True GROUP BY kr.resource)
            SELECT 
                COALESCE(oc.resource, jc.resource) AS resource,
                COALESCE(oc.offer_count, 0) + COALESCE(jc.joined_count, 0) AS released_count,
                COALESCE(jc.joined_count, 0) AS joined_count
            FROM 
                offer_counts oc 
            FULL OUTER JOIN 
                joined_counts jc ON oc.resource = jc.resource 
	        """,(fiscal_year_id,fiscal_year_id))
       
        data = cr.fetchall()
        for row in data:
            rec_data = row[0]
            value = row[1]
            rate = row[2]
            off_join_hire_resource_ratio.append({
                'name': rec_data,
                'category': value,
                'data': rate
            })
        return off_join_hire_resource_ratio
    
    @api.model
    def get_offer_to_join_skill_ratio(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        off_join_skill_ratio = []
        cr = self._cr
        cr.execute("""WITH offer_counts AS (
                SELECT has.kw_skill_master_id as skill,
                    COUNT(*) AS offer_count FROM hr_applicant ha
                JOIN hr_applicant_kw_skill_master_rel has ON has.hr_applicant_id=ha.id
                JOIN hr_recruitment_stage hs ON ha.stage_id = hs.id
                JOIN account_fiscalyear cfy ON ha.create_date BETWEEN cfy.date_start AND cfy.date_stop 
                WHERE hs.code = 'OR' and cfy.id=%s GROUP BY has.kw_skill_master_id ),
            joined_counts AS (
                SELECT has.kw_skill_master_id AS skill,COUNT(*) AS joined_count FROM  hr_applicant ha
                JOIN hr_applicant_kw_skill_master_rel has ON has.hr_applicant_id=ha.id JOIN kwonboard_enrollment k ON ha.id = k.applicant_id
                JOIN hr_employee he ON k.id = he.onboarding_id JOIN hr_recruitment_stage hs ON ha.stage_id = hs.id JOIN account_fiscalyear cfy ON ha.create_date BETWEEN cfy.date_start AND cfy.date_stop 
                WHERE hs.code = 'OA' and cfy.id=%s and he.active=True GROUP BY has.kw_skill_master_id )
            SELECT 
                (select name from kw_skill_master where id = COALESCE(oc.skill, jc.skill)) AS skill,
                COALESCE(oc.offer_count, 0) + COALESCE(jc.joined_count, 0) AS released_count,
                COALESCE(jc.joined_count, 0) AS joined_count
            FROM 
                offer_counts oc 
            FULL OUTER JOIN 
                joined_counts jc ON oc.skill = jc.skill 
	        """,(fiscal_year_id,fiscal_year_id))
       
        data = cr.fetchall()
        for row in data:
            rec_data = row[0]
            value = row[1]
            rate = row[2]
            off_join_skill_ratio.append({
                'name': rec_data,
                'category': value,
                'data': rate
            })
        return off_join_skill_ratio
    
    @api.model
    def get_offer_to_join_company_ratio(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        off_join_comapny_ratio = []
        cr = self._cr
        cr.execute("""WITH offer_counts AS (
                SELECT kb.company_id AS company,
                    COUNT(*) AS offer_count FROM hr_applicant_offer hao JOIN hr_applicant ha ON hao.applicant_id = ha.id 
                JOIN kw_res_branch kb ON hao.job_location=kb.id 
                JOIN hr_recruitment_stage hs ON ha.stage_id = hs.id
                JOIN account_fiscalyear cfy ON ha.create_date BETWEEN cfy.date_start AND cfy.date_stop 
                WHERE hs.code = 'OR' and cfy.id=%s GROUP BY kb.company_id),
            joined_counts AS (
                SELECT kb.company_id AS company,COUNT(*) AS joined_count FROM hr_applicant_offer hao 
                JOIN hr_applicant ha ON hao.applicant_id = ha.id JOIN kw_res_branch kb ON hao.job_location=kb.id  JOIN kwonboard_enrollment k ON ha.id = k.applicant_id
                JOIN hr_employee he ON k.id = he.onboarding_id JOIN hr_recruitment_stage hs ON ha.stage_id = hs.id JOIN account_fiscalyear cfy ON ha.create_date BETWEEN cfy.date_start AND cfy.date_stop 
                WHERE hs.code = 'OA' and cfy.id=%s  and he.active=True GROUP BY kb.company_id)
            SELECT 
                (select alias from kw_res_branch where id = COALESCE(oc.company, jc.company)) AS company,
                COALESCE(oc.offer_count, 0) + COALESCE(jc.joined_count, 0) AS released_count,
                COALESCE(jc.joined_count, 0) AS joined_count
            FROM 
                offer_counts oc 
            FULL OUTER JOIN 
                joined_counts jc ON oc.company = jc.company 
	        """,(fiscal_year_id,fiscal_year_id))
       
        data = cr.fetchall()
        for row in data:
            rec_data = row[0]
            value = row[1]
            rate = row[2]
            off_join_comapny_ratio.append({
                'name': rec_data,
                'category': value,
                'data': rate
            })
        return off_join_comapny_ratio
    
    @api.model
    def get_offer_to_join_designation_ratio(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        offer_join_desg_ratio = []
        cr = self._cr
        cr.execute("""WITH offer_counts AS (
                SELECT hao.designation AS designation,
                    COUNT(*) AS offer_count FROM hr_applicant_offer hao 
                JOIN hr_applicant ha ON hao.applicant_id = ha.id 
                JOIN hr_recruitment_stage hs ON ha.stage_id = hs.id
                JOIN account_fiscalyear cfy ON ha.create_date BETWEEN cfy.date_start AND cfy.date_stop 
                WHERE hs.code = 'OR' and cfy.id=%s
                GROUP BY hao.designation),
            joined_counts AS (
                SELECT hao.designation AS designation,COUNT(*) AS joined_count FROM 
                hr_applicant_offer hao JOIN hr_applicant ha ON hao.applicant_id = ha.id JOIN kwonboard_enrollment k ON ha.id = k.applicant_id
                JOIN hr_employee he ON k.id = he.onboarding_id JOIN hr_recruitment_stage hs ON ha.stage_id = hs.id JOIN account_fiscalyear cfy ON ha.create_date BETWEEN cfy.date_start AND cfy.date_stop 
                WHERE  hs.code = 'OA' and cfy.id=%s  and he.active=True GROUP BY hao.designation)
            SELECT 
                (SELECT name FROM hr_job WHERE id = COALESCE(oc.designation, jc.designation)) AS designation,
                COALESCE(oc.offer_count, 0) + COALESCE(jc.joined_count, 0) AS released_count,
                COALESCE(jc.joined_count, 0) AS joined_count
            FROM 
                offer_counts oc 
            FULL OUTER JOIN 
                joined_counts jc ON oc.designation = jc.designation 
	        """,(fiscal_year_id,fiscal_year_id))
       
        data = cr.fetchall()
        for row in data:
            rec_data = row[0]
            value = row[1]
            rate = row[2]
            offer_join_desg_ratio.append({
                'name': rec_data,
                'category': value,
                'data': rate
            })
        return offer_join_desg_ratio
    
    
    @api.model
    def get_offer_to_join_recruiter_ratio(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        offr_join_recruiter_ratio = []
        cr = self._cr
        cr.execute("""WITH offer_counts AS (
                SELECT kjp.user_id AS recruiter,
                    COUNT(*) AS offer_count FROM hr_applicant ha 
                JOIN kw_hr_job_positions kjp ON kjp.id=ha.job_position
                JOIN hr_recruitment_stage hs ON ha.stage_id = hs.id
                JOIN account_fiscalyear cfy ON ha.create_date BETWEEN cfy.date_start AND cfy.date_stop 
                WHERE hs.code = 'OR' and cfy.id=%s GROUP BY kjp.user_id),
            joined_counts AS (
                SELECT  kjp.user_id AS recruiter,COUNT(*) AS joined_count FROM 
            hr_applicant ha JOIN kw_hr_job_positions kjp ON kjp.id=ha.job_position JOIN kwonboard_enrollment k ON ha.id = k.applicant_id
                JOIN hr_employee he ON k.id = he.onboarding_id JOIN hr_recruitment_stage hs ON ha.stage_id = hs.id JOIN account_fiscalyear cfy ON ha.create_date BETWEEN cfy.date_start AND cfy.date_stop 
                WHERE  hs.code = 'OA' and cfy.id=%s  and he.active=True GROUP BY kjp.user_id)
            SELECT 
                (SELECT name FROM hr_employee WHERE user_id = COALESCE(oc.recruiter, jc.recruiter)) AS recruiter,
                COALESCE(oc.offer_count, 0) + COALESCE(jc.joined_count, 0) AS released_count,
                COALESCE(jc.joined_count, 0) AS joined_count
            FROM 
                offer_counts oc 
            FULL OUTER JOIN 
                joined_counts jc ON oc.recruiter = jc.recruiter 
	        """,(fiscal_year_id,fiscal_year_id))
       
        data = cr.fetchall()
        for row in data:
            rec_data = row[0]
            value = row[1]
            rate = row[2]
            offr_join_recruiter_ratio.append({
                'name': rec_data,
                'category': value,
                'data': rate
            })
        return offr_join_recruiter_ratio
    
    @api.model
    def get_offer_dropout_grade_ratio(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        offer_dropout_ratio_grade = []
        cr = self._cr
        cr.execute("""WITH offer_counts AS (
		    SELECT hao.grade AS grade,
			    COUNT(*) AS offer_count FROM hr_applicant_offer hao 
                    JOIN hr_applicant ha ON hao.applicant_id = ha.id 
                    JOIN hr_recruitment_stage hs ON ha.stage_id = hs.id
                    JOIN account_fiscalyear cfy ON ha.create_date BETWEEN cfy.date_start AND cfy.date_stop 
                    WHERE hs.code = 'OR' and cfy.id=%s GROUP BY hao.grade),
                drop_out_count AS (SELECT hao.grade AS grade,COUNT(*) AS drop_count FROM 
                    hr_applicant_offer hao JOIN hr_applicant ha ON hao.applicant_id = ha.id JOIN hr_recruitment_stage hs ON ha.stage_id = hs.id 
                    JOIN account_fiscalyear cfy ON ha.create_date BETWEEN cfy.date_start AND cfy.date_stop where hs.code='OD' and cfy.id=%s GROUP BY hao.grade),
                joined_counts AS (
                    SELECT hao.grade AS grade,COUNT(*) AS joined_count FROM 
                    hr_applicant_offer hao JOIN hr_applicant ha ON hao.applicant_id = ha.id JOIN kwonboard_enrollment k ON ha.id = k.applicant_id
                    JOIN hr_employee he ON k.id = he.onboarding_id JOIN hr_recruitment_stage hs ON ha.stage_id = hs.id JOIN account_fiscalyear cfy ON ha.create_date BETWEEN cfy.date_start AND cfy.date_stop 
                    WHERE hs.code = 'OA' and cfy.id=%s GROUP BY hao.grade)
                SELECT 
                    (SELECT name FROM kwemp_grade_master WHERE id = COALESCE(oc.grade, jc.grade)) AS grade,
                    COALESCE(oc.offer_count, 0) + COALESCE(jc.joined_count, 0) AS released_count,
                    (COALESCE(oc.offer_count, 0) + COALESCE(jc.joined_count, 0) + COALESCE(dc.drop_count, 0))- COALESCE(jc.joined_count, 0) AS drop_out
                FROM 
                    offer_counts oc
                FULL OUTER JOIN 
                    joined_counts jc ON oc.grade = jc.grade
                FULL OUTER JOIN 
                    drop_out_count dc ON dc.grade = oc.grade
                """,(fiscal_year_id,fiscal_year_id,fiscal_year_id))
       
        data = cr.fetchall()
        for row in data:
            rec_data = row[0]
            value = row[1]
            rate = row[2]
            offer_dropout_ratio_grade.append({
                'name': rec_data,
                'category': value,
                'data': rate
            })
        return offer_dropout_ratio_grade
    
    @api.model
    def get_offer_dropout_dept_ratio(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        offer_dropout_ratio_dept = []
        cr = self._cr
        cr.execute("""WITH offer_counts AS (
            SELECT ha.department_id AS department,
                    COUNT(*) AS offer_count from hr_applicant ha 
                JOIN hr_recruitment_stage hs ON ha.stage_id = hs.id
                JOIN account_fiscalyear cfy ON ha.create_date BETWEEN cfy.date_start AND cfy.date_stop 
                WHERE hs.code = 'OR' and cfy.id=%s GROUP BY ha.department_id),
            joined_counts AS (
                SELECT ha.department_id AS department,COUNT(*) AS joined_count FROM 
                hr_applicant ha JOIN kwonboard_enrollment k ON ha.id = k.applicant_id
                JOIN hr_employee he ON k.id = he.onboarding_id JOIN hr_recruitment_stage hs ON ha.stage_id = hs.id JOIN account_fiscalyear cfy ON ha.create_date BETWEEN cfy.date_start AND cfy.date_stop 
                WHERE hs.code = 'OA' and cfy.id=%s GROUP BY ha.department_id)
            SELECT 
                (SELECT name FROM hr_department WHERE id = COALESCE(oc.department, jc.department)) AS department,
                COALESCE(oc.offer_count, 0) + COALESCE(jc.joined_count, 0) AS released_count,
                (COALESCE(oc.offer_count, 0) + COALESCE(jc.joined_count, 0))- COALESCE(jc.joined_count, 0) AS drop_out
            FROM 
                offer_counts oc
            FULL OUTER JOIN 
                joined_counts jc ON oc.department = jc.department
            """,(fiscal_year_id,fiscal_year_id))
       
        data = cr.fetchall()
        for row in data:
            rec_data = row[0]
            value = row[1]
            rate = row[2]
            offer_dropout_ratio_dept.append({
                'name': rec_data,
                'category': value,
                'data': rate
            })
        return offer_dropout_ratio_dept
    
    @api.model
    def get_offer_dropout_loc_ratio(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        offer_dropout_ratio_loc = []
        cr = self._cr
        cr.execute("""WITH offer_counts AS (
                SELECT ha.job_location_id AS location,
                    COUNT(*) AS offer_count from hr_applicant ha 
                JOIN hr_recruitment_stage hs ON ha.stage_id = hs.id
                JOIN account_fiscalyear cfy ON ha.create_date BETWEEN cfy.date_start AND cfy.date_stop 
                WHERE hs.code = 'OR' and cfy.id=%s GROUP BY ha.job_location_id),
           
            joined_counts AS (
                SELECT ha.job_location_id AS location,COUNT(*) AS joined_count FROM 
                hr_applicant ha JOIN kwonboard_enrollment k ON ha.id = k.applicant_id
                JOIN hr_employee he ON k.id = he.onboarding_id JOIN hr_recruitment_stage hs ON ha.stage_id = hs.id JOIN account_fiscalyear cfy ON ha.create_date BETWEEN cfy.date_start AND cfy.date_stop 
                WHERE hs.code = 'OA' and cfy.id=%s  GROUP BY ha.job_location_id)
            SELECT 
                (SELECT name FROM kw_recruitment_location WHERE id = COALESCE(oc.location, jc.location)) AS location,
                COALESCE(oc.offer_count, 0) + COALESCE(jc.joined_count, 0) AS released_count,
                (COALESCE(oc.offer_count, 0) + COALESCE(jc.joined_count, 0))- COALESCE(jc.joined_count, 0) AS drop_out
            FROM 
                offer_counts oc
            FULL OUTER JOIN 
                joined_counts jc ON oc.location = jc.location
            """,(fiscal_year_id,fiscal_year_id))
       
        data = cr.fetchall()
        for row in data:
            rec_data = row[0]
            value = row[1]
            rate = row[2]
            offer_dropout_ratio_loc.append({
                'name': rec_data,
                'category': value,
                'data': rate
            })
        return offer_dropout_ratio_loc
    
    @api.model
    def get_offer_dropout_budget_ratio(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        offer_dropout_ratio_budget_typ = []
        cr = self._cr
        cr.execute("""WITH offer_counts AS (
                SELECT kr.requisition_type as requisition_type,
                    COUNT(*) AS offer_count FROM kw_recruitment_requisition kr Join hr_applicant ha ON ha.mrf_id=kr.id
                JOIN hr_recruitment_stage hs ON ha.stage_id = hs.id
                JOIN account_fiscalyear cfy ON ha.create_date BETWEEN cfy.date_start AND cfy.date_stop 
                WHERE hs.code = 'OR' and cfy.id=%s GROUP BY  kr.requisition_type ),
            joined_counts AS (
                SELECT kr.requisition_type as requisition_type,COUNT(*) AS joined_count  FROM kw_recruitment_requisition kr Join hr_applicant ha ON ha.mrf_id=kr.id
                JOIN kwonboard_enrollment k ON ha.id = k.applicant_id JOIN hr_employee he ON k.id = he.onboarding_id 
                JOIN hr_recruitment_stage hs ON ha.stage_id = hs.id JOIN account_fiscalyear cfy ON ha.create_date BETWEEN cfy.date_start AND cfy.date_stop 
                WHERE hs.code = 'OA' and he.active=True and cfy.id=%s GROUP BY kr.requisition_type)
			
            SELECT 
                COALESCE(oc.requisition_type, jc.requisition_type) AS requisition_type,
                COALESCE(oc.offer_count, 0) + COALESCE(jc.joined_count, 0) AS released_count,
                (COALESCE(oc.offer_count, 0) + COALESCE(jc.joined_count, 0))- COALESCE(jc.joined_count, 0) AS drop_out
            FROM 
                offer_counts oc 
            FULL OUTER JOIN 
                joined_counts jc ON oc.requisition_type = jc.requisition_type 
            """,(fiscal_year_id,fiscal_year_id))
       
        data = cr.fetchall()
        for row in data:
            rec_data = row[0]
            value = row[1]
            rate = row[2]
            offer_dropout_ratio_budget_typ.append({
                'name': rec_data,
                'category': value,
                'data': rate
            })
        return offer_dropout_ratio_budget_typ
    
    @api.model
    def get_offer_dropout_resource_ratio(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        offer_dropout_ratio_offer_resource = []
        cr = self._cr
        cr.execute("""WITH offer_counts AS (
                SELECT hao.offer_type AS resource,
                    COUNT(*) AS offer_count FROM hr_applicant_offer hao 
                JOIN hr_applicant ha ON hao.applicant_id = ha.id 
                JOIN hr_recruitment_stage hs ON ha.stage_id = hs.id
                JOIN account_fiscalyear cfy ON ha.create_date BETWEEN cfy.date_start AND cfy.date_stop 
                WHERE hs.code = 'OR' and cfy.id=%s GROUP BY hao.offer_type),
            joined_counts AS (
                SELECT hao.offer_type AS resource,COUNT(*) AS joined_count FROM 
                hr_applicant_offer hao JOIN hr_applicant ha ON hao.applicant_id = ha.id JOIN kwonboard_enrollment k ON ha.id = k.applicant_id
                JOIN hr_employee he ON k.id = he.onboarding_id JOIN hr_recruitment_stage hs ON ha.stage_id = hs.id JOIN account_fiscalyear cfy ON ha.create_date BETWEEN cfy.date_start AND cfy.date_stop 
                WHERE  hs.code = 'OA'and he.active=True and cfy.id=%s GROUP BY hao.offer_type)
	
            SELECT 
                COALESCE(oc.resource, jc.resource) AS resource,
                COALESCE(oc.offer_count, 0) + COALESCE(jc.joined_count, 0) AS released_count,
                (COALESCE(oc.offer_count, 0) + COALESCE(jc.joined_count, 0))- COALESCE(jc.joined_count, 0) AS drop_out
            FROM 
                offer_counts oc 
            FULL OUTER JOIN 
                joined_counts jc ON oc.resource = jc.resource where oc.resource in ('Intern','Lateral') and jc.resource in ('Intern','Lateral')
            """,(fiscal_year_id,fiscal_year_id))
       
        data = cr.fetchall()
        for row in data:
            rec_data = row[0]
            value = row[1]
            rate = row[2]
            offer_dropout_ratio_offer_resource.append({
                'name': rec_data,
                'category': value,
                'data': rate
            })
        return offer_dropout_ratio_offer_resource
    
    
    @api.model
    def get_offer_dropout_hire_resource_ratio(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        offer_dropout_ratio_hiring_res = []
        cr = self._cr
        cr.execute("""WITH offer_counts AS (
                SELECT kr.resource as resource,
                    COUNT(*) AS offer_count FROM kw_recruitment_requisition kr Join hr_applicant ha ON ha.mrf_id=kr.id
                JOIN hr_recruitment_stage hs ON ha.stage_id = hs.id
                JOIN account_fiscalyear cfy ON ha.create_date BETWEEN cfy.date_start AND cfy.date_stop 
                WHERE hs.code = 'OR' and cfy.id=%s GROUP BY  kr.resource ),
            joined_counts AS (
                SELECT kr.resource as resource,COUNT(*) AS joined_count  FROM kw_recruitment_requisition kr Join hr_applicant ha ON ha.mrf_id=kr.id
                JOIN kwonboard_enrollment k ON ha.id = k.applicant_id JOIN hr_employee he ON k.id = he.onboarding_id 
                JOIN hr_recruitment_stage hs ON ha.stage_id = hs.id JOIN account_fiscalyear cfy ON ha.create_date BETWEEN cfy.date_start AND cfy.date_stop 
                WHERE hs.code = 'OA' and cfy.id=%s and he.active=True GROUP BY kr.resource)
            SELECT 
                COALESCE(oc.resource, jc.resource) AS resource,
                 COALESCE(oc.offer_count, 0) + COALESCE(jc.joined_count, 0) AS released_count,
                (COALESCE(oc.offer_count, 0) + COALESCE(jc.joined_count, 0))- COALESCE(jc.joined_count, 0) AS drop_out
            FROM 
                offer_counts oc 
            FULL OUTER JOIN 
                joined_counts jc ON oc.resource = jc.resource 
			
            """,(fiscal_year_id,fiscal_year_id))
       
        data = cr.fetchall()
        for row in data:
            rec_data = row[0]
            value = row[1]
            rate = row[2]
            offer_dropout_ratio_hiring_res.append({
                'name': rec_data,
                'category': value,
                'data': rate
            })
        return offer_dropout_ratio_hiring_res
    
    @api.model
    def get_offer_dropout_skill_resource_ratio(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        off_drop_skill_ratio = []
        cr = self._cr
        cr.execute("""WITH offer_counts AS (
                SELECT has.kw_skill_master_id as skill,
                    COUNT(*) AS offer_count FROM hr_applicant ha
                JOIN hr_applicant_kw_skill_master_rel has ON has.hr_applicant_id=ha.id
                JOIN hr_recruitment_stage hs ON ha.stage_id = hs.id
                JOIN account_fiscalyear cfy ON ha.create_date BETWEEN cfy.date_start AND cfy.date_stop 
                WHERE hs.code = 'OR' and cfy.id=%s GROUP BY has.kw_skill_master_id ),
                
            joined_counts AS (
                SELECT has.kw_skill_master_id AS skill,COUNT(*) AS joined_count FROM  hr_applicant ha
                JOIN hr_applicant_kw_skill_master_rel has ON has.hr_applicant_id=ha.id JOIN kwonboard_enrollment k ON ha.id = k.applicant_id
                JOIN hr_employee he ON k.id = he.onboarding_id JOIN hr_recruitment_stage hs ON ha.stage_id = hs.id JOIN account_fiscalyear cfy ON ha.create_date BETWEEN cfy.date_start AND cfy.date_stop 
                WHERE hs.code = 'OA' and cfy.id=%s and he.active=True GROUP BY has.kw_skill_master_id )
                
            SELECT 
                (select name from kw_skill_master where id = COALESCE(oc.skill, jc.skill)) AS skill,
                COALESCE(oc.offer_count, 0) + COALESCE(jc.joined_count, 0) AS released_count,
                (COALESCE(oc.offer_count, 0) + COALESCE(jc.joined_count, 0))- COALESCE(jc.joined_count, 0) AS drop_out
            FROM 
                offer_counts oc 
            FULL OUTER JOIN 
                joined_counts jc ON oc.skill = jc.skill 
			
	        """,(fiscal_year_id,fiscal_year_id))
       
        data = cr.fetchall()
        for row in data:
            rec_data = row[0]
            value = row[1]
            rate = row[2]
            off_drop_skill_ratio.append({
                'name': rec_data,
                'category': value,
                'data': rate
            })
        return off_drop_skill_ratio
    
    @api.model
    def get_offer_dropout_company_ratio(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        off_drop_comapny_ratio = []
        cr = self._cr
        cr.execute("""WITH offer_counts AS (
                SELECT kb.company_id AS company, COUNT(*) AS offer_count FROM hr_applicant_offer hao
                JOIN hr_applicant ha ON hao.applicant_id = ha.id 
                JOIN kw_res_branch kb ON hao.job_location=kb.id JOIN hr_recruitment_stage hs ON ha.stage_id = hs.id
                JOIN account_fiscalyear cfy ON ha.create_date BETWEEN cfy.date_start AND cfy.date_stop 
                WHERE hs.code = 'OR' and cfy.id=%s GROUP BY kb.company_id),
                
            joined_counts AS (
                SELECT kb.company_id AS company,COUNT(*) AS joined_count FROM hr_applicant_offer hao 
                JOIN hr_applicant ha ON hao.applicant_id = ha.id JOIN kw_res_branch kb ON hao.job_location=kb.id  JOIN kwonboard_enrollment k ON ha.id = k.applicant_id
                JOIN hr_employee he ON k.id = he.onboarding_id JOIN hr_recruitment_stage hs ON ha.stage_id = hs.id JOIN account_fiscalyear cfy 
                ON ha.create_date BETWEEN cfy.date_start AND cfy.date_stop WHERE hs.code = 'OA' and cfy.id=%s and he.active=True GROUP BY kb.company_id)
                
            SELECT 
                (select alias from kw_res_branch where id = COALESCE(oc.company, jc.company)) AS company,
                COALESCE(oc.offer_count, 0) + COALESCE(jc.joined_count, 0) AS released_count,
                (COALESCE(oc.offer_count, 0) + COALESCE(jc.joined_count, 0))- COALESCE(jc.joined_count, 0) AS drop_out
            FROM 
                offer_counts oc 
            FULL OUTER JOIN 
                joined_counts jc ON oc.company = jc.company 
	        """,(fiscal_year_id,fiscal_year_id))
       
        data = cr.fetchall()
        for row in data:
            rec_data = row[0]
            value = row[1]
            rate = row[2]
            off_drop_comapny_ratio.append({
                'name': rec_data,
                'category': value,
                'data': rate
            })
        return off_drop_comapny_ratio
    
    @api.model
    def get_offer_dropout_designation_ratio(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        offer_drop_desg_ratio = []
        cr = self._cr
        cr.execute("""WITH offer_counts AS (
                SELECT hao.designation AS designation,
                    COUNT(*) AS offer_count FROM hr_applicant_offer hao 
                JOIN hr_applicant ha ON hao.applicant_id = ha.id JOIN hr_recruitment_stage hs ON ha.stage_id = hs.id
                JOIN account_fiscalyear cfy ON ha.create_date BETWEEN cfy.date_start AND cfy.date_stop 
                WHERE hs.code = 'OR' and cfy.id=%s GROUP BY hao.designation),
                
            joined_counts AS (
                SELECT hao.designation AS designation,COUNT(*) AS joined_count FROM 
                hr_applicant_offer hao JOIN hr_applicant ha ON hao.applicant_id = ha.id JOIN kwonboard_enrollment k ON ha.id = k.applicant_id
                JOIN hr_employee he ON k.id = he.onboarding_id JOIN hr_recruitment_stage hs ON ha.stage_id = hs.id JOIN account_fiscalyear cfy ON ha.create_date BETWEEN cfy.date_start AND cfy.date_stop 
                WHERE  hs.code = 'OA' and cfy.id=%s and he.active=True GROUP BY hao.designation)
                
            SELECT 
                (SELECT name FROM hr_job WHERE id = COALESCE(oc.designation, jc.designation)) AS designation,
               COALESCE(oc.offer_count, 0) + COALESCE(jc.joined_count, 0) AS released_count,
                (COALESCE(oc.offer_count, 0) + COALESCE(jc.joined_count, 0))- COALESCE(jc.joined_count, 0) AS drop_out
            FROM 
                offer_counts oc 
            FULL OUTER JOIN 
                joined_counts jc ON oc.designation = jc.designation
			
	        """,(fiscal_year_id,fiscal_year_id))
       
        data = cr.fetchall()
        for row in data:
            rec_data = row[0]
            value = row[1]
            rate = row[2]
            offer_drop_desg_ratio.append({
                'name': rec_data,
                'category': value,
                'data': rate
            })
        return offer_drop_desg_ratio
    
    
    @api.model
    def get_offer_dropout_recruiter_ratio(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        offr_drop_recruiter_ratio = []
        cr = self._cr
        cr.execute("""WITH offer_counts AS (
                SELECT kjp.user_id AS recruiter,
                    COUNT(*) AS offer_count FROM hr_applicant ha 
                JOIN kw_hr_job_positions kjp ON kjp.id=ha.job_position JOIN hr_recruitment_stage hs ON ha.stage_id = hs.id
                JOIN account_fiscalyear cfy ON ha.create_date BETWEEN cfy.date_start AND cfy.date_stop 
                WHERE hs.code = 'OR' and cfy.id=%s GROUP BY kjp.user_id),
            joined_counts AS (
                SELECT  kjp.user_id AS recruiter,COUNT(*) AS joined_count FROM 
            hr_applicant ha JOIN kw_hr_job_positions kjp ON kjp.id=ha.job_position JOIN kwonboard_enrollment k ON ha.id = k.applicant_id
                JOIN hr_employee he ON k.id = he.onboarding_id JOIN hr_recruitment_stage hs ON ha.stage_id = hs.id JOIN account_fiscalyear cfy ON ha.create_date BETWEEN cfy.date_start AND cfy.date_stop 
                WHERE  hs.code = 'OA' and cfy.id=%s and he.active=True GROUP BY kjp.user_id)
            SELECT 
                (SELECT name FROM hr_employee WHERE user_id = COALESCE(oc.recruiter, jc.recruiter)) AS recruiter,
                COALESCE(oc.offer_count, 0) + COALESCE(jc.joined_count, 0) AS released_count,
                (COALESCE(oc.offer_count, 0) + COALESCE(jc.joined_count, 0))- COALESCE(jc.joined_count, 0) AS drop_out
            FROM 
                offer_counts oc 
            FULL OUTER JOIN 
                joined_counts jc ON oc.recruiter = jc.recruiter 
	        """,(fiscal_year_id,fiscal_year_id))
       
        data = cr.fetchall()
        for row in data:
            rec_data = row[0]
            value = row[1]
            rate = row[2]
            offr_drop_recruiter_ratio.append({
                'name': rec_data,
                'category': value,
                'data': rate
            })
        return offr_drop_recruiter_ratio
    
    @api.model
    def get_infant_attration_level_ratio(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        infant_attration_level_ratio = []
        cr = self._cr
        cr.execute("""WITH joined_emp AS (
                SELECT  he.level AS level, COUNT(*) AS joined_count
                FROM hr_employee he
                JOIN kwonboard_enrollment k ON k.id = he.onboarding_id 
                JOIN hr_applicant h ON h.id = k.applicant_id
                JOIN account_fiscalyear af ON he.create_date BETWEEN af.date_start AND af.date_stop
                WHERE he.active = True AND af.id = %s AND level IS NOT NULL GROUP BY he.level ),
            left_emp AS ( SELECT he.level AS level,COUNT(*) AS left_count
                FROM hr_employee he JOIN account_fiscalyear af ON he.last_working_day BETWEEN af.date_start AND af.date_stop  
                WHERE he.active = False AND af.id = %s AND he.last_working_day <= he.date_of_joining + INTERVAL '90 days' AND level IS NOT NULL GROUP BY he.level),
            infra_info AS (
                SELECT
                    COALESCE((SELECT name FROM kw_grade_level WHERE id = COALESCE(je.level, le.level)), 'Unknown') AS level,
                    COALESCE(le.left_count, 0) AS left_count,
                    COALESCE(je.joined_count, 0) AS joined_count
                FROM joined_emp je FULL OUTER JOIN left_emp le ON le.level = je.level )  SELECT level,joined_count,left_count FROM infra_info
        
	        """,(fiscal_year_id,fiscal_year_id))
       
        data = cr.fetchall()
        for row in data:
            level_data = row[0]
            joined_count = row[1]
            left_count = row[2]
            # infra_ratio = row[3]
            infant_attration_level_ratio.append({
                'name': level_data,
                'data': [joined_count, left_count],  # Stack joined_count and left_count
                # 'infra_ratio': infra_ratio
            })

        return infant_attration_level_ratio
       
    
    @api.model
    def get_infant_attration_grade_ratio(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        infant_attration_grade_ratio = []
        cr = self._cr
        cr.execute("""WITH joined_emp AS (
                SELECT  he.grade AS grade, COUNT(*) AS joined_count
                FROM hr_employee he
                JOIN kwonboard_enrollment k ON k.id = he.onboarding_id 
                JOIN hr_applicant h ON h.id = k.applicant_id
                JOIN account_fiscalyear af ON he.create_date BETWEEN af.date_start AND af.date_stop
                WHERE he.active = True
                AND af.id = %s
                AND grade IS NOT NULL
                GROUP BY he.grade),
            left_emp AS (
                SELECT
                    he.grade AS grade,COUNT(*) AS left_count
                FROM
                    hr_employee he
                    JOIN account_fiscalyear af ON he.last_working_day BETWEEN af.date_start AND af.date_stop
                WHERE he.active = False AND af.id = %s AND he.last_working_day <= he.date_of_joining + INTERVAL '90 days' AND grade IS NOT NULL
                GROUP BY he.grade),
            infra_info AS (
                SELECT
                    COALESCE((SELECT name FROM kwemp_grade_master WHERE id = COALESCE(je.grade, le.grade)), 'Unknown') AS grade,
                    COALESCE(le.left_count, 0) AS left_count,
                    COALESCE(je.joined_count, 0) AS joined_count
                    
                FROM
                    joined_emp je
                    FULL OUTER JOIN left_emp le ON le.grade = je.grade
            )
            SELECT
                grade,joined_count,left_count
            FROM
                infra_info """,(fiscal_year_id,fiscal_year_id))
       
        data = cr.fetchall()
        for row in data:
            grade_data = row[0]
            joined_count = row[1]
            left_count = row[2]
            # infra_ratio = row[3]
            infant_attration_grade_ratio.append({
                'name': grade_data,
                'data': [joined_count, left_count],  # Stack joined_count and left_count
                # 'infra_ratio': infra_ratio
            })

        return infant_attration_grade_ratio
      
    
    @api.model
    def get_infant_attration_dept_ratio(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        infant_attration_dept_ratio = []
        cr = self._cr
        cr.execute("""WITH joined_emp AS (
                        SELECT he.department_id AS department,
                            COUNT(*) AS joined_count
                        FROM hr_employee he
                        JOIN kwonboard_enrollment k ON k.id = he.onboarding_id 
                        JOIN hr_applicant h ON h.id = k.applicant_id 
                        JOIN account_fiscalyear af ON he.create_date BETWEEN af.date_start AND af.date_stop
                        WHERE he.active = True 
                        AND af.id=%s
                        AND he.department_id IS NOT NULL 
                        GROUP BY he.department_id
                    ),
                    left_emp AS (
                        SELECT he.department_id AS department,
                            COUNT(*) AS left_count
                        FROM hr_employee he
                        JOIN account_fiscalyear af ON he.last_working_day BETWEEN af.date_start AND af.date_stop
                        WHERE he.active = False 
                        AND af.id=%s
                        AND he.last_working_day <= he.date_of_joining + INTERVAL '90 days'
                        AND he.department_id IS NOT NULL 
                        GROUP BY he.department_id
                    ),
                    infra_info AS (
                        SELECT COALESCE((SELECT name FROM hr_department WHERE id = COALESCE(je.department, le.department)), 'Unknown') AS department_name,
                            COALESCE(le.left_count, 0) AS left_count,
                            COALESCE(je.joined_count, 0) AS joined_count
                        FROM joined_emp je 
                        FULL OUTER JOIN left_emp le ON le.department = je.department
                    )
                    SELECT department_name,
                        joined_count,
                        left_count
                    FROM infra_info """,(fiscal_year_id,fiscal_year_id))
       
        data = cr.fetchall()
        for row in data:
            dept_data = row[0]
            joined_count = row[1]
            left_count = row[2]
            # infra_ratio = row[3]
            infant_attration_dept_ratio.append({
                'name': dept_data,
                'data': [joined_count, left_count],  # Stack joined_count and left_count
                # 'infra_ratio': infra_ratio
            })

        return infant_attration_dept_ratio
       
    
    @api.model
    def get_infant_attration_loc_ratio(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        infant_attration_location_ratio = []
        cr = self._cr
        cr.execute("""WITH joined_emp AS (
                    SELECT he.base_branch_id AS location,
                        COUNT(*) AS joined_count
                    FROM hr_employee he
                    JOIN kwonboard_enrollment k ON k.id = he.onboarding_id 
                    JOIN hr_applicant h ON h.id = k.applicant_id 
                    JOIN account_fiscalyear af ON he.create_date BETWEEN af.date_start AND af.date_stop
                    WHERE he.active = True 
                    AND af.id=%s 
                    AND he.base_branch_id IS NOT NULL 
                    GROUP BY he.base_branch_id
                ),
                left_emp AS (
                    SELECT he.base_branch_id AS location,
                        COUNT(*) AS left_count
                    FROM hr_employee he
                    JOIN account_fiscalyear af ON he.last_working_day BETWEEN af.date_start AND af.date_stop
                    WHERE he.active = False 
                    AND he.base_branch_id IS NOT NULL 
                    AND af.id=%s 
                    AND he.last_working_day <= he.date_of_joining + INTERVAL '90 days'
                    GROUP BY he.base_branch_id
                ),
                infra_info AS (
                    SELECT COALESCE((SELECT alias FROM kw_res_branch WHERE id = COALESCE(je.location, le.location)), 'Unknown') AS location_name,
                        COALESCE(le.left_count, 0) AS left_count,
                        COALESCE(je.joined_count, 0) AS joined_count 
                    FROM joined_emp je 
                    FULL OUTER JOIN left_emp le ON le.location = je.location
                )
                SELECT location_name,
                    joined_count,
                    left_count
                FROM infra_info """,(fiscal_year_id,fiscal_year_id))
       
        data = cr.fetchall()
        for row in data:
            loc_data = row[0]
            joined_count = row[1]
            left_count = row[2]
            # infra_ratio = row[3]
            infant_attration_location_ratio.append({
                'name': loc_data,
                'data': [joined_count, left_count],  # Stack joined_count and left_count
                # 'infra_ratio': infra_ratio
            })

        return infant_attration_location_ratio

       
    @api.model
    def get_infant_attration_budget_type_ratio(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        infant_attration_budget_typ_ratio = []
        cr = self._cr
        cr.execute("""WITH joined_emp AS (
                    SELECT he.budget_type AS budget_type,
                        COUNT(*) AS joined_count
                    FROM hr_employee he
                    JOIN kwonboard_enrollment k ON k.id = he.onboarding_id 
                    JOIN hr_applicant h ON h.id = k.applicant_id 
                    JOIN account_fiscalyear af ON he.create_date BETWEEN af.date_start AND af.date_stop
                    WHERE he.active = True 
                    AND af.id=%s 
                    AND he.budget_type IS NOT NULL 
                    GROUP BY he.budget_type
                ),
                left_emp AS ( SELECT he.budget_type AS budget_type,
                        COUNT(*) AS left_count
                    FROM hr_employee he
                    JOIN account_fiscalyear af ON he.last_working_day BETWEEN af.date_start AND af.date_stop
                    WHERE he.active = False 
                    AND af.id=%s 
                	AND he.last_working_day <= he.date_of_joining + INTERVAL '90 days'
                    AND he.budget_type IS NOT NULL 
                    GROUP BY he.budget_type
                ),
                infra_info AS ( SELECT COALESCE(je.budget_type, le.budget_type) AS budget_type,
                        COALESCE(le.left_count, 0) AS left_count,
                        COALESCE(je.joined_count, 0) AS joined_count
                        FROM joined_emp je 
                    FULL OUTER JOIN left_emp le ON le.budget_type = je.budget_type
                ) SELECT budget_type,
                    joined_count,
                    left_count
                FROM infra_info


	        """,(fiscal_year_id,fiscal_year_id))
       
        data = cr.fetchall()
        for row in data:
            budget_data = row[0]
            joined_count = row[1]
            left_count = row[2]
            # infra_ratio = row[3]
            infant_attration_budget_typ_ratio.append({
                'name': budget_data,
                'data': [joined_count, left_count],  # Stack joined_count and left_count
                # 'infra_ratio': infra_ratio
            })

        return infant_attration_budget_typ_ratio
    
    
    @api.model
    def get_infant_attration_resource_ratio(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        infant_attration_resource_ratio = []
        cr = self._cr
        cr.execute("""WITH joined_emp AS (
                    SELECT hao.offer_type AS offer_type,
                        COUNT(*) AS joined_count
                    FROM hr_employee he 
                    JOIN kwonboard_enrollment k ON k.id = he.onboarding_id 
                    JOIN hr_applicant h ON h.id = k.applicant_id 
                    JOIN hr_applicant_offer hao ON h.id = hao.applicant_id 
                    JOIN account_fiscalyear af ON he.create_date BETWEEN af.date_start AND af.date_stop
                    WHERE he.active = True 
                    AND hao.offer_type IS NOT NULL 
                    AND hao.offer_type IN ('Intern','Lateral') 
                    AND af.id = %s 
                    GROUP BY hao.offer_type
                ),
                left_emp AS ( SELECT hao.offer_type AS offer_type,
                        COUNT(*) AS left_count
                    FROM hr_employee he 
                    JOIN kwonboard_enrollment k ON k.id = he.onboarding_id 
                    JOIN hr_applicant h ON h.id = k.applicant_id 
                    JOIN hr_applicant_offer hao ON h.id = hao.applicant_id 
                    JOIN account_fiscalyear af ON he.last_working_day BETWEEN af.date_start AND af.date_stop
                    WHERE he.active = False 
                    AND hao.offer_type IS NOT NULL 
                    AND hao.offer_type IN ('Intern','Lateral') 
                    AND af.id = %s 
                    AND he.last_working_day <= he.date_of_joining + INTERVAL '90 days'
                    GROUP BY hao.offer_type
                ), infra_info AS (
                    SELECT COALESCE(je.offer_type, le.offer_type) AS offer_type,
                        COALESCE(le.left_count, 0) AS left_count,
                        COALESCE(je.joined_count, 0) AS joined_count
                    FROM joined_emp je 
                    FULL OUTER JOIN left_emp le ON le.offer_type = je.offer_type
                )
                SELECT offer_type, joined_count AS joined_count,left_count AS left_count
                FROM infra_info

	        """,(fiscal_year_id,fiscal_year_id))
       
        data = cr.fetchall()
        for row in data:
            resource_data = row[0]
            joined_count = row[1]
            left_count = row[2]
            # infra_ratio = row[3]
            infant_attration_resource_ratio.append({
                'name': resource_data,
                'data': [joined_count, left_count],  # Stack joined_count and left_count
                # 'infra_ratio': infra_ratio
            })

        return infant_attration_resource_ratio
    @api.model
    def get_infant_attration_hiring_typ_ratio(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        infant_attration_hiring_typ_ratio = []
        cr = self._cr
        cr.execute("""WITH joined_emp AS (
                SELECT kr.resource AS resource,
                    COUNT(*) AS joined_count
                FROM hr_employee he 
                JOIN kwonboard_enrollment k ON k.id = he.onboarding_id 
                JOIN hr_applicant h ON h.id = k.applicant_id 
                JOIN kw_recruitment_requisition kr ON kr.id = he.mrf_id 
                JOIN account_fiscalyear af ON he.create_date BETWEEN af.date_start AND af.date_stop
                WHERE he.active = True  AND kr.resource IS NOT NULL AND af.id = %s 
                GROUP BY kr.resource
            ), left_emp AS ( SELECT kr.resource AS resource,
                    COUNT(*) AS left_count
                FROM hr_employee he JOIN kw_recruitment_requisition kr ON kr.id = he.mrf_id
                JOIN account_fiscalyear af ON he.last_working_day BETWEEN af.date_start AND af.date_stop
                WHERE he.active = False 
                AND kr.resource IS NOT NULL 
                AND af.id = %s 
                AND he.last_working_day <= he.date_of_joining + INTERVAL '90 days'
                GROUP BY kr.resource
            ), infra_info AS ( SELECT COALESCE(je.resource, le.resource) AS resource,
                    COALESCE(le.left_count, 0) AS left_count,
                    COALESCE(je.joined_count, 0) AS joined_count
                FROM joined_emp je 
                FULL OUTER JOIN left_emp le ON le.resource = je.resource
            ) SELECT resource,
                joined_count AS joined_count,
                left_count AS left_count
            FROM infra_info

	        """,(fiscal_year_id,fiscal_year_id))
       
        data = cr.fetchall()
        for row in data:
            hiring_res_data = row[0]
            joined_count = row[1]
            left_count = row[2]
            # infra_ratio = row[3]
            infant_attration_hiring_typ_ratio.append({
                'name': hiring_res_data,
                'data': [joined_count, left_count],  # Stack joined_count and left_count
                # 'infra_ratio': infra_ratio
            })
        return infant_attration_hiring_typ_ratio

       
    
    @api.model
    def get_infant_attration_skill_ratio(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        infant_attration_skill_ratio = []
        cr = self._cr
        cr.execute("""WITH joined_emp AS (
                    SELECT he.primary_skill_id AS skill,
                        COUNT(*) AS joined_count
                    FROM hr_employee he 
                    JOIN kwonboard_enrollment k ON k.id = he.onboarding_id 
                    JOIN hr_applicant h ON h.id = k.applicant_id 
                    JOIN kw_skill_master ks ON ks.id = he.primary_skill_id 
                    JOIN account_fiscalyear af ON he.create_date BETWEEN af.date_start AND af.date_stop
                    WHERE he.active = True 
                    AND he.primary_skill_id IS NOT NULL 
                    AND af.id = %s 
                    GROUP BY he.primary_skill_id
                ),
                left_emp AS (
                    SELECT he.primary_skill_id AS skill,
                        COUNT(*) AS left_count
                    FROM hr_employee he 
                    JOIN kw_skill_master ks ON ks.id = he.primary_skill_id
                    JOIN account_fiscalyear af ON he.last_working_day BETWEEN af.date_start AND af.date_stop
                    WHERE he.active = False 
                    AND he.primary_skill_id IS NOT NULL 
                    AND af.id = %s 
                    AND he.last_working_day <= he.date_of_joining + INTERVAL '90 days'
                    GROUP BY he.primary_skill_id
                ),
                infra_info AS (
                    SELECT COALESCE((SELECT name FROM kw_skill_master WHERE id = COALESCE(je.skill, le.skill)), 'Unknown') AS skill,
                        COALESCE(le.left_count, 0) AS left_count,
                        COALESCE(je.joined_count, 0) AS joined_count
                    FROM joined_emp je 
                    FULL OUTER JOIN left_emp le ON le.skill = je.skill
                )
                SELECT skill,
                    joined_count AS joined_count,
                    left_count AS left_count
                FROM infra_info


	        """,(fiscal_year_id,fiscal_year_id))
       
        data = cr.fetchall()
        for row in data:
            skill_data = row[0]
            joined_count = row[1]
            left_count = row[2]
            # infra_ratio = row[3]
            infant_attration_skill_ratio.append({
                'name': skill_data,
                'data': [joined_count, left_count],  # Stack joined_count and left_count
                # 'infra_ratio': infra_ratio
            })
        return infant_attration_skill_ratio

    @api.model
    def get_infant_attration_company_ratio(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        infant_attration_company_ratio = []
        cr = self._cr
        cr.execute("""WITH joined_emp AS (
                SELECT 
                    he.company_id AS company,
                    COUNT(*) AS joined_count
                FROM 
                    hr_employee he 
                    JOIN kwonboard_enrollment k ON k.id = he.onboarding_id 
                    JOIN hr_applicant h ON h.id = k.applicant_id 
                    JOIN res_company rc ON rc.id = he.company_id 
                    JOIN account_fiscalyear af ON he.create_date BETWEEN af.date_start AND af.date_stop
                WHERE 
                    he.active = True 
                    AND he.company_id IS NOT NULL 
                    AND af.id = %s 
                GROUP BY 
                    he.company_id
            ),
            left_emp AS (
                SELECT 
                    he.company_id AS company,
                    COUNT(*) AS left_count
                FROM 
                    hr_employee he 
                    JOIN res_company rc ON rc.id = he.company_id 
                    JOIN account_fiscalyear af ON he.last_working_day BETWEEN af.date_start AND af.date_stop
                WHERE 
                    he.active = False 
                    AND he.company_id IS NOT NULL 
                    AND af.id = %s 
                    AND he.last_working_day <= he.date_of_joining + INTERVAL '90 days'
                GROUP BY 
                    he.company_id
            ),
            infra_info AS (
                SELECT 
                    COALESCE((SELECT name FROM res_company WHERE id = COALESCE(je.company, le.company)), 'Unknown') AS company,
                    COALESCE(le.left_count, 0) AS left_count,
                    COALESCE(je.joined_count, 0) AS joined_count
                    FROM joined_emp je FULL OUTER JOIN left_emp le ON le.company = je.company)
            SELECT  company,left_count,joined_count FROM infra_info


	        """,(fiscal_year_id,fiscal_year_id))
       
        data = cr.fetchall()
        for row in data:
            company_data = row[0]
            left_count = row[1]
            joined_count = row[2]
            # infra_ratio = row[3]
            infant_attration_company_ratio.append({
                'name': company_data,
                'data': [joined_count, left_count],  # Stack joined_count and left_count
                # 'infra_ratio': infra_ratio
            })
        return infant_attration_company_ratio

       
    
    @api.model
    def get_infant_attration_designation_ratio(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        infant_attration_desg_ratio = []
        cr = self._cr
        cr.execute("""WITH joined_emp AS (SELECT he.job_id AS designation,COUNT(*) AS joined_count FROM hr_employee he 
                    JOIN kwonboard_enrollment k ON k.id = he.onboarding_id JOIN hr_applicant h ON h.id = k.applicant_id JOIN hr_job hj ON hj.id = he.job_id 
                    JOIN account_fiscalyear af ON he.create_date BETWEEN af.date_start AND af.date_stop WHERE he.active = True AND he.job_id IS NOT NULL AND af.id = %s GROUP BY he.job_id),
            left_emp AS (SELECT he.job_id AS designation,COUNT(*) AS left_count FROM hr_employee he JOIN hr_job hj ON hj.id = he.job_id 
                    JOIN account_fiscalyear af ON he.last_working_day BETWEEN af.date_start AND af.date_stop
                WHERE he.active = False AND he.job_id IS NOT NULL AND af.id = %s AND he.last_working_day <= he.date_of_joining + INTERVAL '90 days' GROUP BY he.job_id),
            infra_info AS (SELECT COALESCE((SELECT name FROM hr_job WHERE id = COALESCE(je.designation, le.designation)), 'Unknown') AS designation,
                    COALESCE(le.left_count, 0) AS left_count,COALESCE(je.joined_count, 0) AS joined_count
                FROM joined_emp je FULL OUTER JOIN left_emp le ON le.designation = je.designation)
            SELECT designation,left_count,joined_count FROM infra_info


	        """,(fiscal_year_id,fiscal_year_id))
       
        data = cr.fetchall()
        for row in data:
            designation_data = row[0]
            left_count = row[1]
            joined_count = row[2]
            # infra_ratio = row[3]
            infant_attration_desg_ratio.append({
                'name': designation_data,
                'data': [joined_count, left_count],  # Stack joined_count and left_count
                # 'infra_ratio': infra_ratio
            })
        return infant_attration_desg_ratio
    
    @api.model
    def get_infant_attration_recruiter_ratio(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        infant_attration_recruiter_ratio = []
        cr = self._cr
        cr.execute("""WITH joined_emp AS (SELECT kjp.user_id AS recruiter,COUNT(*) AS joined_count FROM hr_employee he 
                    JOIN kwonboard_enrollment k ON k.id = he.onboarding_id JOIN hr_applicant h ON h.id = k.applicant_id 
                    JOIN kw_hr_job_positions kjp ON kjp.id = h.job_position JOIN account_fiscalyear af ON he.create_date BETWEEN af.date_start AND af.date_stop
                    WHERE he.active = True AND kjp.user_id IS NOT NULL AND af.id = %s GROUP BY kjp.user_id),
                left_emp AS (SELECT kjp.user_id AS recruiter,COUNT(*) AS left_count FROM hr_employee he 
                    JOIN kwonboard_enrollment k ON k.id = he.onboarding_id JOIN hr_applicant h ON h.id = k.applicant_id 
                    JOIN kw_hr_job_positions kjp ON kjp.id = h.job_position JOIN account_fiscalyear af ON he.last_working_day BETWEEN af.date_start AND af.date_stop
                    WHERE he.active = False AND kjp.user_id IS NOT NULL AND af.id = %s AND he.last_working_day <= he.date_of_joining + INTERVAL '90 days' GROUP BY kjp.user_id),
                infra_info AS (SELECT COALESCE((SELECT name FROM hr_employee WHERE user_id = COALESCE(je.recruiter, le.recruiter)), 'Unknown') AS recruiter,
                    COALESCE(le.left_count, 0) AS left_count,COALESCE(je.joined_count, 0) AS joined_count
                     FROM joined_emp je FULL OUTER JOIN left_emp le ON le.recruiter = je.recruiter
                ) SELECT recruiter,left_count,joined_count FROM infra_info


	        """,(fiscal_year_id,fiscal_year_id))
       
        data = cr.fetchall()
        for row in data:
            recruiter_data = row[0]
            left_count = row[1]
            joined_count = row[2]
            # infra_ratio = row[3]
            infant_attration_recruiter_ratio.append({
                'name': recruiter_data,
                'data': [joined_count, left_count],  # Stack joined_count and left_count
                # 'infra_ratio': infra_ratio
            })
        return infant_attration_recruiter_ratio

    
    
    @api.model
    def get_dept_mrf_tagged_ratio(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        dept_mrf_tagged = []
        cr = self._cr
        cr.execute("""WITH
        mrf_approved AS (SELECT kr.dept_name AS department,COUNT(*) AS mrf_approved 
            FROM kw_recruitment_requisition kr JOIN account_fiscalyear cfy ON kr.create_date::date >= cfy.date_start AND kr.create_date::date <= cfy.date_stop AND cfy.id=%s
            WHERE  kr.state = 'approve' GROUP BY kr.dept_name), 
        mrf_draft AS (SELECT kr.dept_name AS department,COUNT(*) AS mrf_raised 
                FROM kw_recruitment_requisition kr JOIN account_fiscalyear cfy ON
            kr.create_date::date >= cfy.date_start AND kr.create_date::date <= cfy.date_stop AND cfy.id=%s WHERE  kr.state = 'draft' GROUP BY kr.dept_name)
        SELECT 
                COALESCE((SELECT name FROM hr_department WHERE id = COALESCE(mte.department, ma.department)), 'Unknown') AS department,
                COALESCE(ma.mrf_approved, 0) AS mrf_approved,
                COALESCE(mte.mrf_raised, 0) AS mrf_raised
	        FROM mrf_draft mte FULL OUTER JOIN mrf_approved ma ON mte.department = ma.department

	        """,(fiscal_year_id,fiscal_year_id))
        
        data = cr.fetchall()
        for row in data:
            dept_data = row[0]
            value = row[1]
            rate = row[2]
            dept_mrf_tagged.append({
                'name': dept_data,
                'category': value,
                'data': rate
            })
        return dept_mrf_tagged
    
    @api.model
    def get_location_mrf_tagged_ratio(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        loc_mrf_tagged = []
        cr = self._cr
        cr.execute("""WITH 
            mrf_approved AS ( SELECT 
                (SELECT id FROM kw_res_branch WHERE id=kl.kw_branch_id) AS location,COUNT(*) AS mrf_approved 
                FROM kw_recruitment_requisition kr JOIN kw_recruitment_location_kw_recruitment_requisition_rel krl ON krl.kw_recruitment_requisition_id=kr.id
                JOIN kw_recruitment_location kl ON kl.id=krl.kw_recruitment_location_id 
                JOIN account_fiscalyear cfy ON kr.create_date::date >= cfy.date_start AND kr.create_date::date <= cfy.date_stop AND cfy.id =%s
                WHERE kr.state='approve' GROUP BY  kl.kw_branch_id),
            draft_mrf AS ( SELECT (SELECT id FROM kw_res_branch WHERE id=kl.kw_branch_id) AS location,
                    COUNT(*) AS mrf_raised FROM kw_recruitment_requisition kr 
                    JOIN kw_recruitment_location_kw_recruitment_requisition_rel krl ON krl.kw_recruitment_requisition_id=kr.id
                    JOIN kw_recruitment_location kl ON kl.id=kw_recruitment_location_id 
                    JOIN account_fiscalyear cfy ON kr.create_date::date >= cfy.date_start AND kr.create_date::date <= cfy.date_stop AND cfy.id =%s
                WHERE kr.state='draft' GROUP BY  kl.kw_branch_id)
            SELECT 
                COALESCE((SELECT alias FROM kw_res_branch WHERE id = COALESCE(mte.location, ma.location)), 'Unknown') AS location,
                COALESCE(ma.mrf_approved, 0) AS mrf_approved,COALESCE(mte.mrf_raised, 0) AS mrf_raised
                FROM draft_mrf mte FULL OUTER JOIN mrf_approved ma ON mte.location = ma.location
	        """,(fiscal_year_id,fiscal_year_id))
       
        data = cr.fetchall()
        for row in data:
            loc_data = row[0]
            value = row[1]
            rate = row[2]
            loc_mrf_tagged.append({
                'name': loc_data,
                'category': value,
                'data': rate
            })
        return loc_mrf_tagged
    
    @api.model
    def get_budget_typ_ratio(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        budget_mrf_tagged = []
        cr = self._cr
        cr.execute("""WITH  mrf_approved AS (
            SELECT kr.requisition_type AS budget,
            COUNT(*) AS mrf_approved FROM kw_recruitment_requisition kr 
            JOIN account_fiscalyear cfy ON kr.create_date::date >= cfy.date_start AND kr.create_date::date <= cfy.date_stop AND cfy.id =%s
            WHERE kr.state = 'approve' GROUP BY  kr.requisition_type),
        mrf_draft AS (SELECT kr.requisition_type AS budget,COUNT(*) AS mrf_raised 
            FROM kw_recruitment_requisition kr JOIN account_fiscalyear cfy ON kr.create_date::date >= cfy.date_start AND kr.create_date::date <= cfy.date_stop AND cfy.id =%s
            WHERE  kr.state = 'draft' GROUP BY  kr.requisition_type)
        SELECT COALESCE(mte.budget, ma.budget) AS budget,
        COALESCE(ma.mrf_approved, 0) AS mrf_approved,COALESCE(mte.mrf_raised, 0) AS mrf_raised
            FROM mrf_draft mte FULL OUTER JOIN mrf_approved ma ON mte.budget = ma.budget
                FULL OUTER JOIN mrf_draft md ON mte.budget = md.budget

	        """,(fiscal_year_id,fiscal_year_id))
       
        data = cr.fetchall()
        for row in data:
            budget_data = row[0]
            value = row[1]
            rate = row[2]
            budget_mrf_tagged.append({
                'name': budget_data,
                'category': value,
                'data': rate
            })
        return budget_mrf_tagged
    
    
    @api.model
    def get_hire_resource_typ_ratio(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        hire_resource_mrf_tagged = []
        cr = self._cr
        cr.execute("""WITH mrf_approved AS (SELECT kr.resource AS resource,COUNT(*) AS mrf_approved 
                FROM kw_recruitment_requisition kr 
                JOIN account_fiscalyear cfy 
                ON kr.create_date::date >= cfy.date_start AND kr.create_date::date <= cfy.date_stop AND cfy.id =%s
                WHERE kr.state = 'approve' GROUP BY  kr.resource),  
            mrf_draft AS (SELECT kr.resource AS resource,COUNT(*) AS mrf_raised 
                FROM kw_recruitment_requisition kr JOIN account_fiscalyear cfy 
                ON kr.create_date::date >= cfy.date_start AND kr.create_date::date <= cfy.date_stop AND cfy.id =%s
                        WHERE  kr.state = 'draft' GROUP BY  kr.resource)
                SELECT 
                    COALESCE(mte.resource, ma.resource) AS resource,
                    COALESCE(ma.mrf_approved, 0) AS mrf_approved,
                    COALESCE(mte.mrf_raised, 0) AS mrf_raised FROM mrf_draft mte 
				FULL OUTER JOIN mrf_approved ma ON mte.resource = ma.resource WHERE mte.resource IS NOT NULL and ma.resource IS NOT NULL

	        """,(fiscal_year_id,fiscal_year_id))
       
        data = cr.fetchall()
        for row in data:
            hire_data = row[0]
            value = row[1]
            rate = row[2]
            hire_resource_mrf_tagged.append({
                'name': hire_data,
                'category': value,
                'data': rate
            })
        return hire_resource_mrf_tagged
    
    
    @api.model
    def get_skill_mrf_ratio(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        skill_mrf_tagged = []
        cr = self._cr
        cr.execute("""WITH mrf_approved AS ( SELECT kr.technology AS skill,COUNT(*) AS mrf_approved 
                FROM kw_recruitment_requisition kr 
                JOIN account_fiscalyear cfy ON kr.create_date::date >= cfy.date_start AND kr.create_date::date <= cfy.date_stop AND cfy.id =%s
                WHERE kr.state = 'approve' AND kr.technology IS NOT NULL GROUP BY  kr.technology),
            mrf_draft AS ( SELECT kr.technology AS skill,
                    COUNT(*) AS mrf_raised 	FROM kw_recruitment_requisition kr 
                    JOIN account_fiscalyear cfy ON kr.create_date::date >= cfy.date_start AND kr.create_date::date <= cfy.date_stop AND cfy.id =%s
                WHERE kr.state = 'draft' AND kr.technology IS NOT NULL GROUP BY  kr.technology)
            SELECT 
                COALESCE((SELECT name FROM kw_skill_master WHERE id = COALESCE(mte.skill, ma.skill)), 'Unknown') AS skill,
                COALESCE(ma.mrf_approved, 0) AS mrf_approved,
                COALESCE(mte.mrf_raised, 0) AS mrf_raised
                    FROM mrf_draft mte 
                        FULL OUTER JOIN mrf_approved ma ON mte.skill = ma.skill


	        """,(fiscal_year_id,fiscal_year_id))
       
        data = cr.fetchall()
        for row in data:
            skill_data = row[0]
            value = row[1]
            rate = row[2]
            skill_mrf_tagged.append({
                'name': skill_data,
                'category': value,
                'data': rate
            })
        return skill_mrf_tagged
    
    
    @api.model
    def get_designation_mrf_ratio(self,**kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if kwargs and fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)])
            fiscal_year_id = fiscal_year.id
        designation_mrf_tagged = []
        cr = self._cr
        cr.execute("""WITH mrf_approved AS (SELECT kr.job_position AS designation,
                COUNT(*) AS mrf_approved FROM kw_recruitment_requisition kr 
                    JOIN account_fiscalyear cfy ON kr.create_date::date >= cfy.date_start AND kr.create_date::date <= cfy.date_stop AND cfy.id =%s
                    WHERE kr.state = 'approve' AND kr.job_position IS NOT NULL 	GROUP BY kr.job_position),
                mrf_draft AS ( SELECT kr.job_position AS designation,COUNT(*) AS mrf_raised 
                    FROM kw_recruitment_requisition kr JOIN account_fiscalyear cfy 
                    ON kr.create_date::date >= cfy.date_start AND kr.create_date::date <= cfy.date_stop AND cfy.id =%s
                    WHERE kr.state = 'draft' AND kr.job_position IS NOT NULL GROUP BY  kr.job_position)
                SELECT 
                        COALESCE((SELECT name FROM hr_job WHERE id = COALESCE(mte.designation, ma.designation)), 'Unknown') AS designation,
                        COALESCE(ma.mrf_approved, 0) AS mrf_approved,
                        COALESCE(mte.mrf_raised, 0) AS mrf_raised
                        FROM mrf_draft mte 
			FULL OUTER JOIN mrf_approved ma ON mte.designation = ma.designation


	        """,(fiscal_year_id,fiscal_year_id))
       
        data = cr.fetchall()
        for row in data:
            desg_data = row[0]
            value = row[1]
            rate = row[2]
            designation_mrf_tagged.append({
                'name': desg_data,
                'category': value,
                'data': rate
            })
        return designation_mrf_tagged

   
    @api.model
    def get_dept_wise_vacancy_ratio(self, **kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)], limit=1)
            fiscal_year_id = fiscal_year.id if fiscal_year else None
        dept_vacancy_data = []
        cr = self._cr
        cr.execute("""WITH resources AS (
                SELECT dept_name,SUM(no_of_resource) AS total_resources
                FROM (SELECT DISTINCT ON (kr.code) kr.dept_name,kr.code,kr.no_of_resource
                FROM kw_recruitment_requisition kr JOIN account_fiscalyear cfy 
                ON kr.create_date::date >= cfy.date_start AND kr.create_date::date <= cfy.date_stop AND cfy.id = %s
                WHERE kr.state = 'approve') AS subquery GROUP BY dept_name),
            employees AS (
                SELECT kr.dept_name,COUNT(hr.id) AS active_employees
                FROM hr_employee hr JOIN kw_recruitment_requisition kr 
                ON kr.id = hr.mrf_id JOIN account_fiscalyear cfy ON hr.date_of_joining >= cfy.date_start AND hr.date_of_joining <= cfy.date_stop AND
                kr.create_date::date >= cfy.date_start AND kr.create_date::date <= cfy.date_stop AND cfy.id = %s WHERE kr.state = 'approve' GROUP BY kr.dept_name)
            SELECT (SELECT name from hr_department where id=r.dept_name) as department,r.total_resources,
            COALESCE(r.total_resources, 0) - COALESCE(e.active_employees, 0) AS rest_vacancy_count
            FROM resources r LEFT JOIN employees e ON r.dept_name = e.dept_name
            WHERE COALESCE(r.total_resources, 0) - COALESCE(e.active_employees, 0) <> 0
            GROUP BY r.dept_name, r.total_resources, e.active_employees
            """,
            (fiscal_year_id,fiscal_year_id))

        
        data = cr.fetchall()
        for row in data:
            dept_vacancy_data.append({
                'name': row[0], 
                'category': row[2]
            })
        
        return dept_vacancy_data
    
    @api.model
    def get_desgination_wise_vacancy_ratio(self, **kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)], limit=1)
            fiscal_year_id = fiscal_year.id if fiscal_year else None

        desg_vacancy_data = []
        cr = self._cr
        cr.execute("""WITH resources AS (
            SELECT job_position,SUM(no_of_resource) AS total_resources
            FROM (SELECT DISTINCT ON (kr.code) kr.job_position,kr.code,kr.no_of_resource
            FROM kw_recruitment_requisition kr JOIN account_fiscalyear cfy 
           ON kr.create_date::date >= cfy.date_start AND kr.create_date::date <= cfy.date_stop AND cfy.id = %s
            WHERE kr.state = 'approve' ORDER BY kr.code) AS subquery GROUP BY job_position),
        employees AS (
            SELECT kr.job_position,COUNT(hr.id) AS active_employees
            FROM hr_employee hr JOIN kw_recruitment_requisition kr 
            ON kr.id = hr.mrf_id and kr.job_position = hr.job_id JOIN account_fiscalyear cfy ON hr.date_of_joining >= cfy.date_start AND hr.date_of_joining <= cfy.date_stop AND
            kr.create_date::date >= cfy.date_start AND kr.create_date::date <= cfy.date_stop AND cfy.id = %s WHERE kr.state = 'approve' GROUP BY kr.job_position)
        SELECT (SELECT name from hr_job where id=r.job_position) as position,r.total_resources,
        COALESCE(r.total_resources, 0) - COALESCE(e.active_employees, 0) AS rest_vacancy_count
        FROM resources r LEFT JOIN employees e ON r.job_position = e.job_position
        WHERE COALESCE(r.total_resources, 0) - COALESCE(e.active_employees, 0) <> 0
        GROUP BY r.job_position, r.total_resources, e.active_employees """,
            (fiscal_year_id,fiscal_year_id))

        
        data = cr.fetchall()
        for row in data:
            desg_vacancy_data.append({
                'name': row[0], 
                'category': row[2]
            })
        
        return desg_vacancy_data

    @api.model
    def get_location_wise_vacancy_ratio(self, **kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)], limit=1)
            fiscal_year_id = fiscal_year.id if fiscal_year else None

        loc_vacancy_data = []
        cr = self._cr
        cr.execute("""WITH resources AS (
                SELECT branch_name, SUM(no_of_resource) AS total_resources
            FROM (SELECT DISTINCT ON (kr.code) 
                loc.kw_branch_id AS branch_name,kr.code, kr.no_of_resource FROM kw_recruitment_requisition kr
                JOIN account_fiscalyear cfy ON kr.create_date::date >= cfy.date_start AND kr.create_date::date <= cfy.date_stop AND cfy.id = %s
                JOIN kw_recruitment_location_kw_recruitment_requisition_rel rel ON kr.id = rel.kw_recruitment_requisition_id
                JOIN kw_recruitment_location loc ON rel.kw_recruitment_location_id = loc.id
                WHERE kr.state = 'approve' ORDER BY kr.code
            ) AS subquery GROUP BY branch_name),
            employees AS (SELECT 
            loc.kw_branch_id AS branch_name,
                COUNT(hr.id) AS active_employees FROM kw_recruitment_requisition kr
            JOIN account_fiscalyear cfy ON kr.create_date::date >= cfy.date_start AND kr.create_date::date <= cfy.date_stop  AND cfy.id = %s
            JOIN kw_recruitment_location_kw_recruitment_requisition_rel rel ON kr.id = rel.kw_recruitment_requisition_id
            JOIN kw_recruitment_location loc ON rel.kw_recruitment_location_id = loc.id
            JOIN hr_employee hr ON kr.id = hr.mrf_id AND hr.date_of_joining >= cfy.date_start AND hr.date_of_joining <= cfy.date_stop 
            WHERE kr.state = 'approve' GROUP BY branch_name)
            SELECT (SELECT alias from kw_res_branch where id=r.branch_name) as location,r.total_resources,
            COALESCE(r.total_resources, 0) - COALESCE(e.active_employees, 0) AS rest_vacancy_count
            FROM resources r LEFT JOIN employees e ON r.branch_name = e.branch_name
            WHERE COALESCE(r.total_resources, 0) - COALESCE(e.active_employees, 0) <> 0
            GROUP BY r.branch_name, r.total_resources, e.active_employees
             """,
            (fiscal_year_id,fiscal_year_id))

        
        data = cr.fetchall()
        for row in data:
            loc_vacancy_data.append({
                'name': row[0], 
                'category': row[2]
            })
        
        return loc_vacancy_data

    @api.model
    def get_skill_wise_vacancy_ratio(self, **kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)], limit=1)
            fiscal_year_id = fiscal_year.id if fiscal_year else None

        skill_vacancy_data = []
        cr = self._cr
        cr.execute("""WITH resources AS (
                SELECT technology,SUM(no_of_resource) AS total_resources
                FROM (SELECT DISTINCT ON (kr.code) kr.technology,kr.code,kr.no_of_resource
                FROM kw_recruitment_requisition kr JOIN account_fiscalyear cfy 
                ON kr.create_date::date >= cfy.date_start AND kr.create_date::date <= cfy.date_stop  AND cfy.id =%s
                WHERE kr.state = 'approve' ORDER BY kr.code) AS subquery GROUP BY technology),
            employees AS (
                SELECT kr.technology,COUNT(hr.id) AS active_employees
                FROM hr_employee hr JOIN kw_recruitment_requisition kr 
                ON kr.id = hr.mrf_id JOIN account_fiscalyear cfy ON kr.create_date::date >= cfy.date_start AND kr.create_date::date <= cfy.date_stop
                AND hr.date_of_joining >= cfy.date_start AND hr.date_of_joining <= cfy.date_stop 
                AND cfy.id =%s WHERE kr.state = 'approve' GROUP BY kr.technology)
            SELECT (SELECT name from kw_skill_master where id=r.technology) as position,r.total_resources,
            COALESCE(r.total_resources, 0) - COALESCE(e.active_employees, 0) AS rest_vacancy_count
            FROM resources r LEFT JOIN employees e ON r.technology = e.technology
            WHERE COALESCE(r.total_resources, 0) - COALESCE(e.active_employees, 0) <> 0
            GROUP BY r.technology, r.total_resources, e.active_employees """,
            (fiscal_year_id,fiscal_year_id))

        
        data = cr.fetchall()
        for row in data:
            skill_vacancy_data.append({
                'name': row[0], 
                'category': row[2]
            })
        
        return skill_vacancy_data


    @api.model
    def get_dept_wise_joined_ratio(self, **kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)], limit=1)
            fiscal_year_id = fiscal_year.id if fiscal_year else None

        dept_wise_joined_data = []
        cr = self._cr
        cr.execute("""with a as
            (SELECT e.department_id,e.id, e.name AS name,rr.write_date::date AS mrf_app_date
            FROM hr_employee e join kw_recruitment_requisition rr ON rr.id = e.mrf_id and rr.dept_name = e.department_id
            JOIN account_fiscalyear cfy ON e.date_of_joining >= cfy.date_start AND e.date_of_joining <= cfy.date_stop
            where e.mrf_id is not null and rr.state = 'approve' and cfy.id=%s and e.employement_type not in 
            (SELECT id FROM kwemp_employment_type where code = 'O'))
            select (select name from hr_department where id=a.department_id) as department, COUNT(a.department_id) AS department_count
            from a WHERE a.department_id IS NOT NULL GROUP BY a.department_id """,(fiscal_year_id,))
        
        data = cr.fetchall()
        for row in data:
            dept_wise_joined_data.append({
                'name': row[0], 
                'category': row[1]
            })
        
        return dept_wise_joined_data
    
    @api.model
    def get_desgination_wise_joined_ratio(self, **kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)], limit=1)
            fiscal_year_id = fiscal_year.id if fiscal_year else None

        desg_wise_joined_data = []
        cr = self._cr
        cr.execute("""with a as
                (SELECT e.job_id,e.id, e.name AS name,rr.write_date::date AS mrf_app_date
                FROM hr_employee e join kw_recruitment_requisition rr ON rr.id = e.mrf_id and rr.job_position = e.job_id
                JOIN account_fiscalyear cfy ON e.date_of_joining >= cfy.date_start AND e.date_of_joining <= cfy.date_stop
                where e.mrf_id is not null and rr.state = 'approve' and cfy.id=%s and e.employement_type not in 
                (SELECT id FROM kwemp_employment_type where code = 'O'))
                
                select (select name from hr_job where id=a.job_id) as designation, COUNT(a.job_id) AS designation_count
                from a WHERE a.job_id IS NOT NULL GROUP BY a.job_id """,
            (fiscal_year_id,))

        
        data = cr.fetchall()
        for row in data:
            desg_wise_joined_data.append({
                'name': row[0], 
                'category': row[1]
            })
        
        return desg_wise_joined_data
    
    @api.model
    def get_location_wise_joined_ratio(self, **kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)], limit=1)
            fiscal_year_id = fiscal_year.id if fiscal_year else None

        loc_wise_joined_data = []
        cr = self._cr
        cr.execute("""with a as
            (SELECT e.base_branch_id,e.id, e.name AS name
            FROM hr_employee e join kw_recruitment_requisition rr ON rr.id = e.mrf_id
            JOIN account_fiscalyear cfy ON e.date_of_joining >= cfy.date_start AND e.date_of_joining <= cfy.date_stop
            where mrf_id is not null and rr.state = 'approve' and cfy.id=%s and e.employement_type not in 
            (SELECT id FROM kwemp_employment_type where code = 'O'))
            
            select (select alias from kw_res_branch where id=a.base_branch_id) as location, COUNT(a.base_branch_id) AS location_count
            from a WHERE a.base_branch_id IS NOT NULL GROUP BY a.base_branch_id """,
            (fiscal_year_id,))

        
        data = cr.fetchall()
        for row in data:
            loc_wise_joined_data.append({
                'name': row[0], 
                'category': row[1]
            })
        
        return loc_wise_joined_data

    
    @api.model
    def get_skill_wise_joined_ratio(self, **kwargs):
        fy_data = kwargs.get('fy_id', False)
        today = datetime.today().date()
        if fy_data:
            fiscal_year_id = int(fy_data)
        else:
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', today), ('date_stop', '>=', today)], limit=1)
            fiscal_year_id = fiscal_year.id if fiscal_year else None

        skill_wise_joined_data = []
        cr = self._cr
        cr.execute("""with a as
            (SELECT e.primary_skill_id,e.id, e.name AS name,rr.write_date::date AS mrf_app_date
            FROM hr_employee e join kw_recruitment_requisition rr ON rr.id = e.mrf_id and rr.technology = e.primary_skill_id
            JOIN account_fiscalyear cfy ON e.date_of_joining >= cfy.date_start AND e.date_of_joining <= cfy.date_stop
            where e.mrf_id is not null and rr.state = 'approve' and cfy.id=%s and e.employement_type not in 
            (SELECT id FROM kwemp_employment_type where code = 'O'))
            
            select (select name from kw_skill_master where id=a.primary_skill_id) as skill, COUNT(a.primary_skill_id) AS skill_count
            from a WHERE a.primary_skill_id IS NOT NULL GROUP BY a.primary_skill_id """,
            (fiscal_year_id,))

        
        data = cr.fetchall()
        for row in data:
            skill_wise_joined_data.append({
                'name': row[0], 
                'category': row[1]
            })
        
        return skill_wise_joined_data
    
    
    
    
    @api.model
    def get_fy_filter_data(self):
        financial_year_dict = []
        cr = self._cr
        fy_query = """select id as id,  name as name 
            from account_fiscalyear order by name desc limit 7"""

        cr.execute(fy_query)
        fy_data = cr.fetchall()

        for row in fy_data:
            financial_year_dict.append({'id': row[0], 'name': row[1]})

        return [financial_year_dict]
    
    @api.model
    def get_filter_data(self):
        edging_fy_data = {
            'dashboard_fy_filters': self.get_fy_filter_data(),
        }
        return edging_fy_data
    