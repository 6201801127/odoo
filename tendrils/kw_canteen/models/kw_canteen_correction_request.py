from odoo import fields, models, api
from datetime import date


class CanteenCorrectionRequest(models.Model):
    _name = 'kw_canteen_correction_request'
    _description = 'Canteen Correction Apply'
    _rec_name = "employee_id"

    employee_id = fields.Many2one('hr.employee', string="Employee Name", required=True, tracking=False, readonly=True,
                                  default=lambda self: self.env.user.employee_ids[0:1])
    meal_date = fields.Date(string="Meal Date", required=True)
    reason = fields.Text(string="Reason")
    state = fields.Selection(string="Status",
                             selection=[('draft', 'Draft'), ('applied', 'Applied'), ('approved', 'Approved'),
                                        ('rejected', 'Rejected')], default='draft')
    canteen_meals_ids = fields.One2many("canteen_meal_correction_log", "meal_correction_id", "Canteen Meal Details")
    applied_date = fields.Date(string="Applied Date", default=date.today())
    approved_date = fields.Date(string="Approved Date")

    @api.onchange('meal_date')
    def meal_details_entries(self):
        data = self.env['meal_bio_log'].sudo().search([('recorded_date', '=', self.meal_date),
                                                       ('employee_id', '=', self.employee_id.id),
                                                       ('meal_type_id.meal_code', '=', 'R')])
        self.canteen_meals_ids = False
        self.canteen_meals_ids = [(0, 0, {
                                        'recorded_date': data.recorded_date,
                                        'meal_type_id': data.meal_type_id.id,
                                        'no_of_veg': data.no_of_veg,
                                        'no_of_non_veg': data.no_of_non_veg
                                  })]

    def apply_btn(self):
        self.state = 'applied'

    def approved_btn(self):
        self.state = 'approved'
        self.approved_date = date.today()
        query = f"delete from meal_bio_log where employee_id={self.employee_id.id} and recorded_date='{self.meal_date}'"
        if len(query) > 0:
            self._cr.execute(query)

    def rejected_btn(self):
        self.state = 'rejected'


class CorrectionLog(models.Model):
    _name = 'canteen_meal_correction_log'
    _description = 'Canteen Meal Correction Log'

    recorded_date = fields.Date(string="Date")
    meal_type_id = fields.Many2one("price_master_configuration",string="Meal Type")
    no_of_veg = fields.Integer(string="No Of Veg")
    no_of_non_veg = fields.Integer(string="No Of Non-Veg")
    meal_correction_id = fields.Many2one(comodel_name="kw_canteen_correction_request")
