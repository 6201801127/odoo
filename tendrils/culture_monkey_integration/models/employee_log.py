# -*- coding: utf-8 -*-
"""
Module for Custom Odoo Functionality.

This module contains custom functionality for Odoo, including date manipulation,
API interactions, and other utilities.

"""
from datetime import date
import requests, json
import re
from odoo import tools
from odoo import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta


class CultureMonkeyIntegration(models.Model):
    """
    Model for Culture Monkey Integration.

    This model represents the integration with Culture Monkey for employee list logging.

    Attributes:
        _name (str): The technical name of the model ('employee_list_log').
        _auto (bool): Indicates whether the model is automatically created in the database (False in this case).
        _description (str): Description of the model ('Sync').
        _rec_name (str): Field used as the record name (in this case, 'id').
        _order (str): Default order for records (ascending by 'first_name').

    """
    _name = 'employee_list_log'
    _auto = False
    _description = 'Sync'
    _rec_name = 'full_name'
    _order = 'first_name ASC'

    full_name = fields.Char(string="Full Name")
    first_name = fields.Char(string="First Name", compute="_format_full_name")
    last_name = fields.Char(string="Last Name", compute="_format_full_name")
    date_of_birth = fields.Date(string="Date of Birth")
    ph_no = fields.Char(string="Phone No")
    gender = fields.Selection(string="Gender", selection=[('M', 'Male'), ('F', 'Female')])
    external_id = fields.Many2one('hr.employee', string="Employee")
    parent_id = fields.Many2one('hr.employee', string="Employee")
    department = fields.Many2one('hr.department', string="Department")
    division = fields.Many2one('hr.department', string="Division")
    emp_id = fields.Char(string="Employee Code")
    email_addr = fields.Char(string="Email Address")
    date_joining = fields.Date(string="Date of Joining")
    team_name = fields.Char(string="Team Name")
    location_name = fields.Char(string="Location Name")
    designation = fields.Char(string="Designation")
    level_emp = fields.Char(string="Level")

    culture_monkey_id = fields.Many2one("culture_monkey_sync_data")
    sync_required = fields.Boolean(string="Sync Required")
    ex_employee_sync = fields.Boolean(string="Ex Employee Sync")
    is_active = fields.Boolean(string="Active")

    @api.multi
    def _format_full_name(self):
        p = re.compile(r'^(?P<FIRST_NAME>.+)(\s+)(?P<LAST_NAME>.+)$', re.IGNORECASE)
        for rec in self:
            m = p.match(rec.full_name)
            if m != None:
                rec.first_name = m.group('FIRST_NAME')
                rec.last_name = m.group('LAST_NAME')

    @api.multi
    def sync_data_log(self, *args):
        gender_list = {'male': "Male", 'female': 'Female'}
        sync_payload = {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "date_of_birth": self.date_of_birth.strftime("%Y-%m-%d"),
            "phone_number": self.ph_no if self.ph_no else '',
            "gender": gender_list.get(self.gender, 'Other'),
            "employee_id": self.emp_id,
            "external_id": str(self.external_id.id),
            "email_address": self.email_addr,
            "date_of_joining": self.date_joining.strftime("%Y-%m-%d"),
            "team_name": self.department.name,
            "subteam_name": self.division.name if self.division else '',
            "location_name": self.location_name,
            "designation": self.designation,
            "manager_email": self.parent_id.work_email,
            "custom_attributes": {
                "level": self.level_emp if self.level_emp else '',
            }
        }
        # print("culture_monkey_id >>>> ", self.culture_monkey_id)
        # print("sync_payload=============", sync_payload)
        # print(a)
        mode = 0
        if self.is_active == True:
            monkey_url = "https://csm.culturemonkey.io/api/v1/employees"
            header = {'Authorization': 'Token _lIFvmkXBwD3ay9B9kDL_Q', 'Content-type': 'application/json'}
            if self.culture_monkey_id.exists():
                external_id = sync_payload['external_id']
                del sync_payload['external_id']
                # print("sync_payload 2>>>> ", sync_payload)
                mode = 2
                resp_result = requests.put(monkey_url+f"/{external_id}", headers=header, data=json.dumps(sync_payload))
            else:
                mode = 1
                resp_result = requests.post(monkey_url, headers=header, data=json.dumps(sync_payload))
            json_data = json.dumps(resp_result.json())
            json_record = json.loads(json_data)
            print("json_record===================", json_record)
            self.create_log(json_record, sync_payload, self.external_id.id, json_record.get('id', '0'), mode)
        # else:
        #     self.ex_emp_sync()

    def create_log(self, json_record, values, emp_id, culture_monkey_id, mode):
        log_rec = self.env['culture_monkey_sync_data'].sudo().search([('emp_id', '=', emp_id)])
        if log_rec.exists():
            log_rec.write({
                'data_of_sync': datetime.today(),
                'emp_id': emp_id,
                'culture_monkey_id': culture_monkey_id,
                'response_id': json_record,
                'request_id': values,
                'type': mode,
            })
        else:
            self.env['culture_monkey_sync_data'].sudo().create({
                'data_of_sync': datetime.today(),
                'emp_id': emp_id,
                'culture_monkey_id': culture_monkey_id,
                'response_id': json_record,
                'request_id': values,
                'type': mode,
            })

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW %s AS (
            WITH cm AS (SELECT id, culture_monkey_id, emp_id, sync_required, ex_employee_sync 
                FROM culture_monkey_sync_data)
        
            SELECT emp.id AS id,
                emp.id AS external_id,
                emp.name AS full_name,
                split_part(emp.name, ' ', 1) AS first_name,
                split_part(emp.name, ' ', 2) AS last_name,
                emp.work_email AS email_addr,
                emp.parent_id AS parent_id,
                emp.birthday AS date_of_birth,
                emp.date_of_joining AS date_joining,
                emp.department_id AS department,
                emp.division AS division,
                emp.active AS is_active,
                emp.mobile_phone AS ph_no,
                emp.gender AS gender,
                emp.emp_code AS emp_id,  
                
                (SELECT alias FROM kw_res_branch WHERE id=emp.base_branch_id) AS location_name,
                (SELECT name FROM hr_department WHERE id=emp.department_id) AS team_name,
                (SELECT name FROM hr_job WHERE id = emp.job_id) AS designation,
                (SELECT name FROM kw_grade_level WHERE id = emp.level) AS level_emp,
                cm.culture_monkey_id AS culture_monkey_id,
                cm.sync_required AS sync_required,
                cm.ex_employee_sync AS ex_employee_sync
            
            FROM hr_employee emp
            LEFT JOIN cm ON cm.emp_id=emp.id  
            WHERE (emp.active=True AND emp.employement_type!='5') OR (emp.active=False and cm.id>0)
            ORDER BY is_active desc, full_name
			
        )""" % (self._table)
        self.env.cr.execute(query)

    def get_update_culture_monkey(self):
        # print("method cron==================")
        record = self.env['employee_list_log'].search(
            ['|', ('culture_monkey_id', '=', False), ('sync_required', '=', True)], limit=25)
        # print("record <<<< ", record)
        # print(a)
        for rec in record:
            if rec.date_of_birth:
                rec.sync_data_log()
        self.get_update_ex_employees()

    def get_update_ex_employees(self):
        record = self.env['employee_list_log'].search(
            [('is_active', '=', False), ('culture_monkey_id', '!=', False), ('ex_employee_sync', '!=', True)], limit=25)
        # print('record >>> ', record)
        for rec in record:
            # print('record >>> ',  rec.culture_monkey_id, rec.external_id)
            if rec.culture_monkey_id and rec.external_id:
                rec.ex_emp_sync()
        return True

    def ex_emp_sync(self):
        if self.culture_monkey_id and self.external_id and self.ex_employee_sync != True:
            cm_data = self.culture_monkey_id
            external_id = self.external_id.id
            sync_payload = {
                "is_active": "false",
                # "external_id": external_id.id,
            }
            # print("sync_payload=============", cm_data.id, sync_payload)
            monkey_url = "https://csm.culturemonkey.io/api/v1/employees"
            header = {'Authorization': 'Token _lIFvmkXBwD3ay9B9kDL_Q', 'Content-type': 'application/json'}
            # external_id = cm_data.id
            # print("sync_payload 2>>>> ", sync_payload)
            resp_result = requests.put(monkey_url + f"/{external_id}", headers=header, data=json.dumps(sync_payload))
            json_data = json.dumps(resp_result.json())
            json_record = json.loads(json_data)
            # print("json_record===================", json_record)
            log_rec = self.env['culture_monkey_sync_data'].sudo().search([('emp_id', '=', external_id)])
            # print(" log_rec >>> ", log_rec, external_id)
            if log_rec.exists():
                log_rec.write({'ex_employee_sync': True})
        return True




