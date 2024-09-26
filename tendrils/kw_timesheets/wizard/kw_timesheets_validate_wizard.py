from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TimesheetValidateWizard(models.TransientModel):
    _name        = "kw_timesheets_validate_wizard"
    _description = "Timesheet Validate Wizard"
    
    timesheet_ids = fields.Many2many('account.analytic.line',string="Timesheets",default=lambda self:self.env.context.get('active_ids',[]))
    remark = fields.Text("Remark")

    @api.multi
    def action_approve_timesheets(self):
        # print("context inside timesheet approve",self._context)
        project_work = self.env['kw_project_category_master'].search([('mapped_to','=','Project')],limit=1)

        current_employee = self.env['hr.employee'].search([('user_id','=',self._uid)],limit=1)
        valid_timesheets = self.timesheet_ids.filtered(
            lambda r: (r.employee_id != current_employee and r.validated != True) and
                      ((r.task_id.tl_employee_id == current_employee and r.prject_category_id == project_work and
                        (r.employee_id.emp_category.code != 'TTL' or not r.employee_id.emp_category.code or
                         not r.employee_id.emp_category) and
                        r.employee_id != r.project_id.emp_id and r.employee_id != r.project_id.reviewer_id) or
                       (r.project_id.emp_id == current_employee and r.employee_id == r.task_id.tl_employee_id or
                        not r.task_id.tl_employee_id or r.employee_id.emp_category.code == 'TTL') or
                       (r.employee_id.parent_id == current_employee and r.prject_category_id != project_work or
                        (r.employee_id == r.project_id.reviewer_id and r.prject_category_id == project_work) or
                        (r.prject_category_id == project_work and not r.project_id.reviewer_id)) or
                       (r.project_id.emp_id == r.employee_id and r.project_id.reviewer_id == current_employee)))
        invalid_timesheets = self.timesheet_ids - valid_timesheets
        if invalid_timesheets:
            raise ValidationError("Invalid timesheets selected. Please select valid timesheets.")

        valid_timesheets.write({
            'validated':True,
            'remark':self.remark,
            'approved_by': self.env.user.name
        })
        self.env.user.notify_success("Timesheet(s) Validated Successfully.")

        template = self.env.ref('kw_timesheets.kw_timesheet_ra_pm_reviewer_validate_mail_template')
        
        timesheet_employees = valid_timesheets.mapped('employee_id')
        for employee in timesheet_employees:
            employee_timesheets = valid_timesheets.filtered(lambda r:r.employee_id == employee)
            template.with_context(timesheet_records=employee_timesheets).send_mail(employee_timesheets[0].id,notif_layout="kwantify_theme.csm_mail_notification_light")

    @api.multi
    def action_reject_timesheets(self):
        # print("context inside timesheet reject",self._context)
        project_work = self.env['kw_project_category_master'].search([('mapped_to','=','Project')],limit=1)

        current_employee = self.env['hr.employee'].search([('user_id','=',self._uid)],limit=1)
        valid_timesheets = self.timesheet_ids.filtered(
            lambda r: (r.employee_id != current_employee and r.validated != True) and
                      ((r.task_id.tl_employee_id == current_employee and r.prject_category_id == project_work and
                        (r.employee_id.emp_category.code != 'TTL' or not r.employee_id.emp_category.code or
                         not r.employee_id.emp_category) and
                        r.employee_id != r.project_id.emp_id and r.employee_id != r.project_id.reviewer_id) or
                       (r.project_id.emp_id == current_employee and r.employee_id == r.task_id.tl_employee_id or
                        not r.task_id.tl_employee_id or r.employee_id.emp_category.code == 'TTL') or
                       (r.employee_id.parent_id == current_employee and r.prject_category_id != project_work or
                        (r.employee_id == r.project_id.reviewer_id and r.prject_category_id == project_work) or
                        (r.prject_category_id == project_work and not r.project_id.reviewer_id)) or
                       (r.project_id.emp_id == r.employee_id and r.project_id.reviewer_id == current_employee)))
        invalid_timesheets = self.timesheet_ids - valid_timesheets
        if invalid_timesheets:
            raise ValidationError("Invalid timesheets selected. Please select valid timesheets.")

        valid_timesheets.write({
            'validated':False,
            'remark':self.remark,
            'active':False
        })
        self.env.user.notify_success("Timesheet(s) Rejected Successfully.")

        template = self.env.ref('kw_timesheets.kw_timesheet_ra_pm_reviewer_timesheet_reject_mail_template')
        
        timesheet_employees = valid_timesheets.mapped('employee_id')
        for employee in timesheet_employees:
            employee_timesheets = valid_timesheets.filtered(lambda r:r.employee_id == employee)
            template.with_context(timesheet_records=employee_timesheets).send_mail(employee_timesheets[0].id,notif_layout="kwantify_theme.csm_mail_notification_light")
