from odoo import http, _, SUPERUSER_ID
from odoo.http import request
import base64
import odoo
import socket
import requests
from datetime import datetime
from odoo.addons.web.controllers.main import serialize_exception,content_disposition
import mimetypes
from odoo.addons.web.controllers.main  import Home as HomeBase


# -----block started------for tracking user login detail(lat,lng & ip_add)-------------------
class CustomController(HomeBase):
    def get_public_ip(self):
        try:
            # Use a dummy socket connection to get the public IP address
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            public_ip = s.getsockname()[0]
            s.close()
            return public_ip
        except socket.error as e:
            print(f"Error getting public IP: {e}")
            return None
        
    def get_current_location(self):
        try:
            # Make a request to the ipinfo.io API
            response = requests.get('https://ipinfo.io')
            data = response.json()

            # Extract latitude and longitude from the response
            if 'loc' in data:
                latitude, longitude = map(float, data['loc'].split(','))
                return latitude, longitude
            else:
                print("Location not found in the response.")
                return None, None
        except Exception as e:
            print(f"Error: {e}")
            return None, None
    
    def update_lat_long_record(self,login):
        public_ip = self.get_public_ip()
        current_latitude, current_longitude = self.get_current_location()
        employee = request.env['res.users'].sudo().search([('login','=',login)],limit=1)
        employee_name = request.env['hr.employee'].sudo().search([('user_id','=',employee.id)],limit=1)
        record = request.env['user_login_detail']
        record.create({
            'user_id': employee.id,
            'name': employee_name.name,
            'date_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'ip_address': public_ip,
            'status': "logged into website",
            'lat': current_latitude,
            'lng': current_longitude
        })
        

    @http.route('/web/login', type='http', auth='none')
    def web_login(self, redirect=None, **kw):
        values = request.params.copy()
        # Your custom logic here
        if request.httprequest.method == 'POST':
            old_uid = request.uid
            try:
                uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
                request.params['login_success'] = True
                login = request.params['login']
                self.update_lat_long_record(login)
                return http.redirect_with_hash(self._login_redirect(uid, redirect=redirect))
            except odoo.exceptions.AccessDenied as e:
                request.uid = old_uid
                if e.args == odoo.exceptions.AccessDenied().args:
                    values['error'] = _("Wrong login/password")
                else:
                    values['error'] = e.args[0]
        result = super(CustomController, self).web_login(**kw)
        return result
# ----------------------block end -----------------------------------
    
    



class AboutBsap(http.Controller):
    @http.route("/about-bsap",type="http", website=True, auth="public")
    def about_bsap_page(self, **args):
        return request.render('bsap_website.bsap_about_page')

class GrievanceBsap(http.Controller):
    @http.route("/grievance",type="http", website=True, auth="public")
    def grievance_bsap_page(self, **args):
        return request.render('bsap_website.bsap_grievance_page')

class NotificationBsap(http.Controller):
    @http.route("/notification",type="http", website=True, auth="public")
    def notification_bsap_page(self, **args):
        return request.render('bsap_website.bsap_notification_page')

class ContactUsBsap(http.Controller):
    @http.route("/contact-us",type="http", website=True, auth="public")
    def contact_us_bsap_page(self, **args):
        return request.render('bsap_website.bsap_contact_us_page')
    
    @http.route("/submit-contact-us", type="http",csrf=False, auth="public", website=True)
    def submit_contact_us(self, **post):
        name = post.get('uname')
        mobile = post.get('mobile')
        email = post.get('email')
        subject = post.get('subject')
        message = post.get('message')

        # Validate the data
        if name and email:
            ContactUs = request.env['contact.us']
            ContactUs.create({
                'name': name,
                'mobile': mobile,
                'email': email,
                'subject': subject,
                'message': message
            })
        return request.render('bsap_website.bsap_contact_us_page')
      

class GalleryBsap(http.Controller):
    @http.route("/gallery",type="http", website=True, auth="public")
    def gallery_bsap_page(self, **args):
        return request.render('bsap_website.bsap_gallery_page')


class OrganisationChart(http.Controller):
    @http.route("/organisation-chart",type="http", website=True, auth="public")
    def organisation_chart_bsap_page(self, **args):
        return request.render('bsap_website.bsap_organisation_chart')

class TrainingMannual(http.Controller):
    @http.route("/traning-mannual",type="http", website=True, auth="public")
    def traning_mannual_bsap_page(self, **args):
        return request.render('bsap_website.bsap_training_mannual')

class FaQBSAP(http.Controller):
    @http.route("/faq-bsap",type="http", website=True, auth="public")
    def faq_bsap_page(self, **args):
        faq_data = request.env['cms.faq'].sudo().search([])
        # print(faq_data, '&&&&&&')
        faq_data_even = faq_data.filtered(lambda x: x.id % 2 == 0)
        faq_data_odd = faq_data.filtered(lambda x: x.id % 2 != 0)
        # print(faq_data, '**********')
        return request.render('bsap_website.bsap_faq_page', {'faq_data_even': faq_data_even, 'faq_data_odd': faq_data_odd})

class EmpNotification(http.Controller):

    @http.route("/",type="http", website=True, auth="public")
    def office_order_page(self, **args):
        office_order = request.env['employee.notification'].sudo().search([('type','=','orders')])
        circulars = request.env['employee.notification'].sudo().search([('type','=','circulars')])
        # print("office_order,circulars---------------------",office_order,circulars)
        return http.request.render('bsap_website.bsap_homepage', {'office_order': office_order, 'circulars': circulars})
    
    @http.route("/emp-notification",type="http", website=True, auth="public")
    def emp_notification_page(self, **args):
        emp_data = request.env['employee.notification'].sudo().search([('type','=','employee')])
        # print("emp_data---------------------",emp_data)
        file_ids = [record.id for record in emp_data if record.attachment] 

        return http.request.render('bsap_website.bsap_emp_notification', {'emp_data': emp_data, 'file_ids': file_ids})

    @http.route("/file/<int:file_id>", type="http", website=True, auth="public")
    def show_file(self, file_id, **kwargs):
        emp_record = http.request.env['employee.notification'].sudo().browse(file_id)
        if emp_record and emp_record.attachment:  
            attachment_data = base64.b64decode(emp_record.attachment)
            file_name = emp_record.file_name  

             # Infer MIME type based on file extension
            content_type, _ = mimetypes.guess_type(file_name)
            if not content_type:
                content_type = 'application/octet-stream'  # Default content type if not recognized

            headers = [
                ('Content-Type', content_type),
                ('Content-Disposition', f'attachment; filename="{file_name}"')
            ]

            return http.request.make_response(attachment_data, headers)
        else:
            return http.request.not_found()
      
class BSAPManual(http.Controller):
    @http.route("/bsap-manual",type="http", website=True, auth="public")
    def bsap_manual_page(self, **args):
        bsap_manual = request.env['bsap.manual'].sudo().search([])
        file_ids = [record.id for record in bsap_manual if record.attachment] 
        # print("bsap_manual---------------------",bsap_manual,file_ids)
        return http.request.render('bsap_website.bsap_manual_page', {'bsap_manual': bsap_manual, 'file_ids': file_ids})

    @http.route("/manual/<int:file_id>", type="http", website=True, auth="public")
    def show_file(self, file_id, **kwargs):
        record = http.request.env['bsap.manual'].sudo().browse(file_id)
        # print("----------------------------------------------",record,file_id)
        if record and record.attachment:  
            attachment_data = base64.b64decode(record.attachment)
            file_name = record.file_name  

             # Infer MIME type based on file extension
            content_type, _ = mimetypes.guess_type(file_name)
            if not content_type:
                content_type = 'application/octet-stream'  # Default content type if not recognized

            headers = [
                ('Content-Type', content_type),
                ('Content-Disposition', f'attachment; filename="{file_name}"')
            ]

            return http.request.make_response(attachment_data, headers)
        else:
            return http.request.not_found()
        
class AuditReport(http.Controller):
    @http.route("/audit-report",type="http", website=True, auth="public")
    def audit_report_page(self, **args):
        report = request.env['audit.report'].sudo().search([])
        file_ids = [record.id for record in report if record.attachment] 
        # print("report---------------------",report,file_ids)
        return http.request.render('bsap_website.bsap_audit_report_page', {'report': report, 'file_ids': file_ids})

    @http.route("/report/<int:file_id>", type="http", website=True, auth="public")
    def show_file(self, file_id, **kwargs):
        record = http.request.env['audit.report'].sudo().browse(file_id)
        # print("----------------------------------------------",record,file_id)
        if record and record.attachment:  
            attachment_data = base64.b64decode(record.attachment)
            file_name = record.file_name  

             # Infer MIME type based on file extension
            content_type, _ = mimetypes.guess_type(file_name)
            if not content_type:
                content_type = 'application/octet-stream'  # Default content type if not recognized

            headers = [
                ('Content-Type', content_type),
                ('Content-Disposition', f'attachment; filename="{file_name}"')
            ]

            return http.request.make_response(attachment_data, headers)
        else:
            return http.request.not_found()
        
class Downloads(http.Controller):
    @http.route("/downloads",type="http", website=True, auth="public")
    def bsap_downloads_page(self, **args):
        records = request.env['bsap.download'].sudo().search([])
        file_ids = [record.id for record in records if record.attachment] 
        # print("records---------------------",records,file_ids)
        return http.request.render('bsap_website.bsap_download_page', {'records': records, 'file_ids': file_ids})

    @http.route("/downloads/<int:file_id>", type="http", website=True, auth="public")
    def show_file(self, file_id, **kwargs):
        record = http.request.env['bsap.download'].sudo().browse(file_id)
        # print("----------------------------------------------",record,file_id)
        if record and record.attachment:  
            attachment_data = base64.b64decode(record.attachment)
            file_name = record.file_name  

             # Infer MIME type based on file extension
            content_type, _ = mimetypes.guess_type(file_name)
            if not content_type:
                content_type = 'application/octet-stream'  # Default content type if not recognized

            headers = [
                ('Content-Type', content_type),
                ('Content-Disposition', f'attachment; filename="{file_name}"')
            ]

            return http.request.make_response(attachment_data, headers)
        else:
            return http.request.not_found()

      
class FeedbackBSAP(http.Controller):
    @http.route("/feedback-bsap",type="http", website=True, auth="public")
    def feedback_bsap_page(self, **args):
        return request.render('bsap_website.bsap_feedback_page')
    
    @http.route("/submit-feedback", type="http",csrf=False, auth="public", website=True)
    def submit_feedback(self, **post):
        visited = post.get('visited')
        reason = post.get('reason')
        easy_level = post.get('easy_level')
        email = post.get('email')
        message = post.get('message')
        # print("data------",name,mobile,email,subject,message)

        # Validate the data
        if email and message:
            Feedback = request.env['bsap.feedback']
            Feedback.create({
                'visited': visited,
                'reason': reason,
                'easy_level': easy_level,
                'email': email,
                'message': message
            })
        return request.render('bsap_website.bsap_feedback_page')

class RTIBsap(http.Controller):
    @http.route("/rti-bsap",type="http", website=True, auth="public")
    def rti_bsap_page(self, **args):
        rti_data = request.env['bsap.rti.information'].sudo().search([])
        return request.render('bsap_website.bsap_rti_page', {'rti_data': rti_data})
    
class AssetDeclaration(http.Controller):
    @http.route("/asset-declaration",type="http", website=True, auth="public")
    def asset_bsap_page(self, **args):
        return request.render('bsap_website.bsap_asset_declaration_page')

class Disclaimer(http.Controller):
    @http.route("/disclaimer",type="http", website=True, auth="public")
    def asset_bsap_page(self, **args):
        return request.render('bsap_website.bsap_disclaimer_page')
    
class TermsandCondition(http.Controller):
    @http.route("/terms_and_condition",type="http", website=True, auth="public")
    def asset_bsap_page(self, **args):
        return request.render('bsap_website.bsap_terms_and_condition_page')
    
class Sitemap(http.Controller):
    @http.route("/site-map",type="http", website=True, auth="public")
    def sitemap_bsap_page(self, **args):
        return request.render('bsap_website.bsap_sitemap_page')
    
class Help(http.Controller):
    @http.route("/help",type="http", website=True, auth="public")
    def help_bsap_page(self, **args):
        return request.render('bsap_website.bsap_help_page')
    
class PrivacyPolicy(http.Controller):
    @http.route("/privacy_policy",type="http", website=True, auth="public")
    def asset_bsap_page(self, **args):
        return request.render('bsap_website.bsap_privacy_policy_page')

class OrganizationLocator(http.Controller):
    @http.route("/organization-locator",type="http", website=True, auth="public")
    def sitemap_bsap_page(self, **args):
        bsap_locations = request.env['res.branch'].sudo().search([])
        return request.render('bsap_website.bsap_organization_locator_page',{'bsap_locations': bsap_locations})
    

# class Binary(http.Controller):
#     @http.route('/web/binary/download_document/rti', type='http', auth="public")
#     @serialize_exception
#     def download_document(self, model, field, id, filename, **kw):
#         res = request.env['bsap.rti.information'].sudo().search([('id', '=', id)], limit=1)
#         filecontent = base64.decodebytes(res.file)
#         if not filecontent:
#             return request.not_found()
#         else:
#             if not filename:
#                 filename = '%s_%s' % (model.replace('.', '_'), id)
#                 return request.make_response(filecontent,
#                                              [('Content-Type', 'application/octet-stream'),
#                                               ('Content-Disposition', content_disposition(filename))])
#             return request.make_response(filecontent,
#                                          [('Content-Type', 'application/octet-stream'),
#                                           ('Content-Disposition', content_disposition(filename))])
   
#     @http.route(['/my/departure/leave/<int:leave_id>/download'], type='http', auth="public", website=True)
#     def print_departure(self, leave_id):
#         pdf, _ = request.env.ref('bsap_leaves.action_leave_departure_report').with_user(SUPERUSER_ID)._render_qweb_pdf([leave_id])
#         pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', u'%s' % len(pdf))]
#         data = request.make_response(pdf, headers=pdfhttpheaders)
#         print(data, 'DATTTTTTTTTTTTTTTTTT')
#         return request.make_response(pdf, headers=pdfhttpheaders)

#     @http.route(['/my/leave/certificate/<int:leave_id>/download'], type='http', auth="public", website=True)
#     def print_certificate(self, leave_id):
#         pdf, _ = request.env.ref('bsap_leaves.action_leave_certificate_report').with_user(SUPERUSER_ID)._render_qweb_pdf(
#             [leave_id])
#         pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', u'%s' % len(pdf))]
#         data = request.make_response(pdf, headers=pdfhttpheaders)
#         print(data, 'DATTTTTTTTTTTTTTTTTT')
#         return request.make_response(pdf, headers=pdfhttpheaders)