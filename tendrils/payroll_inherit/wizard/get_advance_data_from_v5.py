import string
from odoo import fields, models, api
import json
import requests
# from datetime import datetime, date
from dateutil import relativedelta

import calendar
import datetime
from math import ceil, floor


class AdvanceData(models.TransientModel):
    _name = "advance_data"
    _description = "get advance data from v5"

    get_data = fields.Selection([('advance_details', 'Advance Details'), ('emi_details', 'EMI Details')], default='advance_details', string='Get Data')
    advance_id = fields.Many2one('kw_advance_apply_salary_advance', string="Advance ID", domain="[('kw_id','!=',False)]")
    page_no = fields.Integer(string="Page No", required=True)
    page_size = fields.Integer(string="Page Size", required=True)

    @api.onchange('get_data')
    def _onchange_apply_for(self):
            self.advance_id = False
            self.page_size = False
            self.page_no = False

    def get_advance_data(self):
        parameter_url = self.env['ir.config_parameter'].sudo().get_param('kwantify_advance_data_url')
        # print(".......................", parameter_url)
        if parameter_url:
            header = {'Content-type': 'application/json', 'Accept': 'text/plain'}

            advance = self.advance_id.kw_id if self.advance_id.kw_id else 0
            advance_data_dict = {
                "AdvanceId": advance,
                "PageNo": self.page_no,
                "PageSize": self.page_size,
            }
            resp = requests.post(parameter_url, headers=header, data=json.dumps(advance_data_dict))
            j_data = json.dumps(resp.json())
            json_record = json.loads(j_data)
            if json_record:
                record_lst = list(map(lambda x : x['AdvanceID'],json_record))
                advance_data = self.env['kw_advance_apply_salary_advance'].sudo().search([('kw_id', 'in', record_lst)])
                query = ""
                for rec in json_record:
                    
                    filtered_advance_data = advance_data.filtered(lambda x: x.kw_id == int(rec['AdvanceID']))
                    check_employee = self.env['hr.employee'].sudo().search([('kw_id', '=', int(rec['Name']))])
                    if check_employee:
                        # apply_date=  datetime.datetime.strptime(rec['AppliedDate'], "%d-%b-%Y").date()
                        require_date =  datetime.datetime.strptime(rec['RequireDate'], "%d-%b-%Y").date()
                        release_date =  datetime.datetime.strptime(rec['ReleaseDate'], "%d-%b-%Y").date()
                        state = 'paid' if rec['Status']=='111' else 'release'
                        if filtered_advance_data:
                            # update the attendance record
                            query += f"update kw_advance_apply_salary_advance set total_install={rec['AdvanceID']},adv_amnt={rec['PaidAmount']},req_date='{require_date}',payment_date='{release_date}',adv_purpose={self.env['kw_advance_purpose'].sudo().search([],limit=1).id},description='Migrated from V5' , state = '{state}' where id = {filtered_advance_data.id};"
                        else:
                            query += f"insert into kw_advance_apply_salary_advance (name,applicant,kw_id,employee_id,total_install,currency_id,adv_amnt,req_date,payment_date,state,adv_purpose,description) values('{self.env['ir.sequence'].next_by_code('kw_apply_salary_advance') or '/'}','self',{rec['AdvanceID']},{check_employee.id},{rec['Installment']},{check_employee.company_id.currency_id.id},{rec['PaidAmount']},'{require_date}','{release_date}','{state}',{self.env['kw_advance_purpose'].sudo().search([],limit=1).id},'Migrated Fron V5');"
                        

                if len(query) > 0:
                    # print('query=======',query)
                    self._cr.execute(query)
            
            self.env['advance_log'].sudo().create(
                {'request_params': advance_data_dict, 'response_result': json_record})


    def get_emi_data(self):
        parameter_url = self.env['ir.config_parameter'].sudo().get_param('kwantify_emi_data_url')
        # print(".......................", parameter_url)
        if parameter_url:
            header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            advance = self.advance_id.kw_id if self.advance_id.kw_id else 0
            advance_data_dict = {
                "AdvanceId": advance,
                "PageNo": self.page_no,
                "PageSize": self.page_size,
            }
            resp = requests.post(parameter_url, headers=header, data=json.dumps(advance_data_dict))
            j_data = json.dumps(resp.json())
            json_record = json.loads(j_data)
            self.env['advance_log'].sudo().create(
                    {'request_params': advance_data_dict, 'response_result': json_record})


