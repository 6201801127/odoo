from odoo import models, fields, api, _
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
import datetime


class CrSRDashboard(models.Model):
    _name = 'cr_sr_dashboard'
    _description = 'cr_sr_dashboard'



    @api.model
    def uploaded_by_cr_sr_count(self, args):
        uploaded_data = []
        cr = self._cr
        year = args.get('current_year')
        month = args.get('current_month')

        current_fiscal_year = self.env['account.fiscalyear'].search([
            ('date_start', '<=', fields.Date.today()),
            ('date_stop', '>=', fields.Date.today())
        ], limit=1)
        
        is_current_fy = False
        if args and year and month:
            query = """
               WITH a AS (SELECT uploaded_by FROM cr_management_report WHERE state = 'Uploaded' AND project_id IS NOT NULL AND project_code IS NOT NULL GROUP BY uploaded_by),
                b AS (SELECT cmr.uploaded_by,COUNT(CASE WHEN cmr.cr_type = 'CR' THEN 1 END) AS cr_count,
                        COUNT(CASE WHEN cmr.cr_type = 'Service' THEN 1 END) AS sr_count
                    FROM cr_management_report cmr JOIN a ON a.uploaded_by = cmr.uploaded_by
                    WHERE cmr.state = 'Uploaded' AND cmr.project_id IS NOT NULL AND cmr.project_code IS NOT NULL AND EXTRACT(YEAR FROM cmr.cr_uploaded_on) = %s AND EXTRACT(MONTH FROM cmr.cr_uploaded_on) = %s
                    GROUP BY cmr.uploaded_by)
                SELECT (select name from hr_employee where id=a.uploaded_by) as uploaded_by,b.cr_count,b.sr_count FROM a JOIN b ON a.uploaded_by = b.uploaded_by
                order by b.cr_count asc , b.sr_count asc
                """
            cr.execute(query, (year, month))
            data = cr.fetchall()
            
        else:
            query = """
                WITH a AS (SELECT uploaded_by FROM cr_management_report WHERE state = 'Uploaded' AND project_id IS NOT NULL AND project_code IS NOT NULL GROUP BY uploaded_by),
                b AS (SELECT cmr.uploaded_by,COUNT(CASE WHEN cmr.cr_type = 'CR' THEN 1 END) AS cr_count,
                        COUNT(CASE WHEN cmr.cr_type = 'Service' THEN 1 END) AS sr_count
                    FROM cr_management_report cmr JOIN a ON a.uploaded_by = cmr.uploaded_by
                    JOIN account_fiscalyear fy ON CURRENT_DATE BETWEEN fy.date_start AND fy.date_stop
                    WHERE cmr.state = 'Uploaded' AND cmr.project_id IS NOT NULL AND cmr.project_code IS NOT NULL 
                    GROUP BY cmr.uploaded_by)
                SELECT (select name from hr_employee where id=a.uploaded_by) as uploaded_by,b.cr_count,b.sr_count FROM a JOIN b ON a.uploaded_by = b.uploaded_by
                ORDER BY b.cr_count ASC, b.sr_count ASC


                """
            cr.execute(query)
            data = cr.fetchall()
            is_current_fy = True
            
        # query = """
        #     SELECT 
        #         km.uploaded_by AS id,
        #         (SELECT name FROM hr_employee WHERE id = km.uploaded_by) AS uploaded_by,
        #         COUNT(CASE WHEN km.cr_type = 'CR' THEN km.id END) AS cr_count,
        #         COUNT(CASE WHEN km.cr_type = 'Service' THEN km.id END) AS service_count,
        #         km.cr_uploaded_on as cr_uploaded_on 
        #     FROM 
        #         kw_cr_management km
        #     WHERE 
        #         km.uploaded_by IS NOT NULL 
        #         AND EXTRACT(YEAR FROM km.cr_uploaded_on) = %s
        #         AND EXTRACT(MONTH FROM km.cr_uploaded_on) = %s
        #     GROUP BY 
        #         km.uploaded_by, km.cr_uploaded_on
        # """
        # cr.execute(query, (year, month))
        # data = cr.fetchall()

        for row in data:
            uploaded_by = row[0]
            cr_count = row[1]
            service_count = row[2]
            # cr_uploaded_on = row[4]
            uploaded_data.append({
                'uploaded_by': uploaded_by,
                'cr_count': cr_count,
                'service_count': service_count,
                'is_current_financial_year': is_current_fy
                # 'cr_uploaded_on': cr_uploaded_on
            })
        return uploaded_data



    @api.model
    def server_instance_cr_sr_count(self):
        server_instance_data = []
        cr = self._cr
        query = f"""
                    select 			
                        c.environment_id as id,
                        (select name from kw_environment_master where id=c.environment_id) AS environment_id,
                        COUNT(CASE WHEN c.cr_type = 'CR' THEN 1 END) AS cr_count,
                        COUNT(CASE WHEN c.cr_type = 'Service' THEN 1 END) AS service_count
                    FROM
 
                        kw_cr_management c
                    WHERE
                        c.stage = 'Uploaded'
                    GROUP BY
                        c.environment_id """

        cr.execute(query)
        data = cr.fetchall()

        for row in data:
            environment_id = row[1]
            cr_count = row[2]
            service_count = row[3]
            server_instance_data.append({
                'environment_id': environment_id,
                'cr_count': cr_count,
                'service_count': service_count
            })
        return server_instance_data

    @api.model
    def working_in_total_no_of_projects(self):
        working_projects_data = []
        cr = self._cr
        query = f"""
                     WITH a AS (
                SELECT  COUNT(project_id) AS project_count FROM kw_project_environment_management WHERE active = True), 
            b AS (SELECT per.hr_employee_id AS employee,STRING_AGG(DISTINCT project_project.name, ',') AS projects
                FROM kw_project_environment_management cmr JOIN hr_employee_kw_project_environment_management_rel per ON 
                per.kw_project_environment_management_id = cmr.id JOIN project_project ON cmr.project_id = project_project.id 
            WHERE cmr.active = True GROUP BY per.hr_employee_id)
            SELECT (SELECT name from hr_employee where id=per.hr_employee_id) AS uploaded_by,b.projects AS project_id,
                 ARRAY_LENGTH(STRING_TO_ARRAY(b.projects, ','), 1) AS project_count
            FROM hr_employee_kw_project_environment_management_rel per JOIN b ON per.hr_employee_id = b.employee
            CROSS JOIN a GROUP BY per.hr_employee_id, a.project_count,b.projects"""

        cr.execute(query)
        data = cr.fetchall()

        for row in data:
            uploaded_by = row[0]
            project_count = row[2]
            working_projects_data.append({
                'uploaded_by': uploaded_by,
                'project_count': project_count,
            })
        return working_projects_data

    @api.model
    def working_in_total_projects_by_serveradmin(self):
        working_serveradmin_data = []
        cr = self._cr
        query = f"""
                    WITH RankedData AS (
                            SELECT 
                                ROW_NUMBER() OVER () AS id,
                                (SELECT name FROM hr_employee WHERE id = hr_employee_id) AS uploaded_by,
                                SUM(CASE WHEN cr_management_report.cr_type = 'CR' THEN 1 ELSE 0 END) AS cr_count,
                                SUM(CASE WHEN cr_management_report.cr_type = 'Service' THEN 1 ELSE 0 END) AS service_count,
                                LAG((SELECT name FROM hr_employee WHERE id = hr_employee_id)) OVER (ORDER BY hr_employee_id) AS prev_uploaded_by
                            FROM 
                                hr_employee_kw_project_environment_management_rel 
                            JOIN 
                                kw_project_environment_management ON kw_project_environment_management.id = hr_employee_kw_project_environment_management_rel.kw_project_environment_management_id
                            JOIN 
                                cr_management_report ON cr_management_report.project_id = kw_project_environment_management.project_id
                            WHERE 
                                cr_management_report.state IN ('Uploaded')
                                AND hr_employee_id IS NOT NULL
                                AND cr_management_report.project_id IS NOT NULL
                                AND cr_management_report.project_code IS NOT NULL
                            GROUP BY
                                hr_employee_id
                        )
                        SELECT 
                            id,
                            CASE WHEN uploaded_by = prev_uploaded_by THEN NULL ELSE uploaded_by END AS uploaded_by,
                            cr_count,
                            service_count
                        FROM 
                            RankedData
                                    """

        cr.execute(query)
        data = cr.fetchall()

        for row in data:
            uploaded_by = row[1]
            cr_count = row[2]
            service_count = row[3]
            working_serveradmin_data.append({
                'uploaded_by': uploaded_by,
                # 'project_name': project_name,
                'cr_count': cr_count,
                'service_count' : service_count,
            })
        return working_serveradmin_data

    @api.model
    def top_project_cr_sr_count(self, args):

        project_data = []
        cr = self._cr
        year = args.get('current_year')
        month = args.get('current_month')
        if args and year and month :
            query = f"""SELECT  
                    ROW_NUMBER() OVER () AS id,
                    (SELECT name FROM project_project WHERE id = kcm.project_id) AS project_name,
                    SUM(CASE WHEN kcm.cr_type = 'CR' THEN 1 ELSE 0 END) AS cr_count,
                    SUM(CASE WHEN kcm.cr_type = 'Service' THEN 1 ELSE 0 END) AS sr_count,
                    MIN(kcm.cr_uploaded_on) AS cr_uploaded_on 
                FROM
                    kw_cr_management AS kcm
                WHERE
                    kcm.stage = 'Uploaded' AND EXTRACT(YEAR FROM cr_uploaded_on) = %s
                                    AND EXTRACT(MONTH FROM cr_uploaded_on) = %s
                GROUP BY kcm.project_id ORDER BY cr_count DESC, sr_count DESC LIMIT 15
                """

            cr.execute(query, (year, month))
            data = cr.fetchall()
        # elif args and year and not month:
        #     year = args.get('current_year')
        #     month = datetime.datetime.now().month
        # elif args and month and not year:
        #     year = datetime.datetime.now().year
        #     month = args.get('current_month')
        else:
            query = f"""SELECT  
                    ROW_NUMBER() OVER () AS id,
                    (SELECT name FROM project_project WHERE id = kcm.project_id) AS project_name,
                    SUM(CASE WHEN kcm.cr_type = 'CR' THEN 1 ELSE 0 END) AS cr_count,
                    SUM(CASE WHEN kcm.cr_type = 'Service' THEN 1 ELSE 0 END) AS sr_count,
                    MIN(kcm.cr_uploaded_on) AS cr_uploaded_on 
                FROM
                    kw_cr_management AS kcm
                WHERE
                    kcm.stage = 'Uploaded' 
                                   
                GROUP BY kcm.project_id ORDER BY cr_count DESC, sr_count DESC LIMIT 15
                """
            cr.execute(query)
            data = cr.fetchall()


        for row in data:
            project_name = row[1]
            cr_count = row[2]
            sr_count = row[3]
            cr_uploaded_on = row[4]
            project_data.append({
                'project_name': project_name,
                'cr_count': cr_count,
                'sr_count': sr_count,
                'cr_uploaded_on': cr_uploaded_on
            })
        return project_data

    @api.model
    def time_range_of_the_day_cr_sr_count(self):
        time_data = []
        cr = self._cr
        query = f"""
                    WITH time_periods AS (
                        SELECT 'Morning (5 AM-12 PM)' AS time_period
                        UNION ALL
                        SELECT 'Afternoon (12 PM-5 PM)'
                        UNION ALL
                        SELECT 'Evening (5 PM-9 PM)'
                        UNION ALL
                        SELECT 'Night (9PM-4 AM)'
                    )

                    SELECT   
                        ROW_NUMBER() OVER () AS id,
                        time_periods.time_period,
                        COALESCE(cr_counts.cr_count, 0) AS cr_count,
                        COALESCE(sr_counts.sr_count, 0) AS sr_count
                    FROM
                        time_periods
                    LEFT JOIN
                        (SELECT   
                            CASE
                                WHEN EXTRACT(HOUR FROM kcm.cr_uploaded_on AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata') BETWEEN 5 AND 11 THEN 'Morning (5 AM-12 PM)'
                                WHEN EXTRACT(HOUR FROM kcm.cr_uploaded_on AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata') BETWEEN 12 AND 16 THEN 'Afternoon (12 PM-5 PM)'
                                WHEN EXTRACT(HOUR FROM kcm.cr_uploaded_on AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata') BETWEEN 17 AND 20 THEN 'Evening (5 PM-9 PM)'
                                ELSE 'Night (9PM-4 AM)'
                            END AS time_period,
                            COUNT(CASE WHEN kcm.cr_type = 'CR' THEN 1 ELSE NULL END) AS cr_count
                        FROM
                            kw_cr_management AS kcm
                        WHERE
                            kcm.stage = 'Uploaded'
                        GROUP BY
                            time_period) AS cr_counts
                    ON
                        time_periods.time_period = cr_counts.time_period
                    LEFT JOIN
                        (SELECT   
                            CASE
                                WHEN EXTRACT(HOUR FROM kcm.cr_uploaded_on AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata') BETWEEN 5 AND 11 THEN 'Morning (5 AM-12 PM)'
                                WHEN EXTRACT(HOUR FROM kcm.cr_uploaded_on AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata') BETWEEN 12 AND 16 THEN 'Afternoon (12 PM-5 PM)'
                                WHEN EXTRACT(HOUR FROM kcm.cr_uploaded_on AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata') BETWEEN 17 AND 20 THEN 'Evening (5 PM-9 PM)'
                                ELSE 'Night (9PM-4 AM)'
                            END AS time_period,
                            COUNT(CASE WHEN kcm.cr_type = 'Service' THEN 1 ELSE NULL END) AS sr_count
                        FROM
                            kw_cr_management AS kcm
                        WHERE
                            kcm.stage = 'Uploaded'
                        GROUP BY
                            time_period) AS sr_counts
                    ON
                        time_periods.time_period = sr_counts.time_period
                    ORDER BY
                        id		"""

        cr.execute(query)
        data = cr.fetchall()

        for row in data:
            time_period = row[1]
            cr_count = row[2]
            sr_count = row[3]

            time_data.append({
                'time_period' : time_period,
                'cr_count': cr_count,
                'sr_count': sr_count,
            })
        return time_data

    @api.model
    def day_wise_staticstis_cr_sr_count(self,args):
        day_wise_data = []
        cr = self._cr
        year = args.get('current_year')
        month = args.get('current_month')
        
        if args and year and month:
            year = args.get('current_year')
            month = args.get('current_month')

            query = """WITH all_dates AS (
                        SELECT generate_series(
                            (SELECT MIN(DATE_TRUNC('day', cr_uploaded_on)) FROM kw_cr_management),
                            (SELECT MAX(DATE_TRUNC('day', cr_uploaded_on)) FROM kw_cr_management),
                            INTERVAL '1 day'
                        ) AS upload_date
                    )
                    SELECT  
                        ROW_NUMBER() OVER () AS id,
                        DATE(ad.upload_date) AS upload_date,
                        COUNT(CASE WHEN kcm.cr_type = 'CR' THEN 1 END) AS cr_count,
                        COUNT(CASE WHEN kcm.cr_type = 'Service' THEN 1 END) AS sr_count
                    FROM
                        all_dates ad
                    LEFT JOIN
                        kw_cr_management AS kcm ON DATE_TRUNC('day', kcm.cr_uploaded_on) = DATE_TRUNC('day', ad.upload_date) AND kcm.stage = 'Uploaded'
                    WHERE
                        EXTRACT(YEAR FROM ad.upload_date) = %s
                        AND EXTRACT(MONTH FROM ad.upload_date) = %s
                    GROUP BY
                        DATE(ad.upload_date)
                    ORDER BY
                        DATE(ad.upload_date)

                            """
                            

            cr.execute(query,(year,month))
            data = cr.fetchall()
        else:

            query = """WITH all_dates AS (
                            SELECT generate_series(
                                DATE_TRUNC('month', CURRENT_DATE),
                                DATE_TRUNC('month', CURRENT_DATE) + INTERVAL '1 month' - INTERVAL '1 day',
                                INTERVAL '1 day'
                            ) AS upload_date
                        )
                        SELECT  
                            ROW_NUMBER() OVER () AS id,
                            DATE(ad.upload_date) AS upload_date,
                            COUNT(kcm.cr_type = 'CR' OR NULL) AS cr_count,
                            COUNT(kcm.cr_type = 'Service' OR NULL) AS sr_count
                        FROM
                            all_dates ad
                        LEFT JOIN
                            kw_cr_management AS kcm ON DATE_TRUNC('day', kcm.cr_uploaded_on) = ad.upload_date AND kcm.stage = 'Uploaded'
                        GROUP BY
                            DATE(ad.upload_date)
                        ORDER BY
						
                            DATE(ad.upload_date)"""

            cr.execute(query)
            data = cr.fetchall()

        for row in data:
            upload_date = row[1]
            cr_count = row[2]
            sr_count = row[3]
            day_wise_data.append({
                'upload_date': upload_date,
                'cr_count': cr_count,
                'sr_count': sr_count
            })
        return day_wise_data