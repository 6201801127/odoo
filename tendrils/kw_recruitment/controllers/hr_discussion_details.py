from odoo import http, _
from odoo.http import request
from odoo.exceptions import ValidationError
import base64
from odoo import models, fields, api
from odoo import http, _
from odoo.api import Environment
from odoo import http, registry as registry_get, SUPERUSER_ID
from datetime import date, timedelta,datetime






class RecruitmentHRDiscussion(http.Controller):
    
    @http.route('/hr-view-HRDiscussion-form/<int:id>', type='http', auth='user', csrf=False ,methods=['GET'],website=True)
    def redirect_bank_screen(self, id,**args):
        applicant_id = id
        master_data = {}
        data = request.env['hr_discussion_applicant_details'].sudo().search([('id','=',applicant_id)])
        # master_data['banks'] = banks
        if data:
        # Prepare the data to be passed to the template
            data_dict = {'docs': data}
            return http.request.render("kw_recruitment.hr_discussion_certifcate_download_template", data_dict)
        else:
            return http.request.redirect('/web')

    @http.route('/get-hr-discussion-details/<int:applicant_id>/<int:id>', type='http', auth="user")
    def get_hr_discussion_details(self, applicant_id=None,id=None, **kwargs):
        if not id:
            raise ValidationError("Invalid ID provided.")
        else:
            applicant = applicant_id
            employee_data = request.env['hr_discussion_applicant_details'].sudo().search([('applicant_id','=',applicant),('id','=',id)],limit=1)
        if not employee_data:
            raise ValidationError("Discussion details not found for this ID.")
        else:
            report_template = request.env.ref('kw_recruitment.download_hr_discussion_certification').sudo().render_qweb_pdf(employee_data.id)
            return request.make_response(
                report_template,
                headers=[('Content-Type', 'application/pdf'),
                         ('Content-Disposition', f'attachment; filename="{employee_data.applicant_id.partner_name}.pdf"')]
            )
            
    
    @http.route('/recruitment/hr/discussion/approve', type='http', auth="public", website=True)
    def approve(self, db, token,name='', id='',discuss_id=''):
        try:
            id = int(id)
        except ValueError:
            return request.not_found()  
        registry = registry_get(db)
        with registry.cursor() as cr:
            env = Environment(cr, SUPERUSER_ID, {})
            applicant_mrf = env['hr.applicant'].browse(id)
            hrdiscusstoken = env['kw_recruitment_requisition_approval'].sudo().search(
                [('mrf_id', '=', applicant_mrf.mrf_id.id), ('applicant_id', '=', id), ('access_token', '=', token)]
            )
            if not hrdiscusstoken:
                return request.not_found()
            else:
                applicant = hrdiscusstoken.sudo().applicant_id
                if name == '':
                    name =applicant.partner_name
            record = env['hr_discussion_applicant_details'].sudo().search(
                [('applicant_id', '=', applicant.id),('id','=',discuss_id)])
            if record.status == 'Accept':
                    return request.render('kw_recruitment.hr_discussion_already_approved_button_redirect')
                
            if record.status == 'Decline':
                return request.render('kw_recruitment.hr_discussion_already_rejected_button_redirect')
            
            if not record.status == 'Accept':
                mail_to=record.create_uid.email
                template_obj= request.env.ref('kw_recruitment.hr_discussion_acceptance_mail_template')				
                recruitment_group =request.env.ref('kw_recruitment.group_tag_budget_user')
                recruitment_emp =recruitment_group.sudo().users and recruitment_group.sudo().users.mapped('employee_ids') or False
                email_cc_users = recruitment_emp and recruitment_emp.sudo().mapped('work_email') or []
                cc_emails = ','.join(set(email_cc_users))

                mail = request.env['mail.template'].sudo().browse(template_obj.id).with_context(
                    name=name,
                    mail_to=mail_to,
                    cc_emails=cc_emails,acceptance_date=datetime.now().strftime('%d %B %Y'),).send_mail(applicant.id,
                            notif_layout='kwantify_theme.csm_mail_notification_light')
                applicant.write({'hr_discussion_status': 'approved'})
                record.write({'status': 'Accept'})
                request.env.user.notify_success(_("Mail sent successfully."))
                return request.render('kw_recruitment.hr_discussion_approve_button_redirect')

    @http.route('/recruitment/hr/discussion/reject', type='http',auth="public", website=True)
    def reject(self, db, token,name='', id='',discuss_id=''):
        try:
            id = int(id)
        except ValueError:
            return request.not_found()  

        registry = registry_get(db)
        with registry.cursor() as cr:
            env = Environment(cr, SUPERUSER_ID, {})
            applicant_mrf = env['hr.applicant'].browse(id)
            hrdiscusstoken = env['kw_recruitment_requisition_approval'].sudo().search(
                [('mrf_id', '=', applicant_mrf.mrf_id.id), ('applicant_id', '=', id), ('access_token', '=', token)]
            )
            if not hrdiscusstoken:
                return request.not_found()
            else:
                applicant = hrdiscusstoken.sudo().applicant_id
                if name == '':
                    name =applicant.partner_name
            record = env['hr_discussion_applicant_details'].sudo().search(
                [('applicant_id', '=', applicant.id),('id','=',discuss_id)])
            
            if record.status == 'Accept':
                    return request.render('kw_recruitment.hr_discussion_already_approved_button_redirect')
                
            if record.status == 'Decline':
                return request.render('kw_recruitment.hr_discussion_already_rejected_button_redirect')
            
            if not record.status == 'Decline':
                mail_to=record.create_uid.email
                template_obj= request.env.ref('kw_recruitment.hr_discussion_decline_mail_template')				
                recruitment_group =request.env.ref('kw_recruitment.group_tag_budget_user')
                recruitment_emp =recruitment_group.sudo().users and recruitment_group.sudo().users.mapped('employee_ids') or False
                email_cc_users = recruitment_emp and recruitment_emp.sudo().mapped('work_email') or []
                cc_emails = ','.join(set(email_cc_users))

                mail = request.env['mail.template'].sudo().browse(template_obj.id).with_context(
                    name=name,
                    mail_to=mail_to,
                    cc_emails=cc_emails,
                    rejection_date=datetime.now().strftime('%d %B %Y'),).send_mail(applicant.id,
                            notif_layout='kwantify_theme.csm_mail_notification_light')
                applicant.write({'hr_discussion_status': 'rejected'})
                record.write({'status': 'Decline'})
                request.env.user.notify_success(_("Mail sent successfully."))
                return request.render('kw_recruitment.hr_discussion_reject_button_redirect')

            #     record = request.env['hr_discussion_applicant_details'].sudo().search([('applicant_id', '=', hrdiscusstoken.applicant_id.id),('applicant_id.hr_discussion_status','not in',['approved','rejected'])])
            #     if record:
            #         record.applicant_id.write({'hr_discussion_status': 'rejected'})

            # elif hrdiscusstoken.applicant_id.hr_discussion_status == 'approved':
                
            #     return http.request.render('kw_recruitment.hr_discussion_already_approved_button_redirect')

            # else:
            #     return http.request.render('kw_recruitment.hr_discussion_already_rejected_button_redirect')

            
            # return http.request.render('kw_recruitment.hr_discussion_reject_button_redirect')



    

   