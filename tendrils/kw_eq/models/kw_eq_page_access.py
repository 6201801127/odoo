from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class PbgMaster(models.Model):
    _name = 'kw_eq_page_access'
    _description = 'Access Configuration'



    page_name = fields.Selection([('software', 'Software'), ('consultancy', 'Consultancy'),('resource', 'Resource'),('ancillary', 'Ancillary'),('ancillary_opx', 'Ancillary/OPE'),('it_infra', 'IT Infra'),('estimate', 'Estimate'),('pbg', 'PBG'),('log','Action Log'),('cashflow','Cash Flow')],string="Page")
    authority_ids = fields.Many2many('kw_eq_master_data','page_access_rel','page_access_id','role_id',string='Authorities')


    @api.constrains('page_name')
    def get_client(self):
        for rec in self:
            if self.env['kw_eq_page_access'].sudo().search([('page_name','=',rec.page_name)])-self:
                raise ValidationError(f"{rec.page_name} configuration already exists")
            




