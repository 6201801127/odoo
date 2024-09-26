import werkzeug

from odoo.api import Environment
import odoo.http as http

from odoo.http import request, Response
from odoo import SUPERUSER_ID, _
from odoo import registry as registry_get
import odoo.addons.calendar.controllers.main as main
import datetime
from datetime import date
from werkzeug.exceptions import BadRequest, Forbidden
from odoo.addons.restful.common import invalid_response
import ast
from ast import literal_eval
from odoo.exceptions import ValidationError
from odoo.exceptions import AccessError




class sbu_tagging_controller(http.Controller):
    @http.route('/approve/', methods=["GET"], type='http', csrf=False, auth="public", website=True)
    def approve_sbu_tagging(self):
        try:
            action_id = request.env.ref('kw_resource_management.sbu_approve_reject_action').id
            view_id = request.env.ref("kw_resource_management.sbu_approve_reject_view_form").id
            profile_url = '/web#view_type=tree&action=%s&model=sbu_approve_reject&view_id=%s' %(action_id,view_id)
            # print("in view action==============================",action_id,view_id,profile_url)
            return http.request.redirect(profile_url)
        except AccessError:
            return werkzeug.utils.redirect('/web/login?error=access')
            
        # data = ast.literal_eval(args)
        # fetch_employee = request.env['hr.employee'].sudo().browse(data['empl'])
        # history_tag = request.env['sbu_tag_untag_log'].sudo()

        # #Mail to rcm while approved
        # param = request.env['ir.config_parameter'].sudo()
        # emp_rcm_users = literal_eval(param.get_param('kw_resource_management.mail_to_rcm', '[]'))
        # emp_rcm_mail = request.env['hr.employee'].browse(emp_rcm_users).mapped('work_email')
        # get_employee_data = request.env['sbu_tagging_wizard'].sudo().browse(data['employee_data'])
        # email_to = ",".join(emp_rcm_mail) or ''
        # sbu = request.env['kw_sbu_master'].sudo().browse(data['sbu_id'])
        # acknowledge = 'Acknowledge'
        # c_date = date.today()
        # current_date = (c_date.strftime("%d-%b-%Y"))
        # template_obj = request.env.ref("kw_resource_management.rcm_mail_template")
        # existing_action_records = history_tag.search([('access_token', '=', str(data['token']))])

        # if existing_action_records:
        #     if 'tag' in existing_action_records.mapped('status'):
        #         # pass
        #         return http.request.render('kw_resource_management.approve_validation')
        #     if 'untag' in existing_action_records.mapped('status'):
        #         # pass
        #         return http.request.render('kw_resource_management.reject_validation')
        #         # pass
        

        # else:
        #     query = ''
        #     for rec in fetch_employee:
        #         data_get = {}
        #         query = f"update hr_employee set sbu_master_id = {sbu.id},sbu_type = '{data['sbu']}'where id = {rec.id}"
        #         request._cr.execute(query)

        #         data_get = {'employee_id': rec.id,
        #                     'status': 'tag',
        #                     'date': date.today(),
        #                     'action_by': data['action_by'],
        #                     'sbu_status': f"{rec.name} tagged to {sbu.name}",
        #                     'sbu_type': data['sbu'],
        #                     'sbu_id':sbu.name,
        #                     'access_token': data['token'],
        #                 }
        #         history_tag.create(data_get)

            # if template_obj:
            #     mail = request.env['mail.template'].browse(template_obj.id).with_context(
            #     email_to=email_to,acknowledge =acknowledge,date=current_date,sbu_head = sbu.representative_id.name,emp_data = get_employee_data).send_mail(get_employee_data.id,notif_layout='kwantify_theme.csm_mail_notification_light')

            # return http.request.render('kw_resource_management.approve_thankyou')
          


    # @http.route('/reject/', methods=["GET"], type='http', csrf=False, auth="public", website=True)
    # def reject_sbu_tagging(self, args):
    #     data = ast.literal_eval(args)
    #     fetch_employee = request.env['hr.employee'].sudo().browse(data['empl'])
    #     history_untag = request.env['sbu_tag_untag_log'].sudo()
        
    #     #Mail to rcm while rejected
    #     param = request.env['ir.config_parameter'].sudo()
    #     emp_rcm_users = literal_eval(param.get_param('kw_resource_management.mail_to_rcm', '[]'))
    #     emp_rcm_mail = request.env['hr.employee'].browse(emp_rcm_users).mapped('work_email')
    #     get_employee_data = request.env['sbu_tagging_wizard'].sudo().browse(data['employee_data'])
    #     email_to = ",".join(emp_rcm_mail) or ''
    #     sbu = request.env['kw_sbu_master'].sudo().browse(data['sbu_id'])
    #     reject = 'Rejected'
    #     c_date = date.today()
    #     current_date = (c_date.strftime("%d-%b-%Y"))
    #     template_obj = request.env.ref("kw_resource_management.rcm_mail_template")
    #     existing_action_records = history_untag.search([('access_token', '=', str(data['token']))])

    #     if existing_action_records:
    #         if 'untag' in existing_action_records.mapped('status'):
    #             # pass
    #             return http.request.render('kw_resource_management.reject_validation')
                
    #         if 'tag' in existing_action_records.mapped('status'):
    #             # pass
    #             return http.request.render('kw_resource_management.approve_validation')
    #             # pass
    #     else:
    #         query = ''
    #         for record in fetch_employee:
    #             query = f"update hr_employee set sbu_master_id = null,sbu_type = null where id = {record.id}"
    #             data_dict = {'employee_id': record.id,
    #                         'status': 'untag',
    #                         'date': date.today(),
    #                         'action_by': data['action_by'],
    #                         'sbu_status': f'{record.name} untagged from {record.sbu_master_id.name}' if record.sbu_master_id else f'{record.name} untagged',
    #                         'sbu_id':record.sbu_master_id.name,
    #                         'access_token': data['token'],
                            
    #             }
    #             request._cr.execute(query)
    #             history_untag.create(data_dict)
                    
    #         if template_obj:
    #             mail = request.env['mail.template'].browse(template_obj.id).with_context(
    #             email_to=email_to,reject = reject,sbu_head = sbu.representative_id.name,date = current_date ,emp_data = get_employee_data).send_mail(get_employee_data.id,notif_layout='kwantify_theme.csm_mail_notification_light')
                   
    #         return http.request.render('kw_resource_management.reject_thankyou')
                        
