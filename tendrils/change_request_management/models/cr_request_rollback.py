"""
Module Name: CrRequestRollbackWizard

Description: This module contains a transient model for managing rollback remarks for change requests in Odoo.
"""
from odoo import api, fields, models, tools, _
from datetime import date, datetime
import calendar


class CrRequestRollbackWizard(models.TransientModel):
    """
    Model class for CR Request Rollback Wizard in Odoo.
    """
    _name = "cr_request_rollback_wizard"
    _description = "CR Request Rollback Remark"

    remark = fields.Text()

    def request_rollback_btn(self):
        if self.env.context.get('current_id'):
            cr_request_rollback_data = self.env['kw_cr_management'].sudo().search(
                [('id', '=', self.env.context.get('current_id'))])
            if cr_request_rollback_data:
                cr_request_rollback_data.write({
                    'stage': 'Request',
                    'request_for_rollback_id': self.env.user.employee_ids.id,
                    'request_for_rollback_cmt': self.remark,
                    'requesr_rollbacked_on': datetime.now()
                })

                template = self.env.ref('change_request_management.kw_cr_management_rollback_email_template')
                # users = self.env['res.users'].sudo().search([])
                # officers = users.filtered(lambda user: user.has_group('change_request_management.group_cr_officer'))
                # cc_emails = ",".join(officers.mapped('email'))

                project = self.env['kw_project_environment_management'].sudo().search(
                    [('project_id', '=', cr_request_rollback_data.project_id.id)])
                if project:
                    # print('in project  request_rollback--------------', project)
                    cc_emp = project.mapped('employee_ids.work_email')
                    for rec in cr_request_rollback_data:
                        notifyemp = rec.notify_emp_ids.mapped('work_email')
                        # print(notifyemp, "cr_request_rollback_data-hold------------------------------------")
                        cc_emp.extend(notifyemp)
                    cc_emails = ",".join(set(cc_emp))
                user_name = self.env.user.employee_ids.display_name

                template.with_context(cc_mail=cc_emails, user_name=user_name).send_mail(cr_request_rollback_data.id,
                                                                                        notif_layout="kwantify_theme.csm_mail_notification_light")

                self.env.user.notify_success("CR request_rollback Successfully.")
