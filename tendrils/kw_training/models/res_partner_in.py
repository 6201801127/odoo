from odoo import api, models


class ResPartnerTraining(models.Model):
    _inherit = "res.partner"

    @api.model
    def default_get(self, fields):
        res = super(ResPartnerTraining, self).default_get(fields)
        if "disable_cdefault" in self._context:
            res['customer'] = False
        return res
