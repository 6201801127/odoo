import datetime
from datetime import timedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date , datetime



class KwGatePassAssign(models.TransientModel):
    _name = 'kw_gatepass_assign'
    _description = "Gatepass Assign Wizard"

    stock_id = fields.Many2one('stock.quant', string="Select Item", domain=[('active','=', True),('repair_damage','in',['repaired',False]),('process_location','=','store'),('quantity','>',0),('status','in',['Draft','Released'])])
    gatepass_type = fields.Selection([
        ('returnable', 'Returnable'),
        ('nonreturnable', 'Non-Returnable'),
    ], string='Gatepass Type',track_visibility='onchange',default='returnable')
    remark = fields.Text(string='Remark')
    type = fields.Selection([
        ('damage', 'Damage'),
        ('e_waste', 'E-Waste'),
        ('other', 'Other'),
    ], string='Type',track_visibility='onchange',default='damage')
   
    repair = fields.Selection([
        ('repair', 'Repair'),
        ('other', 'Other'),
    ], string='Repair/Damage',track_visibility='onchange')
    repair_date = fields.Date('Repair Date')
    repair_remark = fields.Text('Repair Remark')
    
    @api.onchange('gatepass_type')
    def onchange_gatepass_type(self):
        self.repair = ''
        self.type = ''
        self.remark=''
        if self.gatepass_type == 'returnable':
            self.repair = 'repair'
        elif self.gatepass_type == 'nonreturnable':
            self.type = 'damage'
    
    @api.multi
    def assign_gatepass_action(self):
        if self.gatepass_type == 'returnable':
            self.stock_id.write({
                'remark':self.remark,
                'repair_damage':self.repair,
                'gatepass_type':self.gatepass_type,
            })
            self.env['kw_product_repair_log'].sudo().create({
                'products':self.stock_id.product_id.id ,
                'repair_id': self.stock_id.id,
                'repaired_on': False,
                'send_to_repair':date.today(),
                'action_by':self.env.user.employee_ids.name,
            })
            template_id = self.env.ref('kw_inventory.product_gatepass_assign')
            template_id.with_context(product=self.stock_id.product_id.default_code,gatepass=self.gatepass_type,type=self.stock_id.repair_damage).send_mail(self.stock_id.id,notif_layout="kwantify_theme.csm_mail_notification_light")
            self.update_asset_logs()
        else:
            self.stock_id.write({
                'remark':self.remark,
                'repair_damage':self.type,
                'gatepass_type':self.gatepass_type,
            })
            self.env['kw_product_repair_log'].sudo().create({
                'products':self.stock_id.product_id.id ,
                'repair_id': self.stock_id.id,
                'repaired_on': False,
                'send_to_repair':date.today(),
                'action_by':self.env.user.employee_ids.name,
            })
            template_id = self.env.ref('kw_inventory.product_gatepass_assign')
            template_id.with_context(product=self.stock_id.product_id.default_code,gatepass=self.gatepass_type,type=self.type).send_mail(self.stock_id.id,notif_layout="kwantify_theme.csm_mail_notification_light")
            self.update_asset_logs()
    
    @api.multi
    def return_to_store_action(self):
        self.stock_id.write({
               'remark':self.repair_remark,
               'repair_date':self.repair_date,
               'gatepass_type': '',
               'repair_damage':'repaired',
            })
        self.env['kw_product_repair_log'].sudo().create({
                   'products':self.stock_id.product_id.id ,
                   'repair_id': self.stock_id.id,
                   'repaired_on': date.today(),
                   'send_to_repair':False,
                   'action_by':self.env.user.employee_ids.name,
                })
        template_id = self.env.ref('kw_inventory.return_returnable_gatepass')
        template_id.with_context(product=self.stock_id.product_id.default_code,type=self.stock_id.repair_damage,gatepass=self.gatepass_type).send_mail(self.stock_id.id,notif_layout="kwantify_theme.csm_mail_notification_light")
        self.update_asset_log()
        action_id = self.env.ref('kw_inventory.action_nonreturnable_stock').id
        return {
                    'type': 'ir.actions.act_url',
                    'tag': 'reload',
                    'url': f'/web#action={action_id}&model=stock.quant&view_type=list',
                    'target': 'self',
                }
    def update_asset_logs(self):
        asset_data = self.env['account.asset.asset'].sudo().search([('stock_quant_id','=',self.stock_id.id)])
        if asset_data:
            asset_data.repair_history_ids = [(0,0,{
                   'products':self.stock_id.product_id.id ,
                   'repair_id': self.stock_id.id,
                   'repaired_on': False,
                   'send_to_repair':date.today(),
                   'action_by':self.env.user.employee_ids.name,
                })]
    def update_asset_log(self):
        asset_data = self.env['account.asset.asset'].sudo().search([('stock_quant_id','=',self.stock_id.id)])
        if asset_data:
            asset_data.repair_history_ids = [(0,0,{
                   'products':self.stock_id.product_id.id ,
                   'repair_id': self.stock_id.id,
                   'repaired_on': date.today(),
                   'send_to_repair':False,
                   'action_by':self.env.user.employee_ids.name,
                })]
                    
    
    
    