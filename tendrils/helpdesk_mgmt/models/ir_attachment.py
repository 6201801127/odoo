"""
Module for Custom Attachment Model.

This module contains the model definition for extending attachments in Odoo.

"""
from odoo import models, api


class Attachment(models.Model):
    """
    Model for Custom Attachment.

    This class extends the 'ir.attachment' model to provide additional functionality.

    Attributes:
        _inherit (str): The name of the model being inherited ('ir.attachment').
    """
    _inherit = 'ir.attachment'

    @api.model
    def check(self, mode, values=None):
        group_portal = self.env.ref('base.group_portal')
        if (
            values and mode == 'write' and
            values.get('res_model') == 'helpdesk.ticket' and
            group_portal.id in self.env.user.groups_id.ids
        ):
            # when portal user is writing a file attached to a ticket,
            # skip access check to ticket, allowing to write
            # (needed for example by website_portal_comment_attachment)
            del values['res_model']
        return super(Attachment, self).check(mode, values)
