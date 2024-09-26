from odoo import models, fields, api


class TourTravelDetails(models.Model):
    _name = "kw_tour_travel_details"
    _description = "Tour Travel Details"

    tour_id = fields.Many2one("kw_tour", "Tour", required=True, ondelete='cascade')
    arrangement = fields.Selection(string="Travel Arrangement", selection=[('Company', 'Company')],
                                   default="Company", required=True)
    travel_date = fields.Date(string="Travel Date", required=False)
    travel_mode_id = fields.Many2one('kw_tour_travel_mode', "Travel Mode", required=False)
    currency_id = fields.Many2one("res.currency", "Currency", required=False)
    cost = fields.Integer("Cost", required=False)
    document = fields.Binary("Upload Document")

    @api.model
    def default_get(self, fields):
        res = super(TourTravelDetails, self).default_get(fields)
        if self._context.get('default_tour_id', False):
            tour_state = self.env['kw_tour'].browse(self._context.get('default_tour_id')).state
            if tour_state == 'Approved':
                res['arrangement'] = 'Company'
        return res
