import werkzeug
import base64
from datetime import datetime, timedelta
import random, operator
from hashlib import sha1
import io
import secrets
from odoo.addons.base.models.ir_ui_view import keep_query
from odoo import http, api
from odoo.http import request

from werkzeug import wrappers


def file_content(xmlid=None, model=None, id=None, field='content', unique=False,
                 filename=None, filename_field='content_fname', download=False,
                 mimetype=None, default_mimetype='application/octet-stream', env=None):
    return request.registry['ir.http'].file_content(
        xmlid=xmlid, model=model, id=id, field=field, unique=unique,
        filename=filename, filename_field=filename_field, download=download,
        mimetype=mimetype, default_mimetype=default_mimetype, env=env)


class kw_consultancy(http.Controller):

    #  File Download
    @http.route([
        '/web/applicant/cv',
        '/web/applicant/cv/<int:id>',
        '/web/applicant/cv/<int:id>/<string:filename>'
    ], type='http', auth="public")
    def content_file(self, id=None, filename=None):
        # import pdb
        # pdb.set_trace()
        """
            For Download Applicant Document.
        """
        # status, headers, content = file_content(
        #     xmlid=None, model='kw_recruitment_documents', id=id, field='content_file', unique=None, filename=filename,
        #     filename_field=None, download=True, mimetype=None)
        # if status == 304:
        #     response = wrappers.Response(status=status, headers=headers)
        # elif status == 301:
        #     return werkzeug.utils.redirect(content, code=301)
        # elif status != 200:
        #     response = request.not_found()
        # else:
        #     content = io.BytesIO(content)
        #     headers.append(('Content-Length', content.seek(0, 2)))
        #     content.seek(0, 0)
        #     response = wrappers.Response(content, headers=headers, status=status, direct_passthrough=True)
        # return response

        data_cv = request.env['kw_recruitment_documents'].sudo().browse(int(id))
        content_base64 = base64.b64decode(data_cv.content_file)
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(content_base64))]
        # print("dtaaa============", data_cv)
        response = wrappers.Response(content_base64, headers=pdfhttpheaders)
        return response

    @http.route(['/web/applicant/feedback/<int:id>'], type='http', auth="public")
    def content_feedback(self, id=None, filename=None):
        """
            For Download Applicant Feedback from interview details page.
        """
        survey = request.env['survey.user_input'].sudo().browse(int(id))
        pdf = \
        request.env.ref('kw_recruitment.kw_recruitment_interview_feedback_report').sudo().render_qweb_pdf([survey.id])[0]
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
        return request.make_response(pdf, headers=pdfhttpheaders)

    @http.route([
        '/web/applicant/consolidate/<int:id>'], type='http', auth="public")
    def content_feedback_consolidate(self, id=None, filename=None):
        """
            for download consolidate feedback from applicant details page
        """
        survey = request.env['kw_recruitment_consolidated_feedback'].sudo().browse(int(id))
        content_base64 = base64.b64decode(survey.binary_file)
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(content_base64))]
        response = wrappers.Response(content_base64, headers=pdfhttpheaders)
        return response

    # JOB list page
    @http.route('/c/job-openings', type='http', auth="user", website=True)
    def job_openings(self, **kw):
        """
            for list all job opening's for consultancy.

        """
        jobs = request.env['kw_hr_job_positions'].sudo().search(
            [('consultancy_id', 'in', request.env.user.partner_id.ids),('state','=','recruit')])
        applicants = request.env['hr.applicant'].sudo().read_group(
            [('consultancy_id', 'in', request.env.user.partner_id.ids)], ['id'], ['job_position'])
        applicants_count = {}
        if applicants:
            for applicant in applicants:
                applicants_count.update({applicant['job_position'][0]: applicant['job_position_count']})
        return request.render("kw_recruitment_consultancy.kw_consultancy_job_list",
                              {'jobs': jobs, 'applicants_counts': applicants_count})

    # JOB details page
    @http.route('/c/job-details', type='http', auth="user", website=True)
    def job_details(self, **kw):
        """
            for job description.
        """
        job = request.env['kw_hr_job_positions'].sudo().search(
            [('id', '=', int(kw['job_id'])), ('consultancy_id', 'in', request.env.user.partner_id.ids)])
        if not job:
            return request.redirect('/c/job-openings')
        return request.render('kw_recruitment_consultancy.kw_consultancy_job_details', {'job': job})

    # Applicant list page
    @http.route('/c/applicants', type='http', auth="user", website=True)
    def consultancy_view_applicants(self, **kw):
        """
            List all applicants -- job and consultancy wise.
        """
        job = request.env['kw_hr_job_positions'].sudo().search(
            [('id', '=', int(kw['job_id'])), ('consultancy_id', 'in', request.env.user.partner_id.ids)])
        if not job:
            return request.redirect('/c/job-openings')

        applicants = request.env['hr.applicant'].sudo().search(
            [('job_position', '=', int(kw['job_id'])), ('consultancy_id', 'in', request.env.user.partner_id.ids)])
        return request.render("kw_recruitment_consultancy.consultancy_view_applicants",
                            {'applicants': applicants, 'job': job})

    @http.route('/c/applicant-details', type='http', auth="user", website=True)
    def applicant_details(self, **kw):
        """
            Applicant details
        """
        applicant = self._check_applicant_details(**kw)
        feedback = False
        if applicant:
            try:
                feedback_dict = applicant.export_feedbacks()
                feedback = feedback_dict['res_id']
            except:
                pass
        return request.render('kw_recruitment_consultancy.consultancy_applicant_details',
                              {'applicant': applicant, 'feedback': feedback, 'consultancy':applicant.consultancy_id})

    @http.route('/c/add-applicant', type='http', auth="user", website=True)
    def consultancy_add_applicant(self, **kw):
        randomNumberlist = random.sample(range(1, 30), 2)
        # randomNumberlist = secrets.sample(range(1, 30), 2)
        # print("Random number list : ", randomNumberlist)
        operators = {
            '+': operator.add,
            '-': operator.sub,
        }
        # operation = random.choice(list(operators.keys()))
        operation = secrets.choice(list(operators.keys()))

        result = operators.get(operation)(randomNumberlist[0], randomNumberlist[1])

        applicant = self._check_applicant_details(**kw) if kw.get('applicant_id',False) else request.env['hr.applicant'].sudo()

        jobs = request.env['kw_hr_job_positions'].sudo().browse(int(kw['job_id']))
        years = request.env['kw_hr_job_positions'].sudo()._get_year_list()
        months = request.env['kw_hr_job_positions'].sudo()._get_month_list()
        qualifications = request.env['kw_qualification_master'].sudo().search([])
        tech_skills = request.env['kw_skill_master'].sudo().search([])
        return request.render("kw_recruitment_consultancy.consultancy_add_applicant", {
            'applicant': applicant,
            'jobs': jobs,
            'qualifications': qualifications,
            'message': False,
            "random_number": randomNumberlist,
            "operator": operation,
            'result': result,
            'months': months,
            'years': years,
            'tech_skills': tech_skills
        })

    """### Applicant form submit"""

    @http.route('/c/applicant/create', type='json', auth="user", website=True)
    def store_applicant_details(self, **kw):
        """
            Applicant create for respective job listing.
        """
        try:
            payload = {}
            if kw.get('filename', False):
                file_doc = kw.get('file').split(';base64,')
                if len(file_doc) % 4:
                    file_doc += '=' * (4 - len(file_doc) % 4) 
                document_file = file_doc[1].encode()
                # base64_document = base64.decodestring(document_file)
                # base64_encode_doc = base64.encodestring(base64_document)
                document_name = kw['filename']
                # payload['document_ids'] = [[0, 0, {'content_file': base64_document, 'file_name': document_name}]]
            message = 'Application submitted Successfully!'
            message_type = 's'
            Applicant = request.env['hr.applicant'].sudo()
            jobs = request.env['kw_hr_job_positions'].sudo().browse(int(kw['job_position']))
            stage_id = request.env['hr.recruitment.stage'].sudo().search([('code', '=', 'FI')])
            
            payload['partner_name'] = (kw['partner_name'])
            payload['email_from'] = (kw['email_from'])
            payload['partner_mobile'] = (kw['partner_mobile'])
            payload['partner_phone'] = (kw['partner_phone'])
            payload['gender'] = (kw['gender'])
    
            payload['job_position'] = int(kw['job_position'])
            payload['job_location_id'] = int(kw['job_location_id'])
            payload['responsible_id'] = jobs.hr_responsible_id.id
            payload['current_location'] = kw['current_location'].strip() if kw['current_location'] else ''
            payload['qualification_ids'] = [[6, 0, [int(kw['qualification_ids'])]]]
            payload['other_qualification'] = (kw['other_qualification'])
            payload['certification'] = (kw['certification'])
    
            if kw['skill_ids']:
                skill_lst = [int(i) for i in kw['skill_ids'].split(',')]
                payload['skill_ids'] = [[6, 0, skill_lst]]
    
            payload['current_ctc'] = (kw['current_ctc']) if kw['current_ctc'].isnumeric() else 0
            payload['salary_expected'] = (kw['salary_expected']) if kw['salary_expected'].isnumeric() else 0
            payload['notice_period'] = (kw['notice_period'])
            payload['description'] = (kw['description'])
    
            payload['exp_month'] = int(kw['exp_month'])
            payload['exp_year'] = int(kw['exp_year'])
            payload['stage_id'] = stage_id.id
    
            source_id = request.env['utm.source'].sudo().search([('code', '=', 'consultancy')], limit=1)
            if source_id:
                payload['source_id'] = source_id.id
                payload['code_ref'] = source_id.code
            payload['consultancy_id'] = request.env.user.partner_id.id
            if kw['applicant_id']:
                candidate = Applicant.search(['|',
                                              ('partner_mobile', '=', payload['partner_mobile']),
                                              ('email_from', '=', payload['email_from']),

                                              ('id', '!=', int(kw['applicant_id']))
                                              ])
                # ('job_position', '=', payload['job_position']),
                if candidate:
                    message_type = 'f'
                    message = "Duplicate CV Alert !! \n The candidate's profile already exists in system."
                else:
                    Applicant = Applicant.browse(int(kw['applicant_id']))
                    payload['filename'] = Applicant.document_ids.file_name
                    if kw.get('filename', False):
                        if Applicant.document_ids.id:
                            payload['document_ids'] = [[1, Applicant.document_ids.id, {'content_file': document_file, 'file_name': document_name}]]
                        else:
                            payload['document_ids'] = [[0, 0, {'content_file': document_file, 'file_name': document_name}]]
                    record = Applicant.write(payload)
            else:
                if kw.get('filename', False):
                    payload['document_ids'] = [[0, 0, {'content_file': document_file, 'file_name': document_name}]]
                candidate = Applicant.search(['|',
                                              ('partner_mobile', '=', payload['partner_mobile']),
                                              ('email_from', '=', payload['email_from']),

                                              ])
                # ('job_position', '=', payload['job_position'])
                if candidate:
                    message_type = 'f'
                    message = "Duplicate CV Alert !! \n The candidate's profile already exists in system."
                else:
                    record = Applicant.create(payload)
                
        except Exception as e:
            message_type = 'f'
            message = f'Something went wrong! Please try after sometime.{e}'

        url = f'/c/applicants?job_id={int(kw["job_position"])}'
        return {'url': url, 'message': message, 'message_type': message_type}

    @http.route('/c/interviews', type='http', auth="user", website=True)
    def applicant_meetings(self, **kw):
        """
            List all interviews job wise.
        """
        applicant = self._check_applicant_details(**kw)

        meetings = request.env['kw_meeting_events'].sudo().search([
            ('state', '!=', 'cancelled'),
            ('applicant_ids', '=', int(kw['applicant_id']))
        ])
        return request.render('kw_recruitment_consultancy.view_applicant_meetings',
                              {'meetings': meetings, 'applicant': applicant})

    @http.route('/c/schedule-interview', type='http', auth="user", website=True)
    def schedule_meetings(self, **kw):
        """Applicant meeting form details"""
        meeting_data = self.get_meeting_data(**kw)
        return request.render('kw_recruitment_consultancy.schedule_meeting', meeting_data)

    @http.route('/c/interview/create', type='json', auth="user", website=True)
    def store_applicant_meeting_create(self, **kw):
        """ Applicant meeting save"""
        meeting_event = request.env['kw_meeting_events'].sudo()
        vals = {
            'closed_meeting': False, 'zoom_enabled_user': False, 'allday': False,
            'company_id': 1, 'interval': 1, 'end_type': 'count', 'count': 1,
            'month_by': 'date', 'day': 1, 'attendee_notify_option': 'new_attendee',
            'mom_controller_id': False, 'privacy': 'public', 'send_email': True,
            'draft_mom': False, 'ref_name': False, 'res_id': 0, 'project_category': False,
            'project': False, 'meetingtype_code': 'interview',
            'survey_id': False, 'send_to_panel': False, 'send_to_applicant': True,
            'recurrency': False, 'recurrent_id': 0, 'rrule_type': False, 'final_date': False,
            'mo': False, 'tu': False, 'we': False, 'th': False, 'fr': False, 'sa': False, 'su': False,
            'byday': False, 'week_list': False, 'meeting_room_availability_status': False,
            'description': False, 'reference_document': False, 'meeting_group_id': False,
            'mom_required': False, 'send_sms': False, 'send_whatsapp': False, 'notify_to_nsa': False,
            'notify_to_admin': False, 'reminder_id': False, 'message_attachment_count': 0,
            'organiser_id': 1,
            'meeting_category': 'general',
            'create_uid': request.env.user.id,
        }
        # kw['name'] = 'Interview schedule - ' + kw['name']
        applicant_id = int(kw['applicant_id'])
        payload = {}
        # print("applicant:",kw['send_to_applicant'])
        # print("panel:",kw['send_to_panel'])

        if kw['location_id']:
            payload['location_id'] = int(kw['location_id'])

        if kw['meeting_room_id']:
            payload['meeting_room_id'] = int(kw['meeting_room_id'])
        else:
            payload['meeting_room_id'] = self.env['kw_meeting_room_master'].sudo().search([('name','=', 'Virtual'),('active','=', False)]).id

        if kw['employee_ids']:
            payload['employee_ids'] = [[6, 0, [int(emp) for emp in kw['employee_ids'].split(',')]]]

        if kw['applicant_ids']:
            payload['applicant_ids'] = [[6, 0, [int(i) for i in kw['applicant_ids'].split(',')]]]
        if kw['name']:
            payload['agenda_ids'] = [(0, 0, {'name': 'Interview schedule - ' + kw['name']})]

        payload['categ_ids'] = [[6, False, [int(kw['meeting_type_id'])]]]
        payload['logged_user_id'] = request.env.user.id
        payload['meeting_type_id'] = int(kw['meeting_type_id'])
        payload['kw_duration'] = kw['duration']
        payload['kw_start_meeting_time'] = kw['kw_start_meeting_time']
        payload['telephone'] = kw['telephone']
        payload['mode_of_interview'] = kw['mode_of_interview']
        payload['duration'] = kw['duration']
        payload['kw_start_meeting_date'] = kw['kw_start_meeting_date']
        payload['name'] = kw['name']
        payload['recr_other_meeting_url'] = kw['recr_other_meeting_url']
        payload['recr_online_meeting'] = 'other'
        payload['app_mail_check'] = False
        payload['pan_mail_check'] = False
        payload['c_id'] = request.env.user.id
        if kw.get('send_to_applicant', False) == 'option2':
            payload['send_to_applicant'] = True
        else:
            payload['send_to_applicant'] = False
        if kw.get('send_to_panel', False) == 'option1':
            payload['send_to_panel'] = True
        else:
            payload['send_to_panel'] = False
        # del kw['agenda']
        vals.update(payload)
        res = {}
        # print("panel:", vals['send_to_panel'])
        # print("applicant:", vals['send_to_applicant'])
        onchange_fields = ['stop_date', 'kw_start_meeting_date', 'kw_start_meeting_time', 'location_id', 'employee_ids',
                           'start_datetime', 'duration', 'start_date']
        meeting_onchage = meeting_event.new(vals)
        meeting_onchage._onchange_meeting_date_time()
        meeting_onchage._onchange_duration()
        meeting_onchage._onchange_start_date()
        meeting_onchage._onchange_stop_date()
        meeting_onchage.set_categ_ids()
        for field in onchange_fields:
            if field not in vals:
                res[field] = meeting_onchage._fields[field].convert_to_write(meeting_onchage[field], meeting_onchage)

        vals.update(res)
        vals['start'] = vals['start_datetime']
        tdelta_duration = vals['duration'] if vals['duration'] else 0.0
        vals['stop'] = vals['start'] + timedelta(hours=float(tdelta_duration)) - timedelta(seconds=1)
        vals['stop_datetime'] = vals['stop']
        if kw.get('survey_id', False):
            vals['survey_id'] = int(kw['survey_id'])
        message = ''
        try:
            if kw.get('meeting_id', False):
                meeting_record = meeting_event.browse(int(kw['meeting_id']))
                meeting_record.write(vals)
                # print("wartiteeeeeeeeeee called---------------------------------------------------------------------")
                message = 'Successfully Updated!'
                message_type = 's'

            else:
                meeting = meeting_event.create(vals)
                message = 'Meeting Scheduled Successfully!'
                message_type = 's'
        except Exception as e:
            message_list = eval(str(e))
            message = message_list[0]
            message_type = 'f'
            kw['applicant_id'] = applicant_id
            meeting_data = self.get_meeting_data(**kw)
            meeting_data.update({'message': message})
            http.request._cr.rollback()
        url = f'/c/interviews?applicant_id={applicant_id}'
        return {'url': url, 'message': message, 'message_type': message_type}
    
    @http.route('/c/interview/cancel', type='json', auth="user", website=True, csrf=False)
    def applicant_meeting_create(self, data, **kw):
        applicant = request.env['hr.applicant'].sudo().browse(int(data['applicant_id']))
        meeting = request.env['kw_meeting_events'].sudo().search(
            [('id', '=', int(data['meeting_id'])), ('applicant_ids', 'in', [int(data['applicant_id'])])])
        error_msg = ''
        if meeting:
            try:
                meeting.action_cancel_meeting_list_bulk()
                error_msg = 'Successfully canceled'
            except Exception as e:
                error_msg = e
        return {'error_msg': error_msg}

    @http.route('/c/meeting-details', type='http', auth="user", website=True, csrf=False)
    def meeting_details(self, **kw):
        applicant = request.env['hr.applicant'].sudo().browse(int(kw['applicant_id']))
        meeting = request.env['kw_meeting_events'].sudo().browse(int(kw['meeting_id']))
        mode_of_interview = dict(meeting._fields['mode_of_interview'].selection).get(meeting.mode_of_interview)

        meeting_times = request.env['kw_meeting_events'].sudo()._get_time_list()
        meeting_dict = dict((y, x) for x, y in meeting_times)
        p = meeting.kw_start_meeting_time
        meeting_time = list(meeting_dict.keys())[list(meeting_dict.values()).index(p)]
        duration = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(meeting.duration) * 60, 60))

        scores = [j.score for i in meeting for j in i.response_ids if i.id == applicant.id]
        remarks = [j.remark for i in meeting for j in i.response_ids if i.id == applicant.id]

        name = [j.name for i in meeting for j in i.external_attendee_ids if i.id == applicant.id]
        phone = [j.phone for i in meeting for j in i.external_attendee_ids if i.id == applicant.id]
        email = [j.email for i in meeting for j in i.external_attendee_ids if i.id == applicant.id]

        return request.render('kw_recruitment_consultancy.consultancy_meeting_details',
                              {
                                  'duration': duration,
                                  'meeting': meeting,
                                  'moi': mode_of_interview,
                                  'meeting_time': meeting_time,
                                  'applicant': applicant,
                                  'scores': scores,
                                  'remarks': remarks,
                                  'name': name,
                                  'phone': phone,
                                  'email': email
                              })
        
    @http.route('/c/get_meeting_room', type='json', auth="user", website=True, csrf=False)
    def get_meeting_room(self, data, **kw):
        domain = [('location_id', '=', int(data)), ('restricted_access', '=', False) ] if data else []
        rooms = request.env['kw_meeting_room_master'].sudo().search(domain).read(['id', 'name'])
        return {'rooms': rooms}

    def _check_applicant_details(self, **kw):
        applicant = request.env['hr.applicant'].sudo().search(
            [('id', '=', int(kw['applicant_id'])), ('consultancy_id', 'in', request.env.user.partner_id.ids)])
        if not applicant:
            return request.redirect('/c/job-openings')
        return applicant
    
    def get_meeting_data(self, **kw):
        meeting_room = []
        participant = []
        meeting = request.env['kw_meeting_events'].sudo()
        if kw.get('applicant_id', False) and kw.get('meeting_id', False):
            meeting = request.env['kw_meeting_events'].sudo().search(
                [('id', '=', int(kw['meeting_id'])), ('applicant_ids', 'in', [int(kw['applicant_id'])])])
            meeting_room = request.env['kw_meeting_room_master'].sudo().search(
                [('location_id', '=', meeting.location_id.id), ('restricted_access', '=', False)])
        meeting_type = request.env['calendar.event.type'].sudo().search([('name', '=', 'Interview')])
        # participant = request.env['hr.employee'].sudo().search([('user_id', '!=', False)])
        location = request.env['kw_res_branch'].sudo().search([])
        mode_of_interview = request.env['kw_meeting_events'].sudo()._fields['mode_of_interview'].selection
        online_meeting = request.env['kw_meeting_events'].sudo()._fields['recr_online_meeting'].selection
        default_applicant, message = False, False
        if kw.get('applicant_id', False):
            default_applicant = request.env['hr.applicant'].sudo().search(
                [('id', '=', int(kw['applicant_id'])), ('consultancy_id', 'in', request.env.user.partner_id.ids)])
            participant = default_applicant.job_position.panel_members_grp.members_name
            if meeting.applicant_ids:
                default_applicant = meeting.applicant_ids
            applicant = request.env['hr.applicant'].sudo().search(
                [('job_position', '=', default_applicant[0].job_position.id), ('consultancy_id', 'in', request.env.user.partner_id.ids)])
        else:
            applicant = request.env['hr.applicant'].sudo().search([('consultancy_id', 'in', request.env.user.partner_id.ids)])
       
        meeting_times = request.env['kw_meeting_events'].sudo()._get_time_list()
        duration = request.env['kw_meeting_events'].sudo()._get_duration_list()
        interview_forms = request.env['survey.survey'].sudo().search([('survey_type.code','=','recr')])
        meeting_data = {
            'duration': duration,
            'meeting_type': meeting_type,
            'participant': participant,
            'location': location,
            'applicant': applicant,
            'meeting_room': meeting_room,
            'mode_of_interview': mode_of_interview,
            'meeting_times': meeting_times,
            'online_meeting': 'Others',
            'default_applicant': default_applicant,
            'meeting': meeting,
            'interview_forms': interview_forms,
            # 'location_room': location_room,
            'meeting_title': f'Interview schedule - {default_applicant[0].job_position.title}',
        }
        return meeting_data

    @http.route('/c/interview-summary-reports', type='http', auth="user", website=True)
    def summary_reports(self):
        summary_applicant = request.env['hr.applicant'].sudo().search(
            [('consultancy_id', 'in', request.env.user.partner_id.ids)])

        return request.render("kw_recruitment_consultancy.consultancy_interview_summary_reports",
                              {'summary_applicant': summary_applicant})
