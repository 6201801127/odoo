from odoo import models, api, fields




class kw_course_master(models.Model):
    _name = 'kw_course_master'
    _rec_name = 'name'
    _description = 'Certified Professional Drive Course Master'


    name = fields.Char(required=True,string='Course name')
    institute_id = fields.Many2one('kw_institute_master',required=True,string='Institute name')
    active = fields.Boolean(string='Active',default=True)


