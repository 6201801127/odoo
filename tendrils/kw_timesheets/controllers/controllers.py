# -*- coding: utf-8 -*-
import json

from odoo import http
from odoo.http import request
import re
from datetime import date, datetime, timedelta
from odoo.http import request, Response
import calendar


def get_week(current_date):
    week_day_format, week_day = [], []
    one_day = datetime.timedelta(days=1)
    # current_date = current_date
    day_idx = (current_date.weekday() + 1) % 7
    sunday = current_date - datetime.timedelta(days=day_idx)
    current_date = sunday
    for n in range(7):
        current_date += one_day
        week_day_format.append(current_date.strftime("%b %d"))
        week_day.append(current_date)
    return [week_day, week_day_format]


class MyTimesheet(http.Controller):

    @http.route('/weekly-timesheet', type='json', auth="user")
    def weekly_timesheet(self, **kwargs):
        # print(kwargs)
        project_ids, selected_period_id, selected_project_id, project_task_ids = [], [], [], []
        project_category_ids = request.env['kw_project_category_master'].sudo().search_read([], ['id', 'name'])

        current_date = datetime.date.today()
        current_week = get_week(current_date)

        weekly_timesheet_data = {
            'current_week': current_week,
            'project_category': project_category_ids,
            'project': project_ids,
            'selected_period_id': selected_period_id.id if selected_period_id else 0,
            'selected_project_id': selected_project_id.id if selected_project_id else 0,
            'project_task': project_task_ids if project_task_ids else [],

        }

        return weekly_timesheet_data

 

    @http.route('/timesheet/task_assign_panel', auth='user', type='json')
    def get_panel_data(self):
        total_count = request.env['kw_project_task_assign_report'].sudo().search([],limit=1)
        count_vertical= total_count.actual_vertical_resource_tagged
        count_horizontal= total_count.actual_horizontal_resource_tagged
        user = request.env.user
        if user.has_group("hr_timesheet.group_timesheet_manager") or user.has_group("kw_timesheets.group_kw_timesheets_report_manager"):
            vals = {'total_horizonatal': count_horizontal,
                'total_vertical': count_vertical}
        else:
            projects = request.env['project.project'].sudo().search(['|','|',('emp_id.user_id','=',user.id),('sbu_id.representative_id.user_id','=',user.id),('reviewer_id.user_id','=',user.id)]).mapped('id')
            resources = request.env['kw_project_resource_tagging'].sudo().search([('project_id','in',projects),('active','=',True)]).mapped('emp_id.id')
            sbu_resources= request.env['hr.employee'].sudo().search([('id','in',resources)])
            vertical = len(sbu_resources.filtered(lambda x : x.sbu_type == 'sbu'))
            horizontal = len(sbu_resources.filtered(lambda x : x.sbu_type == 'horizontal'))
            vals = {'total_horizonatal': horizontal,
                'total_vertical': vertical}
        
        
        return {
                'html':request.env.ref('kw_timesheets.task_assign_template').render({
                'object': request.env['kw_project_task_assign_report'],
                'values': vals
            })
            
        }

    @http.route('/savedata', type='http', auth="user", method="post", csrf=False)
    def savedata(self, **kwargs):
        project_list = []
        final_project_list = []
        temp_proj_seq = []
        digit = lambda x: re.search(r'\d+', x).group(0)
        for key, value in kwargs.items():
            temp_seq = digit(key)
            if temp_seq not in temp_proj_seq:
                temp_proj_seq.append(temp_seq)
                temp_data = {
                    'prject_category_id': int(kwargs['category_select_' + temp_seq]),
                    'project_id': int(kwargs['project_select_' + temp_seq]),
                    'task_id': int(kwargs['project_task_select_' + temp_seq]),
                    'employee_id': 1,
                    'date': [kwargs['monday_' + temp_seq], kwargs['tuesday_' + temp_seq],
                             kwargs['wednesday_' + temp_seq], kwargs['thursday_' + temp_seq],
                             kwargs['friday_' + temp_seq], kwargs['saturday_' + temp_seq],
                             kwargs['sunday_' + temp_seq]],
                    'unit_amount': [kwargs['mon_' + temp_seq], kwargs['tue_' + temp_seq], kwargs['wed_' + temp_seq],
                                    kwargs['thu_' + temp_seq], kwargs['fri_' + temp_seq], kwargs['sat_' + temp_seq],
                                    kwargs['sun_' + temp_seq]],

                }
                # if temp_data not in project_list:
                project_list.append(temp_data)

        for project in project_list:
            res = {project['date'][i]: project['unit_amount'][i] for i in range(len(project['date']))}
            final_data = {
                'prject_category_id': project['prject_category_id'],
                'project_id': project['project_id'],
                'task_id': project['task_id'],
                'employee_id': 1,
                'date': res

            }
            final_project_list.append(final_data)

        # print(final_project_list)
        for proj in final_project_list:
            for key, value in proj['date'].items():
                rec = request.env['account.analytic.line'].sudo().search(
                    [('employee_id', '=', proj['employee_id']), ('date', '=', key),
                     ('prject_category_id', '=', proj['prject_category_id']), ('project_id', '=', proj['project_id']),
                     ('task_id', '=', proj['task_id'])])
                # print(rec, 'record found in the db')
                if rec:
                    rec.sudo().write({'unit_amount': value})
                else:
                    request.env['account.analytic.line'].sudo().create(
                        {'employee_id': proj['employee_id'], 'prject_category_id': proj['prject_category_id'],
                         'project_id': proj['project_id'], 'task_id': proj['task_id'], 'date': key,
                         'unit_amount': value})

    # @http.route('/employee-timesheet-summary/', auth='public', method="post", website=True, csrf=False)
    # def timesheet_summary_form(self, **kw):
    #     timesheet_form_data = {}
    #     year = datetime.today().year
    #     month = datetime.today().month
    #     day = datetime.today().day
    #     monthDict = {'1': '01', '2': '02', '3': '03', '4': '04',
    #                  '5': '05', '6': '06', '7': '07', '8': '08',
    #                  '9': '09', '10': '10', '11': '11', '12': '12'}

    #     if day >= 26:
    #         if http.request.session.uid is None:
    #             return http.request.redirect('/web')
    #         employee_id = request.env['hr.employee'].sudo().search([('user_id', '=', http.request.session.uid)])
    #         check_record = request.env['kw_timesheet_payroll_report'].sudo().search(
    #             [('employee_id', '=', employee_id.id), ('attendance_year', '=', year),
    #              ('attendance_month', '=', monthDict.get(str(month)))])
    #         if check_record:
    #             if check_record.timesheet_el_days > 0 or check_record.timesheet_paycut_days > 0:
    #                 timesheet_form_data['empname'] = check_record.employee_id.name
    #                 timesheet_form_data['attendancemonth'] = check_record.attendance_month
    #                 timesheet_form_data['attendanceyear'] = check_record.attendance_year
    #                 if str(check_record.required_effort_hour).split('.')[1] == '0':
    #                     trim_required_effort_hour = str(check_record.required_effort_hour).split('.')[0]
    #                 else:
    #                     trim_required_effort_hour = str(check_record.required_effort_hour)
    #                 timesheet_form_data['requiredefforthour'] = trim_required_effort_hour
    #                 if str(check_record.num_actual_effort).split('.')[1] == '0':
    #                     trim_num_actual_effort = str(check_record.num_actual_effort).split('.')[0]
    #                 else:
    #                     trim_num_actual_effort = str(check_record.num_actual_effort)
    #                 timesheet_form_data['numactualeffort'] = trim_num_actual_effort
    #                 if str(check_record.total_effort).split('.')[1] == '0':
    #                     trim_total_effort_hr = (str(check_record.total_effort).split('.')[0])
    #                 else:
    #                     trim_total_effort_hr = str(check_record.total_effort)
    #                 timesheet_form_data['totaleffort'] = abs(int(trim_total_effort_hr))
    #                 if str(check_record.timesheet_el_days).split('.')[1] == '0':
    #                     trim_timesheet_el_days = str(check_record.timesheet_el_days).split('.')[0]
    #                 else:
    #                     trim_timesheet_el_days = str(check_record.timesheet_el_days)
    #                 timesheet_form_data['timesheeteldays'] = trim_timesheet_el_days
    #                 if str(check_record.timesheet_paycut_days).split('.')[1] == '0':
    #                     trim_timesheet_paycut_days = str(check_record.timesheet_paycut_days).split('.')[0]
    #                 else:
    #                     trim_timesheet_paycut_days = str(check_record.timesheet_paycut_days)
    #                 timesheet_form_data['timesheetpaycutdays'] = trim_timesheet_paycut_days
    #                 print(timesheet_form_data)
    #                 return http.request.render("kw_timesheets.kw_timesheet_summary_form",
    #                                            {'timesheet_form_data': timesheet_form_data})
    #         else:
    #             return http.request.redirect('/web')
        # request.env['account.analytic.line'].sudo().create(project_list)
        

    @http.route("/resource-activity-time", type="json", cors='*', auth="none", methods=["POST"], csrf=False)
    def resource_activity(self, **post_data):
        # Get the project_id from the request body
        project_kw_id = post_data.get('project_kw_id')
        start_month = post_data.get('start_month')
        start_year = post_data.get('start_year')
        end_month = post_data.get('end_month')
        end_year = post_data.get('end_year')


        try:
            if not project_kw_id and start_month and start_year and end_month and end_year:
                return Response(
                    json.dumps({"error": "All the params are required in the request body"}),
                    status=400,
                    headers={'Content-Type': 'application/json'}
                ) 

            query = """ SELECT 
                    SUM(a.unit_amount) AS total_effort_hours,
                    a.project_id AS project_id,
                    pp.kw_id AS project_kw_id,
                    (SELECT kw_id FROM project_task WHERE id = p.parent_id) AS activity_kw_id,
                    (SELECT kw_id FROM hr_employee WHERE id = a.employee_id) AS employee_kw_id,
                    DATE(a.date) AS entry_date,
                    CAST(EXTRACT(MONTH FROM a.date) AS INTEGER) AS entry_month,
                    CAST(EXTRACT(YEAR FROM a.date) AS INTEGER) AS entry_year
                FROM account_analytic_line a 
                JOIN project_task p
                LEFT JOIN project_project pp ON pp.id = p.project_id 
                ON a.task_id = p.id 
                WHERE pp.kw_id = %s
                AND (
                    (DATE(a.date) >= DATE(%s || '-' || %s || '-01') AND DATE(a.date) <= DATE(%s || '-' || %s || '-01'))
                )
                GROUP BY a.project_id, p.parent_id, a.employee_id, project_kw_id, entry_date, entry_month, entry_year
            """

            request.env.cr.execute(query, (project_kw_id, start_year, start_month, end_year, end_month))
            query_results = request.env.cr.fetchall()
            response_data = []
            for row in query_results:
                total_effort_hours, project_id, project_kw_id, activity_kw_id, employee_kw_id,entry_date,entry_month,entry_year = row
                response_data.append({
                    "total_effort_hours": total_effort_hours,
                    "project_id": project_id,
                    "project_kw_id": project_kw_id,
                    "activity_kw_id": activity_kw_id,
                    "employee_kw_id": employee_kw_id,
                    "entry_date": entry_date,
                    "entry_month": entry_month,
                    "entry_year": entry_year
                })

            return response_data
        except Exception as e:
            return Response(
                json.dumps({"error": str(e)}),
                status=500,
                headers={'Content-Type': 'application/json'}
            )

    @http.route("/total-activity-effort", type="json", cors='*', auth="none", methods=["POST"], csrf=False)
    def total_activity_time(self, **post_data):
        project_kw_id = post_data.get('project_kw_id')

        try:
            if not project_kw_id:
                return Response(
                    json.dumps({"error": "project_kw_id is required in the request body"}),
                    status=400,
                    headers={'Content-Type': 'application/json'}
                )

            query = """ 
                SELECT 
                    COUNT(p.id) AS total_tasks,
                    CAST(SUM(a.unit_amount) AS NUMERIC(10, 2)) AS total_effort_hours,
                    MIN(DATE(a.date)) AS start_date,
                    MAX(DATE(a.date)) AS end_date,
                    (SELECT kw_id FROM project_task WHERE id = p.parent_id) AS activity_kw_id
                FROM account_analytic_line a 
                JOIN project_task p
                LEFT JOIN project_project pp ON pp.id = p.project_id 
                ON a.task_id = p.id 
                WHERE pp.kw_id = %s
                GROUP BY p.parent_id
            """

            request.env.cr.execute(query, (project_kw_id,))
            query_results = request.env.cr.fetchall()
            response_data = []
            for row in query_results:
                total_tasks, total_effort_hours, start_date, end_date, activity_kw_id = row
                response_data.append({
                    "total_tasks": total_tasks,
                    "total_effort_hours": total_effort_hours,
                    "start_date": start_date,
                    "end_date": end_date,
                    "activity_kw_id": activity_kw_id if activity_kw_id else 0,
                    "project_kw_id": project_kw_id,
                })

            return response_data
        except Exception as e:
            return Response(
                json.dumps({"error": str(e)}),
                status=500,
                headers={'Content-Type': 'application/json'}
            )
        
    @http.route("/project-task-assign-details", type="json", cors='*', auth="none", methods=["POST"], csrf=False)
    def project_details(self, **post_data):
        # Get the project_kw_id from the request body
        # project_kw_id = post_data.get('project_kw_id')

        try:
            query = """
                SELECT 
                    ROW_NUMBER() OVER (ORDER BY p.id) AS id,
                    (SELECT name FROM kw_sbu_master WHERE id = p.sbu_id) AS sbu_name,
                    (SELECT name FROM hr_employee WHERE id = p.emp_id) AS project_manager,
                    (SELECT code FROM crm_lead WHERE id = p.crm_id) AS project_code,
                    name AS project_name,
                    p.kw_id AS project_id,
                    (SELECT COUNT(*) FROM kw_project_resource_tagging rt JOIN hr_employee e ON e.id = rt.emp_id 
                    JOIN hr_department hrd ON hrd.id = e.department_id
                    WHERE rt.project_id = p.id 
                    AND rt.active = true 
                    AND e.sbu_type = 'sbu'
                    AND hrd.code = 'BSS'
                    AND e.sbu_master_id is not null
                    AND e.employement_type not in (SELECT id FROM kwemp_employment_type where code = 'O')
                    AND e.emp_category IN (SELECT id FROM kwmaster_category_name WHERE code = 'DEV')) AS vertical_resource_tagged,
                    (SELECT COUNT(DISTINCT emp_id) FROM kw_project_resource_tagging rt JOIN hr_employee e ON e.id = rt.emp_id WHERE rt.active = true AND e.sbu_type = 'sbu') AS actual_vertical_resource_tagged,
                    (SELECT COUNT(DISTINCT assigned_employee_id) FROM project_task WHERE assigned_employee_id IN (SELECT rt.emp_id FROM kw_project_resource_tagging rt JOIN hr_employee e ON e.id = rt.emp_id WHERE rt.project_id = p.id AND rt.active = true AND e.sbu_type = 'sbu')) AS horizontal_resource_tagged,
                    (SELECT COUNT(DISTINCT emp_id) FROM kw_project_resource_tagging rt JOIN hr_employee e ON e.id = rt.emp_id WHERE rt.active = true AND e.sbu_type = 'horizontal') AS actual_horizontal_resource_tagged,
                    (SELECT COUNT(DISTINCT assigned_employee_id) FROM project_task WHERE assigned_employee_id IN (SELECT rt.emp_id FROM kw_project_resource_tagging rt JOIN hr_employee e ON e.id = rt.emp_id WHERE rt.project_id = p.id AND rt.active = true AND e.sbu_type = 'horizontal')) AS horizontal_resource_tagged
                FROM
                    project_project p
                WHERE
                    active = true;
                                """

            request.env.cr.execute(query)
            query_results = request.env.cr.fetchall()

            results_list = []
            for row in query_results:
                result_dict = {
                    "id": row[0],
                    "sbu_name": row[1],
                    "project_manager": row[2],
                    "project_code": row[3],
                    "project_name": row[4],
                    "project_id": row[5],
                    "vertical_resource_tagged": row[6],
                    # "actual_vertical_resource_tagged": row[7],
                    "horizontal_resource_tagged": row[8],
                    # "actual_horizontal_resource_tagged": row[9],
                    "horizontal_resource_tagged_task_assigned": row[10]
                }
                results_list.append(result_dict)

            return results_list

        except Exception as e:
            return Response(
                json.dumps({"error": str(e)}),
                status=500,
                headers={'Content-Type': 'application/json'}
            )
 
   


    @http.route('/get_sbu_tour_expense_details', auth='public', methods=['POST'], type='json', csrf=False, cors='*')
    def get_sbu_tour_expense_data(self, **kwargs):
        request.env.cr.execute(f''' 
                SELECT 
        row_number() OVER () AS id,
        (SELECT name FROM kw_sbu_master WHERE id = hr.sbu_master_id AND type = 'sbu') AS sbu_name,
        COUNT(hr.name) AS no_of_employee,
        hr.sbu_master_id as sbu_id,
        SUM(ts.total_budget_expense) AS total_expense,
        date_part('year',ts.applied_date)::VARCHAR as year,
        date_part('month',ts.applied_date)::VARCHAR as month_name
        FROM
            hr_employee AS hr
        JOIN
            kw_tour_settlement AS ts ON hr.id = ts.employee_id
        WHERE
            ts.state in ('Granted','Payment Done') AND hr.sbu_type = 'sbu' and hr.active=True
        GROUP BY
            sbu_name, year, month_name,sbu_id order by month_name
                ''')
        sbu_tour_data = request.env.cr.dictfetchall()
        return sbu_tour_data    
     
    @http.route('/get_sbu_resource_cost_details', auth='public', methods=['POST'], type='json', csrf=False, cors='*')
    def get_sbu_resource_cost_data(self, **kwargs):
        request.env.cr.execute(f''' 
                SELECT
                row_number() OVER () as id,
                date_part('year',a.date_to)::VARCHAR as year,
                date_part('month',a.date_to)::VARCHAR as month_name,
                hr.employement_type as emp_type,
                hr.sbu_master_id as sbu_id,
                (select name from kw_sbu_master where id = hr.sbu_master_id and type = 'sbu') as sbu_name,
                sum(b.amount) as ctc
                from hr_employee hr
                join hr_payslip a on a.employee_id=hr.id
                left join hr_payslip_line b 
                on a.id = b.slip_id  
                where b.code = 'CTC' 
                and a.state='done'
                and hr.active = true
                and hr.sbu_master_id in (select id from kw_sbu_master where type = 'sbu')
                and hr.employement_type not in (SELECT id FROM kwemp_employment_type where code in ('O','CE' ))
		        and hr.emp_role not in (SELECT id FROM kwmaster_role_name where code='O')
                group by
                a.date_to,
                hr.employement_type,sbu_name,hr.sbu_master_id
                ''')
        sbu_resource_cost = request.env.cr.dictfetchall()
        return sbu_resource_cost   

    @http.route('/get_horizontal_timesheet_ctc_details', auth='public', methods=['POST'], type='json', csrf=False, cors='*')
    def get_horizontal_timesheet_ctc_data(self, **kwargs):
        request.env.cr.execute(f''' 
                with a as (
                select sum(a.unit_amount) as timesheet_effort,a.employee_id as employee_id,h.employement_type,b.sbu_id as sbu_name,h.date_to,count(l.amount),
                (l.amount/(select num_shift_working_days 
                                        from kw_employee_monthly_payroll_info where attendance_year = date_part('year',h.date_to)and
                                        attendance_month = date_part('month',h.date_to) and employee_id = a.employee_id))*sum(a.unit_amount)/8.5 as average_ctc
                        from account_analytic_line a join project_project b on a.project_id = b.id  
                        join hr_payslip h on a.employee_id = h.employee_id join hr_payslip_line l on h.id = l.slip_id
                        join hr_employee e on e.id = h.employee_id
                        where h.state = 'done' and l.code = 'CTC' and a.date between h.date_from and h.date_to and a.prject_category_id = (select id from kw_project_category_master where mapped_to = 'Project')
                        and e.sbu_type = 'horizontal'
                        group by a.employee_id,b.sbu_id,h.employement_type,h.date_to, l.amount order by h.date_to)
            select  row_number() OVER () AS id,
            date_part('year',date_to)::VARCHAR as year,date_part('month',date_to)::VARCHAR as month_name,sbu_name,employement_type,sum(average_ctc) as average_ctc 
            from a group by sbu_name,employement_type,date_to
                ''')
        horizontal_timesheet_ctc = request.env.cr.dictfetchall()
        return horizontal_timesheet_ctc   

    @http.route('/get_sbu_wise_cost_details', auth='public', methods=['POST'], type='json', csrf=False, cors='*')
    def get_sbu_wise_cost_details(self, **kwargs):
        request.env.cr.execute(f''' 
        with b as (		
	    with a as (				
            select sum(a.unit_amount) FILTER (WHERE a.prject_category_id in (select  id from kw_project_category_master where mapped_to in ('Support','Project')))  AS timesheet_effort,
                coalesce(sum(a.unit_amount) FILTER (WHERE a.prject_category_id in (select  id from kw_project_category_master where mapped_to = 'Support')),0) as adminstrative_work,
                coalesce(sum(a.unit_amount) FILTER (WHERE a.prject_category_id = (select  id from kw_project_category_master where mapped_to = 'Project') 
                                        and a.project_id in (select p.id from project_project p join kw_sbu_master s on p.sbu_id = s.id where s.name = 'SBU 1' )),0) as sbu_1,
                coalesce(sum(a.unit_amount) FILTER (WHERE a.prject_category_id = (select  id from kw_project_category_master where mapped_to = 'Project') 
                                        and a.project_id in (select p.id from project_project p join kw_sbu_master s on p.sbu_id = s.id where s.name = 'SBU 2' )),0) as sbu_2,
                coalesce(sum(a.unit_amount) FILTER (WHERE a.prject_category_id = (select  id from kw_project_category_master where mapped_to = 'Project') 
                                        and a.project_id in (select p.id from project_project p join kw_sbu_master s on p.sbu_id = s.id where s.name = 'SBU 3' )),0) as sbu_3,
                coalesce(sum(a.unit_amount) FILTER (WHERE a.prject_category_id = (select  id from kw_project_category_master where mapped_to = 'Project') 
                                        and a.project_id in (select p.id from project_project p join kw_sbu_master s on p.sbu_id = s.id where s.name = 'SBU 4' )),0) as sbu_4,
                coalesce(sum(a.unit_amount) FILTER (WHERE a.prject_category_id = (select  id from kw_project_category_master where mapped_to = 'Project') 
                                        and a.project_id in (select p.id from project_project p join kw_sbu_master s on p.sbu_id = s.id where s.name = 'SBU 5' )),0) as sbu_5,
                
                a.employee_id AS employee_id,h.date_to,l.amount as ctc from account_analytic_line a join hr_employee e on a.employee_id = e.id 
                join hr_payslip h on a.employee_id = h.employee_id join hr_payslip_line l on h.id = l.slip_id 
                where  e.department_id = (select id from hr_department where code = 'BSS')
                and e.sbu_type='sbu' and e.sbu_master_id is not null and  h.state = 'done' and l.code = 'CTC' and a.date between h.date_from and h.date_to
				and a.unit_amount > 1
                group by a.employee_id,e.sbu_master_id,h.date_to,l.amount order by h.date_to)
                select timesheet_effort,adminstrative_work,round((adminstrative_work/timesheet_effort)*100) as admin_percent,(round((adminstrative_work/timesheet_effort)*100)/100)*ctc as admin_amount,sbu_1,
                round((sbu_1/timesheet_effort)*100) as sbu1_percent,(round((sbu_1/timesheet_effort)*100)/100)*ctc as sbu1_amount,sbu_2,round((sbu_2/timesheet_effort)*100) as sbu2_percent,(round((sbu_2/timesheet_effort)*100)/100)*ctc as sbu2_amount,sbu_3,
                round((sbu_3/timesheet_effort)*100) as sbu3_percent,(round((sbu_3/timesheet_effort)*100)/100)*ctc as sbu3_amount,sbu_4,round((sbu_4/timesheet_effort)*100) as sbu4_percent,
                (round((sbu_4/timesheet_effort)*100)/100)*ctc as sbu4_amount,sbu_5,
                round((sbu_5/timesheet_effort)*100) as sbu5_percent,
                (round((sbu_5/timesheet_effort)*100)/100)*ctc as sbu5_amount,
	
	 			
				case 
				when a.sbu_1 > 0 then
                round((round((sbu_1/timesheet_effort)*100)/100)*ctc + 
                round((sbu_1/timesheet_effort)*100)/(round((sbu_1/timesheet_effort)*100)+round((sbu_2/timesheet_effort)*100)+ 
                round((sbu_3/timesheet_effort)*100)+round((sbu_4/timesheet_effort)*100)+round((sbu_5/timesheet_effort)*100)) *
					  (round((adminstrative_work/timesheet_effort)*100)/100)*ctc)
				when sbu_1+sbu_2+sbu_3+sbu_4+sbu_5 = 0 and (select id from kw_sbu_master where type = 'sbu' and name = 'SBU 1') = (select sbu_master_id from hr_employee where id = a.employee_id) then 
					round(((adminstrative_work/timesheet_effort)*100)/100)*ctc
				else 0 end as final_sbu1_amount,
	
                case 
				when a.sbu_2 > 0 then
                round((round((sbu_2/timesheet_effort)*100)/100)*ctc + 
                round((sbu_2/timesheet_effort)*100)/(round((sbu_1/timesheet_effort)*100)+round((sbu_2/timesheet_effort)*100)+ 
                round((sbu_3/timesheet_effort)*100)+round((sbu_4/timesheet_effort)*100)+round((sbu_5/timesheet_effort)*100)) * (round((adminstrative_work/timesheet_effort)*100)/100)*ctc) 
				when sbu_1+sbu_2+sbu_3+sbu_4+sbu_5 = 0 and (select id from kw_sbu_master where type = 'sbu' and name = 'SBU 2') = (select sbu_master_id from hr_employee where id = a.employee_id) then 
					round(((adminstrative_work/timesheet_effort)*100)/100)*ctc
				else 0 end as final_sbu2_amount,
                
                case 
				when a.sbu_3 > 0  then
                round((round((sbu_3/timesheet_effort)*100)/100)*ctc + 
                round((sbu_3/timesheet_effort)*100)/(round((sbu_1/timesheet_effort)*100)+round((sbu_2/timesheet_effort)*100)+ 
                round((sbu_3/timesheet_effort)*100)+round((sbu_4/timesheet_effort)*100)+round((sbu_5/timesheet_effort)*100)) * (round((adminstrative_work/timesheet_effort)*100)/100)*ctc)
				when sbu_1+sbu_2+sbu_3+sbu_4+sbu_5 = 0 and (select id from kw_sbu_master where type = 'sbu' and name = 'SBU 3') = (select sbu_master_id from hr_employee where id = a.employee_id) then 
					round(((adminstrative_work/timesheet_effort)*100)/100)*ctc
				else 0 end as final_sbu3_amount,
                
				case 
				when a.sbu_4 > 0 then
                round((round((sbu_4/timesheet_effort)*100)/100)*ctc + 
                round((sbu_4/timesheet_effort)*100)/(round((sbu_1/timesheet_effort)*100)+round((sbu_2/timesheet_effort)*100)+ 
                round((sbu_3/timesheet_effort)*100)+round((sbu_4/timesheet_effort)*100)+round((sbu_5/timesheet_effort)*100)) * (round((adminstrative_work/timesheet_effort)*100)/100)*ctc)
				when sbu_1+sbu_2+sbu_3+sbu_4+sbu_5 = 0 and (select id from kw_sbu_master where type = 'sbu' and name = 'SBU 4') = (select sbu_master_id from hr_employee where id = a.employee_id) then 
					round(((adminstrative_work/timesheet_effort)*100)/100)*ctc
				else 0 end as final_sbu4_amount,
                
				case 
				when a.sbu_5 > 0 then
                round((round((sbu_5/timesheet_effort)*100)/100)*ctc + 
                round((sbu_5/timesheet_effort)*100)/(round((sbu_1/timesheet_effort)*100)+round((sbu_2/timesheet_effort)*100)+ 
                round((sbu_3/timesheet_effort)*100)+round((sbu_4/timesheet_effort)*100)+round((sbu_5/timesheet_effort)*100)) * (round((adminstrative_work/timesheet_effort)*100)/100)*ctc)
				when sbu_1+sbu_2+sbu_3+sbu_4+sbu_5 = 0 and (select id from kw_sbu_master where type = 'sbu' and name = 'SBU 5') = (select sbu_master_id from hr_employee where id = a.employee_id) then 
					round(((adminstrative_work/timesheet_effort)*100)/100)*ctc
				else 0 end as final_sbu5_amount,
                employee_id,date_to,ctc from a )
                
            select  row_number() OVER () AS id,
            date_part('year',date_to)::VARCHAR as year,date_part('month',date_to)::VARCHAR as month_name,CONCAT('1~', sum(final_sbu1_amount)) AS sbu1_amount,CONCAT('2~', sum(final_sbu2_amount)) AS sbu2_amount,
            CONCAT('3~', sum(final_sbu3_amount)) AS sbu3_amount,CONCAT('4~', sum(final_sbu4_amount)) AS sbu4_amount,CONCAT('5~', sum(final_sbu5_amount)) AS sbu5_amount
            from b group by date_to
                ''')
        sbu_cost_details = request.env.cr.dictfetchall()
        return sbu_cost_details 
    


    
    @http.route('/EmployeeAssignTask',type="json", cors='*', auth="public", methods=["POST"], csrf=False)
    def get_employee_assigned_tasks(self, **post_data):
        data = []
        kw_project_id = post_data.get('kw_project_id')
        financial_year = post_data.get('financial_year')
        month = int(post_data.get('month'))
        start_year, end_year = map(int, financial_year.split('-'))
        start_date = date(start_year, month, 1) if month >= 4 else date(end_year, month, 1)
        end_date = date(start_date.year, start_date.month, calendar.monthrange(start_date.year, start_date.month)[1])
        employees = request.env['hr.employee'].sudo().search([])
        tasks = request.env['project.task'].sudo().search([('project_id.kw_id','=',kw_project_id),('create_date','>=',start_date),('create_date','<=',end_date),'|',('active','=',True),('active','=',False)])

        for task in tasks:
            created_employee = employees.filtered(lambda emp: emp.user_id.id == task.create_uid.id if task.create_uid else False)
            modified_employee = employees.filtered(lambda emp: emp.user_id.id == task.write_uid.id if task.write_uid else False)
            data.append({
                'TaskID': task.id if task.id else None,
                'ProjectID': task.project_id.kw_id if task.project_id.kw_id else None,
                'PhaseID': None,
                'ActivityID': task.parent_id.kw_id if task.parent_id.kw_id else task.kw_id,
                'AssignTo': task.assigned_employee_id.kw_id if task.assigned_employee_id else None,
                'TaskTitle': task.name if task.name else None,
                'StartDate': task.planning_start_date.strftime('%Y-%m-%d %H:%M:%S') if task.planning_start_date else None,
                'EndDate': task.planning_end_date.strftime('%Y-%m-%d %H:%M:%S') if task.planning_end_date else None,
                'EffortHour': task.planned_hours if task.planned_hours else None,
                'Description': None, 
                'Status': None,
                'AssignTaskStatus': task.task_status if task.task_status else None,
                'AssignBy': created_employee.kw_id if created_employee else None,
                'AssignDate': task.create_date.strftime('%Y-%m-%d %H:%M:%S') if task.create_date else None,
                'UpdateBy': modified_employee.kw_id if modified_employee else None,
                'UpdateOn': task.write_date.strftime('%Y-%m-%d %H:%M:%S') if task.write_date else None,
                'DeletedFlag': 0 if task.active == True else 1,
                'ActivityEndDate': None,
            })

        if not data:
            data.append({'message': 'No data found for the given value in payload.'})
        return data
    


    @http.route('/EmployeeFillTask',type="json", cors='*', auth="public", methods=["POST"], csrf=False)
    def get_employee_fill_tasks(self, **post_data):
        data = []
        kw_project_id = post_data.get('kw_project_id')
        financial_year = post_data.get('financial_year')
        month = int(post_data.get('month'))
        start_year, end_year = map(int, financial_year.split('-'))
        start_date = date(start_year, month, 1) if month >= 4 else date(end_year, month, 1)
        end_date = date(start_date.year, start_date.month, calendar.monthrange(start_date.year, start_date.month)[1])
        employees = request.env['hr.employee'].sudo().search([])
        timesheets = request.env['account.analytic.line'].sudo().search([('project_id.kw_id','=',kw_project_id),('create_date','>=',start_date),('create_date','<=',end_date),'|',('active','=',True),('active','=',False)])

        for timesheet in timesheets:
            modified_employee = employees.filtered(lambda emp: emp.user_id.id == timesheet.write_uid.id if timesheet.write_uid else False)
            assign_by = employees.filtered(lambda emp: emp.user_id.id == timesheet.task_id.create_uid.id if timesheet.task_id.create_uid else False)     
            data.append({
                'FilledTimesheetID': timesheet.id,
                'TimesheetFillDate': timesheet.date,
                'StatusID': None,
                'TaskID': timesheet.task_id.id if timesheet.task_id.id else None,
                'ProjectID': timesheet.project_id.kw_id if timesheet.project_id.kw_id else None,
                'PhaseID': None,
                'ActivityID': timesheet.parent_task_id.kw_id if timesheet.parent_task_id.kw_id else timesheet.task_id.kw_id,
                'AssignTo': timesheet.employee_id.kw_id if timesheet.employee_id.kw_id else None,
                'TaskTitle': timesheet.task_id.name if timesheet.task_id.name else None,
                'StartDate': timesheet.task_id.planning_start_date.strftime('%Y-%m-%d %H:%M:%S') if timesheet.task_id.planning_start_date else None,
                'EndDate': timesheet.task_id.planning_end_date.strftime('%Y-%m-%d %H:%M:%S') if timesheet.task_id.planning_end_date else None,
                'Efforthour': timesheet.unit_amount if timesheet.unit_amount else None,
                'Description': timesheet.name if timesheet.name else None,
                'Status': None,
                'AssignTaskStatus': timesheet.task_status if timesheet.task_status else None,
                'AssignBy': assign_by.kw_id if assign_by else None,
                'AssignDate': timesheet.task_id.create_date.strftime('%Y-%m-%d %H:%M:%S') if timesheet.task_id.create_date else None,
                'UpdateBy': modified_employee.kw_id if modified_employee else None,
                'UpdateOn': timesheet.write_date.strftime('%Y-%m-%d %H:%M:%S') if timesheet.write_date else None,
                'DeletedFlag': 0 if timesheet.active == True else 1,
                'ActivityEndDate': None,
            })
         
        if not data:
            data.append({'message': 'No data found for the given value in payload.'})
        return data