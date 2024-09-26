from odoo import models, api, _


class Confirmation(models.TransientModel):
    _name = "indent.confirm"
    _description = "Confirmation message before approve reject and procure"
    
    
    remark = fields.Text('Remark')
    item_line_id = fields.Many2one('indent.request.items',string='Line')
    type = fields.Selection([('apr', 'Aprrove'), ('reject', 'Reject'), ('procure', 'Procure')])
    
    
    @api.multi
    def button_confirm(self):
        if self.type == 'apr':
            self.item_line_id.button_item_approve()
        if self.type == 'reject':
            self.item_line_id.button_item_reject()
        if self.type == 'procure':
            self.item_line_id.button_procure()