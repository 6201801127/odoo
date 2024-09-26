from odoo import models,fields

class DispatchLetterTracking(models.Model):
    _name   = 'dispatch.letter.tracking'
    _description   = 'Tracking information of dispatch letters'
    _order         = 'action_time desc'

    dispatch_id       = fields.Many2one('dispatch.document', 'Dispatch Letter', required=True,ondelete="cascade")
    action_id         = fields.Many2one('dispatch.letter.stage', 'Action Type', required=True)
    
    action_date       = fields.Date("Date",required=True, default=fields.Date.context_today) #auto
    action_time       = fields.Datetime("Action Taken On", required=True,default=fields.Datetime.now) #auto
    action_by_user_id = fields.Many2one("res.users","Action By", required=True,default=lambda self: self.env.user) #auto
    
    version           = fields.Char("Version")
    new_version       = fields.Char("New Version")
    
    remark            = fields.Text("Remark")
    visible_user_ids  = fields.Many2many(comodel_name='res.users',string="Visible Users")

    old_content       = fields.Html("Old Content")
    new_content       = fields.Html("New Content")
