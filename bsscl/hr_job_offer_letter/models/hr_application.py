from odoo import api, fields, models, _


class Applicant(models.Model):
    _inherit = "hr.applicant"

    bool_stage=fields.Boolean("Boolean stage", compute="_compute_boolean_stage", default=True)

# (wagisha) regarding button hide according to stage
    def _compute_boolean_stage(self):
        model_id = self.env['hr.recruitment.stage'].sudo().search([('name', 'in', ['First Interview', 'Second Interview','Contract Proposal','Contract Signed'])])

        for rec in self:
            if rec.stage_id in model_id:
                rec.bool_stage = False
            else:
                rec.bool_stage = True

    # def _compute_boolean_stage(self):
    #  model_id = self.env['hr.recruitment.stage'].sudo().search([('name','=','Initial Qualification')])
    #  for rec in self:
    #     if rec.stage_id == model_id:
    #         rec.bool_stage = True
    #     else:
    #         rec.bool_stage = False

    def action_quotation_send(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        template_id = self.env['ir.model.data'].xmlid_to_res_id(
            'hr_job_offer_letter.email_template_applicant_job_offer', raise_if_not_found=False)
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)
        if template.lang:
            lang = template._render_lang(self.ids)[self.id]
        ctx = {
            'default_model': 'hr.applicant',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "mail.mail_notification_paynow",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True,
            'model_description': self.with_context(lang=lang),
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }
