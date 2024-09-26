# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# from odoo.api import Environment
import json
from datetime import datetime
from datetime import timedelta, MAXYEAR
from dateutil.relativedelta import relativedelta
from dateutil import rrule as rrule_module
import pytz
import re
import odoo.http as http

from odoo.http import request
from odoo.tools.translate import _
from odoo import SUPERUSER_ID, fields
from odoo.exceptions import UserError, ValidationError


class KwCalendarController(http.Controller):

    # @http.route('/calendar/meeting/existing', type='json', auth="user")
    def check_onetime_availability(self, id, meeting_date, meeting_room, location_id, duration):

        event_calendar = request.env['kw_meeting_events']

        ##convert string to date object
        meeting_date_time = datetime.strptime(meeting_date, "%Y-%m-%d %H:%M:%S")
        meeting_date = meeting_date_time.strftime("%Y-%m-%d")

        meeting_end_datetime = meeting_date_time + timedelta(hours=float(duration))

        user_tz = request.env.user.tz  or 'UTC'
        fmt = "%Y-%m-%d %H:%M:%S"
        local = pytz.timezone(user_tz)

        # print(user_tz)
        """ hide restricted meeting room access"""
        if request.env.user.has_group('kw_meeting_schedule.group_kw_meeting_schedule_manager'):
            room_domain = [('active', '=', True), ('location_id', '=', location_id)]
        else:
            room_domain = [('active', '=', True), ('location_id', '=', location_id),
                           ('restricted_access', '=', False)]

        room_master = request.env['kw_meeting_room_master'].search(room_domain)
        room_data = []

        for room in room_master:
            room_data.append(
                {'id': room.id, 'name': room.name, 'floor_name': room.floor_name, 'capacity': room.capacity,
                 'max_allocation': room.max_allocation})

            # print(room_ids)

        start_datetime = meeting_date + ' 00:00:00'
        end_datetime = meeting_date + ' 23:45:00'

        # print(end_datetime)

        start_loop = datetime.strptime(start_datetime, "%Y-%m-%d %H:%M:%S")
        end_loop = datetime.strptime(end_datetime, "%Y-%m-%d %H:%M:%S")

        intial_time = start_loop
        schedule_time_set = {}

        while start_loop < end_loop:
            start_loop = (start_loop + relativedelta(minutes=+15))
            date_wd_timezone = start_loop.astimezone(local)
            time_index = (datetime.strptime(date_wd_timezone.strftime(fmt),
                                            "%Y-%m-%d %H:%M:%S") - intial_time).seconds / 3600.0

            schedule_time_set[time_index] = [
                {'date_wdout_timezone': start_loop, 'fdate_wdout_timezone': start_loop.strftime('%Y-%m-%d %H:%M:%S'),
                 'date_wd_timezone': date_wd_timezone.strftime(fmt),
                 'time_wd_timezone': date_wd_timezone.strftime('%I:%M %p'), 'room_info': {}}]

        # all_ids                 = str(id).split('-')
        calendar_events = event_calendar.search(
            [('state', '!=', 'cancelled'), ('recurrency', '=', False), ('start', '>=', start_datetime),
             ('start', '<', end_datetime), ('location_id', '=', int(location_id)), ('id', '<>', int(id))])

        # print(calendar_events)       

        for date_info in schedule_time_set:
            info_data = []
            info_data = schedule_time_set[date_info][0]
            # print(info_data)

            """ Check for selected meeting duration overlapping   """
            if info_data['date_wdout_timezone'] >= meeting_date_time and (
                    info_data['date_wdout_timezone'] <= meeting_end_datetime or (
                    info_data['date_wdout_timezone'] - meeting_end_datetime).seconds == 1):
                info_data['event_overlap_sts'] = 1
            else:
                info_data['event_overlap_sts'] = 0

            for event in calendar_events:

                if info_data['date_wdout_timezone'] >= event.start and (
                        info_data['date_wdout_timezone'] <= event.stop or (
                        info_data['date_wdout_timezone'] - event.stop).seconds == 1):
                    # print("inside matching")
                    # print(str(event.meeting_room_id.id)+' '+event.meeting_room_id.name+' '+info_data['time_wd_timezone'])  
                    # print(info_data['fdate_wdout_timezone'])                    

                    if not event.meeting_room_id.id in info_data['room_info']:
                        info_data['room_info'][event.meeting_room_id.id] = {}

                    info_data['room_info'][event.meeting_room_id.id]['event_id'] = event.id
                    info_data['room_info'][event.meeting_room_id.id]['name'] = (event.name[:18] + '..') if len(
                        event.name) > 20 else event.name

                    employee_ext = request.env['hr.employee'].search([('user_id', '=', event.user_id.id)],
                                                                     limit=1).epbx_no
                    info_data['room_info'][event.meeting_room_id.id][
                        'event_details'] = event.name + """\n By: """ + event.user_id.name + """\n Extn: """ + str(
                        employee_ext)
                    info_data['room_info'][event.meeting_room_id.id]['display_time'] = event.display_time

        final_schedule_time = []
        for i in sorted(schedule_time_set):
            if 8 <= i <= 22:
                final_schedule_time.append(schedule_time_set[i][0])

        values = dict(
            event_data=final_schedule_time,
            room_master_data=room_data,
        )

        return values

    @http.route('/calendar/meeting/check_recurring', type='json', auth="user")
    def check_recurring(self, meeting_data):
        # print(meeting_data)

        event_calendar = request.env['kw_meeting_events']
        meeting_id = (meeting_data['res_id'] if 'res_id' in meeting_data else 0)
        """ for recurrent record"""
        if meeting_data['recurrency']:
            data = request.env['calendar.event']._rrule_default_values()
            data['recurrency'] = True
            rrule = self._rrule_serialize(meeting_data)

            parsed_data_concurrent = request.env['calendar.event']._rrule_parse(rrule, data, meeting_data['start'])
            meeting_data.update(parsed_data_concurrent)

            event_date = pytz.UTC.localize(fields.Datetime.from_string(meeting_data['start']))
            rset1 = rrule_module.rrulestr(str(rrule), dtstart=event_date.replace(tzinfo=None), forceset=True,
                                          ignoretz=True)
            # print(list(rset1)) 

            recurring_dates = list(rset1)
            # print(recurring_dates)
            if recurring_dates:
                """ meeting start and end date"""
                meeting_start_date = recurring_dates[0].strftime("%Y-%m-%d")
                meeting_end_date = recurring_dates[-1].strftime("%Y-%m-%d")
                # print(meeting_start_date)
                # print(meeting_end_date)
                # print(meeting_id)
                # all_ids = str(meeting_id).split('-')   ,('recurrent_id','!=',int(meeting_id))
                event_data = event_calendar.search(
                    [('state', '!=', 'cancelled'), ('recurrency', '=', False), ('start', '>=', meeting_start_date),
                     ('start', '<=', meeting_end_date), ('location_id', '=', int(meeting_data['location_id'])),
                     ('meeting_room_id', '=', int(meeting_data['meeting_room_id'])), ('id', '<>', int(meeting_id))])

                # print(event_data)

                recurring_event_data = []
                for date_info in recurring_dates:
                    event_details = {}
                    availability_sts = 1
                    end_datetime = date_info + timedelta(hours=float(meeting_data['duration']))
                    for event in event_data:
                        """ if event exists               """
                        if not (event.stop <= date_info or event.start >= end_datetime):
                            # print("inside matching")
                            # print(date_info)
                            # print(str(event.meeting_room_id.id)+' '+event.meeting_room_id.name)                    

                            availability_sts = 0
                            event_details['event_id'] = event.id
                            event_details['name'] = event.name
                            event_details['creater_name'] = event.user_id.name
                            event_details['display_time'] = event.display_time

                    recurring_event_data.append(
                        {'event_date': date_info.strftime("%Y-%m-%d"), 'availability': availability_sts,
                         'event_details': event_details})

                # print(rset1.exdate(recurring_date))            

                return dict(recurring_event_data=recurring_event_data, )
            else:
                raise ValidationError("Please enter valid date range.")
                # return {'warning': {'title': 'Warning!','message': 'Please enter valid date range.'}}
        else:

            return self.check_onetime_availability(meeting_id, meeting_data['start'], meeting_data['meeting_room_id'],
                                                   meeting_data['location_id'], meeting_data['duration'])

    def _rrule_serialize(self, meeting_data):
        """ Compute rule string according to value type RECUR of iCalendar
            :return: string containing recurring rule (empty if no rule)
        """
        if meeting_data['interval'] and meeting_data['interval'] < 0:
            raise UserError(_('interval cannot be negative.'))
        if meeting_data['count'] and meeting_data['count'] <= 0:
            raise UserError(_('Event recurrence interval cannot be negative.'))

        def get_week_string(freq):
            weekdays = ['mo', 'tu', 'we', 'th', 'fr', 'sa', 'su']
            if freq == 'weekly':
                byday = [field.upper() for field in weekdays if meeting_data[field]]
                if byday:
                    return ';BYDAY=' + ','.join(byday)
            return ''

        def get_month_string(freq):
            if freq == 'monthly':
                if meeting_data['month_by'] == 'date' and (meeting_data['day'] < 1 or meeting_data['day'] > 31):
                    raise UserError(_("Please select a proper day of the month."))

                if meeting_data['month_by'] == 'day' and meeting_data['byday'] and meeting_data[
                    'week_list']:  # Eg : Second Monday of the month
                    return ';BYDAY=' + meeting_data['byday'] + meeting_data['week_list']
                elif meeting_data['month_by'] == 'date':  # Eg : 16th of the month
                    return ';BYMONTHDAY=' + str(meeting_data['day'])
            return ''

        def get_end_date():
            final_date = meeting_data['final_date']
            end_date_new = ''.join((re.compile('\d')).findall(final_date)) + 'T235959Z' if final_date else False
            return (meeting_data['end_type'] == 'count' and (';COUNT=' + str(meeting_data['count'])) or '') + \
                   ((end_date_new and meeting_data['end_type'] == 'end_date' and (';UNTIL=' + end_date_new)) or '')

        freq = meeting_data['rrule_type']  # day/week/month/year
        result = ''
        if freq:
            interval_string = meeting_data['interval'] and (';INTERVAL=' + str(meeting_data['interval'])) or ''
            result = 'FREQ=' + freq.upper() + get_week_string(
                freq) + interval_string + get_end_date() + get_month_string(freq)
        return result
