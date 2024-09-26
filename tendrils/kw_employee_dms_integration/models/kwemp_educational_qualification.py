from odoo import models, fields, api
from odoo.addons.kw_utility_tools import kw_validations


class kwemp_educational_details(models.Model):
    _name = 'kwemp_educational_qualification'

    """##integration with DMS"""
    _inherit = [
        'kwemp_educational_qualification',
        'kw_dms.hr_emp.integration',
    ]

    content_file = fields.Binary(required=True, string="Upload Document")

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            record_name = record.course_id.name
            result.append((record.id, record_name))
        return result

    @api.constrains('content_file')
    def validate_education_file(self):
        allowed_file_list = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf']
        for record in self:
            kw_validations.validate_file_mimetype(record.content_file, allowed_file_list)
            kw_validations.validate_file_size(record.content_file, 4)
