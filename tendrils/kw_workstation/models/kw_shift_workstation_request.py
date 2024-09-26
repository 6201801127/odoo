from odoo.exceptions import ValidationError
from odoo import tools
from odoo import models, fields, api
from datetime import datetime, date


class EmployeeAttendance(models.Model):
    _name = 'kw_swap_workstation'
    _description = 'Workstation request record'

    def _default_workstation_employee(self):
        record = self.env['kw_workstation_master'].sudo().search([('employee_id', '=', self.env.user.employee_ids.id)],
                                                                 limit=1)
        if record:
            return record

    location_name = fields.Selection(string="WFH/WFO",
                                     selection=[('1', 'WFH'), ('2', 'WFO')], required=False, default="2")
    date_of_start = fields.Date(string="Start Date", required=True)
    end_date_of = fields.Date(string="End Date", required=True)
    reason_shift = fields.Text(string="Reason", required=True)
    work_name = fields.Many2one("kw_workstation_master", string="Workstation Name",
                                default=_default_workstation_employee)

    employee_id = fields.Many2one('hr.employee', string="Employee",
                                  default=lambda self: self.env.user.employee_ids)
    state = fields.Selection([('Draft', 'Draft'), ('Applied', 'Applied'),
                              ('Approved', 'Approved'), ('Reject', 'Reject'), ('Reschedule', 'Reschedule')
                              ], string='Status', readonly=True, copy=False, index=True,
                             default='Draft')
    workstation_type = fields.Selection(string="Workstation Type",
                                        selection=[('Swapping_ws', 'Swapping WS'), ('Other', 'Other WS')],
                                        required=True)
    workstation_avail = fields.Many2one('kw_workstation_master', string="Workstation Available")

    shift_change_check = fields.Boolean(string="Shift Check")
    pending_at = fields.Many2one('hr.employee', string="Pending")
    swapping_with = fields.Many2one('hr.employee', string="Swapping With")

    @api.onchange('workstation_type')
    def onchange_workstation_available_emp(self):
        if self.workstation_type == 'Other':
            # print("self onchange==================workstation==========", self.work_name)
            branch_record = self.env['kw_workstation_master'].sudo().search(
                [('branch_id', '=', self.employee_id.base_branch_id.id), ('is_hybrid', '=', True)]).mapped('employee_id')
            # print("branch_record================", branch_record)
            emp_tour = self.env['kw_tour'].sudo().search(
                [('employee_id', 'in', branch_record.ids), ('state', '=', 'Applied')])
            # print("emp_tour>>>>>>>>>>>>>>", emp_tour)
            # if emp_tour:
            #     if emp_tour.date_travel == self.date_of_start and emp_tour.date_return == self.end_date_of:
            #         emp_leave = self.env['hr.leave'].sudo().search([('employee_id','in',branch_record.ids),('state','=','confirm')])
            # print("emp_leave>>>>>>>>>>>>>>>>>>>>>>>.",emp_leave,emp_leave.employee_id.id)
        else:
            if not self.swapping_with:
                self.swapping_with = self.work_name.employee_id - self.employee_id

    @api.constrains('date_of_start', 'end_date_of')
    def get_date_restriction(self):
        if self.date_of_start:
            if self.end_date_of < self.date_of_start:
                raise ValidationError("End date should be after Start date.")
            date_diff = self.date_of_start - date.today()
            duration = self.end_date_of - self.date_of_start
            # duration = self.end_date_of - date.today()
            # print("date_diff=============", date_diff.days)
            # print("duration.days=============", duration.days)
            if date_diff.days < 0:
                raise ValidationError("Start date cannot be a back date.")
            elif date_diff.days > 15:
                raise ValidationError("Start date cannot exceed 15 days from today.")
            elif duration.days > 15:
                raise ValidationError("End date cannot exceed 15 days from start date.")

    def send_to_approve(self):
        template = self.env.ref('kw_workstation.kw_shift_change_email_template')

        if self.workstation_type == 'Swapping_ws':
            logged_in_employee_id = self.env.user.employee_ids.id
            record = self.env['kw_workstation_master'].sudo().search([('name', '=', self.work_name.name)])
            employee_ids = [rec.id for rec in record.employee_id if rec.id != logged_in_employee_id]
            employees = self.env['hr.employee'].sudo().search([('id', 'in', employee_ids)])
            for employee in employees:
                self.write({'state': "Applied",
                            'shift_change_check': True,
                            'pending_at': employee.id})

                if template:
                    email_to = employee.work_email
                    mail_cc = (self.env.user.employee_ids.parent_id.work_email) + ',' + (employee.parent_id.work_email)
                    emp_name = employee.name
                    template.with_context(mail_for='Applied', cc_mail=mail_cc, mail_to=email_to, user_name=emp_name,
                                          date_of=self.date_of_start).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")

            self.env.user.notify_success("Mail sent Successfully.")
        else:
            pass

    def approved_request(self):
        self.write({'state': 'Approved',
                    'pending_at': False})
        # print("self=========================", self.state, self.pending_at)
        record_assign = self.env['kw_workstation_assign'].sudo().search(
            [('assign_date', '=', self.date_of_start), ('workstation_id', '=', self.work_name.id)])
        # print("record_assign============================", record_assign.workstation_id, record_assign,
        #       self.env.user.employee_ids)

        if record_assign:
            record_assign.write({'employee_id': self.env.user.employee_ids.id})

        template = self.env.ref('kw_workstation.kw_shift_change_email_template')
        logged_in_employee_id = self.env.user.employee_ids.id
        record = self.env['kw_workstation_master'].sudo().search([('name', '=', self.work_name.name)])
        employee_ids = [rec.id for rec in record.employee_id if rec.id != logged_in_employee_id]
        employees = self.env['hr.employee'].sudo().search([('id', 'in', employee_ids)])
        for employee in employees:
            # print("record===============", employee.work_email)
            pass
        if template:
            email_to = employee.work_email
            mail_cc = (self.env.user.employee_ids.parent_id.work_email) + ',' + (employee.parent_id.work_email)
            emp_name = employee.name
            # print("email_to=============================", email_to, mail_cc)
            template.with_context(mail_for="Approved", cc_mail=mail_cc, mail_to=email_to, user_name=emp_name).send_mail(
                self.id,
                notif_layout="kwantify_theme.csm_mail_notification_light")

    def reject_request(self):
        self.write({'state': 'Reject',
                    'pending_at': False})

    def send_to_reschedule(self,emp_leave):
        empl_location = self.env['hr.employee'].sudo().search([('location', '=', 'hybrid')])
        # print("empl_location==========================", empl_location)

        record = self.env['kw_workstation_master'].sudo().search(
            [('is_hybrid', '=', True), ('employee_id', '=', emp_leave.employee_id.id)]).mapped('name')
        # print("record====================", record)
        workstation_allocate = self.env['']

        # print(k)
