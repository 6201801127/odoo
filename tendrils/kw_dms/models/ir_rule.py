

import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError

from odoo.addons.kw_dms.tools.security import NoSecurityUid

_logger = logging.getLogger(__name__)

class IrRule(models.Model):
    
    _inherit = 'ir.rule'
    
    @api.model
    @tools.ormcache('self._uid', 'model_name', 'mode')
    def _compute_domain(self, model_name, mode="read"):
        if isinstance(self.env.uid, NoSecurityUid):
            return None
        return super(IrRule, self)._compute_domain(model_name, mode=mode)