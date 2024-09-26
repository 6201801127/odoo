# import re
from datetime import date
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class kw_add_product(models.Model):
    _name = 'kw_add_product'
    _description = "A master model to add the Products"
    _rec_name = 'item_code'
    _order = 'id desc'

    item_code = fields.Many2one('product.product', string="Item Code", required=True)
    item_description = fields.Char(string="Item Description", required=True)
    uom = fields.Char(string="Unit Of Measurement", required=True)
    quantity_required = fields.Float(string="Quantity Required", default=1)
    expected_days = fields.Integer(string="Expected Date in Days", default=1)
    pr_rel = fields.Many2one('kw_purchase_requisition', required=True, ondelete='cascade')
    pr_rel_req_no = fields.Char(string="Requisition No", related='pr_rel.requisition_number')
    status = fields.Char(string="Status", default="Draft")
    remark = fields.Text(string="Remark")
    indnt_no = fields.Char(string="Indent Number", compute="show_indent")
    indent_created = fields.Boolean(string='field_name', default=False)

    @api.constrains('quantity_required')
    def validate_qty_required(self):
        for record in self:
            if record.quantity_required == 0:
                raise ValidationError("Quantity cannot be 0")

    @api.onchange("item_code")
    def _set_description(self):
        for record in self:
            if record.item_code:
                record.item_description = record.item_code.name
                record.uom = record.item_code.uom_id.name

    def show_indent(self):
        for record in self:
            indent_rec = self.env['kw_add_product_consolidation'].sudo().search([('add_product_id', '=', record.id)])
            for rec in indent_rec:
                if rec:
                    record.indnt_no = rec.indent_rel.indent_number
                    record.write({'indent_created': True})
                else:
                    record.write({'indent_created': False})

    def change_approve_value(self):
        # self.update({'status': 'Approved'})
        form_view_id = self.env.ref("kw_inventory.kw_remark_form_view").id
        return {
            'name': ' Remark',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_add_product',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'view_id': form_view_id,
            'target': 'new',
            'domain': [('id', '=', self.id)]
        }

    def change_hold_value(self):
        # self.update({'status': 'Approved'})
        form_view_id = self.env.ref("kw_inventory.kw_remark_hold_form_view").id
        return {
            'name': ' Remark',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_add_product',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'view_id': form_view_id,
            'target': 'new',
            'domain': [('id', '=', self.id)]
        }

    def change_unhold_value(self):
        self.update({'status': 'Draft'})
        self.remark = ""
        self.pr_rel._get_status()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def give_hold_remark(self):
        self.update({'remark': self.remark, 'status': 'Hold'})
        self.pr_rel._get_status()
        form_view_id = self.env.ref("kw_inventory.kw_purchase_requisition_view_form").id
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def give_remark(self):
        self.update({'remark': self.remark, 'status': 'Approved'})
        # print('give remark method called')
        self.pr_rel._get_status()
        form_view_id = self.env.ref("kw_inventory.kw_purchase_requisition_view_form").id
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def give_reject_remark(self):
        self.update({'remark': self.remark, 'status': 'Rejected'})
        # print('give rejected remark method called')
        self.pr_rel._get_status()
        form_view_id = self.env.ref("kw_inventory.kw_purchase_requisition_view_form").id
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def change_reject_value(self):
        # self.update({'status':'Rejected'})
        form_view_id = self.env.ref("kw_inventory.kw_remark_reject_form_view").id
        return {
            'name': ' Remark',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_add_product',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'view_id': form_view_id,
            'target': 'new',
            'domain': [('id', '=', self.id)]
        }

    def view_indent(self):
        form_view_id = self.env.ref("kw_inventory.kw_indent_consolidation_view_form").id
        indent_rec = self.env['kw_consolidation'].sudo().search([('indent_number', '=', self.indnt_no)])
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'kw_consolidation',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': indent_rec.id,
            'view_id': form_view_id,
            'target': 'self',
            'domain': [('id', '=', indent_rec.id)]
        }

    @api.multi
    def create_indent(self):
        indent_rec = lambda rec: self.env['kw_add_product_consolidation'].sudo().search(
            [('add_product_id', '=', rec.id)])
        r = self.filtered(lambda record: not len(indent_rec(record)) > 0)

        Indent_Consolidation = self.env['kw_consolidation']
        cdate = date.today()
        # for record in self:
        #     indent_rec = self.env['kw_add_product_consolidation'].sudo().search([('add_product_id','=',record.id)])
        #     if  len(indent_rec) > 0:
        #         raise ValidationError(f" Indent is already created for Item Code {record.item_code.id}-{record.item_code.name} of Requisition number {record.pr_rel_req_no} ")

        record = Indent_Consolidation.create({
            "date": cdate,
            "status": "Draft",
            "requisition_rel": [(6, 0, [record.pr_rel.id for record in r])],
            "add_product_consolidation_rel": [[0, 0, {"item_code": record.item_code.id if record.item_code else False,
                                                      "item_description": record.item_description if record.item_description else False,
                                                      "quantity_required": record.quantity_required if record.quantity_required else False,
                                                      "status": record.status if record.status else False,
                                                      "add_product_id": record.id,
                                                      }] for record in r]
        })
        record.indent_number = f"INDNT{record.id}"
        self.show_indent()
        self.env.user.notify_success("Product added Successfully")
