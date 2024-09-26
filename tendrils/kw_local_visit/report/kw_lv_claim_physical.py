from odoo import models, fields, api, tools
from odoo.exceptions import ValidationError,UserError
from datetime import datetime, timedelta,date
from dateutil.relativedelta import relativedelta


class PhysicalKwLVClaimReport(models.Model):
    _name = 'kw_lv_claim_physical'
    _description =  "Local Visit Claim Physical Model"
    _rec_name = 'visit_id'


    def _compute_other_values(self):
        settlement_records = self.env['kw_lv_settlement'].sudo().search([])
        for record in self:
            filtered_settlement = settlement_records.filtered(lambda x: record.visit_id.id in x.lv_id.ids)
            record.sbu_id = record.emp_name.sbu_master_id
            record.date_of_settle = filtered_settlement.applied_date
            record.date_of_payment = filtered_settlement.payment_date


    visit_id = fields.Many2one('kw_lv_apply',string='Visit ID')
    emp_name = fields.Many2one('hr.employee',string='Employee Name') 
    emp_no = fields.Char(related='emp_name.emp_code')
    department = fields.Many2one('hr.department',related='emp_name.department_id',string='Department')
    division = fields.Char(related='emp_name.division.name',string='Division')
    wo_name = fields.Char("WO Name")
    wo_code = fields.Char("WO Code")
    ra_approval = fields.Char(string='RA Approval')
    visit_location = fields.Char("Location")
    visit_purpose = fields.Char("Purpose")
    section = fields.Many2one('hr.department','Section',related='visit_id.emp_name.practise')
    sbu_id = fields.Many2one('kw_sbu_master',string="SBU",compute='_compute_other_values')
    branch_location = fields.Many2one('kw_res_branch')
    branch_country = fields.Many2one('res.country')
    date_of_travel = fields.Date(string='Date of Travel')
    km_travel = fields.Float(string='KM Travel',related='visit_id.total_km')
    amt_claim = fields.Float(string='Amount',related='visit_id.price')
    visit_category = fields.Char(string='Visit Category',related='visit_id.visit_category.category_name')
    vehicle_type = fields.Char(string='Vehicle Type',related='visit_id.vehicle_type.vehicle_category_name')
    date_of_settle = fields.Date(string='Date of Settlement',compute='_compute_other_values')
    date_of_payment = fields.Date(string='Date of Payment',compute='_compute_other_values')
