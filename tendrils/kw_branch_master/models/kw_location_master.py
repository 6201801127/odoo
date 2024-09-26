from odoo import models, fields, api
from odoo.exceptions import ValidationError
import pytz


class kwLocationMaster(models.Model):
    _name = 'kw_location_master'
    _description = "Location Details of all CSM Branches"
    _order="name"

    name = fields.Char(string="Location", required=True)
    active = fields.Boolean(string="Active",default=True)
    kw_id = fields.Integer(string="Tendrils ID")
    country_id = fields.Many2one('res.country',string="Country Id")
    date_tz    = fields.Selection('_tz_get', string='Timezone')
    
                                # default=lambda self: self.env.user.tz or 'UTC')
    
    
    @api.model
    def _tz_get(self):
        return [(x, x) for x in pytz.all_timezones]

    @api.model
    def create(self, vals):
        self.env.user.notify_success(message='Location has been created successfully.')
        return super(kwLocationMaster, self).create(vals)

    @api.multi
    def write(self, vals):
        self.env.user.notify_info(message='Location has been updated successfully.')
        return super(kwLocationMaster, self).write(vals)

    @api.constrains('name', 'kw_id')
    def check_constraints(self):
        for rec in self:
            if self.env['kw_location_master'].sudo().search([('name','=',rec.name)])-self:
                raise ValidationError(f"{rec.name} already exists")
            if self.env['kw_location_master'].sudo().search([('kw_id','=',rec.kw_id)])-self:
                raise ValidationError(f"Tendrils ID {rec.kw_id} already exists")


    # @api.model
    # def create(self, vals):
    #     res = super(kwLocationMaster,self).create(vals)
    #     # new_id = self.env['kw_location_master'].sudo().search([],order="id desc",limit=1)
    #     new_rec = self.env['kw_emp_sync_log'].sudo().create({
    #         'model_id' : 'kw_location_master',
    #         'rec_id' : res.id,
    #         'code' : None,
    #         'action' : 'create',
    #         'status' : 0
    #     })
    #     self.env.user.notify_success(message='Location Added successfully.')
    #     return res

    # @api.multi
    # def write(self, vals):
    #     res = super(kwLocationMaster,self).write(vals)
    #     # new_id = self.env['kw_location_master'].sudo().search([],order="id desc",limit=1)
    #     new_rec = self.env['kw_emp_sync_log'].sudo().create({
    #         'model_id' : 'kw_location_master',
    #         'rec_id' : self.id,
    #         'code' : None,
    #         'action' : 'update',
    #         'status' : 0
    #     })
    #     self.env.user.notify_success(message='Location Updated successfully.')
    #     return res
