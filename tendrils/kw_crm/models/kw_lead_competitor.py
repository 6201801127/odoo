# -*- coding: utf-8 -*-

from odoo import models, fields, api

class kw_lead_competitor(models.Model):
    _name       = 'kw_lead_competitor'
    _description= 'Lead competitor Form'


    name=  fields.Char(string="Name of the Competitor" ,required=True)
    full_name=  fields.Char(string="Full Name of the Competitor")
    yoi = fields.Date(string='Year Of Establishment')
    qc= fields.Char(string="Quality Certificate")
    image = fields.Binary("Image", attachment=True,
        help="This field holds the image used as avatar for this contact, limited to 1024x1024px",)
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    email = fields.Char("Email")
    phone = fields.Char("Phone")
    mobile = fields.Char("Mobile")
    website = fields.Char("Company URL")
    average_turnover = fields.Char(string="Average Finicial Turnover")
    active = fields.Boolean('Status', default=True)
    is_competitor = fields.Boolean(string='Is a competitor', default=True)     
