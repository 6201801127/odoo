# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models, tools
from odoo.http import request
from datetime import datetime


class KwGreetings(models.Model):
    _name = "hr_employee_greetings"
    _description = "HR Employee Greetings"

    _auto = False

    emp_id = fields.Many2one('hr.employee', string='Employee')
    name = fields.Char(string='Name', related="emp_id.name")
    department_id = fields.Many2one('hr.department', string='Department', related="emp_id.department_id")
    job_id = fields.Many2one('hr.job', string='Designation', related="emp_id.job_id")

    well_wish_id = fields.Many2one('kw_greetings_send_wishes', string='Well Wish Id')
    well_wish_subject = fields.Char(string='Well Wish Subject', related="well_wish_id.subject")
    formatted_wish_date = fields.Char(string='Well Wish Created Date')
    # well_wish_message    = fields.Text(string='Well Wish Subject',related="well_wish_id.message")

    greeting_type = fields.Selection(string="Greeting Type",
                                     selection=[('birth_day', 'Birth Day'), ('anniversary', 'Anniversary'),
                                                ('year_of_service', 'Year of Service'), ('well_wish', 'Well Wishes')])
    greeting_type_int = fields.Integer(string='Greetings')

    birthday = fields.Date(string='Birthday')
    birthday_month = fields.Integer(string='Birthday Month')
    birthday_day = fields.Integer(string='Birthday Day')
    formatted_birthday = fields.Char(string='Date of Birth')
    # birthday_today_date = fields.Date(string='Birthday Today Date')

    # today_month         = fields.Integer(string='Today Month') 
    # today_day           = fields.Integer(string='Today Day')

    date_of_joining = fields.Date(string='Work Anniversary')
    joining_month = fields.Integer(string='Work Anniversary Month')
    # joining_day             = fields.Integer(string='Work Anniversary Day')
    work_anniversary_years = fields.Integer(string='Work Anniversary Years')
    work_anniversary_day = fields.Char(string='Work Anniversary Formatted')
    # year_of_service_today_date  = fields.Date(string='Year of Service Today Date')

    # marital                 = fields.Many2one('kwemp_maritial_master', string='Marital Status')
    wedding_anniversary = fields.Date(string='Wedding Anniversary')
    anniversary_month = fields.Integer(string='Anniversary Month')
    # anniversary_day         = fields.Integer(string='Anniversary Day')
    formatted_wedding_anniversary = fields.Char(string='Formatted Wedding Anniversary')
    # anniversary_today_date  = fields.Date(string='Anniversary Today Date')

    send_wish_status = fields.Integer(string=u'Send Wish', )
    user_send_wish_status = fields.Integer(string=u'User Wish Status', compute='_get_user_send_wish_status',
                                           default=False)

    @api.model_cr
    def init(self):
        """ Event Question main report """
        tools.drop_view_if_exists(self._cr, 'hr_employee_greetings')
        self._cr.execute(""" CREATE VIEW hr_employee_greetings AS (
        SELECT
                'birth_day' AS greeting_type,
                1 AS greeting_type_int,
                CAST(concat(id,1) AS INT) AS id,
                id AS emp_id,
                CAST(NULL AS INT) AS well_wish_id,
                '' AS formatted_wish_date,
               
                CASE WHEN (date_part('month',birthday) = date_part('month', CURRENT_DATE)) AND (date_part('day',birthday) = date_part('day', CURRENT_DATE))    THEN 1 ELSE 0 END  AS send_wish_status,

                birthday,
                DATE_PART('month',birthday) AS birthday_month,
                DATE_PART('day',birthday) AS birthday_day,
                
                CASE WHEN birthday IS NOT NULL THEN to_char(birthday, 'DD Month') END  AS formatted_birthday ,

                CAST(NULL AS DATE) AS wedding_anniversary,
                0 AS anniversary_month,
                0 AS anniversary_day,
                '' AS formatted_wedding_anniversary,
                CAST(NULL AS DATE) AS date_of_joining,
                0 AS joining_month,
                0 AS joining_day,
                0 AS work_anniversary_years,
                '' AS work_anniversary_day
            FROM
                hr_employee 
            WHERE  
                active=True and birthday is not null 
                and employement_type in (select id from kwemp_employment_type where active=true and code != 'O')

            UNION

            SELECT
                'anniversary' AS greeting_type,                
                2 AS greeting_type_int,
                CAST(concat(id,2) AS INT) AS id,
                id AS emp_id,
                CAST(NULL AS INT) AS well_wish_id,
                '' AS formatted_wish_date,
               
                CASE WHEN (date_part('month',wedding_anniversary) = date_part('month', CURRENT_DATE)) AND (date_part('day',wedding_anniversary) = date_part('day', CURRENT_DATE))    THEN 1 ELSE 0 END  AS send_wish_status,	
                
                CAST(NULL AS DATE) AS birthday,
                0 AS birthday_month,
                0 AS birthday_day,
                '' AS formatted_birthday,
               
                wedding_anniversary,
                date_part('month',wedding_anniversary) AS anniversary_month,
                date_part('day',wedding_anniversary) AS anniversary_day,
                CASE WHEN wedding_anniversary IS NOT NULL THEN to_char(wedding_anniversary, 'DD Month') END  AS formatted_wedding_anniversary ,

                CAST(NULL AS DATE) AS date_of_joining,
                0 AS joining_month,
                0 AS joining_day,
                0 AS work_anniversary_years,
                '' AS work_anniversary_day
            FROM
                hr_employee 
            WHERE 
                active=True and wedding_anniversary is not null
                and employement_type in (select id from kwemp_employment_type where active=true and code != 'O')
            UNION

            SELECT
                'year_of_service' AS greeting_type,
                3 AS greeting_type_int,
                CAST(concat(id,3) AS INT) AS id,
                id AS emp_id, 
                CAST(NULL AS INT) AS well_wish_id,
                '' AS formatted_wish_date,       

                CASE WHEN (date_part('month',date_of_joining) = date_part('month', CURRENT_DATE)) and (date_part('day',date_of_joining) = date_part('day', CURRENT_DATE)) THEN 1 ELSE 0 END  as send_wish_status,	
                
                CAST(NULL AS DATE) AS birthday,
                0 AS birthday_month,
                0 AS birthday_day,
                '' AS formatted_birthday,                

                CAST(NULL AS DATE) AS wedding_anniversary,
                0 AS anniversary_month,
                0 AS anniversary_day,
                '' AS formatted_wedding_anniversary,                
                
                date_of_joining,	
                date_part('month',date_of_joining) AS joining_month,
                date_part('day',date_of_joining) AS joining_day,	
                DATE_PART('year', now()::date) - DATE_PART('year', date_of_joining::date) AS work_anniversary_years,
                CASE WHEN date_of_joining IS NOT NULL THEN to_char(date_of_joining, 'DD Month') END  as work_anniversary_day                    
            FROM
                hr_employee 
            WHERE
                active=True AND date_of_joining is not null AND (DATE_PART('year', now()::date) - DATE_PART('year', date_of_joining::date))>0
                and employement_type in (select id from kwemp_employment_type where active=true and code != 'O')
            UNION

            SELECT
                'well_wish' AS greeting_type,
                4 AS greeting_type_int,
                CAST(concat(send_wish_to,4,id) AS INT) AS id,
                send_wish_to AS emp_id,      
                id AS well_wish_id, 
                to_char(create_date, 'DD-Mon-YYYY') AS formatted_wish_date ,                          

                CASE WHEN (created_date_format = CURRENT_DATE) THEN 1 ELSE 0 END  AS send_wish_status,	                

                CAST(NULL AS DATE) AS birthday,
                0 AS birthday_month,
                0 AS birthday_day,
                '' AS formatted_birthday,                

                CAST(NULL AS DATE) AS wedding_anniversary,
                0 AS anniversary_month,
                0 AS anniversary_day,
                '' AS formatted_wedding_anniversary,                
                
                CAST(NULL AS DATE) AS date_of_joining,
                0 AS joining_month,
                0 AS joining_day,
                0 AS work_anniversary_years,
                '' AS work_anniversary_day      
            FROM
                kw_greetings_send_wishes 
            WHERE                
                created_date_format = CURRENT_DATE and wish_for = '4' and parent_id is null

            ORDER BY greeting_type_int, birthday_month, birthday_day, anniversary_month, anniversary_day, joining_month, joining_day     
        )""")

    # CAST(concat(send_wish_to,4,well_wish_id) AS INT) as id,
    @api.multi
    def button_send_wishes(self):

        view_id = self.env.ref('kw_greetings.kw_greetings_send_wishes_system_greeetings_form_view').id
        target_id = self.emp_id.id
        greetings_wish_for = str(self.greeting_type_int)
        default_parent_id = False

        greetings_default_category = False
        greetings_default_template = False
        default_wish_subject = False
        default_wish_message = False

        if self.greeting_type == 'birth_day':
            if request.env['ir.config_parameter'].sudo().get_param('kw_greetings.greetings_birthday_category'):
                greetings_default_category = int(
                    request.env['ir.config_parameter'].sudo().get_param('kw_greetings.greetings_birthday_category'))

        elif self.greeting_type == 'anniversary':
            if request.env['ir.config_parameter'].sudo().get_param('kw_greetings.greetings_anniversary_category'):
                greetings_default_category = int(
                    request.env['ir.config_parameter'].sudo().get_param('kw_greetings.greetings_anniversary_category'))

        elif self.greeting_type == 'year_of_service':
            if request.env['ir.config_parameter'].sudo().get_param('kw_greetings.greetings_year_of_service_category'):
                greetings_default_category = int(request.env['ir.config_parameter'].sudo().get_param(
                    'kw_greetings.greetings_year_of_service_category'))

        else:
            # if request.env['ir.config_parameter'].sudo().get_param('kw_greetings.greetings_well_wish_category'):
            greetings_default_category = self.well_wish_id.wish_category.id

            default_parent_id = self.well_wish_id.id
            default_wish_subject = self.well_wish_subject
            default_wish_message = self.well_wish_id.wish_message
            greetings_default_template = self.well_wish_id.template_id.id

        # print(greetings_default_category)

        if greetings_default_category and self.greeting_type_int != 4:
            greetings_default_template = int(request.env['kw_greetings_template'].sudo().search(
                [('category_id', '=', greetings_default_category), ('is_default', '=', True)], limit=1))

        return {
            'name': 'Send Wishes',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_greetings_send_wishes',
            # 'res_id': target_id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'views': [(view_id, 'form')],
            #  'view_id': view_id, {'emp_category': [('role_ids', '=', role_id)], }
            # 'domain' : [{'image_id': [('category_id', '=', 1)]}] , 'default_wish_message': 'Happy Birth Day', 'default_image_id':1,
            'context': {'default_send_wish_to': target_id, 'default_parent_id': default_parent_id,
                        'default_sender_id': self.env.uid, 'default_wish_for': greetings_wish_for,
                        'default_template_id': greetings_default_template,
                        'default_wish_category': greetings_default_category,
                        'default_wish_message': default_wish_message, 'default_wish_subject': default_wish_subject},

            'flags': {"toolbar": False},
        }

    # get current user
    @api.multi
    def _get_user_send_wish_status(self):
        for rec in self:
            if rec.greeting_type_int == 4:
                default_templaterec = self.env['kw_greetings_send_wishes'].sudo().search(
                    [('parent_id', '=', int(rec.well_wish_id.id)),
                     ('sender_id', '=', self.env.uid),
                     ('wish_for', '=', str(rec.greeting_type_int)),
                     ('send_wish_to', '=', rec.emp_id.id),
                     ('created_date_format', '=', datetime.now().strftime('%Y-%m-%d'))])
            else:
                default_templaterec = self.env['kw_greetings_send_wishes'].sudo().search(
                    [('parent_id', '=', False),
                     ('sender_id', '=', self.env.uid),
                     ('wish_for', '=', str(rec.greeting_type_int)),
                     ('send_wish_to', '=', rec.emp_id.id),
                     ('created_date_format', '=', datetime.now().strftime('%Y-%m-%d'))])

            rec.user_send_wish_status = len(default_templaterec)
