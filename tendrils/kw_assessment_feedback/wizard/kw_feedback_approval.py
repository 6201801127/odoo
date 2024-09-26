from odoo import api, models,fields
from odoo.exceptions import UserError,ValidationError
from odoo import exceptions, _


class kw_feedback_approval_wizard(models.TransientModel):
    _name = 'kw_feedback_approval_wizard'
    _description = 'Approval Feedback wizard'

    def _get_default_assessment_feedback(self):
        datas = self.env['kw_feedback_details'].browse(self.env.context.get('active_ids'))
        return datas

    feedback = fields.Many2many('kw_feedback_details', readonly=1, default=_get_default_assessment_feedback)
    approval_user = fields.Many2one('hr.employee', string='Approval User', required=True, domain=lambda self: [("user_id.groups_id", "=", self.env.ref( "kw_assessment_feedback.group_assessment_feedback_approval_manager" ).id)])

    @api.multi
    def send_for_approval(self):
        for record in self.feedback:

            if record.feedback_status in ['3']:

                if record.assessment_tagging_id.assessment_type == 'probationary' and not record.prob_status:
                    raise ValidationError(f"Please update the final assessment status first for {record.assessee_id.name}.")

                record.write({
                    'feedback_status': '4',
                    'approval_user': self.approval_user.id
                })
            else:
                pass

        self.env.user.notify_success("Sent for approval successfully.")
        return {'type': 'ir.actions.act_window_close'}
