"""
Module for the DoneRemarksWizard transient model.

This module imports necessary dependencies such as models, fields, and api from Odoo.
It defines the DoneRemarksWizard class, which represents a transient model used for handling
remarks related to completed operations in the system.
"""
from odoo import models, fields, api
from datetime import datetime, date
from ast import literal_eval


class DoneRemarksWizard(models.TransientModel):
    """
    Transient model class representing the Done Remarks Wizard.

    This class provides functionality for handling remarks related to completed operations through a wizard interface.
    """
    _name = 'done.remarks.wizard'
    _description = 'Done Remarks Wizard'

    remarks_for_done = fields.Text(string="Remarks")
    stage_id = fields.Many2one('helpdesk.ticket.stage')

    def action_done_remarks(self):
        """
        Perform an action related to recording remarks for completed operations.

        This method is responsible for handling the action related to recording remarks
        for completed operations. It iterates over the records in the wizard instance,
        retrieves the necessary context, and interacts with the 'helpdesk.ticket' model
        through the Odoo environment.

        Returns:
            None
        """
        for rec in self:
            context = dict(rec._context)
            intObj = rec.env["helpdesk.ticket"]
            int_details = intObj.browse(context.get("active_id"))
            int_details.remarks_for_done = rec.remarks_for_done
            stage = rec.env['helpdesk.ticket.stage'].sudo().search([('code', '=', 'D')], limit=1)
            int_details.stage_id = stage.id
            int_details.done_date = date.today()

            helpdesk_desk_users = rec.env.user
            employee_email = int_details.users_id
            users = rec.env['res.users'].sudo().search([])
            admin = users.filtered(lambda user: user.has_group('helpdesk_mgmt.group_helpdesk_manager') == True)
            # template = rec.env.ref('helpdesk_mgmt.email_template_for_done_remarks')
            template1 = rec.env.ref('helpdesk_mgmt.email_template_for_done')
            from_emails = ','.join(helpdesk_desk_users.mapped('email'))
            to_emails = ','.join(employee_email.mapped('email'))
            cc_email = ','.join(admin.mapped('email'))
            name = ','.join(admin.mapped('name'))

            param = self.env['ir.config_parameter'].sudo()
            mail_group = literal_eval(param.get_param('helpdesk_mgmt.mail_to_user'))
            mail_to = []
            if mail_group:
                emp = self.env['hr.employee'].sudo().search([('id', 'in', mail_group)])
                mail_to += emp.filtered(lambda r: r.work_email != False).mapped('work_email')
            email_cc = ",".join(mail_to) or ''
            # user=int_details.users_email
            # print('user===========',user)
            # template.with_context(email_to=to_emails, email_from=from_emails, email_cc=cc_email, names=int_details.users_id.name,
            #                       remarks=rec.remarks_for_done, name_manager=name).send_mail(int_details.id,
            #                                                               notif_layout="kwantify_theme.csm_mail_notification_light")

            template1.with_context(email_to=to_emails, email_from=from_emails, email_cc=email_cc, names=int_details.users_id.name,
                                  remarks=rec.remarks_for_done, name_manager=name).send_mail(int_details.id,
                                                                          notif_layout="kwantify_theme.csm_mail_notification_light")
        return True
