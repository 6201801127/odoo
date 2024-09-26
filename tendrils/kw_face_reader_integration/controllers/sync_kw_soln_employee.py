from odoo import http
from odoo.http import request
import json

class SyncEmployeeAPIController(http.Controller):
    @http.route('/sync_kw_soln_employee_data', type='json', auth='none', methods=['POST'], csrf=False)
    def sync_employee_data(self, **post):
        try:
            synced_kw_soln_employee_data = request.jsonrequest.get('params', {}).get('data', [])
            print('Received Employee Data:', synced_kw_soln_employee_data)

            if synced_kw_soln_employee_data:
                incoming_ids = [emp_data['id'] for emp_data in synced_kw_soln_employee_data]

                select_query = """
                    SELECT kw_sol_emp_id FROM synced_kwantify_solutions_employee WHERE kw_sol_emp_id IN %s
                """
                request.cr.execute(select_query, (tuple(incoming_ids),))
                existing_ids = [row[0] for row in request.cr.fetchall()]

                new_ids = list(set(incoming_ids) - set(existing_ids))

                new_employees_data = [
                    (emp_data['id'], emp_data['name'], emp_data['department_name'], emp_data['designation'], 
                    emp_data['work_location'], emp_data['administrative_authority'], emp_data['email'], 
                    emp_data['mobile_phone'], emp_data['date_of_joining'], emp_data['employment_type'], 
                    emp_data['vendor_name'], emp_data['gender'], emp_data['birthday'], emp_data['current_ctc'], True)
                    for emp_data in synced_kw_soln_employee_data
                    if emp_data['id'] in new_ids
                ]

                if new_employees_data:
                    insert_query = """
                        INSERT INTO synced_kwantify_solutions_employee (kw_sol_emp_id, name, department_name, designation, 
                        work_location, administrative_authority, email, mobile_phone, date_of_joining, employment_type, 
                        vendor_name, gender, birthday, current_ctc, active)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    request.cr.executemany(insert_query, new_employees_data)

                if existing_ids:
                    # update_query_active = """
                    #     UPDATE synced_kwantify_solutions_employee
                    #     SET active = TRUE
                    #     WHERE kw_sol_emp_id IN %s
                    # """
                    # request.cr.execute(update_query_active, (tuple(incoming_ids),))

                    update_query_inactive = """
                        UPDATE synced_kwantify_solutions_employee
                        SET active = FALSE
                        WHERE kw_sol_emp_id NOT IN %s AND active = TRUE
                        RETURNING hr_employee_ref_id
                    """
                    request.cr.execute(update_query_inactive, (tuple(incoming_ids),))
                
                    deactivate_ids = [row[0] for row in request.cr.fetchall()]
                    if deactivate_ids:
                        to_deactivate_employee_records = request.env['hr.employee'].sudo().search([('id', 'in', deactivate_ids)])
                        if to_deactivate_employee_records:
                            to_deactivate_employee_records.write({'active': False})
                      
                return {'status': 'success', 'message': 'Employee data synchronized successfully'}

            else:
                return {'status': 'error', 'message': 'Invalid data format'}

        except Exception as e:
            return {'status': 'error', 'message': str(e)}


