from datetime import date
from odoo import api, models, fields
from odoo.exceptions import UserError, ValidationError
from odoo import exceptions, _


class kw_inventory_quotation_consolidation_wizard(models.TransientModel):
    _name = 'kw_inventory_quotation_consolidation_wizard'
    _description = 'Inventory quotation consolidation wizard'

    def _get_default_quotation_confirm(self):
        datas = self.env['kw_quotation'].browse(self.env.context.get('active_ids'))
        return datas

    @api.model
    def default_get(self, fields):
        res = super(kw_inventory_quotation_consolidation_wizard, self).default_get(fields)
        # print("default get called",self._context)
        cons_records = self.env['kw_quotation'].browse(self._context.get('active_ids', []))
        message = ""
        message_new = "Quotation Consolidation will be created with Quotation no: " + "\n"
        message_noitem_title = "Quotation Consolidation cannot be created with Quotation no : " + "\n"
        message_noitem = ""

        lst = []
        qo_lst = []
        item_code = []

        # if cons_records:
        #     for r in cons_records:
        #         lst.append(len(r.add_product_consolidation_rel))

        # no_of_records = len(cons_record)
        # if all(x == lst[0] for x in lst):
        #     print('hello')

        # else:
        #     res['message']="Indent do not contain same no of Items"
        #     res['button_hide'] = True

        if cons_records:
            for rec in cons_records:
                if rec.state not in 'sent,response':
                    message_noitem += "Quotation No - " + rec.qo_no + "\n"
                else:
                    message += "Quotation No - " + rec.qo_no + "\n"
                    lst.append(len(rec.order_line))
                    qo_lst.append(rec.id)

            # print(qo_lst)
            for q in qo_lst:
                qo_records = self.env['kw_quotation'].sudo().search([('id', '=', q)])
                if qo_records:
                    for item in qo_records.order_line:
                        if item.product_id.id not in item_code:
                            item_code.append(item.product_id.id)

            if all(x == lst[0] for x in lst):
                for i in item_code:
                    for qo_item in qo_lst:
                        item_record = self.env['kw_quotation_items'].sudo().search(
                            ['&', ('order_id.id', '=', qo_item), ('product_id.id', '=', i)])
                        if item_record:
                            pass
                        else:
                            raise ValidationError('Quotations do not contain Same item code')
            else:
                raise ValidationError('Quotations do not contain same no of items')

        if len(message) > 0 and len(message_noitem) == 0:
            res['message'] = message_new + message
        if len(message_noitem) > 0 and len(message) == 0:
            res['message'] = message_noitem_title + message_noitem
            res['button_hide'] = True
        if len(message_noitem) > 0 and len(message) > 0:
            res['message'] = message_noitem_title + message_noitem + message_new + message
        return res

    inventory_quotation_consolidation = fields.Many2many('kw_quotation', readonly=1,
                                                         default=_get_default_quotation_confirm)
    message = fields.Text(string="Message")
    button_hide = fields.Boolean(string='Button Hide', default=False)
    confirm_message = fields.Char(string="Confirm Message",
                                  default="Are you sure you want to create Quotation Consolidation ?")

    @api.multi
    def button_quotation_consolidation(self):
        neg_vals = []
        vals = []
        val = []
        # req_list = []
        for record in self.inventory_quotation_consolidation:
            # print("self.inventory_quotation_consolidation=====",self.inventory_quotation_consolidation)
            if record.state in 'sent,response':
                # print("record.requisition_ids===",record.requisition_ids)
                mat_list = []
                for req in record.requisition_ids:
                    # req_list.append(record.requisition_ids.ids)
                    
                    # print("req.material_line_id------",req.material_line_id)
                    if req.material_line_id:
                        mat_list.append(req.material_line_id.id)
                # print("mat_list===",mat_list)
                if mat_list:
                    query = f"update kw_add_product_items set order_status='Negotiation',remark='Negotiation by {self.env.user.employee_ids.name}' where id in ({str(mat_list)[1:-1]})"
                
                    self._cr.execute(query)
                record.write({'state': 'negotiation'})
                for rec in record.order_line:
                    if record.id not in val:
                        val.append(record.id)
                    product = self.env['product.product'].sudo().search([('id', '=', rec.product_id.id)])
                    unit = rec.product_uom.id
                    # print(rec.order_id.partner_id)
                    vals.append([0, 0, {
                        'product_id': rec.product_id.id if rec.product_id else False,
                        'name': rec.name if rec.name else False,
                        'product_qty': rec.product_qty if rec.product_qty else False,
                        'date_planned': rec.date_planned,
                        'product_uom': unit,
                        'price_unit': rec.price_unit,
                        'quotation_record_id': rec.id if rec.id else False,
                        'taxes_id': [(4, rec.taxes_id.id)] if rec.taxes_id else False,
                        'partner_id': rec.order_id.partner_id.id,
                        'last_pp': rec.last_pp if rec.last_pp else False,
                        'prd_attachment': record.qo_attachment if record.qo_attachment else False,
                        'file_name': record.file_name if record.file_name else False,
                    }])
        quotation_consolidation = self.env['kw_quotation_consolidation']
        # print("req list++++++++++++++++++++++++++++++++++",req_list,req_list[0][0])
        data=record.requisition_ids.ids if record.requisition_ids else False
        record = quotation_consolidation.create({
            "quotation": [[6, False, val]],
            "order_line": vals,
            "requisition_ids": [(6, False, data if data else [])],
        })
        quotation_consolidation_product = self.env['kw_quotation_consolidation_items'].sudo().search(
            [('order_id.id', '=', record.id)])
        # negotiation = self.env['kw_negotiation']
        if quotation_consolidation_product:
            for rec in quotation_consolidation_product:
                r = self.env['kw_negotiation'].create({'product': rec.product_id.id if rec.product_id else False,
                                                       'product_name': rec.name if rec.name else False,
                                                       'quantity': rec.product_qty if rec.product_qty else False,
                                                       'schedule_date': rec.date_planned,
                                                       'unit_price': rec.price_unit,
                                                       'vendor_id': rec.partner_id.id,
                                                       'consolidation_id': rec.order_id.id,
                                                       'attachment': rec.prd_attachment,
                                                       'file_name': rec.file_name,
                                                       })

                # negotiation = self.env['kw_negotiation']
        # rec = negotiation.create({ [[0,0,{'product':r.product,
        #                             'product_name':r.product_name,
        #                             'quantity': r.quantity,
        #                             'schedule_date':r.schedule_date,
        #                             'unit_price':r.unit_price,
        #                             'vendor_id': r.vendor_id ,
        #                             'consolidation_item_id': record.id, }]for r in neg_vals]})

        self.env.user.notify_success("Quotation Consolidation created successfully")
