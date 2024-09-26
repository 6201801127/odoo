from odoo import models, fields, api


class hr_job(models.Model):
    _inherit = "hr.job"

    name = fields.Char(string=u'Job Position', size=100, required=True)
    kw_id = fields.Integer(string='Tendrils ID')

    @api.constrains('name')
    def check_name(self):
        exists_name = self.env['hr.job'].search(
            [('name', '=', self.name), ('id', '!=', self.id)])
        if exists_name:
            raise ValueError("This Job position \"" + self.name + "\" already exists.")
