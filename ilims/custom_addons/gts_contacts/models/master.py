from odoo import api, fields, models, _


class ResStateCity(models.Model):
    _name = 'res.state.city'

    @api.model
    def _get_default_country(self):
        country = self.env['res.country'].search([('code','=','ET')], limit=1)
        return country.id

    name = fields.Char('City Name')
    state_id = fields.Many2one('res.country.state', 'Region')
    country_id = fields.Many2one('res.country', 'Country', default=lambda self: self._get_default_country())
    parent_id = fields.Many2one('res.state.city', 'Parent City')

    @api.onchange('state_id')
    def onchange_state_id(self):
        if self.state_id:
            self.country_id = self.state_id.country_id.id


class ResLocation(models.Model):
    _name = 'res.location'

    name = fields.Char('Name')
    location_type = fields.Selection([
        ('woreda', 'Woreda'),
        ('kabele', 'Kabele')
    ], status='Location Type')
    sub_city_id = fields.Many2one('res.state.city', 'Sub City')
    woreda_id = fields.Many2one('res.location', 'Parent Woreda')
