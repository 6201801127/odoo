from odoo import models, fields, api
from datetime import datetime, date
from ast import literal_eval


class DoneRemarksWizard(models.TransientModel):
    _name = 'grievance.done.remarks.wizard'
    _description = 'Done Remarks Wizard'

    remarks_for_done = fields.Text(string="Close Remarks")
    word_limit = fields.Integer(string="Limit", default=100)
    stage_id = fields.Many2one('grievance.ticket.stage')

    @api.onchange('remarks_for_done')
    def _check_remarks_description(self):
        if self.remarks_for_done:
            self.word_limit = 500 - len(self.remarks_for_done)

    def action_done_remarks(self):
        for rec in self:
            context = dict(rec._context)
            intObj = rec.env["grievance.ticket"]
            int_details = intObj.browse(context.get("active_id"))
            int_details.remarks_for_done = rec.remarks_for_done
            stage = rec.env['grievance.ticket.stage'].sudo().search([('code', '=', 'D')], limit=1)
            int_details.stage_id = stage.id
            int_details.done_date = date.today()

            if int_details.request == 'self':
                grievance_desk_users = rec.env.user
                employee_email = int_details.users_id.name
                # print("+++++++++++++++++++++++++++++++++++++++",employee_email)
                user=self.env['hr.employee'].sudo().search([('user_id', '=', employee_email)], limit=1)           
                # print("+++++++++++++++++++++++++++++++++++++++",user.name)

                users = rec.env['res.users'].sudo().search([])
                admin = users.filtered(lambda user: user.has_group('kw_grievance_new.group_grievance_manager') == True)
                # res config user
                param = self.env['ir.config_parameter'].sudo()
                mail_group = literal_eval(param.get_param('kw_grievance_new.mail_to_users'))
                mail_to = []
                if mail_group:
                    emp = self.env['hr.employee'].sudo().search([('id', 'in', mail_group)])
                    mail_to += emp.filtered(lambda r: r.work_email != False).mapped('work_email')
                email = ",".join(mail_to) or ''
            
                template = self.env.ref('kw_grievance_new.create_email_template_for_whistleblowing_ticket')
                # email_cc = ','.join(manager.mapped('email'))
                # template = rec.env.ref('kw_grievance_new.email_template_for_done_remarks')
                template1 = rec.env.ref('kw_grievance_new.email_template_for_grievance_done')
                from_emails = ','.join(grievance_desk_users.mapped('email'))
                to_emails = ','.join(user.mapped('work_email'))
                cc_email = ','.join(admin.mapped('email'))
                name = ','.join(admin.mapped('name'))

                # param = self.env['ir.config_parameter'].sudo()
                # mail_group = literal_eval(param.get_param('kw_grievance_new.mail_to_user'))
                # mail_to = []
                # if mail_group:
                #     emp = self.env['hr.employee'].sudo().search([('id', 'in', mail_group)])
                #     mail_to += emp.filtered(lambda r: r.work_email != False).mapped('work_email')
                # email_cc = ",".join(mail_to) or ''
                # user=int_details.users_email
                # print('user===========',user)
                # template.with_context(email_to=to_emails, email_from=from_emails, email_cc=cc_email, names=int_details.users_id.name,
                #                       remarks=rec.remarks_for_done, name_manager=name).send_mail(int_details.id,
                #                                                               notif_layout="kwantify_theme.csm_mail_notification_light")

                template1.with_context(email_to=to_emails, email_from=from_emails,email_cc=email, names=int_details.users_id.name,
                                    remarks=rec.remarks_for_done, name_manager=name).send_mail(int_details.id,
                                                                            notif_layout="kwantify_theme.csm_mail_notification_light")
        return True
