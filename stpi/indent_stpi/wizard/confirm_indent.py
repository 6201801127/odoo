from odoo import models,fields, api, _


class Confirmation(models.TransientModel):
    _name = "indent.confirm"
    _description = "Confirmation message before approve reject and procure"
    
    
    remark = fields.Text('Remark')
    item_line_id = fields.Many2one('indent.request.items',string='Line')
    type = fields.Selection([('apr', 'Aprrove'), ('reject', 'Reject'), ('procure', 'Procure')])
    is_2nd_level = fields.Boolean(default=False)
    
    
    @api.multi
    def button_confirm(self):
        self.item_line_id.remark = self.remark
        if self.type == 'apr':
            if self.is_2nd_level:
                self.item_line_id.button_level2_appove()
            else:
                self.item_line_id.button_item_approve()
        if self.type == 'reject':
            if self.is_2nd_level:
                self.item_line_id.button_level2_reject()
            else:
                self.item_line_id.button_item_reject()
        if self.type == 'procure':
            self.item_line_id.button_procure()
            