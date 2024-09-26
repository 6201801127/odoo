# -*- coding: utf-8 -*-
import pytz
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, tools, _


class kw_vc_apply_report(models.Model):
    _name = "kw_vc_apply_report"
    _description = "visiting card apply report"
    _auto = False

    emp_name = fields.Char(string='Employee Name')
    applied_date = fields.Date(string='Applied On')
    no_of_cards_required = fields.Integer(string='No Of Cards Required')
    date_when_required = fields.Date(string='Required On')
    status = fields.Char(string='Status')
    vendername = fields.Char(string='Vendor Name')
    sentforprinting = fields.Date(string='Sent For Printing On')
    deliveredtouser = fields.Date(string='Delivered To User On')
    dept_name = fields.Char(string='Department Name')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(""" CREATE or REPLACE VIEW %s as (
          select b.id, a.name as emp_name, applied_date as applied_date, no_of_cards_required as no_of_cards_required, d.name as dept_name,
          date_when_required as date_when_required , state as status, c.name as vendername,
          (select action_date from kw_visiting_card_details where card_id=b.id and action_status='Sent For Printing') as sentforprinting,
        (select action_date from kw_visiting_card_details where card_id=b.id and action_status='Delivered to User') as deliveredtouser
            from kw_visiting_card_apply b  
            join hr_employee a  on a.id = b.emp_name
            left join res_partner c on c.id = b.vendor_name
            left join hr_department d on a.department_id = d.id
        )""" % (self._table))

    def view_vc_details(self):
        result_id = self.env['kw_visiting_card_apply'].browse(self.id)
        view_id = self.env.ref('kw_visiting_card.kw_apply_card_form_view').id
        if len(result_id):
            return {
                'name': 'Business Card Details',
                'type': 'ir.actions.act_window',
                'res_model': 'kw_visiting_card_apply',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': result_id.id,
                'view_id': view_id,
                'target': 'same',
                'flags': {'mode': 'readonly'},
            }
        else:
            pass
