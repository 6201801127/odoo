from odoo import http
from odoo.http import request
from werkzeug.exceptions import BadRequest, Forbidden
import base64



class kw_quotation_consolidation(http.Controller):

    @http.route('/quotation-consolidation-decision', type='http', auth="user", website=True)
    def quotation_consolidation_decision_stage(self, **args):
        inventory_dict = dict()
        inventory_dict['quotation_dict'] = []
        inventory_dict['product_id'] = []
        inventory_dict['vendor'] = []
        inventory_dict['vendor_name'] = []
        inventory_dict['p_name'] = []
        inventory_dict['v_data'] = {}
        inventory_dict['min_value'] = {}
        qtions = http.request.env['kw_quotation'].search([])
        for record in qtions:
            inventory_dict['quotation_dict'].append(record.qo_no)
            if record.partner_id.id not in inventory_dict['vendor']:
                inventory_dict['vendor'].append(record.partner_id.id)
                inventory_dict['vendor_name'].append({"id": record.partner_id.id, "name": record.partner_id.name})

        qitems = http.request.env['kw_quotation_items'].search([])
        for rec in qitems:
            if rec.product_id.id not in inventory_dict['product_id']:
                inventory_dict['product_id'].append(rec.product_id.id)
                inventory_dict['p_name'].append({"id": rec.product_id.id, "name": rec.product_id.name})

        for product_id in inventory_dict['product_id']:
            items = request.env['kw_quotation_items'].search([('product_id.id', '=', product_id)])
            for item in items:
                for vendor_id in inventory_dict['vendor']:
                    if item.order_id.partner_id.id == vendor_id:
                        if product_id in inventory_dict['v_data']:
                            inventory_dict['v_data'][product_id].update(
                                {vendor_id: [item.price_unit, item.product_qty, item.price_subtotal]})
                        else:
                            inventory_dict['v_data'][product_id] = {
                                vendor_id: [item.price_unit, item.product_qty, item.price_subtotal]}

        for p_id in inventory_dict['product_id']:
            if p_id in inventory_dict['v_data']:
                x = inventory_dict['v_data'][p_id]
                lst = []
                if x:
                    for i in x:
                        if x[i][0] not in lst:
                            lst.append(x[i][0])

                    lst.sort()
                    if len(lst) >= 3:
                        inventory_dict['min_value'].update({p_id: [lst[0], lst[1], lst[2]]})
                    if 2 <= len(lst) < 3:
                        inventory_dict['min_value'].update({p_id: [lst[0], lst[1], 'NA']})
                    if 1 <= len(lst) < 2:
                        inventory_dict['min_value'].update({p_id: [lst[0], 'NA', 'NA']})

        return http.request.render('kw_inventory.kw_consolidation_details', inventory_dict)

    @http.route('/inventory/product_items_list_panel', auth='user', type='json')
    def get_product_panel_data(self):
        total_count = request.env['kw_add_product_items'].sudo().search([('is_requisition_applied', '=', True)])
        requisitions_count= len(total_count.filtered(lambda x:x.order_status=='Requisition_Approved'))
        quotations_count= len(total_count.filtered(lambda x:x.order_status=='Quotation_Created'))
        negotiation_count= len(total_count.filtered(lambda x:x.order_status=='Negotiation'))
        po_count= len(total_count.filtered(lambda x:x.order_status=='PO_Created'))
        vals = {'requisitions_count': requisitions_count if requisitions_count else 0,'quotations_count': quotations_count if quotations_count else 0,'negotiation_count': negotiation_count if negotiation_count else 0,'po_count': po_count if po_count else 0}
        # print("vals======",vals)
        
        return {
                'html':request.env.ref('kw_inventory.product_items_template').render({
                'object': request.env['kw_add_product_items'],
                'values': vals
            })
            
        }
    @http.route('/inventory/material_request_list_panel', auth='user', type='json')
    def get_material_request_data(self):
        total_count = request.env['kw_material_management'].sudo().search([])
        draft_count= len(total_count.filtered(lambda x:x.state=='Draft'))
        pending_count= len(total_count.filtered(lambda x:x.state=='Pending'))
        hold_count= len(total_count.filtered(lambda x:x.state=='Hold'))
        approved_count= len(total_count.filtered(lambda x:x.state=='Approved'))
        cancelled_count= len(total_count.filtered(lambda x:x.state=='Cancelled'))
        rejected_count= len(total_count.filtered(lambda x:x.state=='Rejected'))
        issued_count= len(total_count.filtered(lambda x:x.state=='Issued'))
        released_count= len(total_count.filtered(lambda x:x.state=='Released'))
        vals = {'draft_count': draft_count if draft_count else 0,
                'pending_count': pending_count if pending_count else 0,
                'hold_count': hold_count if hold_count else 0,
                'approved_count': approved_count if approved_count else 0,
                'cancelled_count': cancelled_count if cancelled_count else 0,
                'rejected_count': rejected_count if rejected_count else 0,
                'issued_count': issued_count if issued_count else 0,
                'released_count': released_count if released_count else 0}
        # print("vals======",vals)
        
        return {
                'html':request.env.ref('kw_inventory.material_request_template').render({
                'object': request.env['kw_material_management'],
                'values': vals
            })
            
        }
    @http.route('/download-gate-pass/<int:rec_id>', methods=['GET'], csrf=False, type='http', auth="public", website=True)
    def accept_gate_pass(self,rec_id, download=False, **args):
        report_obj = request.env['stock.picking'].sudo().search([('id','=',rec_id)])
        # print("report obj ===============",report_obj)
        report_template_id = request.env.ref('kw_inventory.action_report_gate_pass').sudo().render_qweb_pdf(report_obj.id)
        data_record = base64.b64encode(report_template_id[0])
        # print("data_recorddata_recorddata_record", data_record,report_obj)
        ir_values = {
            'name': "Gate Pass",
            'type': 'binary',
            'datas': data_record,
            'datas_fname': f"{report_obj.company_id.name.replace(' ', '-')}-Gate-Pass.pdf",
            'mimetype': 'application/x-pdf',
        }
        pdf_http_headers = [('Content-Type', 'application/pdf'),
                            ('Content-Disposition', f"attachment; filename={report_obj.company_id.name.replace(' ', '-')}-Gate-Pass.pdf"),
                            ('Content-Length', len(data_record))]
        return request.make_response(report_template_id[0], headers=pdf_http_headers)
