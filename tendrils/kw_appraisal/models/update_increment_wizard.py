from odoo import api, models, fields
from odoo.exceptions import UserError
from odoo import exceptions


class UpdateIncrementWizard(models.TransientModel):
    _name = 'update_increment_wizard'
    _description = 'Update Increment Wizard'

    def _get_default_appraisal(self):
        return self.env['hr.appraisal'].browse(self.env.context.get('active_ids'))

    appr = fields.Many2many('hr.appraisal', readonly=1, default=_get_default_appraisal)

    @api.multi
    def action_update_increment(self):
        for record in self:
            for rec in record.appr:
                if rec.update_increment == False:
                    rec.final_increment = (rec.employee_ctc * rec.increment_percentage) / 100
                    rec.update_increment = True
        self.env.user.notify_info(message='Increment Updated Successfully.')
