

from odoo import fields,models,api
from odoo.exceptions import ValidationError


class Cvscreening(models.TransientModel):
    _name = 'cvscreening_wizard'
    _description = "CV Screening"

    job_position = fields.Many2one('kw_hr_job_positions', string="Job Position",
                                   domain="[('enable_applicant_screening', '=', True),('is_published','=',True)]")
    applicants_ids = fields.Many2many('hr.applicant', 'active_applicants_rel', 'applicant_id', 'notify_id',
                                      string="Applicants")
    pannel_memb = fields.Many2one("hr.employee", string="Panel Member")

    @api.onchange('job_position')
    def _set_panelmember_applicants(self):
        for rec in self:
            applicant_list = []
            pan = []
            applicant = self.env['hr.applicant'].sudo().search([('job_position', '=', rec.job_position.id)])
            if applicant:
                for rec1 in applicant:
                    if rec1.id and not rec1.panel_member_id:
                        applicant_list.append(rec1.id)
                panel_member_rec = self.env['hr.employee'].sudo().search(
                    [('id', 'in', rec.job_position.panel_member.ids)])
                for data in panel_member_rec:
                    pan.append(data.id)
            return {'domain': {'applicants_ids': [('id', 'in', applicant_list)], 'pannel_memb': [('id', 'in', pan)]}}

    @api.multi
    def send_mail_to_panel_for_screen(self):
        for rec in self.applicants_ids:
            rec.panel_member_id = self.pannel_memb.id

        if self.pannel_memb:
            panel_member_mail = self.pannel_memb.work_email
            panel_member_name = self.pannel_memb.name
            applicant_data_list = self.applicants_ids
            view_id = self.env.ref('kw_recruitment.cv_sreening_actions_window').id
            status_id = self.env['hr.recruitment.stage'].sudo().search([('code', '=', 'SC')]).id
            for rec in applicant_data_list:
                rec.write({'stage_id': status_id})
            template_id = self.env.ref('kw_recruitment.for_cv_screening_mail_to_assign_panel_member')
            template_id.with_context(mail_to=panel_member_mail, name=panel_member_name, view_id=view_id,
                                     record_ids=applicant_data_list,job=rec.job_position.title,).send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light")
            self.env.user.notify_success("Assign Panel Member mail sent successfully.")
