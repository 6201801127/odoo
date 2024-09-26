from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class SpecialMealConfiguration(models.TransientModel):
    _name = 'special_meal_create_wizard'
    _description = 'special_meal_create_wizard'

    employee_ids = fields.Many2many('hr.employee', 'employee_special_meal_rel', string='Employee Name')

    # @api.multi
    def create_employee_for_special_meal(self):
        for employee in self.employee_ids:
            self.env['kw_canteen_regular_meal'].sudo().create({
                'employee_id': employee.id,
                'start_date': date.today() + relativedelta(days=1),
                'opt_monday': True,
                'opt_tuesday': True,
                'opt_wedday': True,
                'opt_thursday': True,
                'opt_friday': True,
                'opt_saturday': True,
                'opt_sunday': True,
                'sunday_meal_id': self.env.ref('kw_canteen.nonveg').id,
                'monday_meal_id': self.env.ref('kw_canteen.veg').id,
                'tuesday_meal_id': self.env.ref('kw_canteen.veg').id,
                'wedday_meal_id': self.env.ref('kw_canteen.nonveg').id,
                'thursday_meal_id': self.env.ref('kw_canteen.veg').id,
                'friday_meal_id': self.env.ref('kw_canteen.nonveg').id,
                'saturday_meal_id': self.env.ref('kw_canteen.veg').id,
                'is_special': True,
                'state': 'approved'

            })


class SpecialMealConfiguration(models.TransientModel):
    _name = 'special_meal_exclusion_update_wizard'
    _description = 'special_meal_exclusion_update_wizard'

    employee_ids = fields.Many2many('hr.employee', 'exclusion_special_meal_rel', string='Employee Name')
    exclusion_from = fields.Date('Exclusion From')
    exclusion_to = fields.Date('Exclusion To')

    def update_exclusion_for_special_meal(self):
        for employee in self.employee_ids:
            regular_record = self.env['kw_canteen_regular_meal'].sudo().search(
                [('state', '=', 'approved'), ('employee_id', '=', employee.id)])
            if regular_record:
                regular_record.write({
                    'apply_exclusion_boolean': True,
                    'close_meal_ids': [[0, 0, {
                        'start_date': self.exclusion_from,
                        'end_date': self.exclusion_to,
                    }]]

                })
