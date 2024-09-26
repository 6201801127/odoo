"""
Module Name: CrRollbackedWizard

Description: This module contains a transient model for managing rollback remarks for change requests in Odoo.

"""
from odoo import api, fields, models, tools, _
from datetime import date, datetime
import calendar


class CrRollbackedWizard(models.TransientModel):
    """
    Model class for CR Rollbacked Wizard in Odoo.
    """
    _name = "cr_rollbacked_wizard"
    _description = "CR Rollback Remark"

    remark = fields.Text()

    def rollback_btn(self):
        """
        Method to perform rollback action for the change request.
        """
        if self.env.context.get('current_id'):
            cr_rollback_data = self.env['kw_cr_management'].sudo().search(
                [('id', '=', self.env.context.get('current_id'))])
            if cr_rollback_data:
                cr_rollback_data.write({
                    'stage': 'Rollbacked',
                    'cr_rollbacked_on': datetime.now(),
                    'rollbacked_by': self.env.user.employee_ids.id,
                    'rollbacked_cmt': self.remark
                })

            template = self.env.ref('change_request_management.kw_cr_management_rollbacked_email_template')
            # users = self.env['res.users'].sudo().search([])
            # officers = users.filtered(lambda user: user.has_group('change_request_management.group_cr_officer'))
            # cc_emails = ",".join(officers.mapped('email'))
            user_name = self.env.user.employee_ids.display_name
            project_env = self.env['kw_project_environment_management'].sudo().search(
                [('project_id', '=', cr_rollback_data.project_id.id)])
            if project_env:
                mail_to_emails = project_env.mapped('employee_ids.work_email')
                for rec in cr_rollback_data:
                    notifyemp = rec.notify_emp_ids.mapped('work_email')
                    pltform = rec.platform_id.mapped('name')
                    mail_to_emails.extend(notifyemp)
                mail_to = ",".join(set(mail_to_emails))

            template.with_context(email_to=mail_to, user_name=user_name, pltform=pltform).send_mail(cr_rollback_data.id,
                                                                                                    notif_layout="kwantify_theme.csm_mail_notification_light")

            self.env.user.notify_success("CR Rollback Successfully.")
