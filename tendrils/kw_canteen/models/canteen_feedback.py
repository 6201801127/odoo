import string
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date


class CanteenMealFeedBack(models.Model):
    _name = 'kw_canteen_meal_feedback'
    _description = 'Feedback on canteen Meal'
    _rec_name = "employee_id"

    employee_id = fields.Many2one('hr.employee', string="Employee Name", required=True, readonly=True,
                                  default=lambda self: self.env.user.employee_ids[0:1])
    department_id = fields.Char(string='Department', related='employee_id.department_id.name')
    desig_id = fields.Char(string='Designation', related='employee_id.job_id.name')
    feedback_date = fields.Date("Date", default=date.today())
    feedback = fields.Text('Feedback')
    infra_unit_location_id = fields.Many2one('kw_res_branch_unit', string="Infra Unit Location",
                                             related="employee_id.branch_unit_id", store=True)


class CanteenBeverageFeedBack(models.Model):
    _name = 'kw_canteen_beverage_feedback'
    _description = 'Feedback on canteen Beverage'
    _rec_name = "employee_id"

    employee_id = fields.Many2one('hr.employee', string="Employee Name", required=True, readonly=True,
                                  default=lambda self: self.env.user.employee_ids[0:1])
    department_id = fields.Char(string='Department', related='employee_id.department_id.name')
    desig_id = fields.Char(string='Designation', related='employee_id.job_id.name')
    feedback_date = fields.Date("Date", default=date.today())
    feedback = fields.Text('Feedback')
    infra_unit_location_id = fields.Many2one('kw_res_branch_unit', string="Infra Unit Location",
                                             related="employee_id.branch_unit_id", store=True)
