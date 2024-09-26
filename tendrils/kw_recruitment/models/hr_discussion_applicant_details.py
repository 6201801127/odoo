from odoo import models, fields, api
from odoo.exceptions import UserError
from io import BytesIO
import base64
from datetime import date,datetime

class ApplicantHRDiscussionDetails(models.Model):
    _name = 'hr_discussion_applicant_details'
    _description = 'Discussion Details'

    applicant_id = fields.Many2one('hr.applicant', string='Applican"s Name', ondelete='cascade')
    # designation = fields.Many2one('kw_hr_job_positions', string='Designation')
    designation_id = fields.Many2one('hr.job',string="Designation")
    department = fields.Many2one('hr.department', string='Department',domain=[('dept_type.code', '=', 'department')])
    # section = fields.Many2one('hr.department', string="Section")
    date_of_joining = fields.Date(string='Date of Joining')
    job_location = fields.Many2one('kw_recruitment_location',string='Job Location')
    # employment_type = fields.Many2one('kwemp_employment_type',string='Employment Type',domain=[('code','in',['P','S','C'])])
    employment_type = fields.Selection([('FTE', 'FTE'), ('RET', 'RET'),('Traineeship','Traineeship')],string="Employment Type")
    contract_duration = fields.Integer(string="Contract Duration (in months)")
    traineeship_duration = fields.Integer(string="Traineeship Duration (in Months)")
    probation = fields.Integer(string='Probation (in Months)')
    appraisal_eligibility = fields.Selection([('post_completeion', 'Post completion of Probation Period'),('post_completion_traineeship','Post Completion of Traineeship Period')], string="Appraisal Eligibility",)

    increment_eligibility = fields.Date(string='Increment Eligibility')
    service_agreement_required = fields.Selection([('Yes', 'Yes'), ('No', 'No')], string="Service Agreement ")
    service_agreement = fields.Integer(string="Service Agreement (in Months)")
    open_for_travel = fields.Selection([('1', 'Yes'), ('0', 'No')], string="Open for Travel (Int / Dom)",)
    relocation = fields.Selection([('1', 'Yes'), ('0', 'No')], string="Relocation (ST / LT)",)
    non_joining_clients_competitors = fields.Selection([('two_years_from_separation', 'Till 2 Years From the date of exit.')], string="Non-Joining Clients & Competitors",)
    annual_compensation = fields.Integer(string='Annual Compensation')
    provident_fund = fields.Selection([('12_%_basic', '12% of Basic to be deducted each from Employee and Employer part'),('1800_inr_to_be_deducted','1800 INR to be deducted each from Employee and Employer part'),('not_applicable','Not Applicable')],string='Provident Fund')
    gratuity = fields.Selection([('to_be_deducted', 'To be deducted as per Gratuity Act, 1972 ')],string='Gratuity')
    health_insurance = fields.Selection([('health_insurance', 'Health Insurance of 3 Lacs Coverage for Employee sponsored by CSM'), ('esi', ' ESI '),('not_applicable','Not Applicable')],string='Health Insurance / ESI')
    hr_discuss_mail = fields.Selection([('1', 'Yes'), ('0', 'No')], string="Hr Discuss Mail Sent ?")
    
    show_contract_fields = fields.Boolean(string='Show Contract Fields',)
    show_traineeship_fields = fields.Boolean(string="Show Traineeship Fields")
    status = fields.Selection([('Accept', 'Accept'), ('Decline', 'Decline')],string="Status",)
    currency_id = fields.Many2one('res.currency', string='Currency',)


    @api.onchange('employment_type')
    def _onchange_employment_type(self):
        if self.employment_type == 'Traineeship':
            self.show_traineeship_fields = True
            self.show_contract_fields = False
            self.probation = False
            self.appraisal_eligibility = False
            self.increment_eligibility = False
            self.gratuity = False
            self.provident_fund = False
            self.health_insurance = False
            self.non_joining_clients_competitors = False
            self.open_for_travel = False
            self.relocation =  False
            self.annual_compensation = False
            self.currency_id = False
            self.service_agreement = False
            self.service_agreement_required = False


        elif self.employment_type == 'RET':
            self.show_contract_fields = True
            self.show_traineeship_fields = False
            self.gratuity = False
            self.probation = False
            self.appraisal_eligibility = False
            self.increment_eligibility = False
            self.non_joining_clients_competitors = False
            self.open_for_travel = False
            self.relocation =  False
            self.annual_compensation = False
            self.provident_fund = False
            self.health_insurance = False
            self.currency_id = False
            self.service_agreement = False
            self.service_agreement_required = False
        else:
            self.show_contract_fields = False
            self.show_traineeship_fields = False
            self.traineeship_duration = False
            self.contract_duration = False
            self.probation = False
            self.appraisal_eligibility = False
            self.increment_eligibility = False
            self.gratuity = False
            self.provident_fund = False
            self.health_insurance = False
            self.non_joining_clients_competitors = False
            self.open_for_travel = False
            self.relocation =  False
            self.annual_compensation = False
            self.currency_id = False
            self.service_agreement = False
            self.service_agreement_required = False

    @api.depends('employment_type')
    def _compute_show_contract_fields(self):
        for rec in self:
            rec.show_contract_fields = rec.employment_type == 'RET'
            rec.show_traineeship_fields = rec.employment_type == 'Traineeship'

    def hr_discussion_download(self):
        return {
            'type': 'ir.actions.act_url',
            'url': f'/hr-view-HRDiscussion-form/{self.id}',
            'target': 'new',
        }
    
        # result_url = f"/update-bank-details/{slug(current_employee)}"

    def send_hr_discussion_mail(self):
        template_id = self.env.ref('kw_recruitment.hr_discussion_mail_template')
        for record in self:
            pdf = self.env.ref('kw_recruitment.download_hr_discussion_certification').render_qweb_pdf([record.id])[0]
            pdf_base64 = base64.b64encode(pdf)
            attachment = self.env['ir.attachment'].create({
                'name': 'HR Discussion.pdf',
                'type': 'binary',
                'datas': pdf_base64,
                'datas_fname': 'HR Discussion.pdf',
                'res_model': 'hr_discussion_applicant_details',
                'res_id': record.id,
                'mimetype': 'application/pdf'
            })
        applicant_data = self.env['hr_discussion_applicant_details'].search([('id','=',record.id),('applicant_id','=',record.applicant_id.id)])
        if applicant_data:

            applicant_token = self.env['kw_recruitment_requisition_approval'].create(
                {'mrf_id': applicant_data.applicant_id.mrf_id.id if applicant_data.applicant_id.mrf_id else False,
                'applicant_id': applicant_data.applicant_id.id})
            db_name = self._cr.dbname
            if template_id:
                mail = self.env['mail.template'].browse(template_id.id).with_context(
                    dbname=db_name, email_to = self.applicant_id.email_from,
                    token=applicant_token.access_token,discussion_id=applicant_data.id)
                send_mail = mail.send_mail(self.applicant_id.id,notif_layout='kwantify_theme.csm_mail_notification_light')
                current_mail = self.env['mail.mail'].browse(send_mail)
                current_mail.attachment_ids = [(6, 0, [attachment.id])]
            applicant_data.applicant_id.hr_discussion_mail = '1'

            # applicant_data.write({'hr_discuss_mail': '1'})
            
        else:

            applicant_data.create({'applicant_id':self.applicant_id,'designation':self.designation,'department':self.department,'date_of_joining':self.date_of_joining,
            'job_location':self.job_location,'employment_type':self.employment_type,'probation':self.probation,'appraisal_eligibility':self.appraisal_eligibility,
            'increment_eligibility':self.increment_eligibility,'open_for_travel':self.open_for_travel,'relocation':self.relocation,
            'non_joining_clients_competitors':self.non_joining_clients_competitors,'annual_compensation':self.annual_compensation,
            'provident_fund':self.provident_fund,'gratuity':self.gratuity,'health_insurance':self.health_insurance,'hr_discuss_mail':'1'})

            applicant_token = self.env['kw_recruitment_requisition_approval'].create(
                {'mrf_id': self.applicant_id.mrf_id.id if self.applicant_id.mrf_id else False,
                'applicant_id': self.applicant_id.id})
            db_name = self._cr.dbname
            if template_id:
                mail = self.env['mail.template'].browse(template_id.id).with_context(
                    dbname=db_name, email_to = self.applicant_id.email_from,
                    token=applicant_token.access_token)
                send_mail = mail.send_mail(self.applicant_id.id,notif_layout='kwantify_theme.csm_mail_notification_light')
                current_mail = self.env['mail.mail'].browse(send_mail)
                current_mail.attachment_ids = [(6, 0, [attachment.id])]
            applicant_data.applicant_id.hr_discussion_mail = '1'
        self.env.user.notify_success("Mail Sent successfully.")

   