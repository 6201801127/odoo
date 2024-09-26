from odoo import api, fields, models, _
import json
import requests
from datetime import datetime, timedelta, date
from odoo.exceptions import ValidationError


class EmployeeCloseEmployment(models.TransientModel):
    _name = 'close_employment_wizard'
    _description = 'Employee Release Wizard'

    employee_id = fields.Many2one("hr.employee", string="Employee",
                                  domain=[('active', '=', True)])
    last_working_day = fields.Date(string="Last Working Day")
    reason = fields.Many2one('kw_resignation_master', string="Reason")

    @api.onchange('employee_id')
    def onchange_apply_for(self):
        self.last_working_day = False
        self.reason = False
        employee_resig_id = self.env['kw_resignation'].sudo().search(
            [('applicant_id', '=', self.employee_id.id)], limit=1, order="id desc")
        if employee_resig_id:
            self.last_working_day = employee_resig_id.last_working_date
            self.reason = employee_resig_id.reg_type.id

    @api.multi
    def action_close_employeement(self):
        employee_rec = self.env['hr.employee'].sudo().search(
            ['|', ('active', '=', True), ('active', '=', False), ('id', '=', self.employee_id.id)])
        resign_rec = self.env['kw_resignation'].sudo().search([('applicant_id', '=', self.employee_id.id)])
        eos_rec = self.env['kw_eos_checklist'].sudo().search([('applicant_id', '=', self.employee_id.id)])
        clearance_id = self.env['hr.employee.clearance'].sudo().search([('employee_id', '=', self.employee_id.id)])
        user_rec = self.env['res.users'].sudo().search([('id', '=', self.employee_id.user_id.id)])
        if employee_rec:
            employee_rec.sudo().write({'last_working_day': self.last_working_day,
                                       'resignation_reason': self.reason.id,
                                       'active': False})
            
        if clearance_id:
            clearance_id.sudo().write({'last_day_of_service': self.last_working_day})
        if resign_rec:
            resign_rec.sudo().write({
                'last_working_date': self.last_working_day,
                'reg_type':self.reason.id,
                'manual_closing':True,
                'offboarding_process_status': 'Ex-Employee',
                'offboarding_type': 6,
                'state':'close',
            })
        else:
            # Explicitly set the applicant_id to the selected employee
            self.env['kw_resignation'].sudo().create({
                'apply_for': 'others',
                'applicant_id': self.employee_id.id,
                'manual_closing':True,
                'kt_required':'no',
                'month_last_working_date': self.last_working_day.strftime("%B"),
                'report_employement_type': self.employee_id.employement_type.id,
                'base_branch_id': self.employee_id.base_branch_id.id,
                'department_id': self.employee_id.department_id.id,
                'division': self.employee_id.division.id,
                'section': self.employee_id.section.id,
                'practise': self.employee_id.practise.id,
                'job_id': self.employee_id.job_id.id,
                'applicant_name': self.employee_id.id,
                'applicant_code': self.employee_id.emp_code,
                'gender': self.employee_id.gender,
                'ra': self.employee_id.parent_id.id,
                'date_of_joining': self.employee_id.date_of_joining,
                'effective_from': self.last_working_day,
                'offboarding_type': 6,
                'reg_type': self.reason.id,
                'state': 'close',
                'last_working_date': self.last_working_day,
                'offboarding_process_status':'Ex-Employee',
            })

        if eos_rec:
            eos_rec.sudo().write({'last_working_date': self.last_working_day})
        if user_rec:
            user_rec.sudo().write({'active': False})
        json_record = {}
        """ API starts """

        """ sending data to v5 for ex-employee (post method) """
        if self.employee_id.kw_id:
            parameterurl = self.env['ir.config_parameter'].sudo().get_param('kwantify_eos_url')
            EOSurl = parameterurl + 'MoveEOSExEmp'
            header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            EOSDict = {
                "userId": str(self.employee_id.kw_id),
                "LeavingDate": datetime.strptime(str(self.last_working_day), "%Y-%m-%d").strftime("%Y-%m-%d"),
            }
            try:
                resp = requests.post(EOSurl, headers=header, data=json.dumps(EOSDict))
                j_data = json.dumps(resp.json())
                json_record = json.loads(j_data)
            except Exception as e:
                # raise ValidationError("Some error occurred. Please try again later.")
                # print("MoveEOSExEmp: ", e)
                pass

        if 'status' in json_record and json_record.get('status') == 1:
            self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Employment Closed Data',
                                                                   'new_record_log': EOSDict,
                                                                   'request_params': EOSurl,
                                                                   'response_result': json_record})
        self.env.user.notify_success("Converted to Ex-Employee")
        """ API ends """
