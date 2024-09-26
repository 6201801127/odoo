
import logging

from odoo import models, api, SUPERUSER_ID

from odoo.addons.kw_dms_utils.tools import patch
from odoo.addons.kw_dms.tools import security

_logger = logging.getLogger(__name__)

@api.model
@patch.monkey_patch(api.Environment)
def __call__(self, cr=None, user=None, context=None):
    env = __call__.super(self, cr, user, context)
    if user and isinstance(user, security.NoSecurityUid):
        env.uid = user
        return env
    return env