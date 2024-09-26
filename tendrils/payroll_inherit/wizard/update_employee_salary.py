from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, time
from odoo.exceptions import ValidationError


class UpdateEmployeeSalary(models.TransientModel):
    _name = 'update_employee_salary'
    _description = 'Update Employee Salary'

    def _get_insurance_data(self):
        contract_ids = self.env.context.get('selected_active_ids')
        res = self.env['hr.contract'].sudo().search(
            [('id', 'in', contract_ids), ('state', '=', 'open')])
        return res

    contract_ids = fields.Many2many('hr.contract','contract_salary_rel','contract_id','salary_id',default=_get_insurance_data,string="Contract Details")


    


    @api.multi
    def update_emp_salary(self):
        for rec in self.contract_ids:
            query = ''
            query += f"update hr_employee set at_join_time_ctc = {rec.at_join_time_ctc},basic_at_join_time = {rec.basic_at_join_time},current_basic = {rec.current_basic} ,productivity = {rec.productivity}, commitment = {rec.commitment},conveyance = {rec.conveyance},current_ctc = {rec.wage},hra = {rec.house_rent_allowance_metro_nonmetro},esi_applicable = '{rec.esi_applicable}',is_consolidated = '{rec.is_consolidated}' WHERE id = {rec.employee_id.id};"
            if rec.bank_account:
                query += f"update hr_employee set bank_account = '{rec.bank_account}' WHERE id = {rec.employee_id.id};"
            if rec.bank_id:
                query += f"UPDATE hr_employee SET bankaccount_id = {rec.bank_id.id} WHERE id = {rec.employee_id.id};"
            if rec.struct_id:
                query += f"update hr_employee set struct_id = {rec.struct_id.id} WHERE id = {rec.employee_id.id};"
            if rec.enable_epf:
                query += f"update hr_employee set enable_epf = '{rec.enable_epf}' WHERE id = {rec.employee_id.id};"
            if rec.enable_gratuity:
                query += f"update hr_employee set enable_gratuity = '{rec.enable_gratuity}' WHERE id = {rec.employee_id.id};"
            if rec.pf_deduction != 'other':
                query += f"update hr_employee set pf_deduction = '{rec.pf_deduction}' WHERE id = {rec.employee_id.id};"
            if rec.uan_id:
                query += f"UPDATE hr_employee SET uan_id = '{rec.uan_id}' WHERE id = {rec.employee_id.id};"
            else:
                query += f"UPDATE hr_employee SET uan_id = '' WHERE id = {rec.employee_id.id};"
            if rec.esi_id:
                query += f"UPDATE hr_employee SET esi_id = '{rec.esi_id}' WHERE id = {rec.employee_id.id};"
            else:
                query += f"UPDATE hr_employee SET esi_id = '' WHERE id = {rec.employee_id.id};"



            self._cr.execute(query)
            



    @api.multi
    def update_nps_to_profile(self):
        for rec in self.contract_ids:
            query = ''
            if rec.is_nps:
                employee_check_query = f"SELECT id FROM nps_employee_data WHERE employee_id = {rec.employee_id.id};"
                self._cr.execute(employee_check_query)
                nps_id = self._cr.fetchone()
                is_nps = rec.is_nps if rec.is_nps else 'None'
                contribution = rec.contribution if rec.contribution else 'NULL'
                existing_pran_no = rec.existing_pran_no if rec.existing_pran_no else None
                pran_no = rec.pran_no if rec.pran_no else ''
                state = 'Not_started' if rec.is_nps == 'No' else 'Running' if rec.is_nps == 'Yes' and rec.pran_no else 'Requested'
                if nps_id:
                    query += f"UPDATE nps_employee_data SET is_nps='{is_nps}', contribution={contribution} , existing_pran_no='{existing_pran_no}', pran_no='{pran_no}', state='{state}',action_taken_date='{date.today().strftime('%Y-%m-%d')}' WHERE employee_id={rec.employee_id.id};"
                    if rec.pran_no:
                        template = self.env.ref('payroll_inherit.nps_enrolment_approved_mail_template')
                        email_to = rec.employee_id.work_email if rec.employee_id.work_email else []
                        cc_emails = ",".join(set(self.env['hr.employee'].sudo().search([('id', 'in', list(map(int, self.env['ir.config_parameter'].sudo().search([('key', '=', 'NPS Mail CC Employees')]).value.strip('[]').split(','))))]).mapped('work_email')))
                        applied_user = rec.employee_id.name if rec.employee_id.name else 'User'
                        subject_emp = f"{applied_user} ({rec.employee_id.emp_code})" if rec.employee_id.emp_code else applied_user
                        contribution = f"{rec.contribution}% of Basic Salary" if rec.contribution else None
                        pran_no = rec.pran_no if rec.pran_no else 'To be generated'
                        template.with_context(email_to=email_to,cc_emails=cc_emails,applied_user=applied_user,subject_emp=subject_emp,contribution=contribution,pran_no = pran_no).send_mail(nps_id[0],notif_layout="kwantify_theme.csm_mail_notification_light")

                else:
                    emp_query = f"""SELECT e.id, ep.id AS profile_id, ec.id AS contract_id FROM hr_employee e LEFT JOIN kw_emp_profile ep ON e.id = ep.emp_id LEFT JOIN hr_contract ec ON e.id = ec.employee_id WHERE e.id = {rec.employee_id.id};"""
                    self._cr.execute(emp_query)
                    emp_result = self._cr.fetchall()
                    profile_id = emp_result[0][1] if emp_result and emp_result[0][1] else 'NULL'
                    contract_id = emp_result[0][2] if emp_result and emp_result[0][2] else 'NULL'
                    state = 'Running' if rec.is_nps == 'Yes' else 'Not_started'
                    state = 'Not_started' if rec.is_nps == 'No' else 'Running' if rec.is_nps == 'Yes' and rec.pran_no else 'Requested'
                    query += f"INSERT INTO nps_employee_data (employee_id, is_nps, contribution, existing_pran_no, pran_no,emp_profile_id,emp_contract_id,state,action_taken_date) VALUES ({rec.employee_id.id}, '{is_nps}', {contribution}, '{existing_pran_no}', '{pran_no}',{profile_id}, {contract_id},'{state}','{date.today().strftime('%Y-%m-%d')}');"
                
            if query:
                self._cr.execute(query)
            