from odoo import models, fields, api

class kw_handbook_types(models.Model):
    _name        = 'kw_handbook_type'
    _description = 'A model to manage employee handbook type'
    _rec_name    = 'name'
    _order = 'sequence'
    
    name = fields.Char('Name', required=True)
    code         = fields.Char(string="Code", required=True)
    sequence = fields.Integer(string="Sequence", default=10, required=True, help="Gives the sequence order of types.")

    @api.model
    def create(self, vals):
        record = super(kw_handbook_types, self).create(vals)
        if record:
            self.env.user.notify_success(message='Handbook Type created successfully.')
        else:
            self.env.user.notify_danger(message='Handbook Type creation failed.')
        return record

    
    def write(self, vals):
        res = super(kw_handbook_types, self).write(vals)
        if res:
            self.env.user.notify_success(message='Handbook Type updated successfully.')
        else:
            self.env.user.notify_danger(message='Handbook Type update failed.')
        return res