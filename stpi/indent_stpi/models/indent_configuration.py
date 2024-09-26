from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta
from datetime import datetime, date
import xmlrpc.client
import jwt

class Vendor(models.Model):
    _name = 'grn.vendor'
    _description = "GRN Vendor"
    _order = 'id desc'
    
    def _default_branch(self):
        return self.env.user.default_branch_id

    name = fields.Char('Name')
    active = fields.Boolean('Active',default=True)
    email = fields.Char('Email')
    branch_id = fields.Many2one('res.branch', string='Center', default=_default_branch)
    
    _sql_constraints = [
        ('email_uniq', 'unique(email)', 'Vendor Already Exist!'),
    ]

class SerialNumber(models.Model):
    _name = 'indent.serialnumber'
    _description = "Indent Serial number"

    name = fields.Char('Serial Number')
    grn = fields.Boolean('GRN')
    issue = fields.Boolean('Issue')
    issue = fields.Boolean('Issue')
    branch_id = fields.Many2one('res.branch', string='Center', store=True)
    item_category_id = fields.Many2one('product.category', string='Item Category')
    item_id = fields.Many2one('indent.stock', string='Item')
    assigned = fields.Boolean('Assigned')
    is_asset = fields.Boolean('is Asset?')
    coe_asset_id = fields.Char('Asset id')
    grn_id = fields.Many2one('indent.request', string='GRN')
    issue_id = fields.Many2one('issue.request', string='Issue')
    state = fields.Selection(
        [('draft', 'Draft'), ('to_approve', 'To Approve'), ('approved', 'Approved'), ('rejected', 'Rejected')
         ], string='Status', default='draft')
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Serial Number must be unique!'),
    ]
    
    # @api.one
    # @api.constrains('name')
    # def _check_name(self):
    #     exist = self.search([('name','=',self.name)])
    #     if exist:
    #         raise ValidationError(_('Serial Number must be unique!'))
    
    @api.multi
    def fill_asset_details(self):
        """Request item details to COE server to create asset.
        :return: COE Asset form redirect
        """
        
        if not self.coe_asset_id:
            server_connection_id = self.env['server.connection'].search([('active', '=', True)])
            url = server_connection_id.url
            db = server_connection_id.db_name
            common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
            models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
            # print('==========models================', models)
            uid = 2
            # password = self.env.user.password
            password = 'admin'
            id = models.execute_kw(db, uid, password, 'account.asset.asset', 'create',
                                   [{"name": False if self.item_id.name is None else self.item_id.name,
                                     "serial_number": False if self.name is None else self.name,
                                     "invoice_no": False if self.grn_id.bill_no is None else self.grn_id.bill_no,
                                     "purchase_date": False if self.grn_id.purchase_date is None else self.grn_id.purchase_date,
                                     "invoice_date": False if self.grn_id.bill_date is None else self.grn_id.bill_date,
                                     # "first_depreciation_manual_date": self.Indent_id.date_of_receive,
                                     "code": False if self.item_id.specification is None else str(self.item_id.specification),
                                     "salvage_value": 1,
                                     "category_id": 6,
                                     "value": 1,
                                     "invoice_doc": False if self.grn_id.upload_invoice is None else self.grn_id.upload_invoice,
                                     "filename": False if self.grn_id.filename is None else self.grn_id.filename,
                                     'login': self.env.user.login}])
            # print('==========asset_data================', id)
            self.coe_asset_id = id
            asset_id = id
        else:
            asset_id = self.coe_asset_id
        key = ",jy`\;4Xpe7%KKL$.VNJ'.s6)wErQa"
        connection_rec = self.env['server.connection'].search([], limit=1)
        if not connection_rec:
            raise UserError(_('No Server Configuration Found !'))
        encoded_jwt = jwt.encode({'token': self.env.user.token}, key)
        if type(encoded_jwt) is str:
            encoded_jwt_str = str(encoded_jwt)
        else:
            encoded_jwt_str = str(encoded_jwt, "utf-8") # str(encoded_jwt.decode("utf-8"))
        action = {
            'name': connection_rec.name,
            'type': 'ir.actions.act_url',
            'url': str(connection_rec.url).strip() + "/asset/indent?login=" + str(
                self.env.user.login) + "&password=" +  encoded_jwt_str + "&menu_id=" + str(asset_id),
            'target': 'new',
        }
        return action

    @api.multi
    def send_for_approval(self):
        for res in self:
            res.write({'state': 'to_approve'})


    @api.multi
    def button_approved(self):
        for res in self:
            res.write({'state': 'approved'})


    @api.multi
    def button_reject(self):
        for res in self:
            res.write({'state': 'rejected'})

    @api.multi
    def button_send_back(self):
        for res in self:
            res.write({'state': 'draft'})


class ItemMaster(models.Model):
    _name = 'indent.stock'
    _description = "Item Master"
    _order = 'id desc'
    


    def _default_branch_id(self):
        emp = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.uid)], limit=1)
        return emp.branch_id.id


    name = fields.Char('Item')
    category_id = fields.Many2one('product.category', string='Category', domain=[('indent_category','=',True)] )
    branch_id = fields.Many2one('res.branch', string='Center', default=_default_branch_id, store=True)
    specification = fields.Text('Specifications')
    asset = fields.Boolean('is Asset?')
    serial_bool = fields.Boolean(string='Serial Number')
    issue = fields.Integer('Issue')
    received = fields.Integer('Received')
    balance = fields.Integer('Balance')
    is_barcode = fields.Boolean('Barcode Required?')
    # child_indent_stocks = fields.One2many('child.indent.stock', 'child_indent_stock', string='Availing Indent for year Ids')




    # @api.multi
    # def unlink(self):
    #     for rec in self:
    #         for line in rec.child_indent_stocks:
    #             line.sudo().unlink()
    #     return super(ItemMaster, self).unlink()

    @api.onchange('asset')
    def set_serial_true(self):
       for rec in self:
            if rec.asset == True:
                rec.serial_bool = True
                rec.is_barcode = True
            else:
                rec.serial_bool = False
                rec.is_barcode = False

class ChildIndentStock(models.Model):
    _name = 'child.indent.stock'
    _description = " Availing Indent for year"
    _order = 'id desc'


    def _default_branch_id(self):
        emp = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.uid)], limit=1)
        return emp.branch_id.id

    name = fields.Char('Name')
    specification = fields.Text('Specifications')
    branch_id = fields.Many2one('res.branch', string='Center', default=_default_branch_id, store=True)
    asset = fields.Boolean('is Asset?')
    child_indent_stock = fields.Many2one('indent.stock', string='Item Master')
    serial_bool = fields.Boolean(string='Serial Number')
    issue = fields.Integer('Issue')
    received = fields.Integer('Received')
    balance = fields.Integer('Balance')
    category_id = fields.Many2one('product.category', related='child_indent_stock.category_id', store=True, readonly=False)
    is_barcode = fields.Boolean('Barcode Required?')



            

    
    
class ProductCategory(models.Model):
    _inherit = "product.category"
    
    @api.model
    def _get_domain(self):
        branch_ids = self.env.user.branch_ids.ids
        return [('branch_ids','in',branch_ids)]
    
    indent_category = fields.Boolean('is indent Category?', help="To segregate odoo default ")
    user_id = fields.Many2many('res.users', string='Responsible Person', domain=_get_domain)
    level_2 = fields.Boolean('is 2nd level required?', help="To Enable 2nd Level Approver ")
    competent_authority = fields.Many2many('res.users',
                                  'category_competent_authority_rel',
                                  'user_id',
                                  'branch_id',
                                  'Competent Authority',
                                  domain=_get_domain)
    procur_group = fields.Selection(
        [('technical', 'Technical Group'), ('non-technical', 'Non-Technical Group'), ('admin', 'Administrative')
         ], string='Procurement Group')
    
    
    