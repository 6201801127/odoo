"""
Module Name: CrCancelWizard

Description: This module contains a transient model for managing cancellation remarks for change requests in Odoo.
"""

from odoo import api, fields, models, tools, _
from datetime import date, datetime
import calendar


class CrCancelWizard(models.TransientModel):
    """
    Model class for CR Cancel Wizard in Odoo.
    """
    _name = "cr_cancel_wizard"
    _description = "CR cancel Remark"

    remark = fields.Text()

    def cancel_btn(self):
        if self.env.context.get('current_id') and self._context.get('button') == 'Cancel':
            # cancel by user
            cr_cancel_data = self.env['kw_cr_management'].sudo().search(
                [('id', '=', self.env.context.get('current_id'))])
            if cr_cancel_data:
                cr_cancel_data.write({
                    'stage': 'Cancel',
                    'cr_cancelled_on': datetime.now(),
                    'cr_cancelled_by': self.env.user.employee_ids.id,
                    'cancel_cmt': self.remark
                })

                template = self.env.ref('change_request_management.kw_cr_management_cancel_email_template')

                project = self.env['kw_project_environment_management'].sudo().search(
                    [('project_id', '=', cr_cancel_data.project_id.id)])
                if project:
                    cc_emp = project.mapped('employee_ids.work_email')
                    cc_emp.extend(project.project_manager_id.mapped('work_email') if project.project_manager_id else [])
                    for rec in cr_cancel_data:
                        notifyemp = rec.notify_emp_ids.mapped('work_email')
                        pltform = rec.platform_id.mapped('name')
                        # print(notifyemp, "notifyemp-------------------------------------")
                        cc_emp.extend(notifyemp)
                    cc_emails = ",".join(set(cc_emp))
                if cr_cancel_data.environment_id.is_approval_required is True:
                    mail_to_list = project.project_manager_id.mapped('work_email')
                    if project.project_id.sbu_id.representative_id:
                        mail_to_list.extend([project.project_id.sbu_id.representative_id.work_email])
                    email_to = ','.join(list(set(mail_to_list)))
                else:
                    if project.server_admin:
                        email_to = ','.join(project.server_admin.mapped('work_email'))
                        cc_emails += ',' + 'kwcr@csm.tech'
                    else:
                        email_to = 'kwcr@csm.tech'

                user_name = self.env.user.employee_ids.display_name
                email_from = self.env.user.employee_ids.work_email

                template.with_context(cc_mail=cc_emails, email_to=email_to, subject="Cancelled", email_from=email_from,
                                      name="CR | Cancel Request Email", mail_for="Cancel", user_name=user_name,
                                      cr_type="CR", pltform=pltform).send_mail(cr_cancel_data.id,
                                                                               notif_layout="kwantify_theme.csm_mail_notification_light")

                self.env.user.notify_success("CR cancel Successfully.")


        elif self.env.context.get('current_id') and self._context.get('button') == 'Hold':
            # hold by SA
            cr_hold_data = self.env['kw_cr_management'].sudo().search(
                [('id', '=', self.env.context.get('current_id'))])
            if cr_hold_data:
                cr_hold_data.write({
                    'stage': 'Hold',
                    'cr_holded_on': datetime.now(),
                    'cr_holded_by': self.env.user.employee_ids.id,
                    'hold_cmt': self.remark
                })

                template = self.env.ref('change_request_management.kw_cr_management_cancel_email_template')

                project = self.env['kw_project_environment_management'].sudo().search(
                    [('project_id', '=', cr_hold_data.project_id.id)])
                if project:
                    cc_emp = project.mapped('employee_ids.work_email')
                    for rec in cr_hold_data:
                        notifyemp = rec.notify_emp_ids.mapped('work_email')
                        pltform = rec.platform_id.mapped('name')
                        # print(notifyemp, "notifyemp-hold------------------------------------")
                        cc_emp.extend(notifyemp)
                        cc_emp.extend(['kwcr@csm.tech'])
                    cc_emails = ",".join(set(cc_emp))
                user_name = self.env.user.employee_ids.display_name
                email_from = self.env.user.employee_ids.work_email
                email_to = cr_hold_data.create_uid.email if cr_hold_data.create_uid.email else False

                template.with_context(cc_mail=cc_emails, mail_for="Hold", email_from=email_from,email_to=email_to,
                                      name="CR | Hold Request Email", subject="Hold", user_name=user_name,
                                      pltform=pltform).send_mail(cr_hold_data.id,
                                                                 notif_layout="kwantify_theme.csm_mail_notification_light")

                self.env.user.notify_success("CR hold Successfully.")

        elif self.env.context.get('current_id') and self._context.get('button') == 'TL_Approve':
            cr_approve_data = self.env['kw_cr_management'].sudo().search([('id', '=', self.env.context.get('current_id'))])
            if cr_approve_data and cr_approve_data.cr_type == 'CR':
                project = self.env['kw_project_environment_management'].sudo().search([('project_id', '=', cr_approve_data.project_id.id)])
                if project.testing_lead_id and cr_approve_data.stage == 'Applied':
                    cr_approve_data.write({
                        'stage': 'Test Lead Approved',
                        'cr_approved_on': datetime.now(),
                        'cr_approved_by': self.env.user.employee_ids.id,
                        'approved_cmt': self.remark
                    })
                    cr_approve_data.is_testing_lead = False
                    template = self.env.ref('change_request_management.kw_cr_management_cancel_email_template')

                    project = self.env['kw_project_environment_management'].sudo().search(
                        [('project_id', '=', cr_approve_data.project_id.id)])
                    if project:
                        cc_emp = project.mapped('employee_ids.work_email')
                        for rec in cr_approve_data:
                            notifyemp = rec.notify_emp_ids.mapped('work_email')
                            pltform = rec.platform_id.mapped('name')
                            # print(notifyemp, "notifyemp-hold------------------------------------")
                            cc_emp.extend(notifyemp)
                            cc_emp.extend(cr_approve_data.cr_raised_by.mapped('work_email'))
                        cc_emails = ",".join(set(cc_emp))
                        email_to = project.project_manager_id.mapped('work_email')[0] if project.project_manager_id else ''
                        if project.project_id.sbu_id.representative_id:
                            if email_to:  
                                email_to += ','
                            email_to += project.project_id.sbu_id.representative_id.work_email
                        user_name = self.env.user.employee_ids.display_name
                        email_from = self.env.user.employee_ids.work_email
                        template.with_context(cc_mail=cc_emails, email_to=email_to, email_from=email_from, mail_for="Approve",
                                            name="CR | Approve Request Email", subject="Approved By TL", user_name=user_name,
                                            pltform=pltform).sudo().send_mail(cr_approve_data.id,
                                            notif_layout="kwantify_theme.csm_mail_notification_light")
            self.env.user.notify_success("CR Approved Successfully From TL.")


        elif self.env.context.get('current_id') and self._context.get('button') == 'Approve':
            cr_approve_data = self.env['kw_cr_management'].sudo().search(
                [('id', '=', self.env.context.get('current_id'))])
            if cr_approve_data and cr_approve_data.cr_type == 'CR':
                cr_approve_data.write({
                    'stage': 'Approve',
                    'cr_approved_on': datetime.now(),
                    'cr_approved_by': self.env.user.employee_ids.id,
                    'approved_cmt': self.remark
                })

                template = self.env.ref('change_request_management.kw_cr_management_cancel_email_template')

                project = self.env['kw_project_environment_management'].sudo().search(
                    [('project_id', '=', cr_approve_data.project_id.id)])
                if project:
                    cc_emp = project.mapped('employee_ids.work_email')
                    for rec in cr_approve_data:
                        notifyemp = rec.notify_emp_ids.mapped('work_email')
                        pltform = rec.platform_id.mapped('name')
                        # print(notifyemp,"notifyemp-hold------------------------------------")
                        cc_emp.extend(notifyemp)
                    cc_emails = ",".join(set(cc_emp))
                    if project.server_admin:
                        email_to = ','.join(project.mapped('server_admin.work_email'))
                        cc_emails += ',' + 'kwcr@csm.tech'
                    else:
                        email_to = 'kwcr@csm.tech'
                user_name = self.env.user.employee_ids.display_name
                email_from = self.env.user.employee_ids.work_email
                template.with_context(cc_mail=cc_emails, email_to=email_to, email_from=email_from, mail_for="Approve",
                                    name="CR | Approve Request Email", subject="Approved", user_name=user_name,
                                    pltform=pltform).sudo().send_mail(cr_approve_data.id,
                                                                        notif_layout="kwantify_theme.csm_mail_notification_light")
                self.env.user.notify_success("CR Approved Successfully.")

            elif cr_approve_data and cr_approve_data.cr_type == 'Service':
                cr_approve_data.write({
                    'stage': 'Approve',
                    'cr_approved_on': datetime.now(),
                    'cr_approved_by': self.env.user.employee_ids.id,
                    'approved_cmt': self.remark
                })
                template = self.env.ref('change_request_management.kw_cr_management_cancel_email_template')

                project = self.env['kw_project_environment_management'].sudo().search(
                    [('project_id', '=', cr_approve_data.project_id.id)])
                if project:
                    cc_emp = project.mapped('employee_ids.work_email')
                    for rec in cr_approve_data:
                        notifyemp = rec.notify_emp_ids.mapped('work_email')
                        pltform = rec.platform_id.mapped('name')
                        # print(notifyemp,"notifyemp-hold------------------------------------")
                        cc_emp.extend(notifyemp)
                    cc_emails = ",".join(set(cc_emp))
                    if project.server_admin:
                        email_to = ','.join(project.mapped('server_admin.work_email'))
                        cc_emails += ',' + 'kwcr@csm.tech'
                    else:
                        email_to = 'kwcr@csm.tech'
                user_name = self.env.user.employee_ids.display_name
                email_from = self.env.user.employee_ids.work_email
                template.with_context(cc_mail=cc_emails, email_to=email_to, email_from=email_from, mail_for="Approve",
                                      name="SR | Approved Request Email", subject="Approved", user_name=user_name,
                                      pltform=pltform).sudo().send_mail(cr_approve_data.id,
                                                                        notif_layout="kwantify_theme.csm_mail_notification_light")
                self.env.user.notify_success("SR Approved Successfully.")

        elif self.env.context.get('current_id') and self._context.get('button') == 'TL_Rejected':
            cr_reject_data = self.env['kw_cr_management'].sudo().search(
                [('id', '=', self.env.context.get('current_id'))])

            if cr_reject_data and cr_reject_data.cr_type == 'CR' and cr_reject_data.stage == 'Applied':
                cr_reject_data.write({
                    'stage': 'Reject',
                    'cr_rejected_on': datetime.now(),
                    'cr_rejected_by': self.env.user.employee_ids.id,
                    'reject_cmt': self.remark
                })
                template = self.env.ref('change_request_management.kw_cr_management_cancel_email_template')

                project = self.env['kw_project_environment_management'].sudo().search([('project_id', '=', cr_reject_data.project_id.id)])
                if project:
                    cc_emp = project.mapped('employee_ids.work_email')
                for rec in cr_reject_data:
                    notifyemp = rec.notify_emp_ids.mapped('work_email')
                    pltform = rec.platform_id.mapped('name')
                    cc_emp.extend(notifyemp)
                # cc_emp.extend(project.project_manager_id.mapped('work_email')) if project.project_manager_id else []
                cc_emp.extend(project.mapped('testing_lead_id.work_email')) if project.testing_lead_id else []
                    
                cc_emails = ",".join(set(cc_emp))
                user_name = self.env.user.employee_ids.display_name
                email_from = self.env.user.employee_ids.work_email
                email_to = cr_reject_data.cr_raised_by.mapped('work_email')[0]
                template.with_context(cc_mail=cc_emails, email_to=email_to, mail_for="Reject", email_from=email_from,
                                    name="CR | Reject Request Email", subject="Rejected", user_name=user_name,
                                    pltform=pltform).send_mail(cr_reject_data.id,
                                                                notif_layout="kwantify_theme.csm_mail_notification_light")

            self.env.user.notify_success("TL CR reject Successfully.")


        elif self.env.context.get('current_id') and self._context.get('button') == 'Rejected':
            cr_approve_data = self.env['kw_cr_management'].sudo().search(
                [('id', '=', self.env.context.get('current_id'))])
            if cr_approve_data and cr_approve_data.cr_type == 'CR':
                cr_approve_data.write({
                    'stage': 'Reject',
                    'cr_rejected_on': datetime.now(),
                    'cr_rejected_by': self.env.user.employee_ids.id,
                    'reject_cmt': self.remark
                })
                template = self.env.ref('change_request_management.kw_cr_management_cancel_email_template')

                project = self.env['kw_project_environment_management'].sudo().search(
                    [('project_id', '=', cr_approve_data.project_id.id)])
                if project:
                    cc_emp = project.mapped('employee_ids.work_email')
                    for rec in cr_approve_data:
                        notifyemp = rec.notify_emp_ids.mapped('work_email')
                        pltform = rec.platform_id.mapped('name')
                        # print(notifyemp,"notifyemp-hold------------------------------------")
                        cc_emp.extend(notifyemp)
                    cc_emp.extend(['kwcr@csm.tech'])
                    # cc_emp.extend(rec.cr_raised_by.mapped('work_email'))
                    email_to = rec.cr_raised_by.mapped('work_email')[0]
                    # cc_emp.extend(project.mapped('testing_lead_id.work_email')) if project.testing_lead_id else ''
                    # cc_emp.extend(project.mapped('database_admin_id.work_email')) if project.database_admin_id else ''
                    cc_emails = ",".join(set(cc_emp))
                user_name = self.env.user.employee_ids.display_name
                email_from = self.env.user.employee_ids.work_email
                # print(email_from, "email from ------------>>>>>>>>>>>>>>>>>>>>>>>>>")
                template.with_context(cc_mail=cc_emails, email_to=email_to, email_from=email_from, mail_for="PM_reject",
                                      name="CR | PM Rejected Email", subject="Rejected", user_name=user_name,
                                      pltform=pltform).sudo().send_mail(cr_approve_data.id,
                                                                        notif_layout="kwantify_theme.csm_mail_notification_light")

                self.env.user.notify_success("CR Rejected Successfully.")
            elif cr_approve_data and cr_approve_data.cr_type == 'Service':
                template = self.env.ref('change_request_management.kw_cr_management_cancel_email_template')
                cr_approve_data.write({
                    'stage': 'Reject',
                    'cr_rejected_on': datetime.now(),
                    'cr_rejected_by': self.env.user.employee_ids.id,
                    'reject_cmt': self.remark
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
                    cc_emails = ",".join(set(cc_emp))
                    email_to = cr_approve_data.cr_raised_by.work_email
                    if project.server_admin:
                        email_to = email_to
                        cc_emails += ',' + 'kwcr@csm.tech'
                    else:
                        email_to = 'kwcr@csm.tech'
                    user_name = self.env.user.employee_ids.display_name
                    email_from = self.env.user.employee_ids.work_email
                    template.with_context(cc_mail=cc_emails, email_to=email_to, email_from=email_from, mail_for="Reject",
                                            name="SR | Rejected Request Email", subject="Rejected", user_name=user_name,
                                            pltform=pltform).sudo().send_mail(cr_approve_data.id,
                                            notif_layout="kwantify_theme.csm_mail_notification_light")
                self.env.user.notify_success("SR Rejected Successfully.")
           