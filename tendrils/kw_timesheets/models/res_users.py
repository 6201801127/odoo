from odoo import models,fields,api

class Users(models.Model):
    _inherit = "res.users"
    
    related_pm_ids = fields.Many2many("hr.employee","Related Project Managers",compute="_compute_related_pms")
    
    @api.multi
    def _compute_related_pms(self):
        for user in self:
            user.related_pm_ids = self.env['project.project'].search([('reviewer_id.user_id','=',user.id)]).mapped('emp_id')
            