"""Part of odoo. See LICENSE file for full copyright and licensing details."""

import functools
import logging
import datetime
from datetime import date, datetime, timedelta
from odoo import http
from odoo.addons.restful.common import (
    extract_arguments,
    invalid_response,
    valid_response,
)
from odoo.http import request
import pytz
from pytz import timezone

_logger = logging.getLogger(__name__)


def validate_token(func):
    """."""

    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        """."""
        access_token = request.httprequest.headers.get("access_token")
        if not access_token:
            return invalid_response(
                "access_token_not_found", "missing access token in request header", 401
            )
        access_token_data = (
            request.env["api.access_token"]
            .sudo()
            .search([("token", "=", access_token)], order="id DESC", limit=1)
        )

        if (
            access_token_data.find_one_or_create_token(
                user_id=access_token_data.user_id.id
            )
            != access_token
        ):
            return invalid_response(
                "access_token", "token seems to have expired or invalid", 401
            )

        request.session.uid = access_token_data.user_id.id
        request.uid = access_token_data.user_id.id
        return func(self, *args, **kwargs)

    return wrap


_routes = ["/api/<model>", "/api/<model>/<id>", "/api/<model>/<id>/<action>"]


class APIController(http.Controller):
    """."""

    def __init__(self):
        self._model = "ir.model"

    # @validate_token
    @http.route('/api/get_today_meeting/<int:room_id>', type="http", auth="none", methods=["GET"], csrf=False, cors='*',website=True)
    def get_today_meeting(self, room_id):
        dt_now = datetime.now()
        today = date.today()
        user_timezone = pytz.timezone('Asia/Kolkata')
        current_time = datetime.strftime(dt_now.replace(tzinfo=pytz.utc).astimezone(user_timezone), "%Y-%b-%d %H:%M")

        current_meeting_list = []
        other_meeting_list = []
        participants_data_list = []
        upcoming_meeting_list = []
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        # base_url = 'http://192.168.203.163:8069'

        """today's current meeting room data"""
        meeting_data = request.env['kw_meeting_events'].sudo().search(
            [('meeting_room_id', '=', room_id), ('kw_start_meeting_date', '=', today),
             ('state', 'not in', ['cancelled']), '|', '&',
             ('start_datetime', '<', dt_now), ('stop_datetime', '>', dt_now), ('start_datetime', '>', dt_now)],
            order='start_datetime asc')
        for record in meeting_data:
            attachment_data = request.env['ir.attachment'].sudo().search([('res_id', '=', record.create_uid.employee_ids.id), ('res_model', '=', 'hr.employee'), ('res_field', '=', 'image')])
            attachment_data.write({'public': True})
            duration = (record.stop - record.start).seconds + 1

            data0 = {
                'FacilityName': 'null',
                'Photopath': '%s/web/image/%s' % (base_url, attachment_data.id) if attachment_data.id else None,
                'duration': duration,
                'meetingId': record.id,
                'meetingTitle': record.name,
                'organizedBy': record.create_uid.employee_ids.name,
                'organizerId': record.create_uid.employee_ids.id,
                'organizerPhoto': record.create_uid.partner_id.image if record.create_uid.partner_id.image else None,
                'roomId': record.meeting_room_id.id,
                'roomName': record.meeting_room_id.name,
                'scheduledDatetime': datetime.strftime(record.start_datetime.replace(tzinfo=pytz.utc).astimezone(user_timezone) + timedelta(seconds=1),"%d %b %Y %I:%M %p"),
                'EndDatetime': datetime.strftime(record.stop_datetime.replace(tzinfo=pytz.utc).astimezone(user_timezone) + timedelta(seconds=1),"%d %b %Y %I:%M %p"),
            }
            if record.start <= dt_now <= record.stop:
                for rec in record.employee_ids:
                    attachment_data = request.env['ir.attachment'].sudo().search(
                        [('res_id', '=', rec.id), ('res_model', '=', 'hr.employee'), ('res_field', '=', 'image')])
                    attachment_data.write({'public': True})
                    data2 = {
                        'Photopath': '%s/web/image/%s' % (base_url, attachment_data.id) if attachment_data.id else None,
                        'participantId': rec.id,
                        'participantName': rec.name,
                        'participantphoto': rec.image if rec.image else None,
                    }
                    participants_data_list.append(data2)
                for rec in record.external_attendee_ids:
                    data2 = {
                        'Photopath': None,
                        'participantId': rec.partner_id.id,
                        'participantName': rec.name,
                        'participantphoto': None,
                    }
                    participants_data_list.append(data2)
                current_meeting_list.append(data0)
            else:
                upcoming_meeting_list.append(data0)

        """today's other meeting room data"""
        other_meeting_records = request.env['kw_meeting_events'].sudo().search(
            [('meeting_room_id.name', '!=', 'Virtual'), ('kw_start_meeting_date', '=', today),
             ('state', '!=', 'cancelled'),
             '|', '&', ('start_datetime', '<', dt_now), ('stop_datetime', '>', dt_now),
             ('start_datetime', '>', dt_now)], order='start_datetime asc')

        other_meeting_data_list = []
        other_meeting_data_dict = {}
        other_meeting_rooms = {}
        other_meeting_rooms_ids = []
        if other_meeting_records:
            for record in other_meeting_records:
                meeting_data = {}
                duration = (record.stop - record.start).seconds + 1
                meeting_data = {
                    'duration': duration,
                    'organizedBy': record.create_uid.employee_ids.name,
                    'organizerId': record.create_uid.employee_ids.id,
                    'roomId': record.meeting_room_id.id,
                    'roomName': record.meeting_room_id.name,
                    'scheduledDatetime': datetime.strftime(record.start_datetime.replace(tzinfo=pytz.utc).astimezone(user_timezone) + timedelta(seconds=1), "%d %b %Y %I:%M %p"),
                    'EndDatetime': datetime.strftime(record.stop_datetime.replace(tzinfo=pytz.utc).astimezone(user_timezone) + timedelta(seconds=1), "%d %b %Y %I:%M %p"),
                }
                other_meeting_data_list.append(meeting_data)
                if record.meeting_room_id.id in other_meeting_data_dict.keys():
                    other_meeting_data_dict[record.meeting_room_id.id].append(meeting_data)
                else:
                    other_meeting_data_dict[record.meeting_room_id.id] = [meeting_data]
                other_meeting_rooms[record.meeting_room_id.id] = {'roomId': record.meeting_room_id.id, 'roomName': record.meeting_room_id.name}
                other_meeting_rooms_ids.append(record.meeting_room_id.id)

        other_meeting_rooms_ids = list(set(other_meeting_rooms_ids))
        if other_meeting_rooms_ids:
            for room_id in other_meeting_rooms_ids:
                data1 = {
                    'OtherMeetingChild': other_meeting_data_dict[room_id],
                    'roomId': room_id,
                    'roomName': other_meeting_rooms[room_id]['roomName'],
                }
                other_meeting_list.append(data1)
        today_meetings = {
            'get_today_meetingResult': {
                'CurrentMeeting': current_meeting_list,
                'Participant': participants_data_list,
                'UpcomingMeeting': upcoming_meeting_list,
                'OtherMeeting': other_meeting_list,
                'ServerTime': [{'Servertime': datetime.strptime(str(datetime.now() + timedelta(hours=5,minutes=30)), "%Y-%m-%d %H:%M:%S.%f").strftime('%d %b %Y %I:%M %p')}],
            }
        }
        blank = [{}]
        if today_meetings:
            return valid_response(today_meetings)
        else:
            return valid_response(blank)
        # return invalid_response(
        #     "invalid object model",
        #     "The model %s is not available in the registry." % ioc_name,
        #     )

    @http.route('/api/get_all_meeting_room_id', type="http", auth="none", methods=["GET"], csrf=False, cors='*',website=True)
    def get_all_room_id(self):
        room_data = request.env['kw_meeting_room_master'].sudo().search(
            [('name', '!=', 'Virtual'), ('restricted_access', '=', False)])
        meeting_room_list = []
        blank = [{}]
        r_data = {}
        if room_data:
            for room in room_data:
                r_data = {
                    'roomId': room.id,
                    'roomName': room.name,
                }
                meeting_room_list.append(r_data)
        if meeting_room_list:
            return valid_response(meeting_room_list)
        else:
            return valid_response(blank)
        # return invalid_response(
        #     "invalid object model",
        #     "The model %s is not available in the registry." % ioc_name,
        #     )

    @http.route('/api/cancelmeeting/<int:meeting_id>/<int:organizer_id>/<int:mpin_id>', type="http", auth="none", methods=["GET"], csrf=False, cors='*',website=True)
    def cancelmeeting(self, meeting_id, organizer_id, mpin_id):
        meeting_record = request.env['kw_meeting_events'].sudo().search([('id', '=', meeting_id)])
        cancel_meeting_list = []
        blank = [{}]
        if meeting_record:
            if organizer_id == meeting_record.create_uid.employee_ids.id or organizer_id in list(meeting_record.employee_ids.ids):
                if meeting_record.mpin == mpin_id and meeting_record.state != 'cancelled':
                    meeting_record.sudo().write({'state':'cancelled'})
                    r_data = {
                        'CancelMeetingResult': "success",
                    }
                    cancel_meeting_list.append(r_data)
                    for attendee in meeting_record.attendee_ids:
                        request.env.ref('kw_meeting_schedule.kw_meeting_calendar_template_meeting_changedate').sudo().send_mail(attendee.id,notif_layout="kwantify_theme.csm_mail_notification_light")

                else:
                    r_data = {
                        'CancelMeetingResult': "Invalid MPIN",
                    }
                    cancel_meeting_list.append(r_data)
        if cancel_meeting_list:
            return valid_response(cancel_meeting_list)
        else:
            return valid_response(blank)
        # return invalid_response(
        #     "invalid object model",
        #     "The model %s is not available in the registry." % ioc_name,
        #     )

    @http.route('/api/EndMeeting/<int:meeting_id>/<string:end_time>/<int:duration>/<int:mpin_id>', type="http", auth="none", methods=["GET"], csrf=False, cors='*',website=True)
    def end_meeting(self, meeting_id, end_time, duration, mpin_id):
        time_val = datetime.strptime((str(date.today()) + " " + end_time.replace("H",":")),"%Y-%m-%d %I:%M %p")
        meeting_record = request.env['kw_meeting_events'].sudo().search([('id', '=', meeting_id)])
        end_meeting_list = []
        blank = [{}]
        dur = str(duration/3600) , str(datetime.strptime(str(timedelta(seconds=duration)),"%H:%M:%S").strftime("%H:%M")) + ' hrs'
        if meeting_record:
            if meeting_record.mpin == mpin_id:
                meeting_record.sudo().write({
                                    'stop': datetime.strptime(str(time_val), "%Y-%m-%d %H:%M:%S") - timedelta(hours=5,minutes=30,seconds=1),
                                    'duration': float(duration/3600),
                                    # 'kw_duration': float(dur[0]), 
                                    })
                r_data = {
                    'EndMeetingResult': "success",
                }
                end_meeting_list.append(r_data)
            else:
                r_data = {
                    'EndMeetingResult': "Invalid MPIN",
                }
                end_meeting_list.append(r_data)
        if end_meeting_list:
            return valid_response(end_meeting_list)
        else:
            return valid_response(blank)
        # return invalid_response(
        #     "invalid object model",
        #     "The model %s is not available in the registry." % ioc_name,
        #     )

    @http.route('/api/getAllUsers/<int:row>', type="http", auth="none", methods=["GET"], csrf=False, cors='*',website=True)
    def all_users(self, row):
        employee_list = []
        blank = [{}]
        status_val = False
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        # base_url = 'http://192.168.203.163:8069'
        if row == 0:    
            employee_record = request.env['hr.employee'].sudo().search([])
            if employee_record:
                for employee in employee_record:
                    status_val = False
                    attachment_data = request.env['ir.attachment'].sudo().search([('res_id', '=', employee.id), ('res_model', '=', 'hr.employee'), ('res_field', '=', 'image')])
                    attachment_data.write({'public': True})
                    """Checking employee Status"""
                    present_employee = request.env['kw_daily_employee_attendance'].sudo().search(
                        [('attendance_recorded_date','=',datetime.strptime(str(date.today()),'%Y-%m-%d').strftime('%d %b %Y')),
                         ('employee_id', '=', employee.id)])
                    if present_employee and present_employee.status == 'Present':
                        meeting = request.env['kw_meeting_events'].sudo().search([('start_datetime', '<', datetime.now()), ('stop_datetime', '>', datetime.now())])
                        local_visit = request.env['kw_lv_apply'].sudo().search([('state', '=','office_out'),('applied_by', '=', employee.id)])
                        if meeting:
                            for record in meeting:
                                if not local_visit and employee.id in record.employee_ids.ids:
                                    status_val = 'MEETING'
                                if local_visit:
                                    status_val = 'LOCAL VISIT'
                                if not local_visit and employee.id not in record.employee_ids.ids:
                                    status_val = 'PRESENT'
                    if present_employee and present_employee.status in ['Absent','First Half Absent','Second Half Absent']:
                        status_val = 'ABSENT'
                    if present_employee.status == 'On Tour':
                        status_val = 'TOUR'
                    r_data = {
                        'EmployeeId': employee.id,
                        'EmployeeName': employee.name,
                        'Designation':employee.job_id.name if employee.job_id.name else " ",
                        'Mobile':employee.mobile_phone if employee.mobile_phone else " ",
                        'Extension': employee.work_phone if employee.work_phone else " ",
                        'Status':status_val if status_val else " ",
                        'Photo': '%s/web/image/%s' % (base_url, attachment_data.id) if attachment_data.id else None,
                    }
                    employee_list.append(r_data)
        if employee_list:
            return valid_response(employee_list)
        else:
            return valid_response(blank)
        # return invalid_response(
        #     "invalid object model",
        #     "The model %s is not available in the registry." % ioc_name,
        #     )

    @http.route('/api/getSearchUsers/<string:searchtext>', type="http", auth="none", methods=["GET"], csrf=False, cors='*',website=True)
    def search_users(self, searchtext):
        emp_list = []
        blank = [{}]
        status_val = False
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        # base_url = 'http://192.168.203.163:8069'
        if searchtext:
            employee_record = request.env['hr.employee'].sudo().search([('name','ilike',searchtext[1:-1])])
            if employee_record:
                for employee in employee_record:
                    status_val = False
                    attachment_data = request.env['ir.attachment'].sudo().search([('res_id', '=', employee.id), ('res_model', '=', 'hr.employee'), ('res_field', '=', 'image')])
                    attachment_data.write({'public': True})
                    """Checking employee Status"""
                    present_employee = request.env['kw_daily_employee_attendance'].sudo().search([('attendance_recorded_date','=',datetime.strptime(str(date.today()),'%Y-%m-%d').strftime('%d %b %Y')),('employee_id','=',employee.id)])
                    if present_employee and present_employee.status == 'Present':
                        meeting = request.env['kw_meeting_events'].sudo().search([('start_datetime', '<', datetime.now()), ('stop_datetime', '>', datetime.now())])
                        local_visit = request.env['kw_lv_apply'].sudo().search([('state', '=','office_out'),('applied_by', '=', employee.id)])
                        if meeting:
                            for record in meeting:
                                if not local_visit and employee.id in record.employee_ids.ids:
                                    status_val = 'MEETING'
                                if local_visit:
                                    status_val = 'LOCAL VISIT'
                                if not local_visit and employee.id not in record.employee_ids.ids:
                                    status_val = 'PRESENT'
                    if present_employee and present_employee.status in ['Absent','First Half Absent','Second Half Absent']:
                        status_val = 'ABSENT'
                    if present_employee.status == 'On Tour':
                        status_val = 'TOUR'
                    r_data = {
                        'EmployeeId': employee.id,
                        'EmployeeName': employee.name,
                        'Designation':employee.job_id.name if employee.job_id.name else " ",
                        'Mobile':employee.mobile_phone if employee.mobile_phone else " ",
                        'Extension': employee.work_phone if employee.work_phone else " ",
                        'Status':status_val if status_val else " ",
                        'Photo': '%s/web/image/%s' % (base_url, attachment_data.id) if attachment_data.id else None,
                    }
                    emp_list.append(r_data)
        if emp_list:
            return valid_response(emp_list)
        else:
            return valid_response(blank)
        # return invalid_response(
        #     "invalid object model",
        #     "The model %s is not available in the registry." % ioc_name,
        #     )

    @http.route('/api/AddParticipants/<int:meeting_id>/<int:organiser_id>/<int:emp_id>/<string:employeename>', type="http", auth="none", methods=["GET"], csrf=False, cors='*',website=True)
    def add_participants(self, meeting_id, organiser_id, emp_id, employeename):
        current_meeting = []
        other_participant_list = []
        c_t = datetime.strptime(str(datetime.today()), '%Y-%m-%d %H:%M:%S.%f').strftime("%Y-%m-%d %H:%M:%S")
        current_time = datetime.strptime(str(c_t), "%Y-%m-%d %H:%M:%S")
        meeting_record = request.env['kw_meeting_events'].sudo().search([
            ('kw_start_meeting_date', '=', date.today()),
            ('state', 'not in', ['cancelled']),
        ])
        for record in meeting_record:
            if record.id == meeting_id:
                current_meeting.append(record)

            # if record.start >= current_time and record.stop >= current_time or record.start <= current_time and record.stop >= current_time:
            if current_meeting:
                if record.start <= current_meeting[0].start and record.stop >= current_meeting[0].start and record.stop <= current_meeting[0].stop or record.start >= current_meeting[0].start and record.stop <= current_meeting[0].stop or record.start <= current_meeting[0].stop and record.start >= current_meeting[0].start and record.stop >= current_meeting[0].stop:
                    for rec in record.employee_ids:
                        other_participant_list.append(rec.id)
        internal_participants_id = []
        if current_meeting:
            for participant in current_meeting[0].employee_ids:
                internal_participants_id.append(participant.id)
        employee_record = request.env['hr.employee'].sudo().search([('id','=',emp_id)])
        if employee_record:
            internal_participants_id.append(employee_record.id)
        end_meeting_list = []
        blank = [{}]
        r_data = {}
        present_employee = request.env['kw_daily_employee_attendance'].sudo().search(
            [('attendance_recorded_date', '=', datetime.strptime(str(date.today()), '%Y-%m-%d').strftime('%d %b %Y')),
             ('employee_id', '=', emp_id)])
        local_visit = request.env['kw_lv_apply'].sudo().search(
            [('state', '=', 'office_out'), ('applied_by', '=', emp_id), ('visit_date', '=', date.today())])
        if current_meeting and current_meeting[0].create_uid.employee_ids.id == organiser_id:
            if not local_visit and emp_id in current_meeting[0].employee_ids.ids or emp_id in other_participant_list:
                r_data.update({
                    'AddParticipantsResult': "MEETING",
                })
                end_meeting_list.append(r_data)
            if present_employee and present_employee.status == 'Present':
                if local_visit:
                    r_data.update({
                        'AddParticipantsResult': "LOCAL VISIT",
                    })
                    end_meeting_list.append(r_data)
                if emp_id not in current_meeting[0].employee_ids.ids and not local_visit:
                    if emp_id not in other_participant_list:
                        """adding participants"""
                        current_meeting[0].sudo().write({
                            'employee_ids': [(6, 0, internal_participants_id)],
                        })
                        r_data.update({
                            'AddParticipantsResult': "PRESENT",
                        })

                        end_meeting_list.append(r_data)
            if present_employee and present_employee.status in ['Absent','First Half Absent','Second Half Absent']:
                r_data.update({
                    'AddParticipantsResult': "ABSENT",
                })
                end_meeting_list.append(r_data)
            if present_employee.status == 'On Tour':
                r_data.update({
                    'AddParticipantsResult': "TOUR",
                })
                end_meeting_list.append(r_data)
            if present_employee.status == 'On Leave':
                r_data.update({
                    'AddParticipantsResult': "LEAVE",
                })
                end_meeting_list.append(r_data)
        if end_meeting_list:
            return valid_response(end_meeting_list)
        else:
            return valid_response(blank)
        # return invalid_response(
        #     "invalid object model",
        #     "The model %s is not available in the registry." % ioc_name,
        # )
