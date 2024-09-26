from odoo import fields, models, api
from odoo.exceptions import ValidationError
import datetime,calendar
from datetime import date, datetime, time
import json
import requests



class BankDetailsUpdate(models.Model):
    _name = 'bank_details_update'
    _description = 'Bank Details Update By Employee'
    _rec_name = "employee_id"

   
    employee_id = fields.Many2one('hr.employee', string="Employee")
    name = fields.Char(string="Name",related='employee_id.name')
    emp_code = fields.Char(string="Code",related='employee_id.emp_code')
    location = fields.Char(string="Location",related='employee_id.job_branch_id.alias')
    bank_account = fields.Char(string="Account No")
    bank_id = fields.Many2one('res.bank', string="Bank")
    ifsc = fields.Char(string="IFSC",related='bank_id.bic')
    department = fields.Char(string='Department', related='employee_id.department_id.name')
    designation = fields.Char(string='Designation', related='employee_id.job_id.name')
    old_bank_id = fields.Many2one('res.bank', string="Old Bank")
    old_bank_account = fields.Char(string="Old Account No")
    old_ifsc = fields.Char(string="Old IFSC",related='old_bank_id.bic')
    
    @api.multi
    def sync_resource_ctc(self, *args):
        employees = self.env['hr.employee'].search([('active', '=', True),('department_id.code', '=', 'BSS'),('enable_payroll', '=', 'yes'),('grade.name', 'in', ['M1','M2','M3','M4','M5','M6','M7'])])
        payload_list = []
        if employees:
            for employee in employees:
                current_ctc = employee.contract_id.wage if employee.contract_id  else 0
                sync_payload = {
                    "Kw_Emp_ID": employee.kw_id,
                    "transValues": current_ctc,
                }
                payload_list.append(sync_payload)
                # v5_api_url = "http://192.168.61.198/prd.service.portalv6.csmpl.com/OdooSynSVC.svc/EmployeengamentDetails"
                v5_api_url = self.env['ir.config_parameter'].sudo().search([]).filtered(lambda x: x.key == 'URL for Sales Portlet Data Sync').value +'/EmployeengamentDetails'
                header = {'Content-type': 'application/json'}
                
                try:
                    resp = requests.post(v5_api_url, headers=header, data=json.dumps(payload_list))
                    if resp.status_code == 200:
                        json_record = resp.json()
                    else:
                        error_message = f"Failed to sync data for employee ID: {employee.kw_id}. Status code: {resp.status_code}, Response: {resp.text}"
                except Exception as e:
                    error_message = f"Error occurred while syncing data for employee ID: {employee.kw_id}. Error: {str(e)}"
                    
class Employee_NPS_log(models.Model):
    _name = 'kw_employee_update_nps_log'
    _description = 'Employee NPs log'

    employee_id = fields.Many2one("hr.employee", string="Employee")
    skips_check = fields.Integer(string="skips", default=0)