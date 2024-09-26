from odoo import models,api

class ReimbursementDateRange(models.Model):
    _inherit='date.range'
    
    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if 'order_display' in self._context:
            order = self._context['order_display']
        return super(ReimbursementDateRange, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)