from odoo import models, api

class Tag(models.Model):
    _inherit = "muk_dms.tag"

    @api.model
    def create(self,vals):
        res = super(Tag,self).create(vals)
        self.env.user.notify_success("Tag Created Successfully.")
        return res

    @api.multi
    def write(self, vals):
        res = super(Tag, self).write(vals)
        self.env.user.notify_success("Tag Saved Successfully.")
        return res