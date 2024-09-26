from odoo import models, fields

class DepartmentId(models.Model):
    _inherit = "hr.department"

    stpi_doc_id = fields.Char(string='Code')

class JobId(models.Model):
    _inherit = "hr.job"

    status_level = fields.Integer(string='Level')