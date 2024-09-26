from odoo import http
from odoo.addons.http_routing.models.ir_http import unslug
from odoo.http import request
import jwt
import odoo
from odoo import models, fields, api, _

# key = 'chalhatpagle'
key = ",jy`\;4Xpe7%KKL$.VNJ'.s6)wErQa"

class IntermediateWebsitePage(http.Controller):
    @http.route(['/login/intermediate'], type='http', auth="user", website=True)
    def intermediate_detail(self, user_id=None, **post):
        activity,emp_list=[],[]
        user_id = request.env.user
        access_type=[]
        connection_rec=request.env['server.connection'].search([], limit=1)
        base_url= http.request.env["ir.config_parameter"].sudo().get_param("web.base.url").strip()
        url=str(connection_rec.url).strip()
        lab_id = http.request.env['ir.model.data'].sudo().search([('name', '=', 'action_building_configuration'), ('module', '=', 'gts_coe_management')])
        asset_id = http.request.env['ir.model.data'].sudo().search([('name', '=', 'action_account_asset_asset_form'), ('module', '=', 'account_asset')])
        service_id = http.request.env['ir.model.data'].sudo().search([('name', '=', 'action_comman_available_service_menu'), ('module', '=', 'coe_service_management')])
        appraisal_menu = http.request.env['ir.model.data'].sudo().search([('name', '=', 'appraisal_menu_new_action')])
        # print("==========appraisal_menu=============",appraisal_menu,appraisal_menu.res_id)

        asset_url = http.request.env["ir.config_parameter"].sudo().get_param("web.base.url").strip()
        asset_url += ('/web#id=' + '&action=' + str(asset_id.res_id) + '&model=account.asset.assets&view_type=list')
        service_url = base_url + ('/web#id=' + '&action=' + str(service_id.res_id) + '&model=product.product&view_type=kanban')
        lab_url = http.request.env["ir.config_parameter"].sudo().get_param("web.base.url").strip()
        lab_url += ('/web#id=' + '&action=' + str(lab_id.res_id) + '&model=building.configuration&view_type=list')
        encoded_jwt = jwt.encode({'token': user_id.token}, key)
        coe,hrms,coe_hrms,coehrms,asset,services,floor,all = '','','','','','','',''

        for access in user_id.access_type_ids:
            if access.name == 'COE':
                coe = 'COE'
            if access.name == 'HRMS':
                hrms = 'HRMS'
            if access.name == 'COE And HRMS':
                coe_hrms = 'COE And HRMS'
            if access.name == 'STPI Next':
               coehrms = 'COE With HRMS'
            if access.name == 'Asset':
               asset = 'Asset'
            if access.name == 'Services':
               services = 'Services'
            if access.name == 'Floor Plan':
                floor = 'Floor Plan'
        employee_id = request.env['hr.employee'].search([('user_id','=',user_id.id)],limit=1)
        emp_dic={'image':employee_id.image,
                 'department_name':employee_id.department_id.name,
                 'job_name':employee_id.job_id.name,
                 'emp_code':employee_id.emp_code,
                 'emp_name':employee_id.name,
                 'branch_name':employee_id.branch_id.name,
                 'joining_date':employee_id.joining_date,
                 }
        emp_list.append(emp_dic)
        activity_ids = request.env['mail.activity'].search([('user_id','=',user_id.id)])
        for act_id in activity_ids:
            act_dic={
                     'activity_name':act_id.activity_type_id.name,
                     'summary':act_id.summary,
                     'date':act_id.create_date.strftime('%d-%m-%Y'),
            }
            activity.append(act_dic)
        # print("==================login password=============",url, request.env.user.login,str(encoded_jwt.decode("utf-8")),)
        if user_id:
            partner_sudo = request.env['res.users'].sudo().browse(user_id)
            if partner_sudo.exists():
                values = {
                    'login_user': partner_sudo,
                    'access_type': access_type,
                    'edit_page': True,
                    'coe' :coe,
                    'hrms' :hrms,
                    'coe_hrms' :coe_hrms,
                    'coehrms' :coehrms,
                    'all' :all,
                    'services' :services,
                    'asset' :asset,
                    'floor' :floor,
                    'url': url,
                    'asset_url': asset_url,
                    'lab_url': lab_url,
                    'service_url': service_url,
                    'base_url': base_url,
                    'login':request.env.user.login,
                    'instance_type':connection_rec.instance_type,
                    'password':str(encoded_jwt.decode("utf-8")),
                    'activity': activity,
                    'emp_list': emp_list,
                    'appraisal_menu': str(1615),
                    'employee_id': str(employee_id.id),
                    'activity_count': len(activity_ids),
                }
                return request.render("gts_switcher.intermediate_page", values)
        return request.not_found()

