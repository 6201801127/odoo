

import logging

from odoo import api, models, fields

from odoo.addons.kw_dms.tools.security import NoSecurityUid

_logger = logging.getLogger(__name__)

class Base(models.AbstractModel):
    
    _inherit = 'base'

    #----------------------------------------------------------
    # Helper
    #----------------------------------------------------------

    def _filter_access_rules(self, operation):
        if isinstance(self.env.uid, NoSecurityUid):
            return self
        return super(Base, self)._filter_access_rules(operation)
    
    @api.model
    def _apply_ir_rules(self, query, mode='read'):
        if isinstance(self.env.uid, NoSecurityUid):
            return None
        return super(Base, self)._apply_ir_rules(query, mode=mode)
    
    #----------------------------------------------------------
    # Function
    #----------------------------------------------------------

    @api.model
    def suspend_security(self, user=None):
        return self.sudo(user=NoSecurityUid(user or self.env.uid))
    
    @api.multi
    def check_access_rule(self, operation):
        if isinstance(self.env.uid, NoSecurityUid):
            return None
        return super(Base, self).check_access_rule(operation)
    
    @api.model
    def check_field_access_rights(self, operation, fields):    
        if isinstance(self.env.uid, NoSecurityUid):
            return fields or list(self._fields)
        return super(Base, self).check_field_access_rights(operation, fields)