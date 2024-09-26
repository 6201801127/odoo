from odoo import SUPERUSER_ID
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ApplicantBulkShift(models.TransientModel):

    _name = 'applicant.bulk.shift'
    _description = 'Applicant Bulk Shift'

    applicant_ids = fields.Many2many(comodel_name="hr.applicant",string="Applicants",default=lambda self:self.env['hr.applicant'].browse(self._context.get('active_ids')).ids,
    required=True)
    stage_id = fields.Many2one('hr.recruitment.stage', 'Stage', required=True)
    stage_change_reason = fields.Text('Stage Change Reason', required=True)

    @api.multi
    def change_applicant_stage(self):
        if self.applicant_ids:
            if self.env.user.id != SUPERUSER_ID:
                stage_sequence = self.stage_id.sequence
                backward_stage = self.applicant_ids.filtered(lambda r: r.stage_id.sequence > stage_sequence)
                if backward_stage:
                    applicant_str ="\n".join([f"{index}. {ap.name} -----> {ap.stage_id.name}  -----> {self.stage_id.name}" for index,ap in enumerate(self.applicant_ids,start=1)])
                    raise ValidationError(f"""Backward stage shift is not applicable for below applicants.\n
                                            {applicant_str}""")
            self.applicant_ids.write({
                "stage_id": self.stage_id.id,
                'stage_change_reason': self.stage_change_reason
            })
        else:
            raise ValidationError("Please select applicants.")