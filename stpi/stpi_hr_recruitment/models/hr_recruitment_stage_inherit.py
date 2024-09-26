from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HrRecruitmentStageInherit(models.Model):
    _inherit = 'hr.recruitment.stage'
    _order = 'sequence asc'

    code = fields.Char(string="Code", required=True)

    @api.constrains('code')
    def validate_stage_code(self):
        data = self.search([('code','!=',False)]) - self
        for stage in self:
            for rec in data:
                if stage.code.lower() == rec.code.lower():
                    raise ValidationError('Stage Code must be Unique')

