from odoo.exceptions import ValidationError
from odoo import models, fields, api


class KwAuctionItDeclaration(models.TransientModel):
    _name = 'kw_auction_it_declaration'
        
    ref_id = fields.Many2one('kw_auction', default= lambda self:self.env.context.get('current_id'))
    bid_amount = fields.Float(string="Bid Amount")
    check_declaration = fields.Boolean(string='Check Declaration', required=True)

    @api.constrains('bid_amount')
    def _check_bid_amount(self):
        if self.bid_amount <= self.ref_id.reserve_price:
            raise ValidationError("Bid amount must be greater than the initial auction price.")
        

    def proceed_bid_with_declaration(self):
        if self.check_declaration:
            active_id = self.env.context.get('active_id')
            model_data = self.env['kw_auction'].search([('id','=',active_id)])
            
            model_data.bid_ids.create({
            'ref_id':self.env.context.get('current_id'),
            'bidder_id':self.env.user.employee_ids.id,
            'bid_amount':self.bid_amount,
            'status':'interested',
            })
        else:
            raise ValidationError("Please agree to the terms and conditions before proceeding.")