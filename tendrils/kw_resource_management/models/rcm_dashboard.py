from odoo import models, fields, api, _
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta


class Employee(models.Model):
    _name = 'talent_pool_dashboard'
    _description = 'talent_pool_dashboard'

    @api.model
    def get_talent_pool_count(self):
        cr = self._cr
        cr.execute("""select count(*) from sbu_bench_resource """)
        data = cr.fetchall()
        return data

    @api.model
    def get_under_skill_count(self):
        cr = self._cr
        cr.execute("""select count(*) from sbu_bench_resource sbr
                        join kw_engagement_master pmaster on pmaster.id= sbr.engagement_plan_by_id
	                    where  pmaster.code='usp'""")
        data = cr.fetchall()
        return data

    @api.model
    def get_standard_orientation_count(self):
        cr = self._cr
        cr.execute("""select count(*) from sbu_bench_resource sbr
                        join kw_engagement_master pmaster on pmaster.id= sbr.engagement_plan_by_id
                        where  pmaster.code='sop' """)
        data = cr.fetchall()
        return data

    @api.model
    def get_future_projection_count(self):
        cr = self._cr
        cr.execute("""select count(*) from sbu_bench_resource where future_projection is not null""")
        data = cr.fetchall()
        return data

    @api.model
    def get_investment_resource_count(self):
        cr = self._cr
        cr.execute("""select count(*) from sbu_bench_resource sbr
                        join kw_engagement_master pmaster on pmaster.id= sbr.engagement_plan_by_id
                        where  pmaster.code='ir' """)
        data = cr.fetchall()
        return data

    @api.model
    def get_designation_wise_strenth(self):
        designation_data = {}
        cr = self._cr
        cr.execute("""select hj.name,count(*) 
                   from sbu_bench_resource tpr
                    left join hr_job hj on hj.id= tpr.designation
                    where tpr.designation is not null
                    group by hj.name """)
        data = cr.fetchall()
        for row in data:
            designation = row[0]
            value = row[1]
            if designation in designation_data:
                designation_data[designation] += value
            else:
                designation_data[designation] = value

        formatted_data = [[designation, value] for designation, value in designation_data.items()]
        return [formatted_data]

    @api.model
    def get_location_wise_strenth(self):
        location_data = {}
        cr = self._cr
        cr.execute("""select krb.alias,count(*) 
                        from sbu_bench_resource tpr
                        left join kw_res_branch krb on krb.id = tpr.job_branch_id
					    where tpr.job_branch_id is not null
                        group by krb.alias """)
        data = cr.fetchall()
        for row in data:
            location = row[0]
            value = row[1]
            if location in location_data:
                location_data[location] += value
            else:
                location_data[location] = value

        formatted_loc_data = [[location, value] for location, value in location_data.items()]
        return [formatted_loc_data]

    @api.model
    def get_skill_wise_strenth(self):
        skill_data = {}
        cr = self._cr
        cr.execute("""select skl.name,count(*) 
                   from sbu_bench_resource tpr
                    left join kw_skill_master skl on skl.id = tpr.primary_skill_id
					where tpr.primary_skill_id is not null
                    group by skl.name """)
        data = cr.fetchall()
        for row in data:
            skill = row[0]
            value = row[1]
            if skill in skill_data:
                skill_data[skill] += value
            else:
                skill_data[skill] = value

        formatted_skill_data = [[skill, value] for skill, value in skill_data.items()]
        return [formatted_skill_data]

    @api.model
    def get_engagement_plan_wise_distribution(self):
        engagement_plan_data = {}
        cr = self._cr
        cr.execute("""select kem.name,count(*) 
                    from sbu_bench_resource tpr
                    left join kw_engagement_master kem on kem.id= tpr.engagement_plan_by_id
					where tpr.engagement_plan_by_id is not null
                    group by kem.name """)
        data = cr.fetchall()
        for row in data:
            engagement_plan = row[0]
            value = row[1]
            if engagement_plan in engagement_plan_data:
                engagement_plan_data[engagement_plan] += value
            else:
                engagement_plan_data[engagement_plan] = value

        formatted_engagement_plan_data = [[engagement_plan, value] for engagement_plan, value in
                                          engagement_plan_data.items()]
        return [formatted_engagement_plan_data]

    @api.model
    def get_bench_day_wise_distribution(self):
        formatted_bench_days_data = []
        cr = self._cr
        cr.execute("""SELECT 
                            below_90_days,
                            COUNT(*) AS count
                        FROM (
                            SELECT 
                                CASE
                                    WHEN interval_day < 90 THEN '<90 Days'
                                    WHEN interval_day >= 90 AND interval_day < 180 THEN '90-180 Days'
                                    ELSE '>180 Days'
                                END AS below_90_days
                            FROM sbu_bench_resource
                        ) subquery
                        GROUP BY below_90_days
                        ORDER BY
                            CASE below_90_days
                                WHEN '<90 Days' THEN 1
                                WHEN '90-180 Days' THEN 2
                                ELSE 3
                            END
                        """)
        data = cr.fetchall()
        for row in data:
            formatted_bench_days_data.append({
                'name': row[0],
                'y': row[1]
            })
        formatted_bench_days_data.append({

            'name': 'Total',
            'isIntermediateSum': True,
        })
        return [formatted_bench_days_data]

    @api.model
    def get_skill_distribution_in_designation(self):
        query = f"""select  
                    count(*),
                    ksm.name as skill,
                    hj.name as designation
                from sbu_bench_resource tpr
                left join hr_job hj on hj.id=tpr.designation
                join kw_skill_master ksm on ksm.id=tpr.primary_skill_id
                group by ksm.name,hj.name """
        self._cr.execute(query)
        result = self._cr.fetchall()
        skill_distribution = []
        for row in result:
            skill_count = row[0]
            skill = row[1]
            designation = row[2]
            skill_distribution.append({
                'name': skill,
                'category': designation,
                'data': skill_count
            })
        return skill_distribution


class WorkForceAnalyticsDashboard(models.Model):
    _name = "work_force_analytics_dashboard"
    _description = "work_force_analytics_dashboard"


    @api.model
    def get_total_resource_nexus_count(self):
        cr = self._cr
        cr.execute(
            """select count(*) from work_force_analytics_report """)
        data = cr.fetchall()
        return data
    
    @api.model
    def get_company_branch_ditribution(self):
        query = f"""select  
                        count(*),
                        krb.alias as branch,
			            comp.name as company
                        from work_force_analytics_report wr
                        left join res_company comp on comp.id=wr.emp_company_id
                        join kw_res_branch krb on krb.id=wr.job_branch_id
                        where wr.job_branch_id is not null
                        group by krb.alias,comp.name """
        self._cr.execute(query)
        result = self._cr.fetchall()
        company_branch_data = []
        for row in result:
            branch_resource_count = row[0]
            company = row[1]
            branch = row[2]
            company_branch_data.append({
                'name': company,
                'category': branch,
                'data': branch_resource_count
            })
        return company_branch_data
    
    @api.model
    def get_out_source_resource_nexus_count(self):
        cr = self._cr
        cr.execute(
            """select count(*) from work_force_analytics_report wr where wr.employement_type  in (SELECT id FROM kwemp_employment_type where code = 'O') """)
        data = cr.fetchall()
        return data

    @api.model
    def get_total_csm_resource_nexus_count(self):
        cr = self._cr
        cr.execute(
            """select count(*) from work_force_analytics_report wr where wr.employement_type not in (SELECT id FROM kwemp_employment_type where code = 'O') """)
        data = cr.fetchall()
        return data

    @api.model
    def get_delivery_dept_count(self):
        cr = self._cr
        cr.execute(
            """select count(*) from work_force_analytics_report wr where wr.employement_type not in (SELECT id FROM kwemp_employment_type where code = 'O') and wr.department_id in (select id from hr_department where code='BSS')""")
        data = cr.fetchall()
        return data

    @api.model
    def get_sbu_resource_count(self):
        cr = self._cr
        cr.execute(
            """select count(*) from work_force_analytics_report wr where wr.sbu_type='sbu' and wr.sbu_master_id is not null and wr.department_id in (select id from hr_department where code='BSS')""")
        data = cr.fetchall()
        return data

    @api.model
    def get_horizontal_resource_count(self):
        cr = self._cr
        cr.execute(
            """select count(*) from work_force_analytics_report wr where wr.sbu_type='horizontal' and wr.sbu_master_id not in (select id from kw_sbu_master where name='C-Suite') and wr.department_id in (select id from hr_department where code='BSS')""")
        data = cr.fetchall()
        return data

    @api.model
    def get_talent_pool_resource_count(self):
        cr = self._cr
        cr.execute("""select count(*) from sbu_bench_resource""")
        data = cr.fetchall()
        return data

    @api.model
    def get_csuite_resource_count(self):
        cr = self._cr
        cr.execute(
            """select count(*) from work_force_analytics_report wr where wr.sbu_type='horizontal' and wr.sbu_master_id in (select id from kw_sbu_master where name='C-Suite') and wr.department_id in (select id from hr_department where code='BSS') """)
        data = cr.fetchall()
        return data

    @api.model
    def get_cmpn_ovhd_csm_resource_count(self):
        cr = self._cr
        cr.execute("""select count(*) from work_force_analytics_report wr 
                           where wr.employement_type not in (SELECT id FROM kwemp_employment_type where code = 'O')
                                and wr.emp_role in (select id from kwmaster_role_name  where code in ('O'))
                                """)
        data = cr.fetchall()
        return data

    @api.model
    def get_cmpn_ovhd_outsource_resource_count(self):
        cr = self._cr
        cr.execute("""select count(*) from work_force_analytics_report wr 
                           where wr.employement_type in (SELECT id FROM kwemp_employment_type where code = 'O')
                                and wr.emp_role in (select id from kwmaster_role_name  where code in ('O'))
                                """)
        data = cr.fetchall()
        return data

    @api.model
    def get_dlvr_lab_csm_resource_count(self):
        cr = self._cr
        cr.execute("""select count(*) from work_force_analytics_report wr 
                           where wr.employement_type not in (SELECT id FROM kwemp_employment_type where code = 'O')
                                and wr.emp_role in (select id from kwmaster_role_name  where code in ('DL'))
                                """)
        data = cr.fetchall()
        return data

    @api.model
    def get_dlvr_lab_outsource_resource_count(self):
        cr = self._cr
        cr.execute("""select count(*) from work_force_analytics_report wr 
                           where wr.employement_type in (SELECT id FROM kwemp_employment_type where code = 'O')
                                and wr.emp_role in (select id from kwmaster_role_name  where code in ('DL'))
                                """)
        data = cr.fetchall()
        return data

    @api.model
    def get_dlvr_ovhd_csm_resource_count(self):
        cr = self._cr
        cr.execute("""select count(*) from work_force_analytics_report wr 
                           where wr.employement_type not in (SELECT id FROM kwemp_employment_type where code = 'O')
                                and wr.emp_role in (select id from kwmaster_role_name  where code in ('S'))
                                """)
        data = cr.fetchall()
        return data

    @api.model
    def get_dlvr_ovhd_outsource_resource_count(self):
        cr = self._cr
        cr.execute("""select count(*) from work_force_analytics_report wr 
                           where wr.employement_type in (SELECT id FROM kwemp_employment_type where code = 'O')
                                and wr.emp_role in (select id from kwmaster_role_name  where code in ('S'))	
                                """)
        data = cr.fetchall()
        return data

    @api.model
    def get_resource_dpmlnt_csm_resource_count(self):
        cr = self._cr
        cr.execute("""select count(*) from work_force_analytics_report wr 
                           where wr.employement_type not in (SELECT id FROM kwemp_employment_type where code = 'O')
                                and wr.emp_role in (select id from kwmaster_role_name  where code in ('R'))
                                """)
        data = cr.fetchall()
        return data

    @api.model
    def get_resource_dpmnlt_outsource_resource_count(self):
        cr = self._cr
        cr.execute("""select count(*) from work_force_analytics_report wr 
                           where wr.employement_type in (SELECT id FROM kwemp_employment_type where code = 'O')
                                and wr.emp_role in (select id from kwmaster_role_name  where code in ('R'))
                                """)
        data = cr.fetchall()
        return data

    @api.model
    def get_delivery_consultancy_resource_count(self):
        cr = self._cr
        cr.execute("""select count(*) from work_force_analytics_report wr 
                           where wr.employement_type not in (SELECT id FROM kwemp_employment_type where code = 'O')
                                and wr.emp_role in (select id from kwmaster_role_name  where code in ('DC'))
                                """)
        data = cr.fetchall()
        return data

    @api.model
    def get_department_wise_resource_distribution(self):
        dept_data = {}
        cr = self._cr
        cr.execute("""select dept.name,count(*) 
                                from work_force_analytics_report wr
                                left join hr_department dept on dept.id = wr.department_id
                                where wr.department_id is not null 
                                and wr.employement_type not in (SELECT id FROM kwemp_employment_type where code = 'O')
                                group by dept.name """)
        data = cr.fetchall()
        for row in data:
            department = row[0]
            value = row[1]
            if department in dept_data:
                dept_data[department] += value
            else:
                dept_data[department] = value

        formatted_department_data = [[department, value] for department, value in dept_data.items()]
        return [formatted_department_data]

    @api.model
    def get_sbu_wise_resource(self):
        sbu_data = {}
        cr = self._cr
        cr.execute("""select sbm.name,count(*) 
                                from work_force_analytics_report wr
                                left join kw_sbu_master sbm on sbm.id = wr.sbu_master_id
                                where wr.sbu_type='sbu' and wr.sbu_master_id is not null and wr.department_id in (select id from hr_department where code='BSS')
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
    def get_total_delivery_resource_count(self):
        formatted_delivery_data = []
        cr = self._cr
        cr.execute("""SELECT
                                'SBU' AS category,
                                COUNT(*) AS result_count
                                
                            FROM
                                work_force_analytics_report wr
                            WHERE
                                wr.sbu_type = 'sbu'
                                AND wr.sbu_master_id IS NOT NULL
                                AND wr.department_id IN (SELECT id FROM hr_department WHERE code = 'BSS')

                            UNION ALL

                            SELECT
                                'Horizontal' AS category,
                                COUNT(*) AS result_count
                                
                            FROM
                                work_force_analytics_report wr
                            WHERE
                                wr.emp_category IN (SELECT id FROM kwmaster_category_name WHERE code IN ('DIX', 'R&D', 'TQA', 'DBA', 'TD', 'ERP', 'Framework','EIT'))
                                -- AND wr.sbu_master_id NOT IN (SELECT id FROM kw_sbu_master WHERE name = 'C-Suite')
                                AND wr.department_id IN (SELECT id FROM hr_department WHERE code = 'BSS')

                            UNION ALL

                            SELECT
                                'Talent Pool' AS categor,
                                COUNT(*) AS result_count
                                
                            FROM
                                sbu_bench_resource

                            UNION ALL

                            SELECT
                                
                                'C-suite' AS category,
                                COUNT(*) AS result_count
                            FROM
                                work_force_analytics_report wr
                            WHERE
                                wr.sbu_type = 'horizontal'
                                AND wr.sbu_master_id IN (SELECT id FROM kw_sbu_master WHERE name = 'C-Suite')
                                AND wr.department_id IN (SELECT id FROM hr_department WHERE code = 'BSS')
                        """)
        data = cr.fetchall()
        for row in data:
            formatted_delivery_data.append({
                'name': row[0],
                'y': row[1]
            })
        return [formatted_delivery_data]

    @api.model
    def get_horizontal_wise_resource_count(self):
        horizontal_data = {}
        cr = self._cr
        cr.execute("""select ct.name,count(*) 
                                from work_force_analytics_report wr
                                left join kwmaster_category_name ct on ct.id = wr.emp_category
                                where 
                                wr.emp_category in (SELECT id FROM kwmaster_category_name WHERE code IN ('DIX','R&D','TQA','DBA','TD','ERP','Framework','EIT'))
								-- AND wr.sbu_master_id  not in (select id from kw_sbu_master where name='C-Suite')
                                group by ct.name
                """)
        data = cr.fetchall()
        for row in data:
            horizontal_resource = row[0]
            value = row[1]
            if horizontal_resource in horizontal_data:
                horizontal_data[horizontal_resource] += value
            else:
                horizontal_data[horizontal_resource] = value

        formatted_data = [[horizontal_resource, value] for horizontal_resource, value in horizontal_data.items()]
        return [formatted_data]

    @api.model
    def get_employee_role_wise_resource(self, **kwargs):
        role = kwargs.get('role', False)

        employee_role_data = {}
        cr = self._cr
        cr.execute("""select  
                        count(*),
			            kcn.name as role
                        from work_force_analytics_report wr
                        left join kwmaster_category_name kcn on kcn.id=wr.emp_category
                        where wr.emp_category in (select id from kwmaster_category_name where code in ('BA','DEV','TTL','PM')) 
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
    def get_sbu_wise_role_distribution(self):
        query = f"""select  
                        count(*),
                        kcn.name as role,
                        sbm.name as sbu
                        from work_force_analytics_report wr
                        left join kw_sbu_master sbm on sbm.id = wr.sbu_master_id
                        left join kwmaster_category_name kcn on kcn.id=wr.emp_category
						where wr.emp_category in (select id from kwmaster_category_name where code in ('BA','DEV','TTL','PM'))
						AND wr.sbu_master_id is not null
                        AND sbm.type='sbu'
                        group by kcn.name,sbm.name  """
        self._cr.execute(query)
        result = self._cr.fetchall()
        sbu_wise_role = []
        for row in result:
            role_count = row[0]
            role = row[1]
            sbu = row[2]
            sbu_wise_role.append({
                'name': role,
                'category': sbu,
                'data': role_count
            })
        return sbu_wise_role

    @api.model
    def get_location_wise_role_ditribution(self):
        query = f"""select  
                        count(*),
			            kcn.name as role,
                        krb.alias as location
                        from work_force_analytics_report wr
                        left join kwmaster_category_name kcn on kcn.id=wr.emp_category
                        join kw_res_branch krb on krb.id=wr.job_branch_id
                        where wr.emp_category in (select id from kwmaster_category_name where code in ('BA','DEV','TTL','PM')) 
                        and wr.job_branch_id is not null
                        group by krb.alias,kcn.name  """
        self._cr.execute(query)
        result = self._cr.fetchall()
        loc_role_wise = []
        for row in result:
            role_count = row[0]
            location = row[1]
            role = row[2]
            loc_role_wise.append({
                'name': location,
                'category': role,
                'data': role_count
            })
        return loc_role_wise
    
    @api.model
    def get_dba_wise_resource_distribution(self):
        query = f"""
            SELECT  
                    COUNT(*) AS count,
					skl.name AS skill,
                    sbm.name AS sbu
                FROM work_force_analytics_report wr
                LEFT JOIN kw_sbu_master sbm ON sbm.id = wr.sbu_master_id
                LEFT JOIN kw_skill_master skl ON skl.id = wr.primary_skill_id
	
                WHERE 
					wr.sbu_type = 'sbu'
                    AND wr.sbu_master_id IS NOT NULL 
					AND wr.primary_skill_id IN (SELECT id FROM kw_skill_master 
                            WHERE name in('SQL Server','MS SQL','DB Programming(My SQL)','PostgreSQL','Oracle','MySQL','Postgress SQL'))
					AND wr.emp_role IN (SELECT id FROM kwmaster_role_name WHERE code in ('DL'))
					AND wr.emp_category IN (SELECT id FROM kwmaster_category_name WHERE code in ('DEV'))
                    GROUP BY skl.name,sbm.name
					ORDER BY sbm.name
            """
        self._cr.execute(query)
        result = self._cr.fetchall()
        dba_wise_resource = []
        for row in result:
            skill_count = row[0]
            skill = row[1]
            sbu = row[2]
            dba_wise_resource.append({
                'name': skill,
                'category': sbu,
                'data': skill_count
            })
        return dba_wise_resource
    
    @api.model
    def get_emtech_wise_skill_distribution(self):
        query = f"""
            SELECT  
                    COUNT(*) AS count,
					skl.name AS skill,
                    sbm.name AS sbu
                FROM work_force_analytics_report wr
                LEFT JOIN kw_sbu_master sbm ON sbm.id = wr.sbu_master_id
                LEFT JOIN kw_skill_master skl ON skl.id = wr.primary_skill_id
	
                WHERE 
                    wr.sbu_type = 'sbu'
                    AND wr.sbu_master_id IS NOT NULL 
					AND wr.primary_skill_id IN (SELECT id FROM kw_skill_master WHERE name in ('AI/ML','Blockchain','Chatbot','ETL','GIS','IOT','Oracle BI
												','Power BI','SAS','SAS DI','SAS VA','Superset','Tableau','RPA','Informatica'))
                    GROUP BY skl.name,sbm.name
					ORDER BY sbm.name

            """
        self._cr.execute(query)
        result = self._cr.fetchall()
        emtech_skill_resource = []
        for row in result:
            skill_count = row[0]
            skill = row[1]
            sbu = row[2]
            emtech_skill_resource.append({
                'name': skill,
                'category': sbu,
                'data': skill_count
            })
        return emtech_skill_resource

    @api.model
    def get_resource_nexus_filter_data_sql(self):
        employee_role_dict = []
        cr = self._cr

        ### employee role wise  Filter Query Start ###
        employee_role_query = """select club_role as id,club_role as name from work_force_analytics_report where club_role IN ('Coder/Programmer', 'Leader/Manager', 'Project Manager', 'Business Analyst') group by club_role

                            ORDER BY name ASC"""
        # employee_role_query = """select distinct(emp_category) as id,  mst.name as name 
        #                     from work_force_analytics_report wr
        #                     left join kwmaster_category_name mst on mst.id= wr.emp_category
        #                     where wr.emp_category is not null
        #                     order by name asc"""

        cr.execute(employee_role_query)
        employee_role_data = cr.fetchall()

        for row in employee_role_data:
            employee_role_dict.append({'id': row[0], 'name': row[1]})

        ### employee role wise  Filter Query End ###
        return [employee_role_dict]

    @api.model
    def get_resource_nexus_filter_data(self):
        resource_nexus_filter_data = {
            'resource_nexus_dashboard_filters': self.get_resource_nexus_filter_data_sql(),
        }
        return resource_nexus_filter_data


class SkillAnalyticsDashboard(models.Model):
    _name = "skill_data_analytics_dashboard"
    _description = "skill_data_analytics_dashboard"

    @api.model
    def get_location_wise_skill_count(self, **kwargs):
        location = kwargs.get('location', False)
        skill = kwargs.get('skill', False)
        skill_location_wise = []
        cr = self._cr

        skill_query = "sar.primary_skill IS NOT NULL"

        if kwargs and location and skill:
            where_clause = f"{skill_query} AND sar.primary_skill = {skill} AND krb.id = {location}"
        else:
            where_clause = skill_query
            
        query = f"""
            WITH top_skills AS (
                SELECT
                    sar.primary_skill,
                    COUNT(*) AS skill_count
                FROM
                    skill_dashboard_analytics_report sar
                JOIN
                    kw_skill_master ksm ON ksm.id = sar.primary_skill
                LEFT JOIN
                    kw_res_branch krb ON krb.id = sar.emp_location
                GROUP BY
                    sar.primary_skill
                ORDER BY
                    COUNT(*) DESC
                LIMIT 10
            )
            SELECT
                COUNT(*) AS skill_count,
                krb.alias AS location,
                ksm.name AS skill
            FROM
                skill_dashboard_analytics_report sar
            JOIN
                kw_skill_master ksm ON ksm.id = sar.primary_skill
            LEFT JOIN
                kw_res_branch krb ON krb.id = sar.emp_location
            JOIN
                top_skills ts ON sar.primary_skill = ts.primary_skill
            WHERE {where_clause} 
            GROUP BY
                ksm.name,
                krb.alias
            ORDER BY
                skill_count DESC

        """

        cr.execute(query)
        result = cr.fetchall()

        for row in result:
            skill_count = row[0]
            skill = row[1]
            location = row[2]
            skill_location_wise.append({
                'name': skill,
                'category': location,
                'data': skill_count
            })
        return skill_location_wise

    @api.model
    def get_primary_skill_count(self, **kwargs):
        primary_skill = kwargs.get('primary_skill_id', False)
        p_skill = {}
        cr = self._cr

        where_clause = f"sar.primary_skill IS NOT NULL"
        if kwargs and primary_skill:
            where_clause += f" AND sar.primary_skill = {primary_skill}"

        query = f"""
                SELECT skl.name, COUNT(*) AS skill_count
                FROM skill_dashboard_analytics_report sar
                LEFT JOIN kw_skill_master skl ON sar.primary_skill = skl.id
                WHERE {where_clause}
                GROUP BY skl.name
                ORDER BY skill_count DESC
                LIMIT 10
            """

        cr.execute(query)
        data = cr.fetchall()

        for row in data:
            primary = row[0]
            value = row[1]
            if primary in p_skill:
                p_skill[primary] += value
            else:
                p_skill[primary] = value

        primary_skill_data = [[primary, value] for primary, value in p_skill.items()]
        return [primary_skill_data]

    @api.model
    def get_skill_data_count_with_type(self, **kwargs):
        skill_type = kwargs.get('skill_type')
        skill_name = kwargs.get('skill_name')
        limit_clause = "FETCH FIRST 10 ROWS ONLY" if not (kwargs and skill_type) else ""
        skill_type_wise = []

        where_clause = ''
        params = {}
        if kwargs and skill_type and skill_name:
            where_clause = "WHERE skill_type = %(skill_type)s AND skill_id IN %(skill_name)s"
            params = {'skill_type': skill_type, 'skill_name': tuple(skill_name)}

        cr = self._cr
        query = f"""
            WITH ranked_skills AS (
            SELECT
                COUNT(*) AS skill_count,
                skill_type,
                skill_id,
                skill_name,
                ROW_NUMBER() OVER (PARTITION BY skill_name ORDER BY COUNT(*) DESC) AS skill_rank
            FROM (
                SELECT
                    k.name AS skill_name,
                    k.id AS skill_id,
                    CASE
                        WHEN sar.primary_skill = k.id THEN 'Primary'
                        WHEN sar.secondary_skill = k.id THEN 'Secondary'
                        WHEN sar.tertiarry_skill = k.id THEN 'Tertiary'
                    END AS skill_type
                FROM
                    skill_dashboard_analytics_report sar
                JOIN
                    kw_skill_master k ON k.id IN (sar.primary_skill, sar.secondary_skill, sar.tertiarry_skill)
            ) AS subquery
            GROUP BY skill_type, skill_name, skill_id
        )
        SELECT
            skill_count,
            skill_type,
            skill_name,
            skill_id
        FROM (
            SELECT DISTINCT ON (skill_name)
                skill_count,
                skill_type,
                skill_id,
                skill_name
            FROM ranked_skills
             {where_clause}
            ORDER BY skill_name, skill_count DESC
             {limit_clause}
        ) AS top_skills
        ORDER BY
            CASE skill_type
                WHEN 'Primary' THEN 1
                WHEN 'Secondary' THEN 2
                WHEN 'Tertiarry' THEN 3
            END,
            skill_count DESC,
            skill_name,
            skill_type
        """.format(where_clause=where_clause, limit_clause=limit_clause)

        cr.execute(query, params)
        result = cr.fetchall()

        for row in result:
            skill_count = row[0]
            skill_name = row[1]
            skill_type = row[2]
            skill_type_wise.append({
                'name': skill_name,
                'category': skill_type,
                'data': skill_count
            })
        return skill_type_wise

    @api.model
    def get_skill_wise_role_count(self, **kwargs):
        role = kwargs.get('role', False)
        skill = kwargs.get('skill', False)
        skill_wise_role = []
        cr = self._cr

        skill_query = "sar.primary_skill IS NOT NULL"

        if kwargs and role and skill:
            if role == 'Coder/Programmer':
                query = "select id from hr_job where name IN ('Data Engineer', 'Programmer', 'Programmer Analyst','Research Analyst','Software Engineer','Sr. Data Analyst','Sr. Data Engineer','Sr. Database Analyst','Sr. Programmer Analyst','Sr. Software Engineer')"
            elif role == 'Leader/Manager':
                query = "select id from hr_job where name IN ('Data Scientist', 'Module Lead', 'Project Leader','Sr. Project leader','Sr. Tech Lead','Tech Lead','Technical Architect')"
            elif role == 'Project Manager':
                query = "select id from hr_job where name IN ('Associate Project Manager', 'Associate VP (Projects)', 'Chief Digital Officer','Chief Service Delivery Officer','Chief Technology Officer','Program Manager','Project Manager','Sr. Project Manager','VP-Project Management')"
            elif role == 'Business Analyst':
                query = "select id from hr_job where name IN ('Business Analyst (Projects)', 'Associate Business Analyst', 'Business Analyst','Lead Business Analyst','Sr. Business Analyst')"
            where_clause = f"{skill_query} AND sar.primary_skill = {skill} AND des.id in ({query})"
        else:
            where_clause = skill_query

        query = f"""
            SELECT *
                FROM (
                    SELECT
                        COUNT(*) AS record_count,
                        CASE 
                            WHEN des.name IN ('Data Engineer', 'Programmer', 'Programmer Analyst','Research Analyst','Software Engineer','Sr. Data Analyst','Sr. Data Engineer','Sr. Database Analyst','Sr. Programmer Analyst','Sr. Software Engineer') THEN 'Coder/Programmer'
                            WHEN des.name IN ('Data Scientist', 'Module Lead', 'Project Leader','Sr. Project leader','Sr. Tech Lead','Tech Lead','Technical Architect') THEN 'Leader/Manager'
                            WHEN des.name IN ('Associate Project Manager', 'Associate VP (Projects)', 'Chief Digital Officer','Chief Service Delivery Officer','Chief Technology Officer','Program Manager','Project Manager','Sr. Project Manager','VP-Project Management') THEN 'Project Manager'
                            WHEN des.name IN ('Business Analyst (Projects)', 'Associate Business Analyst', 'Business Analyst','Lead Business Analyst','Sr. Business Analyst') THEN 'Business Analyst'
                        END AS role,
                        skl.name AS skill
                    FROM
                        skill_dashboard_analytics_report sar
                    LEFT JOIN
                        hr_job des ON des.id = sar.designation
                    JOIN
                        kw_skill_master skl ON skl.id = sar.primary_skill
                    WHERE  {where_clause}
                    GROUP BY role, skill
                ) AS subquery
                WHERE role IS NOT NULL 
                ORDER BY record_count DESC, skill, role
                limit 10
            """

        cr.execute(query)
        result = cr.fetchall()

        for row in result:
            record_count = row[0]
            skill = row[1]
            role = row[2]
            skill_wise_role.append({
                'name': skill,
                'category': role,
                'data': record_count
            })
        return skill_wise_role

    @api.model
    def sbu_wise_skill_count(self, **kwargs):
        sbu = kwargs.get('sbu', False)
        skill = kwargs.get('skill', False)
        sbu_wise_skill = []
        cr = self._cr
        skill_query = "sar.primary_skill is not null"
        where_clause = (
            f'{skill_query} and sar.primary_skill = {skill} and sbu.id = {sbu}') if kwargs and sbu != False and skill != False else "sar.primary_skill in (SELECT ID FROM kw_skill_master WHERE name IN ('.Net','.Net MVC','JAVA','PHP','Angular JS','ETL','GIS','Chatbot','DevOps','Cloud'))"

        query = f"""select  
                        count(*),
                        skl.name as skill,
			            sbu.name as sbu
                        from skill_dashboard_analytics_report sar
                        left join kw_sbu_master sbu on sbu.id=sar.sbu_master_id
                        join kw_skill_master skl on skl.id=sar.primary_skill
                        where {where_clause} and sbu.type='sbu' and sar.sbu_master_id is not null
                        group by skl.name,sbu.name  """

        cr.execute(query)
        result = cr.fetchall()

        for row in result:
            skill_count = row[0]
            skill = row[1]
            sbu = row[2]
            sbu_wise_skill.append({
                'name': skill,
                'category': sbu,
                'data': skill_count
            })
        return sbu_wise_skill

    @api.model
    def get_emtech_skill_count(self, **kwargs):
        emtech_skill = kwargs.get('emtech_skill_id', False)
        skill_data_em_tech = []
        cr = self._cr

        where_clause = f"sar.primary_skill IS NOT NULL"
        if kwargs and emtech_skill:
            where_clause += f" AND sar.primary_skill = {emtech_skill}"

        query = f"""SELECT 
                        skl.name,
                        COUNT(CASE WHEN sar.sbu_type = 'sbu'  THEN sar.emp_id END) AS sbu_count,
                        COUNT(CASE WHEN sar.sbu_type = 'horizontal'  THEN sar.emp_id END) AS horizontal_count 
                    FROM 
                        skill_dashboard_analytics_report sar 
                    LEFT JOIN 
                        kw_sbu_master sm ON sm.id = sar.sbu_master_id 
                    LEFT JOIN 
                        kw_skill_master skl ON skl.id = sar.primary_skill 
                    WHERE 
                        {where_clause} 
                        AND sar.sbu_master_id IS NOT NULL 
                        AND sar.primary_skill in (select id from kw_skill_master where name in ('AI/ML','Chatbot','Data Science','ETL','GIS','Hyper Ledger Fabric','IOT','Oracle BI','Power BI','SAS','SAS D1','SAS DI','SAS VA','Superset','Tableau','Cloud')) 
                    GROUP BY 
                        skl.name"""

        cr.execute(query)
        data = cr.fetchall()

        for row in data:
            skill = row[0]
            sbu_count = row[1]
            horizontal_count = row[2]
            skill_data_em_tech.append({
                'name': skill,
                'sbu_count': sbu_count,
                'horizontal_count': horizontal_count
            })

        return skill_data_em_tech

    @api.model
    def get_certification_skill_count(self, **kwargs):
        certification_course = kwargs.get('certification_id', False)
        certification_data = {}
        cr = self._cr
        where_clause = (
            f"certification_id is not null and certification_id = {int(certification_course)}"
        ) if kwargs and certification_course is not False else (
            "certification_id in (SELECT ID FROM kwmaster_stream_name WHERE name IN ('PMP','Prince 2','CBAP','ISTQB','Kubernets','Azure','Oracle','MCTS/MCP','DBA','CCNA','Secuirty','TOGAF'))"
        )
        query = f"""SELECT cn.name, COUNT(*) AS certification_count
                        FROM (
                            SELECT certification_course_1 AS certification_id FROM skill_dashboard_analytics_report WHERE certification_course_1 IS NOT NULL
                            UNION ALL
                            SELECT certification_course_2 AS certification_id FROM skill_dashboard_analytics_report WHERE certification_course_2 IS NOT NULL
                            UNION ALL
                            SELECT certification_course_3 AS certification_id FROM skill_dashboard_analytics_report WHERE certification_course_3 IS NOT NULL
                            UNION ALL
                            SELECT certification_course_4 AS certification_id FROM skill_dashboard_analytics_report WHERE certification_course_4 IS NOT NULL
                            UNION ALL
                            SELECT certification_course_5 AS certification_id FROM skill_dashboard_analytics_report WHERE certification_course_5 IS NOT NULL
                        ) AS certification_subquery
                        LEFT JOIN kwmaster_stream_name cn ON cn.id = certification_subquery.certification_id
                        where ({where_clause})
                        GROUP BY cn.name"""

        cr.execute(query)

        data = cr.fetchall()
        for row in data:
            certification = row[0]
            value = row[1]
            if certification in certification_data:
                certification_data[certification] += value
            else:
                certification_data[certification] = value

        formatted_certification_data = [[certification, value] for certification, value in certification_data.items()]
        return [formatted_certification_data]

    @api.model
    def get_database_skill_count(self, **kwargs):

        designation = kwargs.get('designation', False)
        db_skill = kwargs.get('db_skill', False)

        skill_db_wise = []

        cr = self._cr
        skill_query = "sar.primary_skill is not null"

        where_clause = (
            f'{skill_query} and sar.primary_skill = {db_skill} and kcn.id = {designation}') if kwargs and designation != False and db_skill != False else f'{skill_query}'

        query = f"select count(*),skl.name as skill,kcn.name as designation from skill_dashboard_analytics_report sar left join hr_job kcn on kcn.id=sar.designation \
                            join kw_skill_master skl on skl.id=sar.primary_skill and sar.primary_skill is not null where {where_clause} and sar.primary_skill in (select id from kw_skill_master where name ilike '%sql%') group by skl.name,kcn.name"

        cr.execute(query)
        result = cr.fetchall()

        for row in result:
            skill_count = row[0]
            skill = row[2]
            designation = row[1]
            skill_db_wise.append({
                'name': skill,
                'category': designation,
                'data': skill_count
            })
        return skill_db_wise

    @api.model
    def get_ext_it_skill_count(self, **kwargs):
        ex_skill = kwargs.get('ex_it_skill_id', False)
        external_it_data = {}
        cr = self._cr
        where_clause = (
            f'sar.primary_skill is not null and sar.primary_skill = {ex_skill}') if kwargs and ex_skill != False else 'sar.primary_skill is not null'
        query = f"select skl.name,count(*) from skill_dashboard_analytics_report sar left join kw_sbu_master sm on sm.id= sar.sbu_master_id left join kw_skill_master skl on skl.id=sar.primary_skill where {where_clause} and sar.sbu_master_id is not null and sar.sbu_master_id = (select id from kw_sbu_master where name ='External-IT') and sar.primary_skill is not null group by skl.name"

        cr.execute(query)
        data = cr.fetchall()
        for row in data:
            ext_it_skill = row[0]
            value = row[1]
            if ext_it_skill in external_it_data:
                external_it_data[ext_it_skill] += value
            else:
                external_it_data[ext_it_skill] = value

        formatted_external_it_data = [[ext_it_skill, value] for ext_it_skill, value in external_it_data.items()]
        return [formatted_external_it_data]

    @api.model
    def get_dashboard_filter_data_sql(self):
        ### Primary Skill Filter Query Start ###
        primary_skill_dict, emtech_skill_dict, certification_dict, db_dict, ex_it_dict, loc_skill_dict, skill_type_dict, skill_role_dict, sbu_skill_dict, pst_skill_type_dict, designation_dict = [], [], [], [], [], [], [], [], [], [], []
        cr = self._cr
        primary_skill_query = """
                SELECT DISTINCT(primary_skill) AS id, mst.name
                FROM skill_dashboard_analytics_report sr
                LEFT JOIN kw_skill_master mst ON mst.id = sr.primary_skill
                WHERE sr.primary_skill IS NOT NULL
                ORDER BY mst.name ASC """
        cr.execute(primary_skill_query)
        primary_skill_data = cr.fetchall()

        for row in primary_skill_data:
            primary_skill_dict.append({'id': row[0], 'name': row[1]})
        ### Primary Skill Filter Query End ###

        ### EmTech Filter Query Start ###

        emtech_skill_query = """
                SELECT 
                    DISTINCT sr.primary_skill AS id, 
                    mst.name
                FROM 
                    skill_dashboard_analytics_report sr
                LEFT JOIN 
                    kw_skill_master mst ON mst.id = sr.primary_skill
                WHERE 
                    sr.primary_skill IS NOT NULL
                    AND sr.primary_skill in (select id from kw_skill_master where name in ('AI/ML','Chatbot','Cloud','Data Science','ETL','GIS','Hyper Ledger Fabric','IOT','Oracle BI','Power BI','SAS','SAS D1','SAS DI','SAS VA','Superset','Tableau'))
                ORDER BY 
                    mst.name ASC
            """
        self.env.cr.execute(emtech_skill_query)
        emtech_skill_data = self.env.cr.fetchall()

        for row in emtech_skill_data:
            emtech_skill_dict.append({'id': row[0], 'name': row[1]})
        ### EmTech Filter Query End ###

        ### certification Filter Query Start ###

        certification_skill_query = """SELECT id, name
                FROM (
                    SELECT DISTINCT
                        sr.certification_course_1 as id,
                        mst1.name
                    FROM
                        skill_dashboard_analytics_report sr
                    LEFT JOIN
                        kwmaster_stream_name mst1 ON mst1.id = sr.certification_course_1
                    WHERE
                        sr.certification_course_1 IS NOT NULL

                    UNION

                    SELECT DISTINCT
                        sr.certification_course_2 as id,
                        mst2.name
                    FROM
                        skill_dashboard_analytics_report sr
                    LEFT JOIN
                        kwmaster_stream_name mst2 ON mst2.id = sr.certification_course_2
                    WHERE
                        sr.certification_course_2 IS NOT NULL

                    UNION

                    SELECT DISTINCT
                        sr.certification_course_3 as id,
                        mst3.name
                    FROM
                        skill_dashboard_analytics_report sr
                    LEFT JOIN
                        kwmaster_stream_name mst3 ON mst3.id = sr.certification_course_3
                    WHERE
                        sr.certification_course_3 IS NOT NULL

                    UNION

                    SELECT DISTINCT
                        sr.certification_course_4 as id,
                        mst4.name
                    FROM
                        skill_dashboard_analytics_report sr
                    LEFT JOIN
                        kwmaster_stream_name mst4 ON mst4.id = sr.certification_course_4
                    WHERE
                        sr.certification_course_4 IS NOT NULL

                    UNION

                    SELECT DISTINCT
                        sr.certification_course_5 as id,
                        mst5.name
                    FROM
                        skill_dashboard_analytics_report sr
                    LEFT JOIN
                        kwmaster_stream_name mst5 ON mst5.id = sr.certification_course_5
                    WHERE
                        sr.certification_course_5 IS NOT NULL
                ) AS subquery
                ORDER BY name ASC  """
        self.env.cr.execute(certification_skill_query)
        certification_skill_data = self.env.cr.fetchall()

        for row in certification_skill_data:
            certification_dict.append({'id': row[0], 'name': row[1]})
        ### certification Filter Query End ###

        ### database bifurcation Filter Query Start ###

        db_skill_query = (
            f"SELECT distinct (skl.id) as skl_id, skl.name as skill FROM skill_dashboard_analytics_report sar LEFT JOIN kw_skill_master skl ON skl.id = sar.primary_skill WHERE sar.primary_skill IN (select id from kw_skill_master where name ilike '%sql%')order by skill asc")
        self.env.cr.execute(db_skill_query)
        db_skill_data = self.env.cr.fetchall()

        for row in db_skill_data:
            db_dict.append({'id': row[0], 'name': row[1]})
        # ### database bifurcation Filter Query End ###

        ### skill wise total ex-it Filter Query Start ###

        ex_it_query = """SELECT 
                        DISTINCT sr.primary_skill AS id, 
                        mst.name
                    FROM 
                        skill_dashboard_analytics_report sr
                    LEFT JOIN 
                        kw_skill_master mst ON mst.id = sr.primary_skill
                    WHERE 
                        sr.primary_skill IS NOT NULL
                        AND sr.sbu_master_id IN (SELECT id FROM kw_sbu_master WHERE name = 'External-IT')
                    ORDER BY 
                        mst.name ASC;
                    """
        self.env.cr.execute(ex_it_query)
        ex_it_data = self.env.cr.fetchall()

        for row in ex_it_data:
            ex_it_dict.append({'id': row[0], 'name': row[1]})
        # ###  skill wise total ex-it Filter Query End ###

        ### location wise skill Filter Query Start ###

        location_query = """SELECT 
                            DISTINCT krb.alias AS location,
                            krb.id AS location_id
                        FROM 
                            skill_dashboard_analytics_report sar
                        LEFT JOIN 
                            kw_res_branch krb ON krb.id = sar.emp_location
                        JOIN 
                            kw_skill_master ksm ON ksm.id = sar.primary_skill
                        WHERE 
                            sar.primary_skill IS NOT NULL
                        GROUP BY 
                            krb.id, krb.alias
                        ORDER BY 
                            location ASC;
                        """
        self.env.cr.execute(location_query)
        location_data = self.env.cr.fetchall()

        for row in location_data:
            loc_skill_dict.append({'id': row[1], 'name': row[0]})
        ### location wise skill Filter Query End ###

        ### skill type wise skill Filter Query Start ###

        skill_type_query = """SELECT
                    distinct(skill_type) AS name
                FROM (
                    SELECT
                        DISTINCT primary_skill AS skill_id,
                        ksm.name AS skill_name,
                        'Primary' AS skill_type
                    FROM
                        skill_dashboard_analytics_report sar
                    JOIN
                        kw_skill_master ksm ON ksm.id = sar.primary_skill

                    UNION ALL

                    SELECT
                        DISTINCT secondary_skill AS skill_id,
                        ksm.name AS skill_name,
                        'Secondary' AS skill_type
                    FROM
                        skill_dashboard_analytics_report sar
                    JOIN
                        kw_skill_master ksm ON ksm.id = sar.secondary_skill

                    UNION ALL

                    SELECT
                        DISTINCT tertiarry_skill AS skill_id,
                        ksm.name AS skill_name,
                        'Tertiary' AS skill_type
                    FROM
                        skill_dashboard_analytics_report sar
                    JOIN
                        kw_skill_master ksm ON ksm.id = sar.tertiarry_skill
                ) AS subquery 
                GROUP BY
                    skill_name, skill_type """
        self.env.cr.execute(skill_type_query)
        skill_type_data = self.env.cr.fetchall()

        for row in skill_type_data:
            skill_type_dict.append({'id': row[0], 'name': row[0]})
        ### skill type wise skill Filter Query End ###

        ### skill type wise skill Filter Query2 Start ###

        all_skill_query = """SELECT id as id, name as name from kw_skill_master where skill_type in (select id from kw_skill_type_master where skill_type in ('Technical')) order by name  asc;
                            """
        self.env.cr.execute(all_skill_query)
        skill_type_pst_data = self.env.cr.fetchall()

        for row in skill_type_pst_data:
            pst_skill_type_dict.append({'id': row[0], 'name': row[1]})

        ### skill type wise skill Filter Query2 End ###
        ### role wise skill Filter Query Start ###

        skill_role_query = """ select club_role as id,club_role as name from skill_dashboard_analytics_report where club_role IN ('Coder/Programmer', 'Leader/Manager', 'Project Manager', 'Business Analyst') group by club_role

                            ORDER BY name ASC
                        """

        cr.execute(skill_role_query)
        role_skill_data = cr.fetchall()
        for row in role_skill_data:
            skill_role_dict.append({'id': row[0], 'name': row[1]})
        ### role wise skill Filter Query End ###
        designation_query = """ SELECT distinct(designation) as id ,mst.name as name
                FROM skill_dashboard_analytics_report sr
                LEFT JOIN hr_job mst ON mst.id = sr.designation
                WHERE sr.designation IS NOT NULL ORDER BY name ASC
                        """

        cr.execute(designation_query)
        designation_data = cr.fetchall()
        for row in designation_data:
            designation_dict.append({'id': row[0], 'name': row[1]})
        ### SBU wise skill Filter Query Start ###

        sbu_skill_query = """SELECT distinct(sbu_master_id) as id ,sbu.name as name
                FROM skill_dashboard_analytics_report sr
                LEFT JOIN kw_sbu_master sbu ON sbu.id = sr.sbu_master_id
                WHERE sr.sbu_master_id IS NOT NULL and sbu.type='sbu' """
        cr.execute(sbu_skill_query)
        sbu_skill_data = cr.fetchall()
        for row in sbu_skill_data:
            sbu_skill_dict.append({'id': row[0], 'name': row[1]})
        ### SBU wise skill Filter Query End ###

        return [primary_skill_dict, emtech_skill_dict, certification_dict, db_dict, ex_it_dict, loc_skill_dict,
                skill_type_dict, skill_role_dict, sbu_skill_dict, pst_skill_type_dict, designation_dict]

    @api.model
    def get_filter_data(self):
        dashboard_filter_data = {
            'dashboard_filters': self.get_dashboard_filter_data_sql(),
        }
        return dashboard_filter_data
