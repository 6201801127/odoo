# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.api import Environment
import odoo.http as http
from odoo.http import request, Response
from odoo import SUPERUSER_ID
from odoo import registry as registry_get

from datetime import datetime
import json
import werkzeug.wrappers


class MeetingScheduleController(http.Controller):

    @http.route('/meeting_schedule/meeting/accept', type='http', auth="user", website=True)
    def accept(self, db, token, action, id, **kwargs):
        registry = registry_get(db)
        error_message = False
        with registry.cursor() as cr:
            env = Environment(cr, SUPERUSER_ID, {})
            attendee = env['kw_meeting_attendee'].search([('access_token', '=', token)], limit=1)
            if attendee:
                attendee.do_accept()
            if not attendee:
                error_message = "Invalid Invitation Token."
            elif request.session.uid and request.session.login != 'anonymous':
                # if valid session but user is not match
                user = env['res.users'].sudo().browse(request.session.uid)
                if attendee.partner_id != user.partner_id:
                    error_message = "Invitation cannot be forwarded via email. This event/meeting belongs to %s and you are logged in as %s. Please ask organizer to add you." % (
                        attendee.email, user.email)
        if error_message:
            return Response(error_message, status=400)
        # return self.view(db, token, action, id, view='form')

        return http.request.render('kw_meeting_schedule.kw_meeting_schedule_response_template', {'datas': attendee})

    @http.route('/meeting_schedule/meeting/decline', type='http', auth="user", website=True)
    def declined(self, db, token, action, id):
        registry = registry_get(db)
        error_message = False
        with registry.cursor() as cr:
            env = Environment(cr, SUPERUSER_ID, {})
            attendee = env['kw_meeting_attendee'].search([('access_token', '=', token)])
            if attendee:
                attendee.do_decline()
            if not attendee:
                error_message = "Invalid Invitation Token."
            elif request.session.uid and request.session.login != 'anonymous':
                # if valid session but user is not match
                user = env['res.users'].sudo().browse(request.session.uid)
                if attendee.partner_id != user.partner_id:
                    error_message = "Invitation cannot be forwarded via email. This event/meeting belongs to %s and you are logged in as %s. Please ask organizer to add you." % (
                        attendee.email, user.email)
        if error_message:
            return Response(error_message, status=400)
        # return self.view(db, token, action, id, view='form')
        return http.request.render('kw_meeting_schedule.kw_meeting_schedule_response_template', {'datas': attendee})

    @http.route('/meeting_schedule/meeting/view', type='http', auth="kwmeetingcalender")
    def view(self, db, token, action, id, view='calendar'):
        registry = registry_get(db)
        with registry.cursor() as cr:
            # Since we are in auth=none, create an env with SUPERUSER_ID
            env = Environment(cr, SUPERUSER_ID, {})
            attendee = env['kw_meeting_attendee'].search([('access_token', '=', token), ('event_id', '=', int(id))])
            if not attendee:
                return request.not_found()
            timezone = attendee.partner_id.tz
            lang = attendee.partner_id.lang or 'en_US'
            event = env['kw_meeting_events'].with_context(tz=timezone, lang=lang).browse(int(id))

            # If user is internal and logged, redirect to form view of event
            # otherwise, display the simplifyed web page with event informations
            if request.session.uid and request.env['res.users'].browse(request.session.uid).user_has_groups(
                    'base.group_user'):
                return werkzeug.utils.redirect('/web?db=%s#id=%s&view_type=form&model=kw_meeting_events' % (db, id))

            # NOTE : we don't use request.render() since:
            # - we need a template rendering which is not lazy, to render before cursor closing
            # - we need to display the template in the language of the user (not possible with
            #   request.render())
            response_content = env['ir.ui.view'].with_context(lang=lang).render_template(
                'kw_meeting_schedule.invitation_page_anonymous', {
                    'event': event,
                    'attendee': attendee,
                })
            return request.make_response(response_content, headers=[('Content-Type', 'text/html')])

    # Function used, in RPC to check every 5 minutes, if notification to do for an event or not
    # @http.route('/meeting_schedule/notify', type='json', auth="user")
    # def notify(self):
    #     return request.env['calendar.alarm_manager'].get_next_notif()

    # @http.route('/meeting_schedule/notify_ack', type='json', auth="user")
    # def notify_ack(self, type=''):
    #     return request.env['res.partner']._set_calendar_last_notif_ack()

    """REST API to get the meeting schedule data"""
    @http.route('/meetingSchedulerDetailsV3/<meeting_date>/<int:emp_kw_id>/<int:type>', type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def meetingSchedulerDetailsV3(self, meeting_date, emp_kw_id, type):
        meeting_events = request.env['kw_meeting_events'].sudo()
        meeting_rooms = request.env['kw_meeting_room_master'].sudo()
        meeting_activities = request.env['kw_meeting_agenda_activities'].sudo()
        meeting_date = datetime.strptime(meeting_date, "%d-%m-%Y").date()
        meeting_info = {}

        pendingTask = meeting_activities.search_count(
            [('activity_type', '=', 'activity'), ('state', '!=', 'completed'), ('assigned_to.kw_id', '=', emp_kw_id)])

        """all meeting data"""
        if type == 0:
            meeting_data = meeting_events.search(
                [('state', 'not in', ['cancelled']), ('recurrency', '=', False), ('start', '>=', meeting_date),
                 ('start', '<=', meeting_date)])
            data1 = []

            completed_task = meeting_activities.search_count(
                [('activity_type', '=', 'activity'), ('state', '=', 'completed'),
                 ('assigned_to.kw_id', '=', int(emp_kw_id))])

            for meeting in meeting_data:
                start_time = meeting.display_time[meeting.display_time.rfind("(") + 1:meeting.display_time.rfind("To") - 1]
                end_time = meeting.display_time[meeting.display_time.rfind("To") + 3:meeting.display_time.rfind(")")]
                meeting_theme = ', '.join(meeting.categ_ids.mapped('name'))
                participants = ', '.join(meeting.employee_ids.mapped('name'))

                data1.append({"ARRANGED_BY": meeting.user_id.name, "START_TIME": start_time, "END_TIME": end_time,
                              "INFO_REQUIRED": meeting.name, "MEETING_ID": meeting.id,
                              "MEETING_STATUS": '1' if meeting.meeting_start_status else '0',
                              "MOM_STATUS": '1' if meeting.mom_required else '0', "ROOM_ID": meeting.meeting_room_id.id,
                              "SCHEDULE_TYPE": 'R' if meeting.parent_id else 'O', "THEME": meeting_theme,
                              "USER_EXIST": "1" if emp_kw_id in meeting.employee_ids.mapped('kw_id') else "0",
                              "completedTask": completed_task, "participants": participants,
                              "pendingTask": pendingTask})

            data2 = []
            meeting_rooms = meeting_rooms.search([('visibility_status', '=', True)])
            for room in meeting_rooms:
                data2.append({"ROOM_ID": room.id, "ROOM_NAME": room.name})

            meeting_info = {'meetingSchedulerDetailsV3Result': [{"data1": data1, "data2": data2, "data3": [], "data4": [
                {"TASKS_COUNT": completed_task + pendingTask}]}]}

        elif type == 1:
            """my meeting data"""
            data3 = []
            my_meeting_data = meeting_events.search(
                [('state', 'not in', ['cancelled']), ('recurrency', '=', False), ('start', '>=', meeting_date),
                 ('start', '<=', meeting_date), ('employee_ids.kw_id', 'in', [emp_kw_id])])

            for meeting in my_meeting_data:
                start_time = meeting.display_time[meeting.display_time.rfind("(") + 1:meeting.display_time.rfind("To") - 1]
                end_time = meeting.display_time[meeting.display_time.rfind("To") + 3:meeting.display_time.rfind(")")]
                meeting_theme = ', '.join(meeting.categ_ids.mapped('name'))

                data3.append({"START_TIME": start_time, "END_TIME": end_time, "MEETING_ID": meeting.id,
                              "ROOM_ID": meeting.meeting_room_id.id, "ROOM_NAME": meeting.meeting_room_id.name,
                              "SCHEDULE_TYPE": 'R' if meeting.parent_id else 'O', "THEMENAME": meeting_theme,
                              "TOT_PENDING_TASK": pendingTask, "NO_OF_MEETING": ""})

            meeting_info = {'meetingSchedulerDetailsV3Result': [{"data1": [], "data2": [], "data3": data3, "data4": []}]}

        return werkzeug.wrappers.Response(
            status=200,
            content_type="application/json; charset=utf-8",
            response=json.dumps(meeting_info),
        )
