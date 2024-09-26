from datetime import date
from odoo import api, models, fields
from odoo.exceptions import UserError, ValidationError


class KwMaterialRequestQuotationWizard(models.TransientModel):
    _name = 'kw_material_request_quotation_wizard'
    _description = 'Inventory quotation wizard'

    def _get_default_item_records(self):
        datas = self.env['kw_requisition_requested'].browse(self.env.context.get('active_ids'))
        return datas

    all_requisition_ids = fields.Many2many('kw_requisition_requested','kw_material_request_quotation_wizard_requisition_rel','wiz_id','partner_id', readonly=1, default=_get_default_item_records)
    message = fields.Text(string="Message")
    button_hide = fields.Boolean(string='Button Hide', default=False)
    confirm_message = fields.Char(string="Confirm Message", default="Are you sure you want to Create Quotation ?")
    vendor_ids = fields.Many2many('res.partner', 'kw_material_request_quotation_wizard_partner_rel','wiz_id','partner_id',string='Vendor', required=True,
                             domain="[('supplier','=',True), ('parent_id', '=', False)]")

    @api.model
    def default_get(self, fields):
        # print("default----------",self._context.get('active_ids', []))
        res = super(KwMaterialRequestQuotationWizard, self).default_get(fields)
        cons_records = self.env['kw_requisition_requested'].browse(self._context.get('active_ids', []))
        message = ""
        message_new = "Quotation will be created for Items : " + "\n"
        message_noitem_title = "No Balance Quantity left for Items : " + "\n"
        message_noitem = ""

        if cons_records:
            for rec in cons_records:
                # if rec.available_qty:
                message += "Item Code - " + str(rec.alternate_requisition_item.default_code if rec.alternate_requisition_item else rec.item_code.default_code) + " with Item Quantity-" + str(rec.order_qty) + ' '+ str(rec.uom) +"\n"
                # else:
                #     message_noitem += "Item Code - " + str(rec.item_code.default_code) + "\n"

        if len(message) > 0 and len(message_noitem) == 0:
            res['message'] = message_new + message
        
        return res

    @api.multi
    def create_items_quotation(self):
        vals = {}
        val = []
        values = []
        # print("all_requisition_ids==============",self.all_requisition_ids)
        for record in self.all_requisition_ids:
            # print("record==============",record)
            if record.material_line_id:
                record.material_line_id.write({'order_status':'Quotation_Created','remark':f'Quotation by {self.env.user.employee_ids.name}'})
            if record.id not in val:
                val.append(record.id)
            unit = record.item_code.uom_id.id
            if record.alternate_requisition_item and record.alternate_requisition_item.id not in vals:
                # print("inside if=====================",record.alternate_requisition_item.id,record.quantity_required)
                vals[record.alternate_requisition_item.id] = [record.item_description, record.quantity_required, unit, [record.id]]
                #check if the same key exist as product id, if exist then update quatity else pass
            elif record.item_code.id and record.item_code.id not in vals and not record.alternate_requisition_item.id:
                # print("inside elif==========1===========",record.item_code.id,record.quantity_required)
                vals[record.item_code.id] = [record.item_description, record.quantity_required, unit, [record.id ]]
            elif record.alternate_requisition_item.id in vals:
                # print("inside elif========2=============",record.alternate_requisition_item.id,record.quantity_required)
                vals[record.alternate_requisition_item.id][1] += record.quantity_required
            elif record.item_code.id in vals:
                # print("inside elif========3=============",record.item_code.id,record.quantity_required)
                vals[record.item_code.id][1] += record.quantity_required
                
        # print('data====================================================',vals)
        for r in vals:
            values.append([0, 0, {
                'product_id': r,
                'name': vals[r][0],
                'product_qty': vals[r][1],
                'date_planned': date.today(),
                'product_uom': vals[r][2],
                'price_unit': 0,
                "items_record_ids": [[6, False, vals[r][3]]],
            }])
        # print("values--------------",values)
        if len(val) > 0 and len(values) > 0:
            quotation = self.env['kw_quotation'].sudo()
            for rec in self.vendor_ids:
                record = quotation.create({
                    "requisition_ids": [[6, False, val]],
                    "partner_id": rec.id,
                    "order_line": values
                })
            for rec in self.all_requisition_ids:
                rec.status='Quotation'
            self.env.user.notify_success("Quotation created successfully")
