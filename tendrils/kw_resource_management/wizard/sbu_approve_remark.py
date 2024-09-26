from odoo import api, fields, models, tools, _
from datetime import date, datetime
import calendar
from ast import literal_eval




class SBUApproveRemark(models.TransientModel):
    _name = "sbu_approve_remark"
    _description = "SBU Approve Remark"
    
    
    remark = fields.Text()
    
    
    def approve_btn(self):
        if self.env.context.get('current_id'):
            sbu_approve_data = self.env['sbu_approve_reject'].sudo().search([('id','=', self.env.context.get('current_id'))])
            # print(sbu_approve_data,"sbu_approve_data>>>>>>>>>>>>>>>>>>>>>>>>>>....................................")
            if sbu_approve_data:
                sbu_approve_data.write({
                    'state':'approve',
                    'remark':self.remark
                })
              
                query = ''
                sbu_id = sbu_approve_data.sbu_master_id.id
                if sbu_approve_data.primary_skill_id:
                    query = f"update hr_employee set sbu_master_id ={sbu_id},sbu_type = '{sbu_approve_data.sbu_type}',primary_skill_id={sbu_approve_data.primary_skill_id.id} where id = {sbu_approve_data.emp_id.id}"
                else:
                    query = f"update hr_employee set sbu_master_id ={sbu_id},sbu_type = '{sbu_approve_data.sbu_type}' where id = {sbu_approve_data.emp_id.id}"
                self._cr.execute(query)
                history_tag = self.env['sbu_tag_untag_log'].sudo()

                data_get = {'employee_id': sbu_approve_data.emp_id.id,
                            'status': 'tag',
                            'date': date.today(),
                            'action_by': self.env.user.employee_ids.id,
                            'sbu_status': f"{sbu_approve_data.emp_id.name} tagged to {sbu_approve_data.sbu_master_id.name}",
                            'sbu_type': sbu_approve_data.sbu_type,
                            'sbu_id':sbu_approve_data.sbu_master_id.name,
                            # 'access_token': data['token'],
                        }
                history_tag.create(data_get)

                #Mail to rcm while rejected
                param = self.env['ir.config_parameter'].sudo()
                emp_rcm_users = literal_eval(param.get_param('kw_resource_management.mail_to_rcm', '[]'))
                emp_rcm_mail = self.env['hr.employee'].browse(emp_rcm_users).mapped('work_email')
                email_to = ",".join(emp_rcm_mail) or ''
                state = sbu_approve_data.state
                sbu_head = sbu_approve_data.sbu_master_id.representative_id.name
                sbu_approve_data = sbu_approve_data.id
                c_date = date.today()
                current_date = (c_date.strftime("%d-%b-%Y"))
                template_obj = self.env.ref("kw_resource_management.rcm_mail_template")


                    
                if template_obj:
                    mail = self.env['mail.template'].browse(template_obj.id).with_context(
                    email_to=email_to,state_approve = state,sbu_head = sbu_head,date=current_date,sbu_approve_data=sbu_approve_data).send_mail(sbu_approve_data,notif_layout='kwantify_theme.csm_mail_notification_light')
              
