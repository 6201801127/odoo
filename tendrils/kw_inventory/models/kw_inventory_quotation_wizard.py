from datetime import date
from odoo import api, models, fields
from odoo.exceptions import UserError, ValidationError
# from odoo import exceptions, _


class kw_inventory_quotation_wizard(models.TransientModel):
    _name = 'kw_inventory_quotation_wizard'
    _description = 'Inventory quotation wizard'

    def _get_default_quotation_confirm(self):
        datas = self.env['kw_consolidation'].browse(self.env.context.get('active_ids'))
        return datas

    @api.model
    def default_get(self, fields):
        res = super(kw_inventory_quotation_wizard, self).default_get(fields)
        # print("default get called", self._context)
        cons_records = self.env['kw_consolidation'].browse(self._context.get('active_ids', []))
        message = ""
        message_new = "Quotation will be created for Items : " + "\n"
        message_noitem_title = "No Balance Quantity left for Items : " + "\n"
        message_noitem = ""

        if cons_records:
            for rec in cons_records:
                for r in rec.add_product_consolidation_rel:
                    if r.quantity_balance != 0:
                        message += "Item Code - " + str(r.item_code.default_code) + " with Item Quantity-" + str(
                            r.quantity_balance) + "\n"
                    else:
                        message_noitem += "Item Code - " + str(r.item_code.default_code) + "\n"

        if len(message) > 0 and len(message_noitem) == 0:
            res['message'] = message_new + message
        if len(message_noitem) > 0 and len(message) == 0:
            res['message'] = message_noitem_title + message_noitem
            res['button_hide'] = True
        if len(message_noitem) > 0 and len(message) > 0:
            res['message'] = message_noitem_title + message_noitem + message_new + message
        return res

    # @api.model
    # def default_get(self, fields):
    #     res = super(kw_inventory_quotation_wizard, self).default_get(fields)
    #     print("default get called",self._context)
    #     cons_records = self.env['kw_consolidation'].browse(self._context.get('active_ids',[]))
    #     message = ""
    #     message_new = "Quotation will be created for Items : " + "\n"
    #     message_noitem_title = "No Balance Quantity left for Items : " + "\n"
    #     message_noitem = ""
    #     lst = []
    #     if cons_records:
    #         for r in cons_records:
    #             lst.append(len(r.add_product_consolidation_rel))
    #     no_of_records = len(cons_record)
    #     if all(x == lst[0] for x in lst):
    #         print('hello')
    #     else:
    #         res['message']="Indent do not contain same no of Items"
    #         res['button_hide'] = True
    #     return res

    inventory_quotation = fields.Many2many('kw_consolidation', readonly=1, default=_get_default_quotation_confirm)
    message = fields.Text(string="Message")
    button_hide = fields.Boolean(string='Button Hide', default=False)
    confirm_message = fields.Char(string="Confirm Message", default="Are you sure you want to Create Quotation ?")
    vendor = fields.Many2one('res.partner', string='Vendor', required=True,
                             domain="[('supplier','=',True), ('parent_id', '=', False)]")

    @api.onchange('vendor')
    def _onchange_vendor(self):
        cons_records = self.env['kw_consolidation'].browse(self._context.get('active_ids', []))
        for c in cons_records:
            # print(c.indent_number)
            quotation_record = self.env['kw_quotation'].sudo().search([])
            if quotation_record:
                for record in quotation_record:
                    for indnt in record.indent:
                        if c.indent_number == indnt.indent_number:
                            # print(record.partner_id)
                            # print(self.vendor)
                            if record.partner_id.id == self.vendor.id:
                                raise ValidationError("This Vendor is already selected Please choose another")

    @api.multi
    def button_quotation(self):
        vals = {}
        val = []
        values = []
        for record in self.inventory_quotation:
            # record.write({'state':'Quotation'})
            record.state = 'Quotation'
            for rec in record.add_product_consolidation_rel:
                if rec.quantity_balance != 0:
                    if record.id not in val:
                        val.append(record.id)
                    product = self.env['product.product'].sudo().search([('id', '=', rec.item_code.id)])
                    unit = product.uom_id.id
                    if rec.item_code.id in vals:
                        vals[rec.item_code.id][1] += rec.quantity_balance
                        vals[rec.item_code.id][3].append(rec.id)
                    else:
                        vals[rec.item_code.id] = [rec.item_description, rec.quantity_balance, unit, [rec.id]]

        for r in vals:
            values.append([0, 0, {
                'product_id': r,
                'name': vals[r][0],
                'product_qty': vals[r][1],
                'date_planned': date.today(),
                'product_uom': vals[r][2],
                'price_unit': 0,
                "indent_record_id": [[6, False, vals[r][3]]],
            }])

        if len(val) > 0 and len(values) > 0:
            quotation = self.env['kw_quotation']
            cdate = date.today()
            record = quotation.create({
                "indent": [[6, False, val]],
                "partner_id": self.vendor.id,
                "order_line": values
            })
            self.env.user.notify_success("Quotation created successfully")
