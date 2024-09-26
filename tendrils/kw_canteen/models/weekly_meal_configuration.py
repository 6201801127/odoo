from odoo import models, fields, api
from odoo.exceptions import ValidationError

class WeeklyMealConfiguration(models.Model):
    _name = 'weekly_meal_configuration'
    _description = 'Weekly Meal Configuration'

    weekdays = fields.Selection([('1', 'Monday'),
                                ('2', 'Tuesday'),
                                ('3', 'Wednesday'),
                                ('4', 'Thursday'),
                                ('5', 'Friday'),
                                ('6', 'Saturday'),
                                ('7', 'Sunday')], required=True, string="Weekdays")
    items = fields.Text(string="Items", required=True)

    @api.constrains('weekdays')
    def validate_weekdays(self):
        template_rec = self.env['weekly_meal_configuration'].search([]) - self
        filtered_rec = template_rec.filtered(lambda x: x.weekdays == self.weekdays)
        if len(filtered_rec) > 0:
            raise ValidationError("The code \"" + self.weekdays + "\" already exists.")