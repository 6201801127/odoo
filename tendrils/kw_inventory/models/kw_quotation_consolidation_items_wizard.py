from datetime import date
from odoo import api, models, fields
from odoo.exceptions import UserError, ValidationError
import uuid


class kw_qc_items_wizard(models.TransientModel):
    _name = 'kw_qc_items_wizard'
    _description = 'Inventory quotation consolidation items wizard'

    def _get_default_quotation_consolidation_confirm(self):
        datas = self.env['kw_quotation_consolidation_items'].browse(self.env.context.get('active_ids'))
        return datas

    def _default_access_token(self):
        return uuid.uuid4().hex
    
    access_token = fields.Char('Token', default=_default_access_token)

    @api.model
    def default_get(self, fields):
        vals = {}
        message = ""
        message_new = "Purchase Order will be created for : " + "\n"
        res = super(kw_qc_items_wizard, self).default_get(fields)
        # print("default get called",self._context)
        cons_records = self.env['kw_quotation_consolidation_items'].browse(self._context.get('active_ids', []))
        if cons_records:
            for record in cons_records:
                message += record.product_id.display_name + " and Vendor - " + record.partner_id.name + "\n"
                if record.product_id.id in vals:
                    if vals[record.product_id.id][0] == record.partner_id.id:
                        raise ValidationError(
                            "Product with Same Item Code and Same Vendor cannot be Selected more than Once")
                    else:
                        vals[record.product_id.id] = [record.partner_id.id]
                else:
                    vals[record.product_id.id] = [record.partner_id.id]
            res['message'] = message_new + message
        return res

    inventory_purchase_order = fields.Many2many('kw_quotation_consolidation_items', readonly=1,
                                                default=_get_default_quotation_consolidation_confirm)
    message = fields.Text(string="Message")

    @api.multi
    def button_quotation_consolidation_items(self):
        emp_data = self.env['res.users'].sudo().search([])
        po_approver_user = emp_data.filtered(lambda user: user.has_group('kw_inventory.group_chief_executive') == True)
        po_approver_mail =','.join(po_approver_user.mapped('employee_ids.work_email')) if po_approver_user else ''
        po_approver_name =','.join(po_approver_user.mapped('employee_ids.name')) if po_approver_user else ''
        po_approver_emp_code =','.join(po_approver_user.mapped('employee_ids.emp_code')) if po_approver_user else ''
        po_vendor_id = []
        vendor_ids = []
        qc_ids_list = []
        vals = []
        val = []
        quotation_consolidation = self.env['purchase.order']
        for record in self.inventory_purchase_order:
            if record.order_id.requisition_ids:
                for rec in record.order_id.requisition_ids:
                    if rec.material_line_id:
                        rec.material_line_id.write({"order_status":'PO_Created','remark':f'Purchase ourder created by {self.env.user.employee_ids.name}'})

            if record.id not in val:
                val.append(record.id)
            if record.partner_id.id not in vendor_ids:
                vendor_ids.append(record.partner_id.id)
        for vendor_list_ids in vendor_ids:
            vendor_qc_item_records = self.env['kw_quotation_consolidation_items'].sudo().search(
                ['&', '&', ('id', 'in', val), ('partner_id', '=', vendor_list_ids), ('state', '=', 'approve')])

            if len(vendor_qc_item_records) > 1:
                for prd_id in vendor_qc_item_records:
                    if prd_id.partner_id.id not in po_vendor_id:
                        po_vendor_id.append(prd_id.partner_id.id)
                    product = self.env['product.product'].sudo().search([('id', '=', prd_id.product_id.id)])
                    unit = prd_id.product_uom.id
                    vals.append([0, 0, {
                        'boolean_create': True,
                        'product_id': prd_id.product_id.id if prd_id.product_id else False,
                        'name': prd_id.name if prd_id.name else ' ',
                        'product_qty': prd_id.product_qty if prd_id.product_qty else False,
                        'date_planned': prd_id.date_planned,
                        'product_uom': unit,
                        'price_unit': prd_id.price_unit,
                        'quotation_items_ids': prd_id.id if prd_id.id else False,
                        'taxes_id': [(4, prd_id.taxes_id.id)] if prd_id.taxes_id else False,
                    }])

                    if prd_id.order_id.id not in qc_ids_list:
                        qc_ids_list.append(prd_id.order_id.id)
            else:
                product = self.env['product.product'].sudo().search([('id', '=', vendor_qc_item_records.product_id.id)])
                unit = vendor_qc_item_records.product_uom.id
                r = self.env['purchase.order'].create({
                    "boolean_create_po": True,
                    "pending_at":po_approver_name,
                    "po_created_by":self.env.user.employee_ids.id,
                    "partner_id": vendor_qc_item_records.partner_id.id,
                    "qc_ids": [(4, vendor_qc_item_records.order_id.id)],
                    "order_line": [[0, 0, {
                        'boolean_create': True,
                        'product_id': vendor_qc_item_records.product_id.id if vendor_qc_item_records.product_id else False,
                        'name': vendor_qc_item_records.name if vendor_qc_item_records.name else ' ',
                        'product_qty': vendor_qc_item_records.product_qty if vendor_qc_item_records.product_qty else False,
                        'date_planned': vendor_qc_item_records.date_planned,
                        'product_uom': unit,
                        'price_unit': vendor_qc_item_records.price_unit,
                        'quotation_items_ids': vendor_qc_item_records.id if vendor_qc_item_records.id else False,
                        'taxes_id': [
                            (4, vendor_qc_item_records.taxes_id.id)] if vendor_qc_item_records.taxes_id else False,
                    }]],
                    # "quotation_items_ids":[[6,False,val]],
                })

                if r:
                    for recs in r.order_line:
                        db_name = self._cr.dbname
                        poview = self.env.ref('purchase.purchase_rfq')
                        action_id = self.env['ir.actions.act_window'].search([('id', '=', poview.id)], limit=1).id
                        template_id = self.env.ref('kw_inventory.purchase_order_created') 
                        template_id.with_context(dbname=db_name,
                                                name=r.name,
                                                active_id=self.env.context.get('active_id'),
                                                action_id=action_id,
                                                token=self.access_token,
                                                po_approver_emp_code=po_approver_emp_code,
                                                pr_user_mail=po_approver_mail,
                                                po_approver_name=po_approver_name,
                                                po_no=r.name,
                                                product=recs.product_id.name,
                                                product_code=recs.product_id.default_code,
                                                qty=recs.product_qty,
                                                price=recs.price_unit).send_mail(r.id,notif_layout="kwantify_theme.csm_mail_notification_light")  
                        for rec in self.inventory_purchase_order:
                            rec.po_create = True

                prqn_id = []
                for rec in r.order_line:
                    for qo_id in rec.quotation_items_ids.order_id.quotation:
                        # print("qoid====================",qo_id)
                        for pr_ids in qo_id.requisition_ids:
                            if pr_ids.id not in prqn_id:
                                prqn_id.append(pr_ids.id)
                                # print("list value=============================",prqn_id)
                r.write({
                    "requisition_ids": [(4, x, None) for x in prqn_id],
                    "state": "sent"
                })
                prqn_id.clear()

            if vals:
                record = quotation_consolidation.create({
                    # "quotation_items_ids":[[6,False,val]],
                    "boolean_create_po": True,
                    'partner_id': po_vendor_id[0],
                    "qc_ids": [[6, False, qc_ids_list]],
                    "order_line": vals,
                })

                if record:
                    for rec in self.inventory_purchase_order:
                        rec.po_create = True

                prq_id = []
                for rec in record.order_line:
                    for qo_id in rec.quotation_items_ids.order_id.quotation:
                        for pr_ids in qo_id.requisition_ids:
                            if pr_ids.id not in prq_id:
                                prq_id.append(pr_ids.id)
                record.write({
                    "requisition_ids": [(4, x, None) for x in prq_id],
                    "state": "sent"
                })
                # prq_id.clear()

            po_vendor_id.clear()
            qc_ids_list.clear()
            vals.clear()
        self.env.user.notify_success("Purchase Order Created Successfully")
