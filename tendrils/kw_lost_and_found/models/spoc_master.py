from odoo import models,fields,api

class LostAndFoundResponseLog(models.Model):
    _name = 'spoc_master_lnf'
    _description = 'Lost And Found SPOC Master'
    _rec_name = 'employee_id'

    office_location_id = fields.Many2one('kw_res_branch_unit',string="Office Location")
    employee_id = fields.Many2one('hr.employee',string="Employee")

    _sql_constraints = [
        ('office_location_id_unique', 'unique (office_location_id)', 'Already SPOC member has been assigned to this Office Location.'),
    ]