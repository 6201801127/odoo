# import re
from odoo import api, fields, models, tools
from odoo.exceptions import UserError, ValidationError
from datetime import date,datetime

class kwAnnualMaintenanceCost(models.Model):
    _name = "annual_maintenance_costs"
    _description = "annual_maintenance_costs"

    asset_id = fields.Many2one('account.asset.asset', string='Assets ID')
    name = fields.Char(string='AMC name')
    type = fields.Char(string='AMC Type')
    no_of_service = fields.Integer(string='No of Service/Visits')
    completed_service = fields.Integer(string='Completed Servcie/Visits')
    actual_start_date = fields.Datetime(string='Actual Start Date')
    actual_end_date = fields.Datetime(string='Actual End Date')
    from_date = fields.Date(string='From Date(AMC)')
    to_date = fields.Date(string='To Date(AMC)')
    status = fields.Selection([('active', 'Active'), ('inactive', 'Inactive')])


class kw_asset(models.Model):
    _inherit = "account.asset.asset"
    _rec_name = 'name'
    _description = "Asset"

    # name = fields.Many2one('product.product', string="Asset", required=False,
    #                        domain=[('product_tmpl_id.is_asset', '=', True)])
    name = fields.Char(string="Asset")
    stock_quant_id = fields.Many2one('stock.quant', string="Stock")
    asset_id = fields.Many2one('product.product', string="Asset", related='stock_quant_id.product_id', store=True)
    template_id = fields.Many2one('product.template', string="Product Type",
                                  related='stock_quant_id.product_id.product_tmpl_id', store=True)
    # asset_name = fields.Char(string="Name")
    asset_type = fields.Selection(string='Asset Type', related='stock_quant_id.material_type', store=True)
    transfer_history_ids = fields.One2many('kw_stock_quant_log', 'asset_id', string='Transfer History')
    asset_owner_id = fields.Many2one('hr.employee', string="Employee Name", related='stock_quant_id.employee_id',
                                     store=True)
    asset_owner_branch_id = fields.Many2one('kw_res_branch', string="Location",
                                            related='stock_quant_id.dept_id.branch_id', store=True)
    department_id = fields.Many2one('hr.department', string="Department",
                                    related='stock_quant_id.employee_id.department_id', store=True)
    desigation_id = fields.Many2one('hr.job', string="Designation", related='stock_quant_id.employee_id.job_id',
                                    store=True)
    mobile_no = fields.Char("Mobile NUMBER", related='stock_quant_id.employee_id.mobile_phone', store=True)
    emp_code = fields.Char("Employee Code", related='stock_quant_id.employee_id.emp_code', store=True)
    invoice_date = fields.Date(string='Invoice Date')
    invoice_data = fields.Char(string="Invoice")
    expiry_warranty_date = fields.Date(string='Expiry Warranty Date')
    invoice_doc = fields.Binary(string='Upload Invoice', attachment=True)
    file_name = fields.Char("File Name", track_visibility='onchange')
    spec = fields.Char(string='Specifications', compute='compute_specification')
    fa_code = fields.Char(string='FA Code', related='stock_quant_id.fa_code')
    annual_maintenance_line_ids = fields.One2many('annual_maintenance_costs', 'asset_id', string='AMC')
    order_id = fields.Many2one('purchase.order', string='Purchase Order')
    order_ids = fields.Many2many('purchase.order', 'account_asset_po_rel', 'asset_id', 'po_id',
                                 string='Purchase History')
    requisition_ids = fields.Many2many('kw_requisition_requested', 'account_asset_requisition_rel', 'asset_id',
                                       'requisition_id', string='Requisition Ids')
    type = fields.Selection(related="category_id.type", string='Type', required=False)  # overided field
    residual_percentage = fields.Float('Residual Percentage')
    residual_value = fields.Float('Residual Value', compute='compute_residual_value')
    remaining_value = fields.Float('Remaining Value', compute='compute_residual_value')
    repair_history_ids = fields.One2many('kw_product_repair_log', 'asset_id', string='Repair History')
    asset_tracker_ids = fields.One2many('kw_asset_tracker_log', 'asset_id', string='Asset Tracker')
    host_name = fields.Char(string="Host Name")
    os = fields.Char(string="OS")
    ms_office = fields.Char(string="MS Office")
    liscence = fields.Char(string="Liscence")
    project_code = fields.Char(string='Project Code')
    room = fields.Char(string='Room')
    section = fields.Char(string='Section')
    bag = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Laptop Bag')
    age = fields.Float(string='Age(Yrs)')
    brand = fields.Char(string="Brand")
    model_no = fields.Char(string="Model No")
    gatepass_status = fields.Selection([('allowed', 'Allowed'), ('notallowed', 'Not Allowed')],
                                       string='Gate Pass Status', default='notallowed')
    gp_date_from = fields.Date(string='From')
    gp_date_to = fields.Date(string='To')
    image = fields.Binary("Photo", related='stock_quant_id.employee_id.image',
                          help="This field holds the image used as photo for the employee, limited to 1024x1024px.")
    perticulars = fields.Char("Perticulars")
    fiscal_year = fields.Many2one('account.fiscalyear',string='Fiscal Year')
    serial_no = fields.Char('Serial No')
    quantity = fields.Char("Quantity",default='1')
    item_name = fields.Char("Item Name")
    location = fields.Char("Location")
    vendor_name = fields.Char("Vendor Name")

    @api.multi
    def action_in_out_gatepass(self):
        view_id = self.env.ref('kw_inventory.kw_asset_tracker_wiz_form').id
        return {
            'name': 'In/Out remark',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_asset_tracker_wiz',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'target': 'new',
            'view_id': view_id,
            'context':{'default_asset_id':self.id}
        }
    
    @api.onchange('gatepass_status')
    def onchange_gatepass_status(self):
        if self.gatepass_status:
            self.gp_date_from = False
            self.gp_date_to = False

    @api.onchange('stock_quant_id')
    def onchnage_stock_quant_id(self):
        # print("---onchnage_stock_quant_id----")
        if self.stock_quant_id:
            query =f""" select d.id,d.name from stock_quant a
                        join stock_move_line b on a.lot_id = b.lot_id
                        join stock_picking c on c.id = b.picking_id
                        join purchase_order d on d.name = c.origin
                        join stock_production_lot x on x.id = a.lot_id
                        where b.lot_name = '{self.stock_quant_id.lot_id.name}' and b.lot_id={self.stock_quant_id.lot_id.id} and a.quantity >0 """
            self._cr.execute(query)
            order_id = self._cr.fetchall()
            
            if order_id:
                self.order_id = int(order_id[0][0])
                self.order_ids = [(6,0,[int(order_id[0][0])])]
                if self.order_id:
                    grn_data =  self.env['stock.picking'].search([('origin','=',self.order_id.name),('process_location','=','grn')])
                    if grn_data:
                        self.invoice_data= grn_data.invoice_number
                        self.invoice_date = grn_data.invoice_date
            
            quant_details = self.env['kw_stock_quant_log'].search([('material_id','=',int(self.stock_quant_id))])
            if quant_details:
                self.transfer_history_ids = [(6,0,quant_details.ids)]
            repair_details = self.env['kw_product_repair_log'].search([('repair_id','=',int(self.stock_quant_id))])
            # print("repair details===============",repair_details)
            if repair_details:
                self.repair_history_ids = [(6,0,repair_details.ids)]
                # print("self===================",self.repair_history_ids)
            
            
    @api.onchange('order_id')
    def onchnage_order_id(self):
        if self.order_id.requisition_ids:
            self.requisition_ids = [(6,0,self.order_id.requisition_ids.ids)]
        if self.order_id.partner_id:
            self.partner_id = self.order_id.partner_id.id
        if self.order_id.date_order:
            self.date = self.order_id.date_order.date()
            self.first_depreciation_manual_date = self.order_id.date_order.date()
            
    @api.model
    def create(self, values):
        # if 'stock_quant_id' in values:
        #     quant_details = self.env['kw_stock_quant_log'].search([('material_id','=',int(values['stock_quant_id']))])
        #     if quant_details:
        #         values['transfer_history_ids'] = [(6,0,quant_details.ids)]
        result = super(kw_asset, self).create(values)
        # repair_details = self.env['kw_product_repair_log'].search([('repair_id','=',int(result.stock_quant_id))])
        # quant_details = self.env['kw_stock_quant_log'].search([('material_id','=',int(result.stock_quant_id))])
        # if quant_details:
        #     result.transfer_history_ids = [(6,0,quant_details.ids)]
        # if repair_details:
        #     result.repair_history_ids = [(6,0,repair_details.ids)]
        # result.stock_quant_id.fa_code = result.name
        template_id = result.env.ref('kw_inventory.asset_creation_email_template')
        template_id.with_context().send_mail(result.id,notif_layout="kwantify_theme.csm_mail_notification_light")
       
        return result
            

    @api.depends('stock_quant_id')
    def compute_specification(self):
        for rec in self:
            varent_ids=rec.stock_quant_id.product_id.attribute_value_ids.ids
            spec_details = self.env['product.attribute.value'].search([('id','in',varent_ids)])
            spec_list = []
            for rec in spec_details:
                spec_list.append(r','.join(rec.attribute_id.value_ids.mapped('name')))
            rec.spec = str(','.join(spec_list))
            
    @api.depends('value','residual_percentage')
    def compute_residual_value(self):
        for record in self:
            record.residual_value = record.value * (record.residual_percentage / 100)
            record.remaining_value = record.value - (record.value * (record.residual_percentage / 100))
            
    
    # @api.onchange('name')
    # def _name_onchange(self):
    #     for record in self:
    #         # print(record.name)
    #         asset_rec = self.env['account.asset.asset'].sudo().search([('name.id', '=', record.name.id)])
    #         if len(asset_rec) > 0:
    #             raise ValidationError(
    #                 f"Record for [{record.name.product_tmpl_id.default_code}] {record.name.product_tmpl_id.name} is already present please select another")

        
class kwAssetTrackerLog(models.Model):
    _name = "kw_asset_tracker_log"
    _description = "Asset Tracker Log"
    
    asset_id = fields.Many2one('account.asset.asset')
    stock_id = fields.Many2one('stock.quant',string='Stock Id')
    check_in = fields.Datetime(string='Check-in')
    check_out = fields.Datetime(string='Check-out')
    remark = fields.Char(string='Action Taken By')
    action_by = fields.Many2one('res.users')
    owner_id = fields.Many2one('hr.employee',string='Owner')
    asset_status = fields.Selection([
        ('in', 'In'),
        ('out', 'Out'),
    ], string='Asset Status')

class kw_asset_report(models.Model):
    _name = "kw_asset_report"
    _description = "Asset Custom Report"
    _auto = False
    _order = "category_id,product,depreciation_date asc"
    # _rec_name       = 'Product'

    category_id = fields.Char(string="Category Name")
    product = fields.Char(string="Asset Name")
    purchase_date = fields.Date(string="Purchase Date")
    value = fields.Float(string="Gross Amount")
    salvage_value = fields.Float(string="Salvage Value")
    value_residual = fields.Float(string="Residual Value")
    depreciation_date = fields.Date(string="Depreciation Dates")
    amount = fields.Float(string="Depreciation Amount")
    current_value = fields.Float(string="Current Value")
    boolean_invisible = fields.Boolean(string='Boolean Invisible', compute='_get_value')

    def _get_value(self):
        dict_prod = {}
        for record in self:
            if record.product not in dict_prod:
                dict_prod[record.product] = [record.id]
        for dict_p in dict_prod:
            for rec in self:
                if rec.product == dict_p and rec.id == dict_prod[dict_p][0]:
                    rec.boolean_invisible = True
                # print(dict_p,dict_prod[dict_p][0])

    # @api.model_cr
    # def init(self):
    #     tools.drop_view_if_exists(self._cr, 'view_kw_asset_report')
    #     self._cr.execute("""
    #         create or replace view view_kw_asset_report as (
    #             select e.id as id, a.name as category_id,concat('[',d.default_code,']',' ', d.name) as product,b.date as purchase_date,b.value,b.salvage_value,(b.value-b.salvage_value) as value_residual,e.depreciation_date,e.depreciated_value as amount,e.remaining_value as current_value
    #             from account_asset_category a join account_asset_asset b on a.id = b.category_id
    #             join product_product c on c.id = b.name join product_template d on c.product_tmpl_id = d.id
    #             join account_asset_depreciation_line e  on b.id = e.asset_id)""")
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(""" CREATE or REPLACE VIEW %s as (
            select e.id as id, a.name as category_id,concat('[',d.default_code,']',' ', d.name) as product,b.date as purchase_date,b.value,b.salvage_value,(b.value-b.salvage_value) as value_residual,e.depreciation_date,e.amount as amount,e.remaining_value as current_value
            from account_asset_category a join account_asset_asset b on a.id = b.category_id
            join product_product c on c.id = b.asset_id join product_template d on c.product_tmpl_id = d.id
            join account_asset_depreciation_line e  on b.id = e.asset_id)""" % (self._table))
