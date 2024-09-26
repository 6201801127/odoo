from odoo import SUPERUSER_ID
from odoo import api, fields, models
from odoo.exceptions import ValidationError

class ChangeStage(models.TransientModel):
    _name = 'change.stage'
    _description = 'Change Stage'

    @api.model
    def get_stage_domain(self):
        domain = []
        if self.env.user.id != SUPERUSER_ID:
            applicant = self.applicant_id.browse(self._context.get('active_id'))
            domain = ['&',('sequence','>',applicant.stage_id.sequence),'|',('job_id','=',False),('job_id','=',applicant.job_id.id)]
        return domain

    applicant_id = fields.Many2one('hr.applicant',string="Applicant", default=lambda self:self._context.get('active_id'))
    stage_id = fields.Many2one('hr.recruitment.stage', 'Stage', required=True,domain=get_stage_domain)
    stage_change_reason = fields.Text('Stage Change Reason',  required=True)

    @api.multi
    def action_state_change(self):
        # hr_applicants = self.env['hr.applicant'].browse(self.env.context.get('active_ids'))
        if self.env.user.id != SUPERUSER_ID:
            valid_stages = self.stage_id.search(['&',('sequence','>',self.applicant_id.stage_id.sequence),'|',('job_id','=',False),('job_id','=',applicant.job_id.id)])
            if self.stage_id not in valid_stages:
                raise ValidationError("Please select valid stage to move.")

        self.applicant_id.write({
            'stage_id': self.stage_id.id,
            'stage_change_reason': self.stage_change_reason
        })
