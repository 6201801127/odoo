from odoo import models, api, fields




class kw_institute_master(models.Model):
    _name = 'kw_institute_master'
    _rec_name = 'name'
    _description = 'Certified Professional Drive Institute Master'


    name = fields.Char(required=True,string='Institute name')
    active = fields.Boolean(string='Active',default=True)


