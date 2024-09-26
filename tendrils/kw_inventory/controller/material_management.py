import pytz
import datetime
from datetime import date
import base64
import io
import werkzeug
from werkzeug.exceptions import BadRequest, Forbidden
from werkzeug.utils import redirect
import werkzeug.urls
import math, random, string
from ast import literal_eval

import odoo.addons.calendar.controllers.main as main
from odoo.api import Environment
import odoo.http as http
from odoo.http import request
from odoo import SUPERUSER_ID, _
from odoo import registry as registry_get
from odoo.exceptions import ValidationError, AccessDenied


class kw_material_management(http.Controller):
    @http.route('/material_management/hod/approve', type='http', auth="user", website=True)
    def material_management_approve(self, db, token, action):
        # import pdb
        # pdb.set_trace()
        # print("in approve==================================================")
        registry = registry_get(db)
        # print(registry,"-----registry-----")
        with registry.cursor() as cr:
            env = Environment(cr, SUPERUSER_ID, {})
            materialtoken = env['kw_material_management_user_remark'].search(
                [('access_token', '=', token)])
            # print("materialtoken----------------------------",materialtoken,materialtoken.material_id.pending_at.user_id.id,request.env.uid)
            if not materialtoken:
                return request.not_found()
            if materialtoken.material_id.pending_at.user_id.id != request.env.uid:
                return Forbidden()
            lang = 'en_US'
            # record = request.env['kw_material_management'].sudo().search([('id', '=', materialtoken.material_id.id)])
            record = materialtoken.material_id
            print("record=================",record.id)
            if record.state == 'Pending':
                record.write({'state': 'Approved','pending_at':False})
                record.material_log.create({
                    "action_taken_by": request.env.user.employee_ids.id,
                    "material_id":record.id ,
                    "action_remark": "Approved",
                    "product_id": ','.join([rec.item_code.name for rec in record.add_product_items_ids]),
                    "status": 'Approved',
                })
                emp_data = request.env['res.users'].sudo().search([])
                store_manager = emp_data.filtered(lambda user: user.has_group('kw_inventory.group_store_manager')==True)
                cc_mail= ','.join(store_manager.mapped('employee_ids.work_email')) if store_manager else ''
                
                template_id = request.env.ref('kw_inventory.kw_material_management_approve_email')
                template_id.with_context(to_mail=materialtoken.material_id.employee_id.work_email,
                                        email_from= materialtoken.material_id.employee_id.sbu_master_id.representative_id.work_email if materialtoken.material_id.employee_id.sbu_master_id else materialtoken.material_id.employee_id.division.manager_id.work_email if materialtoken.material_id.employee_id.division.manager_id else materialtoken.material_id.employee_id.department_id.manager_id.work_email , 
                                        cc_mail=cc_mail,
                                        hod_name=materialtoken.material_id.employee_id.sbu_master_id.representative_id.name if materialtoken.material_id.employee_id.sbu_master_id.representative_id else materialtoken.material_id.employee_id.division.manager_id.name if materialtoken.material_id.employee_id.division.manager_id else materialtoken.material_id.employee_id.department_id.manager_id.name,
                                        user_name = materialtoken.material_id.employee_id.name,
                                        department =materialtoken.material_id.employee_id.department_id.name,
                                        date = materialtoken.material_id.date,
                                        product_data = materialtoken.material_id.add_product_items_ids,
                                        sequence=materialtoken.material_id.item_sequence,
                                        sbu_code=materialtoken.material_id.employee_id.sbu_master_id.representative_id.emp_code if materialtoken.material_id.employee_id.sbu_master_id.representative_id else materialtoken.material_id.employee_id.division.manager_id.emp_code if materialtoken.material_id.employee_id.division.manager_id else materialtoken.material_id.employee_id.department_id.manager_id.emp_code,
                                        user_code=materialtoken.material_id.employee_id.emp_code,).send_mail(materialtoken.material_id.id,notif_layout="kwantify_theme.csm_mail_notification_light")
                product_items = request.env['kw_add_product_items']
                data_list = []
                record_set = materialtoken.material_id.add_product_items_ids
                for record in record_set:
                    count=0
                    qty = record.item_code.qty_available
                    for range_data in range(int(record.quantity_required)):
                        data = {
                            "material_rel_id": materialtoken.material_id.id,
                            "product_type":record.product_type,
                            "product_template_id":record.product_template_id.id,
                            "item_code":record.item_code.id,
                            "item_description": record.item_description,
                            "uom":record.uom,
                            "quantity_required":1,
                            "expected_days":record.expected_days,
                            "check_availability":record.check_availability,
                            "employee_id":record.employee_id.id,
                            "status":'Approved',
                            "item_in_stock":qty
                            }
                        count += 1
                        data_list.append(data)
                        # print("data==============================",data)
                query = f"delete from  kw_add_product_items where id in ({str(record_set.ids)[1:-1]})"
                request.env.cr.execute(query)
                for rec in data_list:
                    product_items.sudo().create(rec)
            
                request.env.user.notify_success("Mail sent successfully.")
                return http.request.render('kw_inventory.material_request_button_redirect',{'request_no':materialtoken.material_id.item_sequence,'state':'Approved'})
            else:
                #redirect to approved page
                return http.request.render('kw_inventory.action_already_taken',{'request_no':materialtoken.material_id.item_sequence})
                
                
    @http.route('/material_management/hod/reject', type='http', auth="user", website=True)
    def material_management_reject(self, db, token, action):
        # print("in rejecttttttttttt==================================================")
        registry = registry_get(db)
        with registry.cursor() as cr:
            env = Environment(cr, SUPERUSER_ID, {})
            materialtoken = env['kw_material_management_user_remark'].search(
                [('access_token', '=', token)])
            if not materialtoken:
                return request.not_found()
            if materialtoken.material_id.pending_at.user_id.id != request.env.uid:
                return Forbidden()
            lang = 'en_US'
            record = request.env['kw_material_management'].sudo().search([('id', '=', materialtoken.material_id.id)])
            # print("record=================",record.id)
            record.write({"state":'Rejected','pending_at':False})
            record.material_log.create({
                    "action_taken_by": request.env.user.employee_ids.id,
                    "material_id":record.id ,
                    "action_remark": "Rejected",
                    "product_id": ','.join([rec.item_code.name for rec in record.add_product_items_ids]),
                    "status": 'Rejected',
                })
            query = f"update kw_add_product_items set status='Rejected' where id in ({str(materialtoken.material_id.add_product_items_ids.ids)[1:-1]})"
            request.env.cr.execute(query)
            # print("query===============")
            template_id = request.env.ref('kw_inventory.kw_material_management_reject_email_template')
            template_id.with_context(to_mail=materialtoken.material_id.employee_id.work_email,

                                     hod_name=materialtoken.material_id.employee_id.sbu_master_id.representative_id.name if materialtoken.material_id.employee_id.sbu_master_id.representative_id else materialtoken.material_id.employee_id.division.manager_id.name if materialtoken.material_id.employee_id.division.manager_id else materialtoken.material_id.employee_id.department_id.manager_id.name,

                                     email_from= materialtoken.material_id.employee_id.sbu_master_id.representative_id.work_email if materialtoken.material_id.employee_id.sbu_master_id else materialtoken.material_id.employee_id.division.manager_id.work_email if materialtoken.material_id.employee_id.division.manager_id else materialtoken.material_id.employee_id.department_id.manager_id.work_email,

                                    user_name = materialtoken.material_id.employee_id.name,
                                    department =materialtoken.material_id.employee_id.department_id.name,
                                    date = materialtoken.material_id.date,
                                    product_data = materialtoken.material_id.add_product_items_ids,
                                    sequence=materialtoken.material_id.item_sequence,
                                    sbu_code=materialtoken.material_id.employee_id.sbu_master_id.representative_id.emp_code if materialtoken.material_id.employee_id.sbu_master_id.representative_id else materialtoken.material_id.employee_id.division.manager_id.emp_code if materialtoken.material_id.employee_id.division.manager_id else materialtoken.material_id.employee_id.department_id.manager_id.emp_code,
                                    user_code=materialtoken.material_id.employee_id.emp_code,).send_mail(materialtoken.material_id.id,notif_layout="kwantify_theme.csm_mail_notification_light")
            
        
            request.env.user.notify_success("Mail sent successfully.")
            return http.request.render('kw_inventory.material_request_button_redirect',{'request_no':materialtoken.material_id.item_sequence,'state':'Rejected'})

    @http.route('/requisition/hod/approve', type='http', auth="user", website=True)
    def requisition_approve(self, db, token, action, active_id ,req_no):
       
        registry = registry_get(db)
        # print(registry,"-----registry--- newww req--")
        with registry.cursor() as cr:
            env = Environment(cr, SUPERUSER_ID, {})
            materialtoken = env['kw_add_product_items'].search(
                [('access_token', '=', token),('id','=',active_id)])
            if not materialtoken:
                return request.not_found()
            lang = 'en_US' 
            record = request.env['kw_purchase_requisition'].sudo().search([('material_id', '=', materialtoken.material_rel_id.id),('requisition_number','=',req_no)])
            if record.state == 'Draft':
                record.write({'state': 'Approved','pending_at':False})
                record.add_requisition_rel_ids.write({"remark":'okay',"status":'Approved'})
                return http.request.render('kw_inventory.requisition_button_redirect',{'request_no':req_no,'state':'Approved'})
            # return http.request.redirect('/web')  
                
    @http.route('/requisition/hod/reject', type='http', auth="user", website=True)
    def requisition_reject(self, db, token, action,active_id ,req_no):
        registry = registry_get(db)
        # print(registry,"-----registry-----")
        with registry.cursor() as cr:
            env = Environment(cr, SUPERUSER_ID, {})
            materialtoken = env['kw_add_product_items'].search(
                [('access_token', '=', token),('id','=',active_id)])
            if not materialtoken:
                return request.not_found()
        
            lang = 'en_US' 
            record = request.env['kw_purchase_requisition'].sudo().search([('material_id', '=', materialtoken.material_rel_id.id),('requisition_number','=',req_no)])
            if record.state == 'Pending':
                record.write({'state': 'Rejected','pending_at':False})
                query = f"update kw_requisition_requested set status='Rejected' where id in ({str(materialtoken.add_requisition_rel_ids.ids)[1:-1]})"
                request.env.cr.execute(query)
                return http.request.render('kw_inventory.requisition_button_redirect',{'request_no':req_no,'state':'Rejected'})
            return http.request.redirect('/web')

    @http.route('/purchase/ceo/approve', type='http', auth="user", website=True)
    def purchase_approve(self, db, token, action, active_id ,name):
       
        registry = registry_get(db)
        # print(registry,"-----registry--- newww req--")
        with registry.cursor() as cr:
            env = Environment(cr, SUPERUSER_ID, {})
            materialtoken = env['kw_qc_items_wizard'].search(
                [('access_token', '=', token),('id','=',active_id)])
            # if not materialtoken:
            #     return request.not_found()
            lang = 'en_US' 
            record = request.env['purchase.order'].sudo().search([('name', '=', name)],limit=1)
            # print("ceo records==============================",record)
            if record and record.state == 'sent':
                # print("inside if of ceooooo==================================")
                record.write({'state': 'approved'}) 
                emp_data = request.env['res.users'].sudo().search([])
                ceo_user = emp_data.filtered(lambda user: user.has_group('kw_inventory.group_chief_executive') == True)
                ceo_user_mail =','.join(ceo_user.mapped('employee_ids.work_email')) if ceo_user else ''
                ceo_user_name =','.join(ceo_user.mapped('employee_ids.name')) if ceo_user else ''
                ceo_user_emp_code =','.join(ceo_user.mapped('employee_ids.emp_code')) if ceo_user else ''
                po_approver_user = emp_data.filtered(lambda user: user.has_group('kw_inventory.group_po_approver') == True)
                po_approver_mail =','.join(po_approver_user.mapped('employee_ids.work_email')) if po_approver_user else ''
                po_approver_name =','.join(po_approver_user.mapped('employee_ids.name')) if po_approver_user else ''
                po_approver_emp_code =','.join(po_approver_user.mapped('employee_ids.emp_code')) if po_approver_user else ''
                template_id = request.env.ref('kw_inventory.purchase_order_approved') 
                for recs in record.order_line:
                    template_id.with_context(ceo_user_mail=ceo_user_mail,
                    ceo_user_name=ceo_user_name,
                    ceo_user_emp_code=ceo_user_emp_code,
                    po_approver_emp_code=po_approver_emp_code,
                    pr_user_mail=po_approver_mail,
                    po_approver_name=po_approver_name,
                    po_no=record.name,
                    product=recs.product_id.name,
                    product_code=recs.product_id.default_code,
                    qty=recs.product_qty,
                    price=recs.price_unit).send_mail(record.id,notif_layout="kwantify_theme.csm_mail_notification_light")  
                request.env.user.notify_success("Purchase Order Approved successfully.")   
                return http.request.render('kw_inventory.po_button_redirect',{'request_no':name,'state':'Approved'})   
            else:

                return http.request.redirect('/web')  
                
    @http.route('/purchase/ceo/reject', type='http', auth="user", website=True)
    def purchase_reject(self, db, token, action,active_id ,name):
        registry = registry_get(db)
        # print(registry,"-----registry--- newww req--")
        with registry.cursor() as cr:
            env = Environment(cr, SUPERUSER_ID, {})
            materialtoken = env['kw_qc_items_wizard'].search(
                [('access_token', '=', token),('id','=',active_id)])
            # if not materialtoken:
            #     return request.not_found()
            lang = 'en_US' 
            record = request.env['purchase.order'].sudo().search([('name', '=', name)],limit=1)
            # print("ceo records==============================",record)
            if record and record.state == 'sent':
                # print("inside if of ceooooo==================================")
                record.write({'state': 'reject'}) 
                emp_data = request.env['res.users'].sudo().search([])
                ceo_user = emp_data.filtered(lambda user: user.has_group('kw_inventory.group_chief_executive') == True)
                ceo_user_mail =','.join(ceo_user.mapped('employee_ids.work_email')) if ceo_user else ''
                ceo_user_name =','.join(ceo_user.mapped('employee_ids.name')) if ceo_user else ''
                ceo_user_emp_code =','.join(ceo_user.mapped('employee_ids.emp_code')) if ceo_user else ''
                po_approver = emp_data.filtered(lambda user: user.has_group('kw_inventory.group_po_approver')==True)
                to_mail = ','.join(po_approver.mapped('employee_ids.work_email')) if po_approver else '' 
                user_name = ','.join(po_approver.mapped('employee_ids.name')) if po_approver else ''
                template_id = request.env.ref('kw_inventory.po_cancelled_notification_to_store_manager')
                template_id.with_context(email_to=to_mail,
                                        user_name=user_name,
                                        ceo_user_mail=ceo_user_mail,
                                        ceo_user_name=ceo_user_name,
                                        ceo_user_emp_code=ceo_user_emp_code,
                                        po_name=record.name,
                                        records=record.order_line,
                                        ).send_mail(record.id,notif_layout="kwantify_theme.csm_mail_notification_light")
                request.env.user.notify_success(message='PO Rejected successfully.') 
                return http.request.render('kw_inventory.po_button_redirect',{'request_no':name,'state':'Rejected'})           
            return http.request.redirect('/web')  