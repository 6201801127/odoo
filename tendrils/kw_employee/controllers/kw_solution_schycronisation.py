# -*- coding: utf-8 -*-
import json, requests, base64, datetime
from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError

class KwantifySolutionEmployeeSync(http.Controller):
    @http.route('/sync_kwantify_solution_employee/', methods=['POST'], auth='public', csrf=False, type='json', cors='*')
    def sync_employee_solution_data(self, **kwargs):
        outsourced_employement_id = request.env['kwemp_employment_type'].sudo().search([('code','=','O')],limit=1)
        employee_dict = {}
        # try:
            # import pdb
            # pdb.set_trace()
        if 'result' in kwargs:
            for emp in kwargs['result']:
                if 'name' in emp and len(emp['name'].strip(' ')) == 0:
                    raise ValidationError('Employee name not found.')
                # elif 'emp_code' in emp and len(emp['emp_code'].strip(' ')) == 0:
                #     raise ValidationError('Employee code not found.')
                elif 'date_of_joining' in emp and len(emp['date_of_joining'].strip(' ')) == 0:
                    raise ValidationError('Date of Joining not found.')
                # print(emp.get('id',False))
                # print(emp.id)
                # print(emp.date_of_joining,type(emp.date_of_joining),"###################")
                employee_dict = {
                    'name': emp.get('name',False),
                    'kw_id': emp.get('id',False),
                    'emp_code':emp.get('emp_code',False),
                    "image":emp['image'],
                    'job_id':int(emp.get('job_id',False)),
                    'date_of_joining': datetime.datetime.strptime(emp.get('date_of_joining',False),"%Y-%m-%d").date(),
                    'employement_type':outsourced_employement_id.id if outsourced_employement_id else False,
                    'start_date': datetime.datetime.strptime(emp.get('start_date',False),"%Y-%m-%d").date() if emp['start_date'] else False,
                    'end_date': datetime.datetime.strptime(emp.get('end_date',False),"%Y-%m-%d").date() if emp['end_date'] else False,
                }
                exist_employee_id = request.env['hr.employee'].search([('kw_id','=',int(emp.get('id',False)))],limit=1)
                if exist_employee_id:
                    request.env.cr.execute(f"""update hr_employee set name='{emp.get('name',False)}',kw_id={emp.get('id',False)},
                                        emp_code='{emp.get('emp_code',False)}',job_id={int(emp.get('job_id',False))},date_of_joining='{datetime.datetime.strptime(emp.get('date_of_joining',False),"%Y-%m-%d").date()}',
                                        employement_type='{outsourced_employement_id.id if outsourced_employement_id else False}',
                                        start_date='{datetime.datetime.strptime(emp.get('start_date',False),"%Y-%m-%d").date() if emp['start_date'] else False}',
                                        end_date='{datetime.datetime.strptime(emp.get('end_date',False),"%Y-%m-%d").date() if emp['end_date'] else False}'
                                        where kw_id = {exist_employee_id.kw_id} 
                        """)
                else:
                     employee_data = request.env['hr.employee'].sudo().create(employee_dict)
        #     return {'status':200,'response_data':'Success'}
        # except Exception as e:
        #     # print(e.__dict__)
        #     return {'status': 500, 'error_log': str(e)}
        
        
    @http.route('/get_all_fiscal_years', type='json', auth='user')
    def get_all_fiscal_years(self):
        print("***********************************************")
        fiscal_years = request.env['account.fiscalyear'].search([])
        return {
        'fiscal_years': [
            {'id': fy.id, 'name': fy.name} for fy in fiscal_years
        ]
    }