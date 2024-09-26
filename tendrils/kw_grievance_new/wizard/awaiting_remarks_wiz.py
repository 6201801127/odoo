from multiprocessing import managers
from odoo import models, fields, api
from ast import literal_eval


class AwaitingRemarksWizard(models.TransientModel):
    _name = 'grievance.awaiting.remarks.wizard'
    _description = 'Awaiting Remarks Wizard'

    remarks_for_awaiting = fields.Text(string="Awaiting Remarks")
    stage_id = fields.Many2one('grievance.ticket.stage')

    def action_awaiting_remarks(self):
        context = dict(self._context)
        intObj = self.env["grievance.ticket"]
        int_details = intObj.browse(context.get("active_id"))
        int_details.remarks_for_awaiting = self.remarks_for_awaiting
        stage = self.env['grievance.ticket.stage'].sudo().search([('code', '=', 'H')], limit=1)
        int_details.stage_id = stage.id
        if int_details.request == 'self':
            grievance_desk_users = self.env.user
            user1 = int_details.users_id.name
            user=self.env['hr.employee'].sudo().search([('user_id', '=', user1)], limit=1)
            users = self.env['res.users'].sudo().search([])
            admin = users.filtered(lambda user1: user1.has_group('kw_grievance_new.group_grievance_manager')==True)
            template = self.env.ref('kw_grievance_new.email_template_for_awaiting_grievance_remarks')
            # template1 = self.env.ref('kw_grievance_new.email_template_for_grievance_awaiting')
            from_emails = ','.join(grievance_desk_users.mapped('email'))
            to_email = ','.join(user.mapped('work_email'))
            cc_emails = ','.join(admin.mapped('email'))
            managers = ','.join(admin.mapped('name')) 
            # name = ','.join(admin.mapped('name'))
            param = self.env['ir.config_parameter'].sudo()
            mail_group = literal_eval(param.get_param('kw_grievance_new.mail_to_users'))
            mail_to = []
            if mail_group:
                emp = self.env['hr.employee'].sudo().search([('id', 'in', mail_group)])
                mail_to += emp.filtered(lambda r: r.work_email != False).mapped('work_email')
            email_cc = ",".join(mail_to) or ''

            template.with_context(email_to=to_email, email_cc=email_cc,from_email=from_emails, names=int_details.users_id.name,
                                remarks=self.remarks_for_awaiting, name_manager=managers).send_mail(int_details.id,
                                                                            notif_layout="kwantify_theme.csm_mail_notification_light")

        # template1.with_context(email_to=to_email, from_email=from_emails, names=int_details.users_id.name,
        #                           remarks=self.remarks_for_awaiting, name_manager=managers).send_mail(int_details.id,
        #                                                                   notif_layout="kwantify_theme.csm_mail_notification_light")
