# -*- coding: utf-8 -*-
from datetime import datetime
import json

from odoo import http
from odoo.http import request


class BioAttendance(http.Controller):

    @http.route('/sync_bio_attendance/', methods=['POST'], auth='public', csrf=False, type='json', cors='*')
    def sync_bio_attendance(self, **args):
        """ @params : json
                bio_attendance ; string
            @returns : json
                status :int
        """

        # try:
        # print('The START  ::::::::::', datetime.now())
        # print(args)

        if 'bio_attendance' in args and args['bio_attendance']:
            # print(args['bio_attendance'].split('~'))
            # 7,7,307,7,26,'2020-07-02 18:22',3230451~11,11,1430,11,38,'2020-07-02 18:22',3230452~11,11,1428,11,38,'2020-07-02 18:22',3230453~11,11,26,11,38,'2020-07-02 18:22',3230454~11,11,1149,11,37,'2020-07-02 18:23',3230456~                

            req_bio_attendance = args['bio_attendance'].strip('~')

            bio_response = request.env['kw_bio_atd_request_response'].sudo().create(
                {'name': args['guid'] if 'guid' in args and args['guid'] else '', 'request_info': req_bio_attendance})

            # all_bio_attendance = [bio_rec.split(',') if bio_rec else None for bio_rec in req_bio_attendance.split('~')]
            # print(all_bio_attendance)

        # print('The END  ::::::::::', datetime.now())

        return {'status': 200,
                'response_data': json.loads(bio_response.response) if bio_response and bio_response.response else ''}
        # except Exception as e:
        #     return {'status': 500, 'error_log': str(e)}


    @http.route('/holiday_calendar_api/', methods=['GET'], auth='public', csrf=False, type='json', cors='*')
    def sync_holiday_calendar_api(self, **args):
        try:
            if args['year'] and args['branch_id'] and args['shift_id']:
                cal_start = datetime.now().date().replace(month=1, day=1, year=int(args['year']))
                cal_end = datetime.now().date().replace(month=12, day=31, year=int(args['year']))
                personal_calendar = None
                employee_id = None
                branch_id = args['branch_id'] 
                shift_id = args['shift_id']
                year=args['year']
                public_holiday=[]
                calendar_data = request.env['resource.calendar.leaves'].get_calendar_global_leaves(branch_id,shift_id,personal_calendar,employee_id,cal_start,cal_end)
                holiday_cal = calendar_data.get('holiday_calendar')
                for rec in holiday_cal:
                    if rec.get('week_off')== '2' and rec.get('year')==int(year):
                        public_holiday.append(rec)
                return {'status': 200,
                        'public_holiday': public_holiday,
                        }
        except Exception as e:
            # print("exception---------------",e)
            a=(f"The {e} field is required")
            return {'error': a,
                        }