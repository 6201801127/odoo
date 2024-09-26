from odoo import models, fields, api,tools
from datetime import datetime,date
from ast import literal_eval
import requests


class CurrentDateMealReport(models.Model):
    _name="current_day_meal_report"
    _description = "Daily Meal Report"
    _auto=False

    veg_count = fields.Integer(string=" Total no. of Veg")
    non_veg_count = fields.Integer(string="Total no. of Non-veg")
    infra_loc_id = fields.Many2one("kw_res_branch_unit",string="Unit/Branch")
    recorded_date = fields.Date(string="Date")
    
    # whatsapp_template = fields.Many2one('kw_whatsapp_template', "WhatsApp Template",
    #                                     domain="[('model_id.model', '=', 'kw_announcement')]",
    #                                     ondelete='restrict')

    
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (            
        select row_number() over() as id, sum(m.no_of_veg)  AS veg_count ,
        sum(m.no_of_non_veg)  AS non_veg_count, 
        case 
        when  m.infra_unit_location_id is null then (select id from kw_res_branch_unit where code = 'hq') else m.infra_unit_location_id
        end as infra_loc_id,
        m.recorded_date as recorded_date
        from meal_bio_log m join hr_employee as e on m.employee_id = e.id 
        where m.recorded_date = CURRENT_DATE 
        group by infra_loc_id,m.recorded_date  
                        )""" % (self._table))

    # @api.model
    # def send_today_meals_details(self):
    #     today_meal = self.env['current_day_meal_report'].search([('recorded_date','=',date.today())])
    #     kw_whatsapp_message_log_model = self.env['kw_whatsapp_message_log']
    #     kw_whatsapp_message_log_data = []
    #     veg_count,nveg_count,non_veg_count,nnon_veg_count,mobile_no =0,0,0,0,0
    #     try:
    #         param = self.env['ir.config_parameter'].sudo()
    #         canteen_autorities = literal_eval(param.get_param('kw_canteen.notify_cook_ids'))
    #         if canteen_autorities:
    #             for rec in today_meal:
    #                 if rec.infra_loc_id.code != 'hq':
    #                     veg_count += rec.veg_count
    #                     non_veg_count += rec.non_veg_count
    #                 if rec.infra_loc_id.code == 'hq':
    #                     nveg_count += rec.veg_count
    #                     nnon_veg_count += rec.non_veg_count
    #             empls = self.env['hr.employee'].search([('id', 'in', canteen_autorities), ('active', '=', True)])
    #             whatsapp_template = self.env['kw_whatsapp_template'].sudo().search([('model_id.model', '=', 'current_day_meal_report')], limit=1)
    #             if whatsapp_template:
    #                 for record in empls:
    #                     mobile_no = '+91' + record.whatsapp_no
    #                     message = whatsapp_template.message.format(nveg_count=nveg_count,nnon_veg_count=nnon_veg_count,veg_count=veg_count,non_veg_count=non_veg_count)
    #                     html_msg = message.replace('\\n', '\n')
    #                     kw_whatsapp_message_log_data.append({'mobile_no': mobile_no, 'message': html_msg})
    #     except Exception as e:
    #         raise Warning("Some error occurred while sending whatsApp notification: %s" % str(e))
    #     if len(kw_whatsapp_message_log_data) > 0:
    #         kw_whatsapp_message_log_model.create(kw_whatsapp_message_log_data)
                
                
    @api.model
    def send_today_meals_details(self):
        today_meal = self.env['current_day_meal_report'].search([('recorded_date','=',date.today())])
        number_lst = []
        number = ''
        veg_count,nveg_count,non_veg_count,nnon_veg_count =0,0,0,0
        param = self.env['ir.config_parameter'].sudo()
        canteen_autorities = literal_eval(param.get_param('kw_canteen.notify_cook_ids'))
        if canteen_autorities:
            for rec in today_meal:
                if rec.infra_loc_id.code == 'camp-office':
                    veg_count += rec.veg_count
                    non_veg_count += rec.non_veg_count
                if rec.infra_loc_id.code == 'hq':
                    nveg_count += rec.veg_count
                    nnon_veg_count += rec.non_veg_count
            current_date = datetime.strptime(str(date.today()),"%Y-%m-%d").strftime("%d-%b-%Y")
            message_1 = f'Meal Report : {current_date} \n Location : CSM HQ \n Veg meal : {nveg_count} \n Non-veg meal : {nnon_veg_count} \n Location : Camp Office \n Veg meal : {veg_count} \n Non-veg meal : {non_veg_count}. \n CSM Technologies'
            html_msg = message_1.replace('\\n', '\n')
            message = html_msg
            empls = self.env['hr.employee'].search([('id', 'in', canteen_autorities), ('active', '=', True)])
            header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            for record in empls:
                number_lst.append(record.mobile_phone)
            number += ','.join(number_lst)
            url = f'https://api.bulksmsgateway.in/sendmessage.php?user=csmwebu&password=Csmpl$4980&mobile={number}&message={message}&sender=CSMTEC&type=3&template_id=1207165330538187709'
            response=requests.post(url, headers=header)
            self.env['kw_canteen_response_log'].sudo().create({
                'request_date': date.today(),
                'request':message,
                'response':response
            })
                
        
        
        
      