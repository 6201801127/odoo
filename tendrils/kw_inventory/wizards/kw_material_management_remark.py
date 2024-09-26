import datetime
from datetime import timedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import uuid


class kwMaterialManagementUserRemark(models.Model):
    _name = 'kw_material_management_user_remark'
    _description = "Material Request"

    def _default_access_token(self):
        return uuid.uuid4().hex
    
    access_token = fields.Char('Token', default=_default_access_token)
    material_id = fields.Many2one('kw_material_management', string="Material")
    remark = fields.Text(string='Remark')

    @api.multi
    def submit_user_action(self):
        if (self._context.get('submit_material_request') or self._context.get('record_set')) and not (self._context.get('cancel_item_request') or self._context.get('send_back_request')):
            self.material_id.write({"remark":self.remark,"state":'Pending'})
            self.material_id.assign_pending_at()
            self.material_id.material_log.create({
                    "action_taken_by": self.env.user.employee_ids.id,
                    "material_id":self.material_id.id ,
                    "product_id": ','.join([rec.item_code.name for rec in self.material_id.add_product_items_ids]),
                    "action_remark": self.remark,
                    "status": 'Pending',
                })
            mrfview = self.env.ref('kw_inventory.kw_material_request_take_action_window')
            action_id = self.env['ir.actions.act_window'].search([('id', '=', mrfview.id)], limit=1).id
            # print('action id================',action_id)
            db_name = self._cr.dbname
            self.material_id.add_product_items_ids.write({"remark":self.remark,"status":'Pending'})
            template_id = self.env.ref('kw_inventory.kw_material_management_request_email_template')
            template_id.with_context(dbname=db_name,
                        action_id=action_id,
                        token=self.access_token,

                        email_to=self.material_id.employee_id.sbu_master_id.representative_id.work_email if self.material_id.employee_id.sbu_master_id else self.material_id.employee_id.division.manager_id.work_email if self.material_id.employee_id.division.manager_id else self.material_id.employee_id.department_id.manager_id.work_email,

                        emp_code= self.material_id.employee_id.sbu_master_id.representative_id.emp_code if self.material_id.employee_id.sbu_master_id else self.material_id.employee_id.division.manager_id.emp_code if self.material_id.employee_id.division.manager_id else self.material_id.employee_id.department_id.manager_id.emp_code,

                        department=self.material_id.employee_id.department_id.name,
                        date = self.material_id.date,

                        user_name=self.material_id.employee_id.sbu_master_id.representative_id.name if self.material_id.employee_id.sbu_master_id else self.material_id.employee_id.division.manager_id.name if self.material_id.employee_id.division.manager_id else self.material_id.employee_id.department_id.manager_id.name,).send_mail(self.material_id.id,notif_layout="kwantify_theme.csm_mail_notification_light")
            self.env.user.notify_success("Material Request Send For Approval Successfully.")

            # # Add line on the basis of no of items required.
            # product_items = self.env['kw_add_product_items']
            # data_list = []
            # record_set = product_items.sudo().browse(int(self._context.get('record_set'))) if self._context.get('record_set') else False
            # if not record_set:
            #     record_set = self.material_id.add_product_items_ids
            # for record in record_set:
            #     count=0
            #     qty = record.item_code.qty_available
            #     for range_data in range(record.quantity_required):
            #         data = {
            #             "status": "Draft",
            #             "material_rel_id": self.material_id.id,
            #             "product_type":record.product_type,
            #             "product_template_id":record.product_template_id.id,
            #             "item_code":record.item_code.id,
            #             "item_description": record.item_description,
            #             "uom":record.uom,
            #             "quantity_required":1,
            #             "expected_days":record.expected_days,
            #             "check_availability":record.check_availability,
            #             "employee_id":record.employee_id.id,
            #             "status":'Pending',
            #             "item_in_stock":qty
            #             }
            #             # "item_in_stock":qty - count if qty > 0 else 0
            #         count += 1
            #         data_list.append(data)
            # query = f"delete from  kw_add_product_items where id in ({str(record_set.ids)[1:-1]})"
            # self._cr.execute(query)
            # for rec in data_list:
            #     product_items.sudo().create(rec)
        elif self._context.get('send_back_request'):
            if self.material_id.state == 'Pending':
                self.material_id.write({"remark":self.remark,"state":'Draft',"pending_at":False})
                query = f"update kw_add_product_items set status='Draft' where id in ({str(self.material_id.add_product_items_ids.ids)[1:-1]})"
                self._cr.execute(query)
                template_id = self.env.ref('kw_inventory.kw_material_management_request_send_back_email')

                email_to_user = self.material_id.employee_id.sbu_master_id.representative_id.work_email if self.material_id.employee_id.sbu_master_id else self.material_id.employee_id.division.manager_id.work_email if self.material_id.employee_id.division.manager_id else self.material_id.employee_id.department_id.manager_id.work_email

                sbu_emp_code= self.material_id.employee_id.sbu_master_id.representative_id.emp_code if self.material_id.employee_id.sbu_master_id else self.material_id.employee_id.division.manager_id.emp_code if self.material_id.employee_id.division.manager_id else self.material_id.employee_id.department_id.manager_id.emp_code

                user_name = self.material_id.employee_id.sbu_master_id.representative_id.name if self.material_id.employee_id.sbu_master_id else self.material_id.employee_id.division.manager_id.name if self.material_id.employee_id.division.manager_id else self.material_id.employee_id.department_id.manager_id.name

                user_code= self.material_id.employee_id.emp_code

                template_id.with_context(email_to=email_to_user,user_name=user_name,sbu_emp_code=sbu_emp_code,user_code=user_code).send_mail(self.material_id.id,notif_layout="kwantify_theme.csm_mail_notification_light")
            self.material_id.material_log.create({
                "action_taken_by": self.env.user.employee_ids.id,
                "material_id": self.material_id.id,
                "product_id": ','.join([rec.item_code.name for rec in self.material_id.add_product_items_ids]),
                "action_remark": self.remark,
                "status": 'Draft',
            })

        elif self._context.get('cancel_item_request'):
            if self.material_id.state == 'Pending':
                self.material_id.write({"remark":self.remark,"state":'Cancelled',"pending_at":False})
                query = f"update kw_add_product_items set status='Cancelled' where id in ({str(self.material_id.add_product_items_ids.ids)[1:-1]})"
                self._cr.execute(query)
                template_id = self.env.ref('kw_inventory.material_request_user_cancel_email_template')

                email_to_user = self.material_id.employee_id.sbu_master_id.representative_id.work_email if self.material_id.employee_id.sbu_master_id else self.material_id.employee_id.division.manager_id.work_email if self.material_id.employee_id.division.manager_id else self.material_id.employee_id.department_id.manager_id.work_email

                sbu_emp_code= self.material_id.employee_id.sbu_master_id.representative_id.emp_code if self.material_id.employee_id.sbu_master_id else self.material_id.employee_id.division.manager_id.emp_code if self.material_id.employee_id.division.manager_id else self.material_id.employee_id.department_id.manager_id.emp_code

                user_name = self.material_id.employee_id.sbu_master_id.representative_id.name if self.material_id.employee_id.sbu_master_id else self.material_id.employee_id.division.manager_id.name if self.material_id.employee_id.division.manager_id else self.material_id.employee_id.department_id.manager_id.name
                
                user_code= self.material_id.employee_id.emp_code
                template_id.with_context(email_to=email_to_user,user_name=user_name,sbu_emp_code=sbu_emp_code,user_code=user_code).send_mail(self.material_id.id,notif_layout="kwantify_theme.csm_mail_notification_light")
            self.material_id.material_log.create({
                    "action_taken_by": self.env.user.employee_ids.id,
                    "material_id":self.material_id.id ,
                    "product_id": ','.join([rec.item_code.name for rec in self.material_id.add_product_items_ids]),
                    "action_remark": self.remark,
                    "status": 'Cancelled',
                })
        else:
            pass
        # return {'type': 'ir.actions.act_window_close'}
        action_id = self.env.ref('kw_inventory.kw_material_request_action_window').id
        return {
                    'type': 'ir.actions.act_url',
                    'tag': 'reload',
                    'url': f'/web#action={action_id}&model=kw_material_management&view_type=list',
                    'target': 'self',
                }


class kwMaterialManagementHodRemark(models.TransientModel):
    _name = 'kw_material_management_hod_remark'
    _description = "Material Request"

    material_id = fields.Many2one('kw_material_management', string="Material")
    remark = fields.Text(string='Remark')

    @api.multi
    def submit_hod_action(self):
        if self._context.get('submit_hod_approve'):
            self.material_id.write({"state":'Approved'})
            self.material_id.assign_pending_at()
            self.material_id.material_log.create({
                    "action_taken_by": self.env.user.employee_ids.id,
                    "material_id":self.material_id.id ,
                    "action_remark": self.remark,
                    "product_id": ','.join([rec.item_code.name for rec in self.material_id.add_product_items_ids]),
                    "status": 'Approved',
                })
            emp_data = self.env['res.users'].sudo().search([])
            store_manager = emp_data.filtered(lambda user: user.has_group('kw_inventory.group_store_manager')==True)
            cc_mail=','.join(store_manager.mapped('employee_ids.work_email')) if store_manager else ''
            template_id = self.env.ref('kw_inventory.kw_material_management_approve_email')
            template_id.with_context(to_mail=self.material_id.employee_id.work_email,
                                    cc_mail=cc_mail,

                                    email_from=self.material_id.employee_id.sbu_master_id.representative_id.work_email if self.material_id.employee_id.sbu_master_id else self.material_id.employee_id.division.manager_id.work_email if self.material_id.employee_id.division.manager_id else self.material_id.employee_id.department_id.manager_id.work_email,

                                    hod_name=self.material_id.employee_id.sbu_master_id.representative_id.name if self.material_id.employee_id.sbu_master_id else self.material_id.employee_id.division.manager_id.name if self.material_id.employee_id.division.manager_id else self.material_id.employee_id.department_id.manager_id.name,

                                    sbu_code=self.material_id.employee_id.sbu_master_id.representative_id.emp_code if self.material_id.employee_id.sbu_master_id else self.material_id.employee_id.division.manager_id.emp_code if self.material_id.employee_id.division.manager_id else self.material_id.employee_id.department_id.manager_id.emp_code,

                                    user_name = self.material_id.employee_id.name,
                                    user_code=self.material_id.employee_id.emp_code,
                                    department =self.material_id.employee_id.department_id.name,
                                    date = self.material_id.date,
                                    product_data = self.material_id.add_product_items_ids,
                                    sequence=self.material_id.item_sequence,).send_mail(self.material_id.id,notif_layout="kwantify_theme.csm_mail_notification_light")
            #  Add line on the basis of no of items required.
            product_items = self.env['kw_add_product_items']
            data_list = []
            record_set = self.material_id.add_product_items_ids
            for record in record_set:
                count=0
                qty = record.item_code.qty_available
                for range_data in range(int(record.quantity_required)):
                    data = {
                        "status": "Draft",
                        "material_rel_id": self.material_id.id,
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
            self._cr.execute(query)
            for rec in data_list:
                product_items.sudo().create(rec)
            
        elif self._context.get('submit_hod_reject'):
            self.material_id.write({"remark":self.remark,"state":'Rejected','pending_at':False})
            self.material_id.material_log.create({
                    "action_taken_by": self.env.user.employee_ids.id,
                    "material_id":self.material_id.id ,
                    "action_remark": self.remark,
                    "product_id": ','.join([rec.item_code.name for rec in self.material_id.add_product_items_ids]),
                    "status": 'Rejected',
                })
            query = f"update kw_add_product_items set status='Rejected',remark='Remark by {self.env.user.employee_ids.name}-{self.remark}' where id in ({str(self.material_id.add_product_items_ids.ids)[1:-1]})"
            self._cr.execute(query)
            template_id = self.env.ref('kw_inventory.kw_material_management_reject_email_template')
            # print("sequence==========================",self.material_id,self.material_id.item_sequence)
            template_id.with_context(to_mail=self.material_id.employee_id.work_email,
            
                                    email_from=self.material_id.employee_id.sbu_master_id.representative_id.work_email if self.material_id.employee_id.sbu_master_id else self.material_id.employee_id.division.manager_id.work_email if self.material_id.employee_id.division.manager_id else self.material_id.employee_id.department_id.manager_id.work_email,

                                    hod_name=self.material_id.employee_id.sbu_master_id.representative_id.name if self.material_id.employee_id.sbu_master_id else self.material_id.employee_id.division.manager_id.name if self.material_id.employee_id.division.manager_id else self.material_id.employee_id.department_id.manager_id.name,

                                    sbu_code=self.material_id.employee_id.sbu_master_id.representative_id.emp_code if self.material_id.employee_id.sbu_master_id else self.material_id.employee_id.division.manager_id.emp_code if self.material_id.employee_id.division.manager_id else self.material_id.employee_id.department_id.manager_id.emp_code,

                                    user_name = self.material_id.employee_id.name,
                                    user_code=self.material_id.employee_id.emp_code,
                                    department =self.material_id.employee_id.department_id.name,
                                    date = self.material_id.date,
                                    product_data = self.material_id.add_product_items_ids,
                                    sequence=self.material_id.item_sequence,).send_mail(self.material_id.id,notif_layout="kwantify_theme.csm_mail_notification_light")
        else:
            pass

        action_id = self.env.ref('kw_inventory.kw_material_request_action_window').id
        return {
                    'type': 'ir.actions.act_url',
                    'tag': 'reload',
                    'url': f'/web#action={action_id}&model=kw_material_management&view_type=list',
                    'target': 'self',
                }

        

class kwMaterialManagementStoreManagerRemark(models.TransientModel):
    _name = 'kw_material_management_store_management_remark'
    _description = "Wizard: Material Store manager Remark"

    material_id = fields.Many2one('kw_material_management', string="Material")
    message = fields.Text(string="Message")
    remark = fields.Text(string='Remark')
    log_id = fields.Many2one('kw_product_assign_release_log', string="Log")
    

    @api.multi
    def submit_store_manager_action(self):
        if self._context.get('store_manager_assign'):
                
            non_rejected_data = self.material_id.add_product_items_ids.filtered(lambda x: x.status =='Approved' and x.is_rejected == False)
            for rec in non_rejected_data:
                query = f"update stock_quant set is_issued=True,employee_id={rec.employee_id.id},material_ref_no={self.material_id.item_sequence} where id = {rec.stock_master_id.id}"
                self._cr.execute(query)
            #update parent and child status
            req_data = self.material_id.add_product_items_ids.filtered(lambda x: x.status in ['Requisition_Approved','Quotation_Created','Negotiation'])
            if not req_data:
                self.material_id.write({"state":'Issued','remark':self.remark})
            else:
                raise ValidationError("You cannot Assign unless all products are available.")
            query = f"update kw_add_product_items set status='Issued',remark='{self.remark}' where id in ({str(non_rejected_data.ids)[1:-1]})"
            self._cr.execute(query)
            for rec in non_rejected_data:
                self.log_id.create({
                    "assigned_on":self.write_date,
                    "products": rec.item_code.id,
                    "quantity": rec.quantity_required,
                    "assigned_to": rec.employee_id.id,
                    "materil_id":rec.stock_master_id.id ,
                    "action_by": self.env.user.employee_ids.name,
                    "status": 'Issued',
                })
               
                    
        elif self._context.get('store_manager_reject'):
            non_issued_data = self.material_id.add_product_items_ids.filtered(lambda x: x.status =='Approved' and x.status !='Issued' and x.is_rejected == False)
            query = f"update kw_add_product_items set status='Rejected',remark='{self.remark}' where id in ({str(non_issued_data.ids)[1:-1]})"
            self._cr.execute(query)
            #update issue or reject state on the basis of differnt cases
            issued_data = self.material_id.add_product_items_ids.filtered(lambda x: x.status =='Issued')
            hold_data = self.material_id.add_product_items_ids.filtered(lambda x: x.status in ['Hold'])
            req_data = self.material_id.add_product_items_ids.filtered(lambda x: x.status in ['Requisition_Approved','Quotation_Created','Negotiation'])
            if issued_data and not hold_data:
                self.material_id.write({"remark":self.remark,"state":'Issued'})
            else:
                if not req_data:
                    self.material_id.write({"remark":self.remark,"state":'Rejected'})
        else:
            pass
