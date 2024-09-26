import base64
import datetime
from dateutil import relativedelta
from odoo import api, models, fields,_
from odoo.exceptions import UserError, ValidationError
import tempfile
from num2words import num2words
import os
import decimal
# from odoo.tools.profiler import profile



class AppraisalPublishMail(models.TransientModel):
    _name = 'appraisal_publish_wizard'
    _description = 'Appraisal wizard'

    def _get_default_appraisal(self):
        return self.env['shared_increment_promotion'].sudo().search([('id','in',self.env.context.get('active_ids')),('status','=','completed')])
    def _get_default_appraisal_resend_data(self):
        if len(self.env.context.get('active_ids')) == 1:
            self._cr.execute(f"select id from shared_increment_promotion where id = {self.env.context.get('active_ids')[0]} and status = 'resentdata_submitted_chro'")
        else:
            active_tuple = tuple(self.env.context.get('active_ids'))
            self._cr.execute(f"select id from shared_increment_promotion where id in {active_tuple} and status = 'resentdata_submitted_chro'")
        promotion_data = [row[0] for row in self._cr.fetchall()]
        return promotion_data

    appr = fields.Many2many('shared_increment_promotion','appraisal_completed_rel','wizard_id','appr_id', readonly=1, default=_get_default_appraisal)
    appr_ids = fields.Many2many('shared_increment_promotion','appraisal_resend_rel','wizard_id','appr_id', readonly=1, default=_get_default_appraisal_resend_data)
   
    def currencyInIndiaFormat(self,n):
        d = decimal.Decimal(str(n))
        if d.as_tuple().exponent < -2:
            s = str(n)
        else:
            s = '{0:.2f}'.format(n)
        l = len(s)
        i = l-1
        res = ''
        flag = 0
        k = 0
        while i >= 0:
            if flag == 0:
                res = res + s[i]
                if s[i] == '.':
                    flag = 1
            elif flag == 1:
                k = k + 1
                res = res + s[i]
                if k == 3 and i - 1 >= 0:
                    res = res + ','
                    flag = 2
                    k = 0
            else:
                k = k + 1
                res = res + s[i]
                if k == 2 and i - 1 >= 0:
                    res = res + ','
                    flag = 2
                    k = 0
            i = i - 1

        return res[::-1]
    
    def resend_appraisal_increment(self):
        for appraisal in self.appr_ids:
            employee_ids = appraisal.mapped('employee_id').ids
            if len(employee_ids) == 1:
                employee_id = employee_ids[0]
                self._cr.execute("""SELECT id, chro_actual_ctc, revised_ctc, increment_effective_date, revised_job_id, revised_jd_boolean, revised_grade_id, revised_band_id, period_id FROM shared_increment_promotion WHERE employee_id = %s AND status = 'resentdata_submitted_chro'""", (employee_id,))
                rec = self._cr.fetchone()
                if rec:
                    inc_id, chro_actual_ctc, revised_ctc, increment_effective_date, revised_job_id, revised_jd_boolean, revised_grade_id, revised_band_id, period_id = rec
                    incremented_ctc = self.currencyInIndiaFormat(chro_actual_ctc * 12) if chro_actual_ctc else 0
                    revised_increment_ctc = self.currencyInIndiaFormat(revised_ctc * 12) if revised_ctc else 0
                    new_ctc_per_month = self.currencyInIndiaFormat(revised_ctc) if revised_ctc else 0

                    job_role_id = self.env['hr.job.role'].search([('designations', 'in', [revised_job_id])], limit=1)
                    template = self.env.ref('kw_appraisal.kw_appraisal_only_increment_email_template')
                    employee = self.env['hr.employee'].browse(employee_id)
                    currency = employee.company_id.currency_id.name

                    a = template.with_context(
                        inc=revised_ctc if revised_ctc else 0,
                        incremented_ctc=f'{incremented_ctc} {currency}',
                        revised_increment_ctc=f'{revised_increment_ctc} {currency}',
                        monthly_revised_ctc=f'{new_ctc_per_month} {currency}',
                        effective_date=increment_effective_date,
                        jd=job_role_id.description if revised_jd_boolean else '',
                    ).send_mail(inc_id, notif_layout="kwantify_theme.csm_mail_notification_light")

                    body_html = self.env['mail.mail'].browse(a)

                    updates = {}
                    if revised_job_id:
                        updates['job_id'] = revised_job_id
                    if revised_grade_id:
                        updates['grade'] = revised_grade_id
                    if revised_band_id:
                        updates['emp_band'] = revised_band_id

                    if updates:
                        employee.sudo().write(updates)
                    
                    self.env.user.notify_info(message='Appraisal Published Successfully.')
                    
                    self._cr.execute("""UPDATE shared_increment_promotion SET status = 'settle' WHERE id = %s""", (inc_id,))
                    pdf_content = self.generate_pdf_from_email_content(body_html.body_html)
                    # Attach the PDF to the appraisal record
                    self.env['shared_increment_promotion'].browse(inc_id).write({ 'appraisal_doc_attach': base64.b64encode(pdf_content)})
                    self._cr.execute(f"select id from kw_emp_profile where emp_id = {employee_ids[0]}")
                    profile = self._cr.fetchone()
                    if profile:
                        self._cr.execute(f"select assessment_period from kw_assessment_period_master where id = {period_id}")
                        assessment_year = self._cr.fetchone()
                        self.env['appraisal_details_docs'].sudo().create({
                            'increment_id': inc_id,
                            'profile_id': profile[0],
                            'period_id': period_id,
                            'appraisal_doc_attach': base64.b64encode(pdf_content),
                            'file_name': f'{assessment_year[0]} - Appraisal Document'
                        })
                else:
                    pass
    @api.multi
    def process_eligible_users(self):
        for appraisal in self.appr:
            employee_ids = appraisal.mapped('employee_id').ids
            if len(employee_ids) == 1:
                employee_id = employee_ids[0]
                self._cr.execute("""
                    SELECT id, current_ctc, chro_amount_auto, chro_actual_ctc,new_job_id,employee_id,date_of_joining,increment_effective_date,jd_boolean,new_grade_id,new_band_id,period_id FROM shared_increment_promotion WHERE employee_id = %s AND status = 'completed'""", (employee_id,))
                rec = self._cr.fetchone()
                inc_id, current_ctc, chro_amount_auto, chro_actual_ctc, new_job_id, employee_id,date_of_joining,increment_effective_date,jd_boolean,new_grade_id,new_band_id,period_id = rec
                
                if inc_id:
                    current_ctc = self.currencyInIndiaFormat(current_ctc * 12)
                    increment_per_month = self.currencyInIndiaFormat(chro_amount_auto * 12)
                    new_ctc_per_annum = self.currencyInIndiaFormat(chro_actual_ctc * 12)
                    new_ctc_per_month = self.currencyInIndiaFormat(chro_actual_ctc)
                    
                    job_role_id = self.env['hr.job.role'].search([('designations', 'in', [new_job_id])], limit=1)
                    template = self.env.ref('kw_appraisal.kw_shared_appraisal_result_email_template')

                    diff = relativedelta.relativedelta(datetime.datetime.today().date(), date_of_joining)
                    employee_service_years = diff.years if diff.years > 0 else 1
                    # text_representation = num2words(employee_service_years)
                    employee = self.env['hr.employee'].browse(employee_id)
                    currency = employee.company_id.currency_id.name         
                    a = template.with_context(
                        current_ctc=f'{current_ctc} {currency}',
                        increment_per_month=f'{increment_per_month} {currency}',
                        increment_monthly=f'{new_ctc_per_month} {currency}',
                        new_ctc_per_annum=f'{new_ctc_per_annum} {currency}',
                        experience=f"{employee_service_years} {'years' if employee_service_years > 1 else 'year'}",
                        effective_date = increment_effective_date,
                        # text_representation = text_representation,
                        jd=job_role_id.description if jd_boolean ==  True else '',
                        ).send_mail(inc_id, notif_layout="kwantify_theme.csm_mail_notification_light")

                    body_html = self.env['mail.mail'].browse(a)

                    updates = {}
                    if new_job_id:
                        updates['job_id'] = new_job_id
                    if new_grade_id:
                        updates['grade'] = new_grade_id
                    if new_band_id:
                        updates['emp_band'] = new_band_id

                    if updates:
                        employee.sudo().write(updates)
                    self.env.user.notify_info(message='Appraisal Published Successfully.')  
                    self._cr.execute("""UPDATE shared_increment_promotion SET status = 'mail_send' WHERE id = %s""", (inc_id,))
                    
                    pdf_content = self.generate_pdf_from_email_content(body_html.body_html)
                    inc = self.env['shared_increment_promotion'].browse(inc_id)
                    inc.write({
                        'appraisal_doc_attach': base64.b64encode(pdf_content),
                    })
                    self._cr.execute(f"select id from kw_emp_profile where emp_id = {employee_ids[0]}")
                    profile = self._cr.fetchone()
                    if profile:
                        self._cr.execute(f"select assessment_period from kw_assessment_period_master where id = {period_id}")
                        assessment_year = self._cr.fetchone()
                        self.env['appraisal_details_docs'].sudo().create({
                            'increment_id': inc_id,
                            'profile_id': profile[0],
                            'period_id': period_id,
                            'appraisal_doc_attach': inc.appraisal_doc_attach,
                            'file_name': f'{assessment_year[0]} - Appraisal Document'
                        })

                else:
                    pass

    def generate_pdf_from_email_content(self, email_content):
        pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        if not isinstance(email_content, str):
            email_content = str(email_content)

        encoded_content = email_content.encode('utf-8')

        html_file_path = tempfile.NamedTemporaryFile(delete=False, suffix='.html').name
        with open(html_file_path, 'wb') as html_file:
            html_file.write(encoded_content)

        wkhtmltopdf_command = f'wkhtmltopdf {html_file_path} {pdf_file.name}'

        os.system(wkhtmltopdf_command)
        os.remove(html_file_path)
        with open(pdf_file.name, 'rb') as pdf_file:
            pdf_content = pdf_file.read()

        os.remove(pdf_file.name)

        return pdf_content




          