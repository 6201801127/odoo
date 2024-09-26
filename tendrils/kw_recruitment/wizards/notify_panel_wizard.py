from odoo import fields,models,api
from odoo.exceptions import ValidationError


class notifywizard(models.TransientModel):
    _name = 'notify_wizard'
    _description = 'Notify Wizard'
    
    def _default_employee(self):
        if self._context.get('active_applicant_id') and not self._context.get('hide_panel'):
            applicant_id = self.env['hr.applicant'].browse(self._context['active_applicant_id'])
        elif self._context.get('value'):
            applicant_id = self.env['kw_notify_to_panel'].browse(self._context.get('value')).mapped('applicant_id')
        return applicant_id
    
    def _default_panel(self):
        if self._context.get('active_applicant_id') and not self._context.get('hide_panel'):
            applicant_id = self.env['hr.applicant'].browse(self._context['active_applicant_id'])
            panel_member=applicant_id.filtered(lambda x : not x.panel_member_id)
        elif self._context.get('value'):
            applicant_id = self.env['kw_notify_to_panel'].browse(self._context.get('value')).mapped('applicant_id')
            panel_member=applicant_id.filtered(lambda x : not x.panel_member_id)
        return panel_member

    applicant_ids = fields.Many2many('hr.applicant', 'active_applicant_rel', 'applicant_id', 'notify_id',
                                     string="Applicants", default=_default_employee)
    hide_panel = fields.Boolean(string='Hide Panel Member', compute='_hide_panel_data')
    pending_panel_member_ids = fields.Many2many('hr.applicant', 'pending_panel_rel', 'applicant_id', 'notify_id',
                                                string="Pending Panel Member", default=_default_panel)

    @api.depends('applicant_ids')
    def _hide_panel_data(self):
        for record in self:
            # if self._context.get('hide_notify_to_panel'):
            #     record.hide_panel = True
            # else:
            record.hide_panel = True
    
    @api.multi
    def update_stage(self):
        applicant_ids = self.applicant_ids.filtered(lambda x : x.panel_member_id)
        if applicant_ids:
            panel_member_list = applicant_ids.mapped('panel_member_id')
            status_id = self.env['hr.recruitment.stage'].sudo().search([('code', '=', 'SC')]).id
            for rec in applicant_ids:
                rec.write({'stage_id': status_id})
                
            for record in panel_member_list:
                panel_applicants = applicant_ids.filtered(lambda r: r.panel_member_id.id == record.id)
                mails = record.mapped('work_email')[0] if record.mapped('work_email') else ''
                panel_name=record.mapped('name')[0] if record.mapped('name') else ''
                view_id = self.env.ref('kw_recruitment.sreening_actions_window').id
                template_id = self.env.ref('kw_recruitment.for_screening_mail_to_panel_member')
                applicant_name = panel_applicants.mapped('partner_name')[0] if panel_applicants.mapped('partner_name') else ''
                template_id.with_context(names=panel_name, emails=mails, view_id=view_id, record_ids=panel_applicants,
                                         applicant_name=applicant_name).send_mail(status_id,
                                                                                  notif_layout="kwantify_theme.csm_mail_notification_light")
                self.env.user.notify_success("Applicant details mail sent successfully.")
        else:
            raise ValidationError("Please Add Panel Members of the selected applicants.")
