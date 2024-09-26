from odoo import models, api, fields,_

class DepartmentId(models.Model):
    _inherit = "hr.department"

    stpi_doc_id = fields.Char(string='ID')


class JobId(models.Model):
    _inherit = "hr.job"

    status_level = fields.Integer(string='Level')