import werkzeug.utils
import werkzeug.wrappers
import werkzeug.wsgi
from odoo import http
from odoo.http import request, serialize_exception as _serialize_exception, Response


class FaceReaderIntegration(http.Controller):
    @http.route('/face_update_status', auth='public', methods=['POST'], type='json', csrf=False, cors='*')
    def def_face_update_status(self, **kw):
        bio_id = int(kw.get('Id'))
        employee = request.env['hr.employee'].sudo().search([('biometric_id', '=', bio_id)])
        # print('employee for capture status', employee)
        if employee:
            employee.capture_status = True
            return {'Status': 200, 'message': 'Employee status updated successfully!'}
        else:
            return {'Status': 400, 'message': 'Employee Not Found!'}

    @http.route('/employee_count', auth='public', methods=['POST'], type='json', csrf=False, cors='*')
    def get_employee_count(self, **kwargs):
        request.env.cr.execute(f""" select count(*) as total_count,(select count(*) from meal_bio_log 
        where meal_type_id = (select id from price_master_configuration where meal_code = 'R') 
        and recorded_date= current_date) as regular_meal_count, 
        (select count(*) from meal_bio_log where meal_type_id = (select id from price_master_configuration 
        where meal_code = 'G') and recorded_date= current_date) as guest_meal_count,
        (select now()) as current_date_time 
        from hr_employee where active=True and id_card_no is not NULL""")
        employee_count = request.env.cr.dictfetchall()
        return employee_count    

    @http.route('/get_employee_details', auth='public', methods=['POST'], type='json', csrf=False, cors='*')
    def get_location_employee_data(self, **kwargs):
        request.env.cr.execute(f''' 
                select 
                 
                (select name from kw_card_master where id = hr.id_card_no) as RFID,
                hr.id as employee_id,
                hr.name as employee_name,
                hr.biometric_id as bio_id,
                (select name from hr_job where id = hr.job_id )as designation,
                (select name from hr_department where id = hr.department_id ) as department,
                hr.image_url as photo,
                coalesce((select 
                    case 
                        when mbl.employee_id = hr.id and mbl.meal_type = 'regular' then 'regular'
                        when mbl.employee_id = hr.id and mbl.meal_type = 'guest' then 'guest'
                    else 'guest' end as meal_type
                    from meal_bio_log mbl where mbl.recorded_date = current_date and mbl.employee_id = hr.id limit 1
                ),'guest') as meal_type
                from hr_employee hr where active=True and employement_type != 5
                ''')
        emp_data = request.env.cr.dictfetchall()
        return emp_data     

    @http.route('/get_location', auth='public', methods=['POST'], type='json', csrf=False, cors='*')
    def get_office_location(self, **kwargs):
        request.env.cr.execute(f''' select id as location_id,
                                    name  as location_name 
                                    from kw_res_branch 
                                    where active=True''')
        emp_location = request.env.cr.dictfetchall()
        return emp_location   


    # @http.route('/get_device_name', auth='public', methods=['POST'], type='json', csrf=False, cors='*')
    # def get_device_name_from_no(self, **kwargs):
    #     try:
    #         device_no= kwargs.get('device_no')
    #         request.env.cr.execute(f''' select type as Used_for ,sync_status from kw_device_master 
    #                                     where device_id={device_no}''')
    #         device_used_for = request.env.cr.dictfetchall()
    #         if device_no:
    #             return device_used_for 
    #         # else:
    #         #     return {'device_used_for': "Device Not Found!"}  
    #     except Exception as e:
    #         data = {'status': 500, 'error_log': str(e)}
    #     return data



    @http.route('/get_bench_sbu_ctc', auth='public', methods=['POST'], type='json', csrf=False, cors='*')
    def get_bench_emp_ctc_job_sbu(self, **kwargs):
        data={}
        try:
            # device_no= kwargs.get('device_no')
            request.env.cr.execute(f''' select cast(line.year as integer) as year,line.month,
            count(hr.id) filter (where  hr.sbu_master_id is not null and  kw.code = 'DEV') as sbu_developer_count,
            count(hr.id) filter (where  hr.sbu_master_id is not null and  kw.code = 'TTL') as sbu_tl_count,
            sum(line.total) filter (where line.code = 'CTC' and  hr.sbu_master_id is not null and kw.code in ('DEV','TTL')) as sbu_ctc,
            count(hr.id) filter (where  hr.sbu_master_id is null and  kw.code = 'DEV') as bench_developer_count,
            count(hr.id) filter (where  hr.sbu_master_id is null and  kw.code = 'TTL') as bench_tl_count,
            sum(line.total) filter (where line.code = 'CTC' and  hr.sbu_master_id is  null and kw.code in ('DEV','TTL')) as bench_ctc
            from hr_employee as hr left join kwmaster_category_name as kw on hr.emp_category = kw.id  join
                        hr_payslip_line as line
                        on  hr.id = line.employee_id and line.code='CTC' join hr_payslip as p
                        on p.id = line.slip_id and p.state='done' where  hr.emp_role = (select id from kwmaster_role_name where code='DL') and line.month is not null and line.year is not null
            group by line.year,line.month,p.date_to''')
            count = request.env.cr.dictfetchall()
            if count:
                return count 
            # else:
            #     return {'device_used_for': "Device Not Found!"}  
        except Exception as e:
            data = {'status': 500, 'error_log': str(e)}
        return data

    @http.route('/get_emp_gross_tds', auth='public', methods=['POST'], type='json', csrf=False, cors='*')
    def get_bench_emp_ctc_job_tds(self, **kwargs):
        data={}
        try:
            # device_no= kwargs.get('device_no')
            year = str(kwargs.get('year'))
            month = int(kwargs.get('month'))
            request.env.cr.execute(f''' with gross as (select row_number() over() as id,
		   e.emp_code as emp_code,
		   e.kw_id as kw_id,
		   e.name as employee,
		   doc.doc_number as pan,
		   fy.name as financial_year,
		   l.amount  as gross_amount,
			h.date_to as date_to,
			l.year as year,
			l.month as month
			from hr_payslip_line l
		   	join hr_payslip h  on l.slip_id = h.id
			join hr_employee e on h.employee_id = e.id
		   	left join kwemp_identity_docs as doc on doc.emp_id= h.employee_id and doc.name='1'
		   	join account_fiscalyear as fy on h.date_to between fy.date_start and fy.date_stop
			where  l.code in ('GROSS') and h.state='done' and l.amount > 0 and l.year='{year}' and l.month={month}
		  	),
		tds as (select row_number() over() as id,
		   e.emp_code as emp_code,
		   e.kw_id as kw_id,
		   e.name as employee,
		   doc.doc_number as pan,
		   fy.name as financial_year,
		   l.amount  as tds_amount,
			h.date_to as date_to,
			l.year as year,
			l.month as month
			from hr_payslip_line l
		   	join hr_payslip h  on l.slip_id = h.id
			join hr_employee e on h.employee_id = e.id
		   	left join kwemp_identity_docs as doc on doc.emp_id= h.employee_id and doc.name='1'
		   	join account_fiscalyear as fy on h.date_to between fy.date_start and fy.date_stop
			where  l.code in ('TDS') and h.state='done' and l.amount > 0 and  l.year='{year}' and l.month={month}
		  	)
		select b.date_to,b.emp_code,b.kw_id,b.employee,b.pan,b.financial_year,a.gross_amount,b.tds_amount,b.year,b.month from 
		tds as b
		join gross as a on a.employee = b.employee and a.date_to = b.date_to''')
            count = request.env.cr.dictfetchall()
            if count:
                return count 
            # else:
            #     return {'device_used_for': "Device Not Found!"}  
        except Exception as e:
            data = {'status': 500, 'error_log': str(e)}
        return data
           



    @http.route('/get_central_bench_resource', auth='public', methods=['POST'], type='json', csrf=False, cors='*')
    def get_sbu_central_bench_report(self, **kwargs):
        request.env.cr.execute(f'''  
        SELECT
            hr.kw_id as kw_id
           
                from hr_employee as hr 
                    join kwmaster_category_name as category
                    on hr.emp_category = category.id
                    join hr_department as hrd on hrd.id= hr.department_id
                    where hr.active =true and hrd.code='BSS' and hr.kw_id is  not null  and 
                    hr.emp_role in (select id from kwmaster_role_name  where code in ('DL','R','S')) and 
                    hr.emp_category in(select id from kwmaster_category_name where code in ('TTL','DEV','PM','BA','IFS','SS','SMS'))
                    and hr.sbu_master_id is null and hr.employement_type not in (SELECT id FROM kwemp_employment_type where code = 'O')
					and hr.id not in (select applicant_id from kw_resignation  where state not in ('reject','cancel') and applicant_id is not null)
					and hr.id not in (select employee_id from hr_leave where state in ('validate') and  date_to > current_date and holiday_status_id in (select id from hr_leave_type where leave_code in ('MT','SAB','SPL')))
					''')
        bench_record = request.env.cr.dictfetchall()
        return bench_record   
    
    
    @http.route('/get_resource_mis_report', auth='public', methods=['POST'], type='json', csrf=False, cors='*')
    def get_resource_mis_report(self, **kwargs):
            request.env.cr.execute(f'''  
            SELECT 
                    mr.emp_code as employee_code,
                    mr.name as employee_name,
                    (select name from kwemp_employment_type where id = mr.employement_type)  as employement_type,
                    (select name from kwmaster_role_name where id = mr.emp_role ) as employee_role,
                    (select name from kwmaster_category_name where id = mr.emp_category ) as employee_category,
                    (select alias from kw_res_branch where id = mr.job_branch_id) as job_branch,
                    (select name from kw_sbu_master where id = mr.sbu_master_id) as sbu_master,
                    (select name from hr_department where id = mr.department_id) as department,
                    (select name from hr_department where id = mr.division) as division,
                    (select name from hr_department where id = mr.section) as section,
                    mr.budget_type as budget_type,
                    (select name from project_project where id = mr.emp_project_id) as employee_project,
                    mr.start_date as contract_start_date,
                    mr.end_date as contract_end_date,
                    mr.joining_type as joined_as,
                    mr.date_of_joining as date_of_joining,
                    mr.date_of_exit as date_of_exit,
                    (select name from kw_grade_level where id = mr.emp_level) as employee_level,
                    mr.location as location,
                    mr.previous_company_experience_display_abbr as previous_company_experience,
                    mr.csm_experience_display as csm_experience,
                    mr.total_experience_display as total_experience,
                    (select name from hr_employee where id = mr.parent_id) as reporting_authority,
                    mr.gender as gender
                    
                    from hr_employee_mis_report mr

                        ''')
            mis_records = request.env.cr.dictfetchall()
            return mis_records 
        