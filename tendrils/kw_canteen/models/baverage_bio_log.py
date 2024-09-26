from odoo import models, fields, api
# from odoo.exceptions import ValidationError, AccessError

class BaverageBioLog(models.Model):
    _name="baverage_bio_log"
    _description = "Beverage Bio Log"
    _rec_name = "employee_id"
    _order="recorded_date desc"

    employee_id = fields.Many2one('hr.employee','Employee')
    emp_code = fields.Char(string="Emp. Code")
    beverage_type_id=fields.Many2one("kw_canteen_beverage_type",string="Beverages")
    emp_name = fields.Char(related="employee_id.name",string="Employee")
    emp_designation_id = fields.Many2one(related="employee_id.job_id",string="Designation",store=True)
    infra_unit_location_id = fields.Many2one('kw_res_branch_unit', string="Infra Unit Location",store=True)
    essl_id = fields.Integer('ESSL ID')
    recorded_date = fields.Datetime('Date')
    month = fields.Integer(string='Month')
    total_price = fields.Float('Total Price')
