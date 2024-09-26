import re
from odoo import models, fields, api
from datetime import date
from odoo.exceptions import ValidationError


class kw_indent_consolidation(models.Model):
    _name = 'kw_consolidation'
    _description = "A master model to create the Indent Consolidation"
    _rec_name = "indent_number"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'id desc'

    date = fields.Date(string='Date', default=fields.Date.context_today, required=True)
    requisition_rel = fields.Many2many('kw_purchase_requisition', string="Purchase Requisition Relationship")
    indent_number = fields.Char(string="Indent Number", required=True, default="New", readonly="1")
    department = fields.Many2many('hr.department', 'kw_indent_department_rel', string="Department",
                                  track_visibility='always')
    project_code = fields.Char(string="Project Code", )
    add_product_consolidation_rel = fields.One2many("kw_add_product_consolidation", 'indent_rel', string="Item Details")
    state = fields.Selection([
        ('Indent', 'Quotation Pending'),
        ('Quotation', 'Quotation Created'),
    ], string='Status', readonly=True, index=True, copy=False, default='Indent', track_visibility='onchange')
    quotation_no = fields.Char(string="Indent Number", compute="show_quotation")
    quotation_created = fields.Boolean(string='field_name', default=False)
    create_check = fields.Boolean(string='Create Check', default=False)
    indenting_department = fields.Many2many('hr.department', 'kw_indent_indt_dept_rel', string='Indenting Department')

    @api.onchange("requisition_rel")
    def _set_department(self):
        for record in self:
            if record.requisition_rel:
                record.add_product_consolidation_rel = False
                for rec in record.requisition_rel:
                    if rec.add_product_rel:
                        vals = []
                        for items in rec.add_product_rel:
                            if items.status == 'Approved':
                                vals.append([0, 0, {
                                    'item_code': items.item_code if items.item_code else False,
                                    'item_description': items.item_description if items.item_description else False,
                                    'quantity_required': items.quantity_required if items.quantity_required else False,
                                    'status': items.status if items.status else False,
                                    'add_product_id': [(4, items.id)]
                                }])
                        record.add_product_consolidation_rel = vals
                    else:
                        record.requisition_rel.add_product_rel = False
            else:
                record.add_product_consolidation_rel = False

    def show_quotation(self):
        for record in self:
            vals = []
            i = ""
            quotation_rec = self.env['kw_quotation'].sudo().search([])
            for rec in quotation_rec:
                for r in rec.indent:
                    if record.indent_number == r.indent_number:
                        vals.append(rec.qo_no)

            for x in vals:
                if len(i) == 0:
                    i = x
                else:
                    i = i + ',' + x
            record.quotation_no = i
            if len(record.quotation_no) == 0:
                record.write({'quotation_created': False})
            else:
                record.write({'quotation_created': True})

    @api.model
    def create(self, vals):
        if vals.get('indent_number', 'New') == 'New':
            vals['indent_number'] = self.env['ir.sequence'].next_by_code('kw_indent') or '/'
        return super(kw_indent_consolidation, self).create(vals)
        # new_record = super(kw_indent_consolidation, self).create(vals)
        # self.env.user.notify_success(message='Indent Consolidation Created Successfully.')
        # return new_record

    @api.multi
    def write(self, vals):
        res = super(kw_indent_consolidation, self).write(vals)
        # self.env.user.notify_success(message='Indent Consolidation Updated Successfully.')
        return res

    @api.multi
    def create_quotation(self):
        form_view_id = self.env.ref("kw_inventory.kw_inventory_quotation_wizard").id
        return {
            'name': ' Remark',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_inventory_quotation_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view_id,
            'target': 'new',
        }

    @api.multi
    def unlink(self):
        for record in self:
            qo_no_rec = self.env['kw_quotation'].sudo().search([])
            if qo_no_rec:
                for qo in qo_no_rec:
                    for rec in qo.indent:
                        if record.quotation_no == rec.quotation_no:
                            raise ValidationError(
                                f"Record cannot be Deleted. Indent No - {record.indent_number} is referenced by Quotation No {qo.qo_no}")
        return super(kw_indent_consolidation, self).unlink()
