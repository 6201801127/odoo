# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from datetime import timedelta
from pytz import utc

from odoo import api, fields, models
from odoo.tools import float_utils
from odoo.addons.resource.models.resource import Intervals

# This will generate 16th of days
ROUNDING_FACTOR = 16


class ResourceMixin(models.AbstractModel):
    _inherit = 'resource.mixin'

    def kw_get_work_days_data(self, from_datetime, to_datetime, exclude_leaves=True, calendar=None, domain=None):
        """
            By default the resource calendar is used, but it can be
            changed using the `calendar` argument.

            `domain` is used in order to recognise the leaves to take,
            None means default value ('time_type', '=', 'leave')

            Returns a dict {'days': n, 'hours': h} containing the
            quantity of working time expressed as days and as hours.
        """
        resource = self.resource_id
        calendar = calendar or self.resource_calendar_id

        # naive datetime are made explicit in UTC
        if not from_datetime.tzinfo:
            from_datetime = from_datetime.replace(tzinfo=utc)
        if not to_datetime.tzinfo:
            to_datetime = to_datetime.replace(tzinfo=utc)

        # total hours per day: retrieve attendances with one extra day margin,
        # in order to compute the total hours on the first and last days
        from_full = from_datetime - timedelta(days=1)
        to_full = to_datetime + timedelta(days=1)

        intervals = calendar._attendance_intervals(from_full, to_full, resource)
        day_total = defaultdict(float)
        for start, stop, meta in intervals:
            day_total[start.date()] += (stop - start).total_seconds() / 3600

        # actual hours per day
        if exclude_leaves:
            leave_intervals = calendar.with_context(employee_id=self.id)._work_intervals(from_datetime, to_datetime, resource, domain)

            # print(type(intervals))
            updated_intervals = []
            for start, stop, attend in leave_intervals:

                # week_offs               = set(attend.mapped('week_off'))
                # unique_week_offs        = (list(week_offs)) 
                # week_off_status         = True if len(unique_week_offs) == 1 and True in unique_week_offs else False
                roaster_shift = self.env['kw_employee_roaster_shift'].search(
                    [('employee_id', '=', self.id), ('date', '=', start.date())])

                if roaster_shift:
                    if not roaster_shift.week_off_status:
                        updated_intervals.append((start, stop, meta))
                else:
                    updated_intervals.append((start, stop, meta))

            # print(type(Intervals(updated_intervals)))
            intervals = Intervals(updated_intervals)
           
        else:
            intervals = calendar._attendance_intervals(from_datetime, to_datetime, resource)

        day_hours = defaultdict(float)
        for start, stop, meta in intervals:
           
            day_hours[start.date()] += (stop - start).total_seconds() / 3600

        # print('---------------------')
        # print(day_hours)

        # compute number of days as quarters
        # days = sum(
        #     float_utils.round(ROUNDING_FACTOR * day_hours[day] / day_total[day]) / ROUNDING_FACTOR
        #     for day in day_hours
        # )
        return {
            'days': len(day_hours),
            'hours': sum(day_hours.values()),
        }
