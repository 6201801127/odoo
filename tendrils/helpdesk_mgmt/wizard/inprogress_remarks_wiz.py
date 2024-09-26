"""
Module: remarks_wizard

This module defines a wizard for managing remarks related to in-progress tasks.

Classes:
    RemarksWizard: A transient model representing a wizard for managing remarks.

"""
from odoo import models, fields, api
from ast import literal_eval


class RemarksWizard(models.TransientModel):
    """
    RemarksWizard class defines a transient model representing a wizard for managing remarks.

    Attributes:
        _name (str): The technical name of the model.
        _description (str): The description of the model.
        remarks_for_inprogress (fields.Text): A text field for storing remarks related to in-progress tasks.

    """
    _name = 'remarks.wizard'
    _description = 'Remarks Wizard'

    remarks_for_inprogress = fields.Text(string="Inprogress Remarks")
    stage_id = fields.Many2one('helpdesk.ticket.stage')

    def action_remarks(self):
        context = dict(self._context)
        intObj = self.env["helpdesk.ticket"]
        int_details = intObj.browse(context.get("active_id"))
        int_details.remarks_for_inprogress = self.remarks_for_inprogress
        stage = self.env['helpdesk.ticket.stage'].sudo().search([('code', '=', 'IP')], limit=1)
        int_details.stage_id = stage.id
        if stage:
            helpdesk_desk_users = self.env.user
            employee_email = int_details.users_id
            users = self.env['res.users'].sudo().search([])
            admin = users.filtered(lambda user: user.has_group('helpdesk_mgmt.group_helpdesk_manager') == True)
            template = self.env.ref('helpdesk_mgmt.email_template_for_inprogress_remarks')
            template1 = self.env.ref('helpdesk_mgmt.email_template_for_inprogress')
            from_emails = ','.join(helpdesk_desk_users.mapped('email'))
            to_email = ','.join(employee_email.mapped('email'))
            cc_emails = ','.join(admin.mapped('email'))
            name = ','.join(admin.mapped('name'))
            # res settings


            param = self.env['ir.config_parameter'].sudo()
            mail_group = literal_eval(param.get_param('helpdesk_mgmt.mail_to_user'))
            mail_to = []
            if mail_group:
                emp = self.env['hr.employee'].sudo().search([('id', 'in', mail_group)])
                mail_to += emp.filtered(lambda r: r.work_email != False).mapped('work_email')
            email_cc = ",".join(mail_to) or ''

            
            template.with_context(email_cc=email_cc, email_to=cc_emails, from_email=from_emails, names=int_details.users_id.name,
                                  remarks=self.remarks_for_inprogress, name_manager=name).send_mail(int_details.id,
                                                                                 notif_layout="kwantify_theme.csm_mail_notification_light")

            template1.with_context(email_to=to_email, from_email=from_emails, email_cc=cc_emails, names=int_details.users_id.name,
                                  remarks=self.remarks_for_inprogress, name_manager=name).send_mail(int_details.id,
                                                                          notif_layout="kwantify_theme.csm_mail_notification_light")
        return True
