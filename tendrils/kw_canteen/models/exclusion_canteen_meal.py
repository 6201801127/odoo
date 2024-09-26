from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ExclusionCanteenMeal(models.Model):
    _name = 'exclusion_canteen_meal'
    _description = 'exclusion_canteen_meal'

    reason = fields.Text(string="Reason")
    start_date = fields.Date(string="Starting Date")
    end_date = fields.Date(string="End Date")
    exclusion_type = fields.Selection([('temporary', 'Temporary'), ('permanent', 'Permanent')], default='temporary',
                                      required=True, string="Exclusion Type", tracking=True)
    regular_id = fields.Many2one(comodel_name="kw_canteen_regular_meal", string="Regular Meal ID", ondelete='cascade')

    @api.constrains('start_date', 'end_date')
    def exclusion_date_valid(self):
        if self.end_date:
            if (self.end_date - self.start_date).days + 1 < 3:
                raise ValidationError('Meal Exclusion Can Be Applied For Minimum 3 Days.')
