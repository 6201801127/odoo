from odoo import models, fields, api
import requests, json
from datetime import datetime


class kw_apply_salary_advance(models.Model):
    _inherit = 'kw_advance_apply_salary_advance'

    kw_id = fields.Integer('KW ID')
    kw_status = fields.Char('KW Status')

    @api.multi
    def write(self, vals):
        enable_api = self.env['ir.config_parameter'].sudo().get_param('kw_advance_claim.advance_api')
        if vals.get('state') == 'grant' and not self.kw_id and enable_api:
            employee = self.env['hr.employee'].search([('user_id', '=', self.create_uid.id)])
            """Advance API -- UserAdvanceEntry"""
            parameterurl = self.env['ir.config_parameter'].sudo().get_param('kwantify_advance_url')
            AdvanceEntryURL = parameterurl + 'UserAdvanceEntry'
            header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            values = {
                "UserID": self.employee_id.kw_id,
                "AmountRequired": self.adv_amnt_required,
                "installment": self.total_install,
                "RequiredDate": self.req_date.strftime("%d-%b-%Y"),
                "AdvanceType": 1,
                "Advancecause": self.adv_purpose.kw_id,
                "Currency": self.currency_id.name,
                "Remarks": self.remark,
                "status": 3,
                "ApproveBy": self.approval_id.kw_id,
                "ApprovedAmount": self.approval_amount,
                "GrantedBy": self.action_taken_by.kw_id,
                "GrantedAmount": self.adv_amnt,
                "PaymentDate": self.write_date.strftime("%d-%b-%Y"),
                "CreatedBy": employee.kw_id,
                "ProjectType": "",
                "Projectid": 0,
                "Emistartdate": self.emi_start_date.strftime("%d-%b-%Y")
            }
            resp = requests.post(AdvanceEntryURL, headers=header, data=json.dumps(values))
            j_data = json.dumps(resp.json())
            json_record = json.loads(j_data)
            self.create_log(json_record, values, name='Salary Advance Creation')
            ##
            for rec in json_record:
                if rec.get('Status') == '3':
                    vals['kw_id'] = rec.get('AdvanceID')

            if vals.get('kw_id', False):
                """ Add EMI to kwantify """
                count = 0
                # line_list = []
                for line in self.deduction_line_ids:
                    count += 1
                    installments = {
                        "AdvanceID": vals.get('kw_id'),
                        "Month": line.month,
                        "Year": line.year,
                        "Amount": line.principal_amt,
                        "EMIAmountwithIntrest": line.amount,
                        "Paymentdate": line.payment_date.strftime("%d-%b-%Y"),
                        "CreatedBy": employee.kw_id,
                        "Interest": line.monthly_interest,
                        "installmentNo": count,
                        "Paidstatus": 0,
                        "AccountpaidStatus": 0,
                        "AdvanceDeTID": 0
                    }
                    InstallmentEntryURL = parameterurl + 'employee_SalaryAdvance_EMIUPD'
                    response = requests.post(InstallmentEntryURL, headers=header, data=json.dumps(installments))
                    data = json.dumps(response.json())
                    jsonrec = json.loads(data)
                    self.create_log(jsonrec, installments, name='Installment Details')

                    for rec in jsonrec:
                        if rec.get('Status') == '1':
                            line.kw_id = rec.get('AdvanceDeTID')
                    # line_list.append(installments)

        return super(kw_apply_salary_advance, self).write(vals)

    def get_emi_details(self):
        """Advance API -- employee_SalaryAdvance_EMIDetails"""
        enable_api = self.env['ir.config_parameter'].sudo().get_param('kw_advance_claim.advance_api')
        if enable_api:
            parameterurl = self.env['ir.config_parameter'].sudo().get_param('kwantify_advance_url')
            EMIDetailsURL = parameterurl + 'employee_SalaryAdvance_EMIDetails'
            header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            values = {
                "AdvanceID": self.kw_id
            }
            resp = requests.post(EMIDetailsURL, headers=header, data=json.dumps(values))
            j_data = json.dumps(resp.json())
            json_record = json.loads(j_data)
            if json_record != []:
                for rec in json_record:
                    if rec.get('Paymentdate'):
                        line = self.deduction_line_ids.filtered(
                            lambda r: r.deduction_date.strftime("%b-%Y") == datetime.strptime(rec.get('Paymentdate'),
                                                                                            '%d-%b-%Y').strftime("%b-%Y"))
                        if line:
                            status = 'draft'
                            if rec.get('Paidstatus') == 2:
                                status = 'paid'
                            line.write({'status': status})

    def create_log(self, json_record, values, name=False):
        self.env['kw_kwantify_integration_log'].sudo().create({
            'name': name,
            # 'error_log': error_log,
            # 'new_record_log': new_record_string,
            'response_result': json_record,
            'request_params': values,
        })
