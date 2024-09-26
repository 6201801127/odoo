from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _get_default_country(self):
        country = self.env['res.country'].search([('code', '=', 'ET')], limit=1)
        # print('----------------------',country)
        return country.id

    city_id = fields.Many2one('res.state.city', 'City')
    sub_city_id = fields.Many2one('res.state.city', 'Sub City')
    woreda_id = fields.Many2one('res.location', 'Woreda')
    kabele_id = fields.Many2one('res.location', 'Kabele')
    employee_str = fields.Integer('Employee Strength')
    turnover = fields.Float('Turnover')
    year_of_establishment = fields.Selection([('2021', '2021'), ('2022', '2022')], string='Year of Establishment')
    country_id = fields.Many2one('res.country', 'Country' , default=lambda self: self._get_default_country())
