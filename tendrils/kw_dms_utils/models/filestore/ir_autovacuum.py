
import time
import logging
import datetime
import dateutil

from odoo import _
from odoo import models, api, fields
from odoo.tools.safe_eval import safe_eval

from odoo.addons.kw_dms_utils.fields import file

_logger = logging.getLogger(__name__)

class AutoVacuum(models.AbstractModel):
    
    _inherit = 'ir.autovacuum'
    
    @api.model
    def power_on(self, *args, **kwargs):
        res = super(AutoVacuum, self).power_on(*args, **kwargs)
        file.clean_store(self.env.cr.dbname, self.env)
        return res