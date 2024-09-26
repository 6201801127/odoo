"""
Module Name: CrUploadedWizard

Description: This module contains a transient model for managing uploaded remarks for change requests in Odoo.
"""
from odoo import api, fields, models, tools, _
from datetime import date, datetime
import calendar
from odoo.exceptions import ValidationError, UserError


class CrUploadedWizard(models.TransientModel):
    """
    Model class for CR Uploaded Wizard in Odoo.
    """
    _name = "cr_uploaded_wizard"
    _description = "CR Uploaded Remark"

    # def _get_project_data(self):
    #     project_data = []
    #     user_upload = self.env.user.employee_ids.id
    #     project_data = self.env['project.task']
    #     project_category_data = project_data.sudo().search([('project_id','=',self.project_id.id),('assigned_employee_id','=',user_upload),('prject_category_id.mapped_to','=','Project')])
    #     if project_category_data.exists():
    #         project_data.append(project_category_data.prject_category_id.id)
    #         print(project_data,"=======project_data=========")
    #     return [('id', '=', project_data)]

    remark = fields.Text()
    project_id = fields.Many2one('project.project', string="Project",
                                 default=lambda self: self.env.context.get('current_proj'), readonly=1)
    prject_category_id = fields.Many2one('kw_project_category_master', string='Category Name',
                                         domain=[('code', '=', 'PW')])
    parent_task_id = fields.Many2one('project.task', string="Activity")
    task_id = fields.Many2one('project.task', string="Task")
    time_spent = fields.Float(string="Time Spent", default=0.0)
    date_of = fields.Date(string="Date", default=date.today())

    @api.onchange('prject_category_id')
    def project_category_data(self):
        user_upload = self.env.user.employee_ids
        if not self.prject_category_id:
            domain = {}
            self.parent_task_id = False
            self.task_id = False
            task_domain = [('id', '=', 0)]
            parent_task_domain = [('id', '=', 0)]

        elif self.prject_category_id and self.prject_category_id.mapped_to == 'Project':
            tasks = self.env['project.task'].sudo().search(
                [('mapped_to', 'in', user_upload.department_id.ids),
                 ('project_id', '=', self.project_id.id),
                 ('prject_category_id', '=', self.prject_category_id.id),
                 ('assigned_employee_id.user_id', '=', self.env.user.id),
                 ('task_status', 'not in', ['Completed'])])
            task_domain = [('id', 'in', tasks.ids)]
            parent_task_domain = [('id', 'in', tasks.mapped('parent_id').ids)]
            domain = {'domain': {'parent_task_id': parent_task_domain, 'task_id': task_domain}}
        return domain

    def upload_btn(self):
        if self.env.context.get('current_id'):
            cr_upload_data = self.env['kw_cr_management'].sudo().search(
                [('id', '=', self.env.context.get('current_id'))])
            if cr_upload_data:
                cr_upload_data.write({
                    'stage': 'Uploaded',
                    'cr_uploaded_on': datetime.now(),
                    'uploaded_by': self.env.user.employee_ids.id,
                    'is_uploaded': True,
                    'uploaded_cmt': self.remark
                })
                # if cr_upload_data.cr_type == 'CR' or cr_upload_data.cr_type == 'Service' :
                if (self.prject_category_id
                        and self.parent_task_id
                        and self.task_id
                        and self.time_spent > 00.00
                        and self.date_of):
                    timesheet_record = self.env['account.analytic.line'].create(
                        {'employee_id': self.env.user.employee_ids.id,
                         'date': self.date_of,
                         'prject_category_id': self.prject_category_id.id,
                         'project_id': self.project_id.id,
                         'parent_task_id': self.parent_task_id.id,
                         'task_id': self.task_id.id,
                         'unit_amount': self.time_spent,
                         'name': self.remark})
                    cr_upload_data.write({'prject_category_id': self.prject_category_id.id,
                                          'parent_task_id': self.parent_task_id.id,
                                          'task_id': self.task_id.id,
                                          'time_spent': self.time_spent,
                                          'date_of': self.date_of})

                template = self.env.ref('change_request_management.kw_cr_management_uploaded_email_template')
                # users = self.env['res.users'].sudo().search([])
                # officers = users.filtered(lambda user: user.has_group('change_request_management.group_cr_officer'))
                # cc_emails = ",".join(officers.mapped('email'))
                user_name = self.env.user.employee_ids.display_name
                cc_emp = []
                project_env = self.env['kw_project_environment_management'].sudo().search(
                    [('project_id', '=', cr_upload_data.project_id.id)])
                if project_env:
                    mail_to_emails = project_env.mapped('employee_ids.work_email')
                    mail_to = ",".join(set(mail_to_emails))

                    cc_emp.extend(project_env.mapped('project_manager_id.work_email'))
                    for rec in cr_upload_data:
                        notifyemp = rec.notify_emp_ids.mapped('work_email')
                        pltform = rec.platform_id.mapped('name')
                        # cc_emp.extend(rec.cr_raised_by.mapped('work_email'))
                        cc_emp.extend(notifyemp)
                    cc_emp.extend(project_env.mapped('testing_lead_id.work_email')) if project_env.testing_lead_id else []
                    cc_emp.extend(project_env.mapped('database_admin_id.work_email')) if project_env.database_admin_id else []

                    mail_cc = ','.join(set(cc_emp)) + ',' + 'kwcr@csm.tech'

                    # user_name = cr_upload_data.env.user.employee_ids.name
                    # user_code = cr_upload_data.env.user.employee_ids.emp_code
                    # user_data = user_name + '(' + user_code + ')'

                    template.with_context(email_to=mail_to, mail_cc=mail_cc, user_name=user_name,
                                      pltform=pltform).send_mail(cr_upload_data.id,
                                                                 notif_layout="kwantify_theme.csm_mail_notification_light")

                self.env.user.notify_success("Uploaded Successfully.")


class CrPMApprovedWizard(models.TransientModel):
    """
    Model class for Change Request PM Approved Wizard in Odoo.
    """
    _name = "cr_pm_approved_wizard"
    _description = "CR PM Remark"

    @api.model
    def default_get(self, fields):
        res = super(CrPMApprovedWizard, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])
        res.update({
            'approved_cr_ids': active_ids,
        })
        return res

    approved_cr_ids = fields.Many2many(
        string='Details',
        comodel_name='kw_cr_management',
        relation='cr_approved_rel',
        column1='approved_id',
        column2='cr_id',
    )

    remarks = fields.Text(string="Remark")

    def pm_approver_btn(self):
        if self.approved_cr_ids:
            template = self.env.ref('change_request_management.kw_cr_management_cancel_email_template')
            for cr_approve_data in self.approved_cr_ids:
                if (cr_approve_data.cr_type == 'Service'
                    and cr_approve_data.stage == 'Applied'
                    and cr_approve_data.is_pm_approval_required == True
                    and cr_approve_data.stage not in ['Approve', 'Reject']):
                    if cr_approve_data:
                        cr_approve_data.write({
                            'stage': 'Approve',
                            'cr_approved_on': datetime.now(),
                            'cr_approved_by': self.env.user.employee_ids.id,
                            'approved_cmt': self.remarks
                        })
                elif (cr_approve_data.cr_type == 'CR'
                        and cr_approve_data.stage in ['Applied','Test Lead Approved']
                        and cr_approve_data.is_pm_approval_required == True
                        and (cr_approve_data.project_id.emp_id.id == self.env.user.employee_ids.id
                            or cr_approve_data.project_id.sbu_id.representative_id.id == self.env.user.employee_ids.id)
                        and cr_approve_data.stage not in ['Approve', 'Reject']):
                    if cr_approve_data:
                        cr_approve_data.write({
                            'stage': 'Approve',
                            'cr_approved_on': datetime.now(),
                            'cr_approved_by': self.env.user.employee_ids.id,
                            'approved_cmt': self.remarks
                        })
                    project = self.env['kw_project_environment_management'].sudo().search(
                        [('project_id', '=', cr_approve_data.project_id.id)])
                    if project:
                        cc_emp = project.mapped('employee_ids.work_email')
                        for rec in cr_approve_data:
                            notifyemp = rec.notify_emp_ids.mapped('work_email')
                            pltform = rec.platform_id.mapped('name')
                            # print(notifyemp,"notifyemp-hold------------------------------------")
                            cc_emp.extend(notifyemp)
                        cc_emp.extend(project.mapped('testing_lead_id.work_email')) if project.testing_lead_id else []
                        cc_emails = ",".join(set(cc_emp))
                        if project.server_admin:
                            email_to = ','.join(project.mapped('server_admin.work_email'))
                            cc_emails += ',' + 'kwcr@csm.tech'
                        else:
                            email_to = 'kwcr@csm.tech'
                    user_name = self.env.user.employee_ids.display_name
                    email_from = self.env.user.employee_ids.work_email

                    template.with_context(cc_mail=cc_emails, email_to=email_to, email_from=email_from,
                                          mail_for="Approve", name="CR | Approve Request Email", subject="Approved",
                                          user_name=user_name, pltform=pltform).send_mail(cr_approve_data.id,
                                                                                          notif_layout="kwantify_theme.csm_mail_notification_light")
                    self.env.user.notify_success("CR Approved Successfully.")

                elif (cr_approve_data.stage in ['Applied','Test Lead Approved']
                      and cr_approve_data.is_pm_approval_required == True
                      and cr_approve_data.project_id.emp_id.id != self.env.user.employee_ids.id
                      and cr_approve_data.stage not in ['Approve', 'Reject']):
                    raise ValidationError("You can not Approve the CR.")
                elif (cr_approve_data.stage == 'Applied'
                      and cr_approve_data.is_pm_approval_required == False
                      and cr_approve_data.project_id.emp_id.id == self.env.user.employee_ids.id
                      and cr_approve_data.stage not in ['Approve', 'Reject']):
                    raise ValidationError("No need to Approval.")
                elif (cr_approve_data.cr_type == 'Service'
                      and cr_approve_data.stage == 'Applied'
                      and cr_approve_data.stage not in ['Approve', 'Reject']):
                    raise ValidationError("No need to Approval.")
                elif (cr_approve_data.stage == 'Applied'
                      and cr_approve_data.is_pm_approval_required == False
                      and cr_approve_data.environment_id.is_approval_required == False
                      and cr_approve_data.stage not in ['Approve', 'Reject']):
                    raise ValidationError("No need to Approval.")
                else:
                    raise ValidationError("Action already been taken.")

    def pm_reject_btn(self):
        if self.approved_cr_ids:
            template = self.env.ref('change_request_management.kw_cr_management_cancel_email_template')
            for cr_approve_data in self.approved_cr_ids:
                if (cr_approve_data.cr_type == 'Service'
                    and cr_approve_data.stage == 'Applied'
                    and cr_approve_data.is_pm_approval_required == True
                    and cr_approve_data.stage not in ['Approve', 'Reject']):
                    if cr_approve_data:
                        cr_approve_data.write({
                            'stage': 'Reject',
                            'cr_rejected_on': datetime.now(),
                            'cr_rejected_by': self.env.user.employee_ids.id,
                            'reject_cmt': self.remarks
                        })

                elif (cr_approve_data.cr_type == 'CR'
                        and cr_approve_data.stage in ['Applied','Test Lead Approved']
                        and cr_approve_data.is_pm_approval_required == True
                        and (cr_approve_data.project_id.emp_id.id == self.env.user.employee_ids.id
                             or cr_approve_data.project_id.sbu_id.representative_id.id == self.env.user.employee_ids.id)
                        and cr_approve_data.stage not in ['Approve', 'Reject']):
                    if cr_approve_data:
                        cr_approve_data.write({
                            'stage': 'Reject',
                            'cr_rejected_on': datetime.now(),
                            'cr_rejected_by': self.env.user.employee_ids.id,
                            'reject_cmt': self.remarks
                        })

                        project = self.env['kw_project_environment_management'].sudo().search(
                            [('project_id', '=', cr_approve_data.project_id.id)])
                        if project:
                            cc_emp = project.mapped('employee_ids.work_email')
                            for rec in cr_approve_data:
                                notifyemp = rec.notify_emp_ids.mapped('work_email')
                                pltform = rec.platform_id.mapped('name')
                                # print(notifyemp,"notifyemp-hold------------------------------------")
                                cc_emp.extend(notifyemp)
                            # cc_emp.extend(rec.cr_raised_by.mapped('work_email'))
                            # cc_emp.extend(project.mapped('testing_lead_id.work_email')) if project.testing_lead_id else ''
                            # cc_emp.extend(project.mapped('database_admin_id.work_email')) if project.database_admin_id else ''
                            cc_emails = ",".join(set(cc_emp))
                            email_to = ','.join(cr_approve_data.mapped('cr_raised_by.work_email'))
                            cc_emails += ',' + 'kwcr@csm.tech'
                            # else:
                            #     email_to = 'kwcr@csm.tech'
                        user_name = self.env.user.employee_ids.display_name
                        email_from = self.env.user.employee_ids.work_email

                        template.with_context(cc_mail=cc_emails, email_to=email_to, email_from=email_from,
                                              mail_for="PM_reject", name="CR | PM Rejected Email", subject="Rejected",
                                              user_name=user_name, pltform=pltform).send_mail(cr_approve_data.id,
                                                                                              notif_layout="kwantify_theme.csm_mail_notification_light")

                    self.env.user.notify_success("CR Rejected Successfully.")
                elif (cr_approve_data.cr_type == 'CR'
                      and cr_approve_data.stage in ['Applied','Test Lead Approved']
                      and cr_approve_data.is_pm_approval_required == True
                      and cr_approve_data.project_id.emp_id.id != self.env.user.employee_ids.id
                      and cr_approve_data.stage not in ['Approve', 'Reject']):
                    raise ValidationError("You cannot Reject the CR.")
                elif (cr_approve_data.cr_type == 'CR'
                      and cr_approve_data.stage == 'Applied'
                      and cr_approve_data.is_pm_approval_required == False
                      and cr_approve_data.project_id.emp_id.id == self.env.user.employee_ids.id
                      and cr_approve_data.stage not in ['Approve', 'Reject']):
                    raise ValidationError("No need to Reject.")
                elif (cr_approve_data.cr_type == 'Service'
                      and cr_approve_data.stage == 'Applied'
                      and cr_approve_data.stage not in ['Approve', 'Reject']):
                    raise ValidationError("No need to Reject.")
                elif (cr_approve_data.stage == 'Applied'
                      and cr_approve_data.is_pm_approval_required == False
                      and cr_approve_data.environment_id.is_approval_required == False
                      and cr_approve_data.stage not in ['Approve', 'Reject']):
                    raise ValidationError("No need to Reject.")

                else:
                    raise ValidationError("Action already been taken.")
