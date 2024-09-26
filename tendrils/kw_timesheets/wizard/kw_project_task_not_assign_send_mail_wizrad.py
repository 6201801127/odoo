import datetime
from datetime import timedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date

class ProjectTasknotAssignNotifyemail(models.TransientModel):
    _name = 'kw_project_task_not_assign_mail'
    _description = "Project Task Not Assigned Summary"

    def _get_default_task_not_assigned(self):
        datas = self.env['kw_project_task_not_assign_report'].browse(self.env.context.get('active_ids'))
        return datas

    @api.multi
    def send_mail_task_not_assigned(self):
        manager_name = []
        email_to = []
        email_cc = []
        project = []
        data = []
        rcm_manager = []
        rcm_member = self.env['hr.employee'].sudo().search([('department_id.code', '=', 'RACM')]).mapped('work_email')
        email_cc.extend(rcm_member)
        rcm = self.env.ref('kw_resource_management.group_budget_manager')
        rcm_emp = rcm.users.mapped('employee_ids') if rcm else ''
        cc_mail = ','.join(rcm_emp.mapped('work_email'))
        context = dict(self._context)
        datas = self.env['kw_project_task_not_assign_report'].browse(self.env.context.get('active_ids'))
        for rec in datas:
            data.append({
                'emp_code' :  rec.employee_id.emp_code,
                'name': rec.employee_id.name,
                'designation': rec.employee_id.job_id.name,
                'category' : rec.emp_role.name,
                'department' : rec.employee_id.department_id.name
            })
            manager_name.append(rec.project_id.emp_id.name) 
            email_to.append(rec.project_id.emp_id.work_email)
            email_cc.extend([rec.project_id.sbu_id.representative_id.work_email if rec.project_id.sbu_id.representative_id.work_email else '',rec.project_id.reviewer_id.work_email and rec.project_id.reviewer_id.parent_id == True if rec.project_id.reviewer_id.work_email and rec.project_id.reviewer_id.parent_id == True else ''])
            project.append(rec.project_id.name)

        template = self.env.ref('kw_timesheets.kw_timesheet_task_not_assigned_mail_template')
        if template and email_to[0]:
            template.with_context(mail_for='Ticket', email_cc=','.join(set(email_cc)), manager = manager_name[0], date = f'{date.today()}', project_name = project[0],
                                  email_to = email_to[0], data = data).\
                send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")

        self.env.user.notify_success("Mail Sent Successfully.")
