
import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError

from odoo.addons.kw_dms.tools.security import NoSecurityUid

_logger = logging.getLogger(__name__)

class IrModelAccess(models.Model):
    
    _inherit = 'ir.model.access'
    
    @api.model
    @tools.ormcache_context('self._uid', 'model', 'mode', 'raise_exception', keys=('lang',))
    def check(self, model, mode='read', raise_exception=True):
        if isinstance(self.env.uid, NoSecurityUid):
            return True
        return super(IrModelAccess, self).check(model, mode=mode, raise_exception=raise_exception)