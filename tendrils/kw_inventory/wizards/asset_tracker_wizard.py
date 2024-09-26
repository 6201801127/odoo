import datetime
from datetime import timedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date , datetime



class AssetTrackerWizard(models.TransientModel):
    _name = 'kw_asset_tracker_wiz'
    _description = "Asset Tracker Wiz"

    asset_id = fields.Many2one('account.asset.asset', string="Asset Id")
    asset_status = fields.Selection([
        ('in', 'In'),
        ('out', 'Out'),
    ], string='Asset Status',default='in')
    remark = fields.Text(string='Remark')
    
    @api.multi
    def in_out_gatepass_action(self):
        if self.asset_status == 'in':
            self.update_asset_tracker_log(datetime.now(),False)
        else:
            self.update_asset_tracker_log(False,datetime.now())
    
        action_id = self.env.ref('kw_inventory.asset_tracker_window').id
        return {
                    'type': 'ir.actions.act_url',
                    'tag': 'reload',
                    'url': f'/web#action={action_id}&model=account.asset.asset&view_type=list',
                    'target': 'self',
                }
    
    def update_asset_tracker_log(self,check_in=False,check_out=False):
        # print('asset log----')
        if self.asset_id:
            data={
                   'asset_id': self.asset_id.id,
                   'stock_id': self.asset_id.stock_quant_id.id,
                   'action_by':self.env.user.id,
                   'remark':self.remark,
                   'owner_id':self.asset_id.asset_owner_id.id,
                   'asset_status':self.asset_status,
                }
            if check_in:
                data['check_in']=check_in
            else:
                data['check_out']=check_out
            self.asset_id.asset_tracker_ids = [(0,0,data)]
                    
    
    
    