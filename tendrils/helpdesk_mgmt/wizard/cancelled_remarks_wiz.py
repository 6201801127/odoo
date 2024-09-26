"""
Module for the CancelledRemarksWizard transient model.

This module imports necessary dependencies such as models, fields, and api from Odoo.
It defines the CancelledRemarksWizard class, which represents a transient model used for handling
remarks related to cancellations in the system.

"""
from odoo import models, fields, api
from ast import literal_eval


class CancelledRemarksWizard(models.TransientModel):
    """
    Transient model class representing the Cancelled Remarks Wizard.

    This class provides functionality for handling remarks related to cancellations through a wizard interface.
    """
    _name = 'cancelled.remarks.wizard'
    _description = 'Remarks Wizard'

    remarks_for_cancelled = fields.Text(string="Cancel Remarks")
    stage_id = fields.Many2one('helpdesk.ticket.stage')

    def action_cancelled_remarks(self):
        context = dict(self._context)
        intObj = self.env["helpdesk.ticket"]
        int_details = intObj.browse(context.get("active_id"))
        int_details.remarks_for_cancelled = self.remarks_for_cancelled
        stage = self.env['helpdesk.ticket.stage'].sudo().search([('code', '=', 'C')], limit=1)
        int_details.stage_id = stage.id
        helpdesk_desk_users = self.env.user
        employee_email = int_details.users_id
        users = self.env['res.users'].sudo().search([])
        admin = users.filtered(lambda user: user.has_group('helpdesk_mgmt.group_helpdesk_manager') == True)
        template = self.env.ref('helpdesk_mgmt.email_template_for_cancelled_remarks')
        template1 = self.env.ref('helpdesk_mgmt.email_template_for_cancelled')
        from_emails = ','.join(helpdesk_desk_users.mapped('email'))
        to_email = ','.join(employee_email.mapped('email'))
        cc_emails = ','.join(admin.mapped('email'))
        name = ','.join(admin.mapped('name'))
        param = self.env['ir.config_parameter'].sudo()
        mail_group = literal_eval(param.get_param('helpdesk_mgmt.mail_to_user'))
        mail_to = []
        if mail_group:
            emp = self.env['hr.employee'].sudo().search([('id', 'in', mail_group)])
            mail_to += emp.filtered(lambda r: r.work_email != False).mapped('work_email')
        email_cc = ",".join(mail_to) or ''
        template.with_context(email_cc=email_cc, email_to=cc_emails, email_from=from_emails, names=int_details.users_id.name,
                              remarks=self.remarks_for_cancelled, name_manager=name).send_mail(int_details.id,
                                                                            notif_layout="kwantify_theme.csm_mail_notification_light")

        template1.with_context(email_to=to_email, email_from=from_emails, names=int_details.users_id.name,
                                  remarks=self.remarks_for_cancelled, name_manager=name).send_mail(int_details.id,
                                                                          notif_layout="kwantify_theme.csm_mail_notification_light")
