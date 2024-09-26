"""
Module for the AwaitingRemarksWizard transient model.

This module imports necessary dependencies such as models and fields from Odoo.
It defines the AwaitingRemarksWizard class, which represents a transient model used for handling
awaiting remarks functionality in the system.

Example:
    This module is utilized within the Odoo environment to manage awaiting remarks through a wizard interface.

Usage:
    Developers can use instances of the AwaitingRemarksWizard class to handle awaiting remarks
    functionality within the Odoo system.
"""
from multiprocessing import managers
from odoo import models, fields, api
from ast import literal_eval


class AwaitingRemarksWizard(models.TransientModel):
    """
    Transient model class representing the Awaiting Remarks Wizard.

    This class provides functionality for handling awaiting remarks through a wizard interface.
    """
    _name = 'awaiting.remarks.wizard'
    _description = 'Awaiting Remarks Wizard'

    remarks_for_awaiting = fields.Text(string="Awaiting Remarks")
    stage_id = fields.Many2one('helpdesk.ticket.stage')

    def action_awaiting_remarks(self):
        context = dict(self._context)
        intObj = self.env["helpdesk.ticket"]
        int_details = intObj.browse(context.get("active_id"))
        int_details.remarks_for_awaiting = self.remarks_for_awaiting
        stage = self.env['helpdesk.ticket.stage'].sudo().search([('code', '=', 'H')], limit=1)
        int_details.stage_id = stage.id
        helpdesk_desk_users = self.env.user
        user = int_details.users_id
        users = self.env['res.users'].sudo().search([])
        admin = users.filtered(lambda user: user.has_group('helpdesk_mgmt.group_helpdesk_manager')==True) 
        template = self.env.ref('helpdesk_mgmt.email_template_for_awaiting_remarks')
        template1 = self.env.ref('helpdesk_mgmt.email_template_for_awaiting')
        from_emails = ','.join(helpdesk_desk_users.mapped('email'))
        to_email = ','.join(user.mapped('email'))
        cc_emails = ','.join(admin.mapped('email'))
        managers = ','.join(admin.mapped('name')) 
        # name = ','.join(admin.mapped('name'))
        param = self.env['ir.config_parameter'].sudo()
        mail_group = literal_eval(param.get_param('helpdesk_mgmt.mail_to_user'))
        mail_to = []
        if mail_group:
            emp = self.env['hr.employee'].sudo().search([('id', 'in', mail_group)])
            mail_to += emp.filtered(lambda r: r.work_email != False).mapped('work_email')
        email_cc = ",".join(mail_to) or ''

        template.with_context(email_to=cc_emails, email_cc=email_cc, from_email=from_emails, names=int_details.users_id.name,
                              remarks=self.remarks_for_awaiting, name_manager=managers).send_mail(int_details.id,
                                                                           notif_layout="kwantify_theme.csm_mail_notification_light")

        template1.with_context(email_to=to_email, from_email=from_emails, names=int_details.users_id.name,
                                  remarks=self.remarks_for_awaiting, name_manager=managers).send_mail(int_details.id,
                                                                          notif_layout="kwantify_theme.csm_mail_notification_light")
