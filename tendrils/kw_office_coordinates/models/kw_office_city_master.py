from odoo import models, fields, api


class kw_office_coordinates(models.Model):
    _name = 'kw_city_master'
    _description = "City Master"
    _rec_name = 'name'

    name = fields.Char(string="City")
    latitude = fields.Char(string="Latitude")
    longitude = fields.Char(string="Longitude")
    country_id = fields.Many2one('res.country', ondelete='cascade', string="Country")
    state_id = fields.Many2one('res.country.state', ondelete='cascade', string="State")
    status = fields.Boolean("Status", default=True)

    # onchange of country change the state
    @api.onchange('country_id')
    def _change_state(self):
        country_id = self.country_id.id
        self.state_id = False
        return {'domain': {'state_id': [('country_id', '=', country_id)]}}