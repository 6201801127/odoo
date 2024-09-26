from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ApplicantRefuseReason(models.TransientModel):

    _name = 'applicant.refuse.reason'
    _description = 'Applicant Refuse Reason'

    applicant_id = fields.Many2one("hr.applicant",string="Applicant",required=True)
    reason = fields.Text("Reason")

    @api.multi
    def action_refuse_applicant(self):
        if (not self.reason) or (not self.reason.strip()):
            raise ValidationError("Please enter reason.")
        self.applicant_id.write({'active': False,'refuse_reason':self.reason})
        arrowstr = '<span aria-label="Changed" class="fa fa-long-arrow-right" role="img" title="Changed"></span>'
        self.applicant_id.message_post(body=f"<ul><li>Refuse Reason {arrowstr} {self.reason}</li></ul>")
        return {'type': 'ir.actions.act_window_close'}
        