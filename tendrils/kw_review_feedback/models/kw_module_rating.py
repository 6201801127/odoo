
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class kw_module_rating(models.Model):
    _name = "kw_module_rating"
    _description = "Module Rating"
    _rec_name = 'module_id'

    module_id = fields.Many2one("kw_choose_module",string="Module Name",domain="[('active_module','=',True)]", ondelete='restrict')
    ratings = fields.Selection([('0','0'),('1','1'),('2','2'),('3','3'),('4','4'),('5','5')], string="Ratings" )

# No duplicate ratings against module
    @api.constrains('module_id')
    def restric_user_rating(self):  
        rec = self.env['kw_module_rating'].sudo().search([])-self
        for m_rec in rec:
            if m_rec.module_id.id == self.module_id.id and m_rec.create_uid.id == self._uid:
                raise ValidationError('You have already given ratings for this module')
        