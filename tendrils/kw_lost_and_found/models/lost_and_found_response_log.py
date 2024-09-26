from odoo import models,fields,api

class LostAndFoundResponseLog(models.Model):
    _name = 'lost_and_found_response_log'
    _description = 'Lost And Found Response Log'

    lf_id = fields.Many2one('kw_lost_and_found',string="Lost & Found")
    employee_id = fields.Many2one('hr.employee',string="Employee")
    response = fields.Text('Response')