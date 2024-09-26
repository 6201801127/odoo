from odoo import models, api

class Category(models.Model):
    _inherit = "muk_dms.category"

    @api.model
    def create(self,vals):
        res = super(Category,self).create(vals)
        self.env.user.notify_success("Category Created Successfully.")
        return res

    @api.multi
    def write(self, vals):
        res = super(Category, self).write(vals)
        self.env.user.notify_success("Category Saved Successfully.")
        return res