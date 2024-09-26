# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo import http
from odoo.http import request
import requests, json
from datetime import datetime,date,timedelta
from odoo.exceptions import ValidationError
import pytz


class kw_debtor_list_master(models.Model):
    _name = 'kw_debtor_list_master'
    _description = 'Debtor List Master'
    _rec_name = 'wo_code'

    kw_invoice_id = fields.Integer(string='KW Id')
    wo_code = fields.Char(string='WO Code')
    invoice_no = fields.Char(string='Invoice Number')
    invoice_date  = fields.Date()
    invoice_amt = fields.Float(string='Invoice Amount')
    pending_amt = fields.Float(string='Pending For Collection')
    expected_date  = fields.Date(string='Expeceted Collection Date')

    wo_id = fields.Integer()
    acc_manager_id = fields.Many2one('hr.employee')
    reviewer_id = fields.Many2one('hr.employee')
    teamleader_id = fields.Many2one('hr.employee')
    invoice_type = fields.Integer()
    updated_by = fields.Integer()
    account_manager_name = fields.Char()
    csg = fields.Char()
    client_address = fields.Char()
    client_name = fields.Char()
    last_updated_on = fields.Char()
    next_execution_time = fields.Char()

    action_log_ids = fields.One2many('kw_debtor_action_log','debt_port_id',string="Action log")
    active = fields.Boolean()
    bad_debtor_provision_amt = fields.Float()
    user_last_modified_date = fields.Datetime()



    @api.model
    def update_debt_model_field(self, rec_id, given_date):
        data = self.env['kw_debtor_list_master'].search([('id', '=', rec_id)])
        sync_data = self.env['kw_sync_portlet_data'].sudo().search([('rec_id', '=', rec_id), ('status', '=', 0)])
        if len(given_date) > 0:
            data.expected_date = given_date
            indian_timezone = pytz.timezone('Asia/Kolkata')
            current_datetime_utc = datetime.now(pytz.utc)
            current_datetime_in_indian = current_datetime_utc.astimezone(indian_timezone) - timedelta(hours=5,minutes=30)
            data.user_last_modified_date = current_datetime_in_indian.strftime('%Y-%m-%d %H:%M:%S %p')
            debt_port_log = self.env['kw_debtor_action_log']
            value = {
                'action_taken_date': date.today(),
                'action_taken_by_id': self.env.user.employee_ids.id,
                'changed_date': given_date,
                'debt_port_id': data.id,
            }
            debt_port_log.create(value)
            if not sync_data:
                sync_value = {
                    'model_id': 'kw_debtor_list_master',
                    'rec_id': rec_id,
                    'created_on': date.today(),
                    'status': 0,
                }
                sync_data.create(sync_value)
            else:
                pass
        else:
            raise ValidationError('Please provide a valid date..')







class DebtorDashboardLog(models.Model):
    _name = 'kw_debtor_action_log'
    _description= 'Debtor Dashboard Action Log'

    action_taken_date = fields.Date(string="Action taken Date")
    action_taken_by_id = fields.Many2one('hr.employee',string="Action taken By")
    changed_date = fields.Date(string="Changed Closing Date")
    debt_port_id = fields.Many2one('kw_debtor_list_master')
