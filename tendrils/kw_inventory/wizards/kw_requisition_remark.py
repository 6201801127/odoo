import datetime
from datetime import timedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class kwRequisitionUserRemark(models.TransientModel):
    _name = 'kw_requisition_user_remark'
    _description = "Material Request"

    requisition_id = fields.Many2one('kw_purchase_requisition', string="Material")
    remark = fields.Text(string='Remark')


    @api.multi
    def submit_user_action(self):
        action_id = self.env.ref('kw_inventory.kw_purchase_requisition_action_window').id
        if self._context.get('apply_requisition_request'):
            emp_data = self.env['res.users'].sudo().search([])
            store_manager = emp_data.filtered(lambda user: user.has_group('kw_inventory.group_dept_budget_head') == True)
            self.requisition_id.write({"remark":self.remark,"state":'Pending','pending_at': store_manager.mapped('name')[0]})
            self.requisition_id.add_requisition_rel_ids.write({"remark":self.remark,"status":'Pending'})
        elif self._context.get('approve_requisition_request'):
            action_id = self.env.ref('kw_inventory.kw_purchase_requisition_take_action_window').id
            self.requisition_id.write({"remark":self.remark,"state":'Approved','pending_at':False})
            self.requisition_id.add_requisition_rel_ids.write({"remark":self.remark,"status":'Approved'})
            emp_data = self.env['res.users'].sudo().search([])
            pr_user = emp_data.filtered(lambda user: user.has_group('kw_inventory.group_pr_user') == True)
            # print('pr user===================',pr_user)
            # print('pr user===================',pr_user.email,)
            if self.requisition_id.material_id:
                query = f"update kw_add_product_items set pending_at='PR Team : Req -{self.requisition_id.requisition_number}' where id in ({str(self.requisition_id.material_id.add_product_items_ids.ids)[1:-1]})"
                self._cr.execute(query)
            
            pr_user_mail =','.join(pr_user.mapped('employee_ids.work_email')) if pr_user else ''
            # print('pr_user_mail======',pr_user_mail)
            pr_user_name = ','.join(pr_user.mapped('employee_ids.name')) if pr_user else ''
            template_id = self.env.ref('kw_inventory.purchase_requisition_approved')
            for rec in self.requisition_id.add_requisition_rel_ids:
                product = rec.product_template_id.name
                product_code = rec.item_code.default_code
                quantity =rec.quantity_required
                template_id.with_context(pr_user_mail=pr_user_mail,pr_user_name=pr_user_name,product=product,product_code=product_code,quantity=quantity).send_mail(self.requisition_id.id,notif_layout="kwantify_theme.csm_mail_notification_light")
            # exist_data = self.env['kw_requisition_requested'].sudo().search([('requisition_rel_line_id','in',self.requisition_id.add_requisition_rel_ids.ids)])
            # if not exist_data:
            #     for rec in self.requisition_id.add_requisition_rel_ids:
            #         self.env['kw_requisition_requested'].sudo().create({
            #             'sequence':rec.sequence if rec.sequence else '',
            #             'item_code':rec.item_code.id if rec.item_code else False,
            #             'item_description':rec.item_description if rec.item_description else '',
            #             'uom':rec.uom if rec.uom else '',
            #             'quantity_required':rec.quantity_required if rec.quantity_required else False,
            #             'expected_days':rec.expected_days if rec.expected_days else False,
            #             'requisition_rel_id':rec.requisition_rel_id.id if rec.requisition_rel_id else False,
            #             'requisition_rel_line_id':rec.id,
            #             'order_qty':rec.quant_required if rec.quant_required else 0,
            #             'available_qty':rec.available_qty if rec.available_qty else 0,
            #             'remark':rec.remark if rec.remark else '',
            #             'item_in_stock':rec.item_in_stock if rec.item_in_stock else 0,
            #             'check_availability':rec.check_availability if rec.check_availability else False,
            #             'product_type':rec.product_type if rec.product_type else False,
            #             'product_template_id':rec.product_template_id.id if rec.product_template_id else False,
            #             'alternate_name':rec.alternate_name.id if rec.alternate_name else False,
            #             'stock_master_id':rec.stock_master_id.id if rec.stock_master_id else False,
            #             'employee_id':rec.employee_id.id if rec.employee_id else False,
            #             'requisition_remark':rec.requisition_remark if rec.requisition_remark else '',
            #             'action_on':rec.action_on if rec.action_on else False,
            #             'action_taken_on':rec.action_taken_on if rec.action_taken_on else False,
            #             'requisition_action_by':rec.requisition_action_by if rec.requisition_action_by else False,
            #             'quant_available':rec.quant_available if rec.quant_available else 0,
            #             'status':'Approved',
            #             'pending_at':rec.employee_id.department_id.manager_id.id if rec.employee_id.department_id.manager_id else False,
            #             'requirement_type':self.requisition_id.requirement_type if self.requisition_id.requirement_type else '',
            #             'project_code':self.requisition_id.project_code if self.requisition_id.project_code else '',
            #         })
            #     else:
            #         self.env.user.notify_success("Requisition is already created.")
            # template_id = self.env.ref('kw_inventory.kw_material_management_request_email_template')
            # email_to_user = self.requisition_id.employee_id.department_id.manager_id.work_email
            # user_name = self.requisition_id.employee_id.department_id.manager_id.name
            # template_id.with_context(email_to=email_to_user,user_name=user_name).send_mail(self.requisition_id.id,notif_layout="kwantify_theme.csm_mail_notification_light")
        elif self._context.get('send_back_request'):
            if self.requisition_id.state == 'Pending':
                self.requisition_id.write({"remark":self.remark,"state":'Draft',"pending_at":'---'})
                query = f"update kw_requisition_requested set status='Draft' where id in ({str(self.requisition_id.add_requisition_rel_ids.ids)[1:-1]})"
                self._cr.execute(query)
                # exist_data = self.env['kw_requisition_requested'].sudo().search([('requisition_rel_line_id','in',self.requisition_id.add_requisition_rel_ids.ids)])
                # if exist_data:
                #     for rec in exist_data:
                #         rec.state='Draft'
                # template_id = self.env.ref('kw_inventory.kw_material_management_request_send_back_email')
                # email_to_user = self.requisition_id.employee_id.department_id.manager_id.work_email
                # user_name = self.requisition_id.employee_id.department_id.manager_id.name
                # template_id.with_context(email_to=email_to_user,user_name=user_name).send_mail(self.requisition_id.id,notif_layout="kwantify_theme.csm_mail_notification_light")
        
        elif self._context.get('cancel_item_request'):
            if self.requisition_id.state == 'Pending':
                self.requisition_id.write({"remark":self.remark,"state":'Cancelled','pending_at':'---'})
                query = f"update kw_requisition_requested set status='Cancelled' where id in ({str(self.requisition_id.add_requisition_rel_ids.ids)[1:-1]})"
                self._cr.execute(query)
                # template_id = self.env.ref('kw_inventory.material_request_user_cancel_email_template')
                # email_to_user = self.requisition_id.employee_id.department_id.manager_id.work_email
                # user_name = self.requisition_id.employee_id.department_id.manager_id.name
                # template_id.with_context(email_to=email_to_user,user_name=user_name).send_mail(self.requisition_id.id,notif_layout="kwantify_theme.csm_mail_notification_light")
        elif self._context.get('reject_requisition'):
            if self.requisition_id.state == 'Pending' :
                # print("inside reject=========================================")
                action_id = self.env.ref('kw_inventory.kw_purchase_requisition_take_action_window').id
                self.requisition_id.write({"remark":self.remark,"state":'Rejected',"pending_at":'---'})
                emp_data = self.env['res.users'].sudo().search([])
                store_user = emp_data.filtered(lambda user: user.has_group('kw_inventory.group_store_manager') == True)
                store_user_mail = ','.join(store_user.mapped('employee_ids.work_email')) if store_user else ''
                store_user_name = ','.join(store_user.mapped('employee_ids.name')) if store_user else ''
                template_id = self.env.ref('kw_inventory.purchase_requisition_approved')
                for rec in self.requisition_id.add_requisition_rel_ids:
                    product = rec.product_template_id.name
                    product_code = rec.item_code.default_code
                    quantity =rec.quantity_required
                template_id.with_context(pr_user_mail=store_user_mail,pr_user_name=store_user_name,product=product,product_code=product_code,quantity=quantity).send_mail(self.requisition_id.id,notif_layout="kwantify_theme.csm_mail_notification_light")
                query = f"update kw_requisition_requested set status='Rejected' where id in ({str(self.requisition_id.add_requisition_rel_ids.ids)[1:-1]})"
                self._cr.execute(query)
        else:
            pass
        return {
                    'type': 'ir.actions.act_url',
                    'tag': 'reload',
                    'url': f'/web#action={action_id}&model=kw_purchase_requisition&view_type=list',
                    'target': 'self',
                }

class kwRequisitionHodRemark(models.TransientModel):
    _name = 'kw_requisition_hod_remark'
    _description = "Material Request"

    requisition_id = fields.Many2one('kw_requisition_requested', string="Requisition")
    remark = fields.Text(string='Remark')

    @api.multi
    def submit_hod_action(self):
        if self._context.get('submit_hod_approve'):
            self.requisition_id.write({"status":'Approved'})
            
            """ For P-Team requisition """
            if self.requisition_id.requisition_rel_id:
                self.requisition_id.requisition_rel_id.sudo().write({"state":'Approved'})
                self.requisition_id.requisition_rel_line_id.sudo().write({"status":'Approved'})
            """ For store manager requisition """
            if self.requisition_id.material_id and self.requisition_id.material_line_id:
                self.requisition_id.material_line_id.write({"order_status":'Approved'})
           
        elif self._context.get('submit_hod_reject'):
            self.requisition_id.write({"remark":self.remark,"status":'Rejected'})
            """ For P-Team requisition """
            if self.requisition_id.requisition_rel_id:
                self.requisition_id.requisition_rel_id.write({"state":'Cancelled'})
                self.requisition_id.requisition_rel_line_id.write({"status":'Rejected'})
            """ For store manager requisition """
            if self.requisition_id.material_id and self.requisition_id.material_line_id:
                self.requisition_id.material_line_id.write({"status":'Rejected'})

        else:
            pass
        action_id = self.env.ref('kw_inventory.kw_requisition_pending_action_window').id
        return {
                    'type': 'ir.actions.act_url',
                    'tag': 'reload',
                    'url': f'/web#action={action_id}&model=kw_requisition_requested&view_type=list',
                    'target': 'self',
                }