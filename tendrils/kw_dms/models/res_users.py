import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError

from odoo.addons.kw_dms.tools.security import NoSecurityUid
from odoo.addons.kw_dms.tools.security import convert_security_uid

_logger = logging.getLogger(__name__)


class AccessUser(models.Model):
    _inherit = 'res.users'

    # ----------------------------------------------------------
    # Functions
    # ----------------------------------------------------------

    def browse(self, arg=None, *args, **kwargs):
        return super(AccessUser, self).browse(convert_security_uid(arg), *args, **kwargs)

    @classmethod
    def _browse(cls, ids, *args, **kwargs):
        access_ids = [convert_security_uid(id) for id in ids]
        return super(AccessUser, cls)._browse(access_ids, *args, **kwargs)
