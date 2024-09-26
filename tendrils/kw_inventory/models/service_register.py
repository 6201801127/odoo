from odoo import models, fields, api
from odoo.exceptions import ValidationError

class KwServiceRegister(models.Model):
    _name        = "kw_service_register"
    _description = "Service Register"
    _rec_name    = 'sequence_number'
    
    sequence_number = fields.Char(string='Sequence')
    po_reference    = fields.Char(string='PO Reference')
    product_code    = fields.Many2one('product.product',string="Product Code")
    product_type    = fields.Selection(string=' Product Type',selection=[('consu', 'Consumable'), ('service', 'Service'), ('product', 'Product')],related='product_code.type', store=True)
    partner_id      = fields.Many2one('res.partner',string="Vendor")
    quantity        = fields.Float(string='Product Qty')
    product_uom     =fields.Many2one('uom.uom',string="Product Uniit Of Measure")
    price           = fields.Float(string='Price')
    purchase_order_line_id = fields.Many2one('purchase.order.line',string='Material Id')
    employee_id     = fields.Many2one('hr.employee',string="Employee")
    status = fields.Selection([
        ('Issued', 'Issued'),
        ('Not-Issued', 'Not-Issued'),
        ('Returned', 'Returned'),
    ], string='Status',default='Not-Issued',track_visibility='onchange')
    is_issued = fields.Boolean(string="Issued",default=False)
    department_id = fields.Many2one('hr.department',string='Department')
    issue_remark = fields.Text("Remark")
    return_remark = fields.Text("Remark")
    
    
    
    
    @api.onchange('department_id')
    def _changes_in_department_id(self):
        if self.department_id:
            emp_data = self.env['hr.employee'].sudo().search(
                [('department_id', '=', self.department_id.id)])
            return {'domain': {'employee_id': [('id', 'in', emp_data.ids if emp_data else [])], }}
        
    @api.multi
    def service_issue(self):
        form_view_id = self.env.ref("kw_inventory.kw_issue_service_form").id
        return {
            'name': ' Issue Service',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_service_register',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view_id,
            'res_id': self.id,
            'target': 'new',
            'context': {'default_product_code': self.product_code.id},

        }
    def service_issue_action(self):
        if self.employee_id or self.department_id:
            self.status ='Issued'
            self.is_issued=True
        else:
            raise ValidationError("Choose Department for service Issue")
        
    @api.multi
    def service_return(self):
        form_view_id = self.env.ref("kw_inventory.kw_return_service_form").id
        return {
            'name': ' Return Service',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_service_register',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view_id,
            'res_id': self.id,
            'target': 'new',
        }
        
    def service_return_action(self):
        self.status ='Returned'
        self.is_issued=False
        self.department_id=False
        self.employee_id = False
        