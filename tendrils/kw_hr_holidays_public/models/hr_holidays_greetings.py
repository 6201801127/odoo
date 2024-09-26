# -*- coding: utf-8 -*-


from odoo import api, fields, models


class HolidayGreetings(models.Model):

    _name           = 'hr_holiday_greetings'
    _description    = "Holiday Greetings Wish."
    _rec_name       = 'year_id'


    year_id         = fields.Many2one('hr.holidays.public',string='Calendar Year',required=True)
    holiday         = fields.Many2one('hr.holidays.public.line', string ='Holiday' ,required=True)
    greeting        = fields.Html(string='Greetings')

    _sql_constraints = [('year_holiday_uniq', 'unique (year_id,holiday)','This holiday type already exist in same year!')]

    @api.onchange('year_id')
    def onchange_year(self):
        for rec in self:
            if rec.year_id:
                domain = []
                holiday_list = self.env['hr.holidays.public.line'].search([('year_id','=',rec.year_id.id)])
                for holiday in holiday_list:
                    domain.append(holiday.id)
                filter_domain = [('id','in',domain)]
                return {'domain':{'holiday':filter_domain}}

                                