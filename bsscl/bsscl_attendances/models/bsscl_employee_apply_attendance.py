from odoo import models, fields, api
from datetime import date, datetime
import re
# from lxml import etree
from odoo.exceptions import ValidationError, UserError


# MAX_DAYS_FOR_APPLY = 30

class EmployeeApplyAttendance(models.Model):
    _name = 'bsscl_employee_apply_attendance'
    _description = 'Attendance Correction Request'
    _rec_name = 'employee_id'



    applied_for = fields.Selection(string="Applied By", selection=[('self', 'Self'), ('others', 'Others')],
                                   required=True, default='self')
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
   
    department_id = fields.Many2one(string='Department', comodel_name='hr.department',
                                    related="employee_id.department_id")
    designation_id = fields.Many2one(string='Designation', comodel_name='hr.job', related="employee_id.job_id")

    check_in_datetime = fields.Datetime(string='Office-in Date & Time', required=True)
    check_out_datetime = fields.Datetime(string='Office-out Date & Time', required=True)
    reason = fields.Text(string="Reason", required=True)

    action_taken_by = fields.Many2one('hr.employee', string="Action Taken By", ondelete='cascade')
    pending_at = fields.Many2one('hr.employee', string="Pending At", ondelete='cascade')

    authority_remark = fields.Text(string='Remark')
    action_taken_on = fields.Datetime(string='Action Taken On')

    state = fields.Selection(string="Status",
                             selection=[('1', 'Draft'), ('2', 'Applied'), ('3', 'Approved'), ('5', 'Rejected'),
                                        ('6', 'Cancelled')], required=True, default='1')  # ,('4','Approved by HR')
    btn_visibility_status = fields.Boolean(string="Button Visibility", compute="_compute_button_visibility_status")
    check_user = fields.Boolean(string="Check user", compute="_compute_check_user")

    def _compute_check_user(self):
        for rec in self:
            if rec.employee_id.user_id.id == self.env.uid:
                rec.check_user = True
            else:
                rec.check_user = False
    
    def _compute_button_visibility_status(self):
        for rec in self:
            emp_ids = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1).ids
            if rec.employee_id.parent_id.id in emp_ids and rec.state == '2':
                rec.btn_visibility_status = True
            else:
                rec.btn_visibility_status = False


    @api.onchange('applied_for')
    def _get_employee(self):
        emp_ids = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        if self.applied_for == "others":
            self.employee_id = False
            return {'domain': {'employee_id': ([('parent_id', 'in', emp_ids.ids)])}}
        else:
            self.employee_id = emp_ids.id
            return {'domain': {'employee_id': ([('id', 'in', emp_ids.ids)])}}


    @api.constrains('reason')
    def validate_reason(self):
        for record in self:
            if record.reason and not re.match(r'^[A-Za-z]{1}[A-Za-z0-9\s]*$',str(record.reason)):
                raise ValidationError("reason should start from an alphabet and should be alphanumeric")
            
            if len(record.reason) > 100:
                raise ValidationError("maximum lenth for reason is 100 character's.")

            # if re.match("^[a-zA-Z0-9/\s\+-.()]+$", record.reason) == None:
            #     raise ValidationError("Please remove special characters from reason")

    @api.constrains('authority_remark')
    def validate_authority_remark(self):
        for record in self:
            if record.authority_remark and re.match("^[a-zA-Z0-9/\s\+-.,_()]+$", record.authority_remark) == None:
                raise ValidationError("Please remove special characters from remark")

    @api.model
    def create(self, values):
        """
            Create a new record for a model ModelName
            @param values: provides a data for new record
    
            @return: returns a id of new record
        """
        result = super(EmployeeApplyAttendance, self).create(values)      
        for attendance_request in result:
            # diff_hour = attendance_request.check_out_datetime - attendance_request.check_in_datetime
            # if attendance_request.applied_for == 'others' and (
            #         attendance_request.employee_id.parent_id.user_id == self.env.user or self.env.user.has_group(
            #         'hr_attendance.group_hr_attendance_manager')):
            #     attendance_request.write({'state': '3', 'action_taken_by': self.env.user.employee_ids.id,
            #                               'authority_remark': 'Application auto-approved.',
            #                               'action_taken_on': datetime.now()})
                # self.env['hr.attendance'].sudo().create({
                #                 'employee_id':attendance_request.employee_id.id,
                #                 'check_in':attendance_request.check_in_datetime,
                #                 'check_out':attendance_request.check_out_datetime,
                #                 'worked_hours':diff_hour.total_seconds()
                #             })
            # else:
            attendance_request.write({'state': '1'})

                # attendance_request.write({'state': '1', 'pending_at': attendance_request.employee_id.parent_id.id})
        return result
    
    def apply_request(self):
        for rec in self:
            if rec.applied_for == 'self':
                rec.update({'state': '2', 'pending_at': self.employee_id.parent_id.id})
            else:
                rec.update({'state': '3', 'action_taken_by': self.env.user.employee_ids.id,
                                          'authority_remark': 'Application auto-approved.',
                                          'action_taken_on': datetime.now()})
                diff_hour = rec.check_out_datetime - rec.check_in_datetime
                
                self.env['hr.attendance'].sudo().create({
                                'employee_id':rec.employee_id.id,
                                'check_in':rec.check_in_datetime,
                                'check_out':rec.check_out_datetime,
                                'worked_hours':diff_hour.total_seconds()
                            })
                


   
    @api.constrains('employee_id')                                                
    def attendance_mode_validation(self):
        emp_atten = self.env['bsscl_employee_apply_attendance']
        for rec in self:
            attendance_record = emp_atten.sudo().search([('employee_id','=',rec.employee_id.id),('state','in',['2','3'])])
            for record in attendance_record:
                date = record.check_in_datetime.date()
                if rec.check_in_datetime.date() == date:
                    raise ValidationError("You cannot Apply Attendance Twice for the same Date.")

    @api.constrains('check_out_datetime')                                                
    def validate_check_out_datetime(self):
        for rec in self:
            if rec.check_in_datetime.date() != rec.check_out_datetime.date():
                raise ValidationError("Check-in date and check-out date must be same.")
            else:
                if rec.check_in_datetime > rec.check_out_datetime:
                    raise ValidationError("Check-out time must be greater than check-in time.")
                
    @api.constrains('check_in_datetime')
    def date_validation(self):
        for record in self:
            if record.check_in_datetime.date() > datetime.now().date():
                raise ValidationError("Attendance date should not be greater than today's date")

