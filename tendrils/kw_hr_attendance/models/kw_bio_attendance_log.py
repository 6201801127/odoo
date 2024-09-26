# -*- coding: utf-8 -*-
# # BIo attendance service request/ processing :: Created BY : T Ketaki Debadrashini,  On :10-July-2020
import pytz
from datetime import datetime, timedelta
import json

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class BioAttendanceRequest(models.Model):
    _name = 'kw_bio_atd_request_response'
    _description = 'Bio Attendance Request and Response'
    _order = 'create_date desc'

    name = fields.Char(string="Request Id", )
    request_info = fields.Text(string="Received Bio Info", )
    response = fields.Text(string="Generated Bio Response", )

    @api.model
    def create(self, values):
        """
            Create a new record for a model ModelName
            @param values: provides a data for new record
    
            @return: returns a id of new record
        """
        result = super(BioAttendanceRequest, self).create(values)

        result._process_bio_request()
        # print('after atd processing ----------')
        return result

    @api.multi
    def _process_bio_request(self):
        """
            Create a new record for a bio-attendnace enrollment
            @param values: provides a data for new record
    
            @return: returns True
        """
        for record in self:

            all_bio_attendance = [bio_rec.split(',') if bio_rec else None for bio_rec in record.request_info.split('~')]
            # print(all_bio_attendance)
            enrollement_sync_records = self.env['kw_bio_atd_enroll_info']._prepare_enroll_info(all_bio_attendance)

            if enrollement_sync_records:
                # response        = ''
                jsn_response = []
                for sync_record in enrollement_sync_records:
                    response_msg = 'Success' if sync_record.sync_status == 1 else f"Failed to identify user with INT_BIOID={sync_record.enroll_no} for @ATT_ESSLID={sync_record.event_type}"

                    # response +=f"ESSLID-{str(sync_record.event_type)}#SyncStatus-{str(sync_record.sync_status)}#ResponeMsg-{response_msg}#"
                    jsn_response.append(f"ESSLID-{str(sync_record.event_type)}#SyncStatus-{str(sync_record.sync_status)}#ResponeMsg-{response_msg}")
                # print(jsn_response)
                record.response = json.dumps(jsn_response)  # response

            # print('inside atd processing ----------')


class BioAttendanceEnrollInfo(models.Model):
    _name = 'kw_bio_atd_enroll_info'
    _description = 'Bio Attendance Request Processing as per the employee enrollment no'
    _rec_name = 'enroll_no'

    machine_no = fields.Integer(string="Machine No", )
    t_machine_no = fields.Integer(string="T Machine No", )
    enroll_no = fields.Integer(string="Enroll No", )
    enroll_machine_no = fields.Integer(string="Enroll Machine No", )

    verify_mode = fields.Integer(string="Verify Mode", )
    date = fields.Datetime(string="Date with TimeZone", )
    event_type = fields.Integer(string="ESSL ID", )

    # emp_tz_date_time   = fields.Datetime(string="Date in Employee Timezone",)
    sync_status = fields.Integer(string="Sync Status", default=0)

    @api.model
    def _prepare_enroll_info(self, bio_info_request):
        enrollement_info = []
        enrollement_sync_records = self.env['kw_bio_atd_enroll_info']

        for enrolle_info in bio_info_request:
            str_date = "".join((enrolle_info[5].strip("'"), ":00"))

            enrollement_info.append(self._get_enroll_values(machine_no=enrolle_info[0], t_machine_no=enrolle_info[1],
                                                            enroll_no=enrolle_info[2],
                                                            enroll_machine_no=enrolle_info[3],
                                                            verify_mode=enrolle_info[4], date=str_date,
                                                            event_type=enrolle_info[6]))

        # print(enrollement_info)

        if enrollement_info:
            enrollement_sync_records = self.create(enrollement_info)

        return enrollement_sync_records

    def _get_enroll_values(self, machine_no=0, t_machine_no=0, enroll_no=0, enroll_machine_no=0, verify_mode=0,
                           date=None, event_type=0):

        enroll_datetime = datetime.strptime(date, "%Y-%m-%d %H:%M:%S") if date else None

        return {
            'machine_no': int(machine_no),
            't_machine_no': int(t_machine_no),
            'enroll_no': int(enroll_no),
            'enroll_machine_no': int(enroll_machine_no),
            'verify_mode': int(verify_mode),
            'date': enroll_datetime,
            'event_type': int(event_type),
        }

    @api.model
    def create(self, values):
        """
            Create a new record for a model ModelName
            @param values: provides a data for new record
    
            @return: returns a id of new record
        """
        result = super(BioAttendanceEnrollInfo, self).create(values)
        
        attendance_device_ids = self.env['kw_device_master'].search([('type','=','attendance')]).mapped('device_id')
        baverage_device_ids = self.env['kw_device_master'].search([('type','=','baverage')]).mapped('device_id')
        meal_device_ids = self.env['kw_device_master'].search([('type','=','meal')]).mapped('device_id')

        if result.verify_mode in attendance_device_ids:
            result.create_bio_attendance_log()
        elif result.verify_mode in baverage_device_ids:
            result.create_baverage_bio_logs()
        elif result.verify_mode in meal_device_ids:
            result.create_meal_bio_logs()
        else:
            result.create_bio_attendance_log()
        return result

    # #process bio-attendance info
    @api.multi
    def create_bio_attendance_log(self):
        for record in self:
            # utc_date_time sync_status  date

            employee_rec = self.env['hr.employee'].search([('biometric_id', '=', str(record.enroll_no))])
            if employee_rec:
                emp_tz = pytz.timezone(employee_rec.tz or employee_rec.resource_calendar_id.tz or 'UTC')
                datetime_emp_tz = emp_tz.localize(record.date)

                # Convert to employee time zone
                utc_in_datetime = datetime_emp_tz.astimezone(pytz.timezone('UTC'))
                # print(utc_in_datetime)
                prev_date = utc_in_datetime.date() - timedelta(days=1)

                latest_bio_log_rec = self.env['hr.attendance'].sudo().search(
                    [('employee_id', '=', employee_rec.id), ('check_in_mode', '=', 1)], limit=1)

                if latest_bio_log_rec and latest_bio_log_rec.check_in and not latest_bio_log_rec.check_out \
                        and latest_bio_log_rec.check_in.date() in [prev_date, utc_in_datetime.date()] \
                        and latest_bio_log_rec.check_in < datetime.strptime(
                        utc_in_datetime.strftime('%Y-%m-%d %H:%M:%S'), "%Y-%m-%d %H:%M:%S"):

                    latest_bio_log_rec.sudo().write({'check_out': utc_in_datetime})
                else:
                    self.env['hr.attendance'].sudo().create({'employee_id': employee_rec.id,
                                                             'check_in': utc_in_datetime,
                                                             'check_in_mode': 1})

                record.sync_status = 1

    @api.multi
    def create_baverage_bio_logs(self):
        for record in self:
            tea_coffee_id = self.env['kw_canteen_beverage_type'].sudo().search([('device_ids.device_id','in',[record.verify_mode])])
            location_id = self.env['kw_device_master'].sudo().search([('device_id','=',record.verify_mode)],limit=1)
            employee_id = self.env['hr.employee'].search([('biometric_id','=',str(record.enroll_no))],limit=1)
            baverage_dict = {
                'employee_id':employee_id.id,
                'emp_code':employee_id.emp_code,
                'essl_id':record.event_type,
                'beverage_type_id': tea_coffee_id.id,
                'total_price': tea_coffee_id.beverage_price,
                'infra_unit_location_id': location_id.infra_unit_location_id.id,
                'recorded_date':record.date - timedelta(hours=5,minutes=30)}
            self.env['baverage_bio_log'].sudo().create(baverage_dict)
            record.sync_status = 1

    @api.multi
    def create_meal_bio_logs(self):
        for record in self:
            employee_id = self.env['hr.employee'].search([('biometric_id','=',str(record.enroll_no))],limit=1)
            # print("employee_id", employee_id)
            location_id = self.env['kw_device_master'].sudo().search([('device_id','=',record.verify_mode)],limit=1)
            regular_id = self.env['price_master_configuration'].search([('meal_code','=','R')])
            guest_id = self.env['price_master_configuration'].search([('meal_code','=','G')])

            exist_regular_meal_employee_id = self.env['kw_canteen_regular_meal'].sudo().search(['|','&','&',('state','=','approved'),('is_special','=',False),
                '&', '&', '&', '&', ('start_date', '!=', False), ('end_date','!=',False), ('start_date','<=',record.date), ('end_date','>=',record.date), ('employee_id','=',employee_id.id),
                '&', '&', '&', ('start_date','!=', False), ('end_date', '=', False), ('start_date','<=',record.date),('employee_id','=',employee_id.id)],limit=1)
            exist_meal_employee_id = self.env['meal_bio_log'].sudo().search([('employee_id','=',employee_id.id),('recorded_date','=',record.date)],limit=1)

            veg,nonveg =0,0
            wednesday =exist_regular_meal_employee_id.filtered(lambda r:r.opt_wedday == True).mapped('wedday_meal_id.code')
            if  wednesday == 'veg':                   
                veg = 1
            else:
                nonveg = 1
            friday =exist_regular_meal_employee_id.filtered(lambda r:r.opt_friday == True).mapped('friday_meal_id.code')
            if  friday== 'veg':                   
                veg = 1
            else:
                nonveg = 1
            saturday_meal_id =exist_regular_meal_employee_id.filtered(lambda r:r.opt_saturday == True).mapped('saturday_meal_id.code')
            if  saturday_meal_id == 'veg':                   
                veg = 1
            else:
                nonveg = 1
            sunday_meal_id =exist_regular_meal_employee_id.filtered(lambda r:r.opt_sunday == True).mapped('sunday_meal_id.code')
            if  sunday_meal_id == 'veg':                   
                veg = 1
            else:
                nonveg = 1
            day = record.date.weekday()
            no_of_veg = 1 if day == 0 or day == 1 or day ==3 else veg
            no_of_non_veg = 0 if day == 0 or day == 1 or day ==3 else nonveg
            if exist_regular_meal_employee_id and not exist_meal_employee_id:
                exclusion_id = self.env['exclusion_canteen_meal'].search([('regular_id','=',exist_regular_meal_employee_id.id),('start_date','<=',record.date),
                                ('end_date','>=',record.date),('exclusion_type','=','temporary')],limit=1)
                if not exist_regular_meal_employee_id.opt_monday and record.date.weekday() == 0 or \
                    not exist_regular_meal_employee_id.opt_tuesday and record.date.weekday() == 1 or \
                        not exist_regular_meal_employee_id.opt_wedday and record.date.weekday() == 2 or \
                            not exist_regular_meal_employee_id.opt_thursday and record.date.weekday() == 3 or \
                                not exist_regular_meal_employee_id.opt_friday and record.date.weekday() == 4 or \
                                    not exist_regular_meal_employee_id.opt_saturday and record.date.weekday() == 5 or \
                                        not exist_regular_meal_employee_id.opt_sunday and record.date.weekday() == 6:
                    meal_dict = {
                        'employee_id':employee_id.id,
                        'emp_code':employee_id.emp_code,
                        'essl_id':record.event_type,
                        'infra_unit_location_id': location_id.infra_unit_location_id.id,
                        'no_of_veg': no_of_veg,
                        'no_of_non_veg': no_of_non_veg,
                        'recorded_date':record.date,
                        'meal_type_id':guest_id.id,
                        'meal_price':guest_id.price,
                        'card_punch': 'yes'
                    }
                    exist_meal_employee_id.sudo().create(meal_dict)
                elif exclusion_id:
                    guest_meal_dict = {
                    'employee_id':employee_id.id,
                    'emp_code':employee_id.emp_code,
                    'essl_id':record.event_type,
                    'infra_unit_location_id': location_id.infra_unit_location_id.id,
                    'no_of_veg': no_of_veg,
                    'no_of_non_veg': no_of_non_veg,
                    'recorded_date':record.date,
                    'meal_type_id':guest_id.id,
                    'meal_price':guest_id.price,
                    'is_special': exist_regular_meal_employee_id.is_special,
                    'card_punch': 'yes'
                    }
                    exist_meal_employee_id.sudo().create(guest_meal_dict)
                else:
                    meal_dict = {
                        'employee_id':employee_id.id,
                        'emp_code':employee_id.emp_code,
                        'essl_id':record.event_type,
                        'infra_unit_location_id': exist_regular_meal_employee_id.infra_unit_location_id.id,
                        'recorded_date':record.date,
                        'no_of_veg': no_of_veg,
                        'no_of_non_veg': no_of_non_veg,
                        'meal_price':regular_id.price,
                        'meal_type_id':regular_id.id,
                        'is_special': exist_regular_meal_employee_id.is_special,
                        'card_punch': 'yes'
                    }
                    exist_meal_employee_id.sudo().create(meal_dict)
            elif not exist_regular_meal_employee_id and not exist_meal_employee_id:
                meal_dict = {
                    'employee_id':employee_id.id,
                    'emp_code':employee_id.emp_code,
                    'essl_id':record.event_type,
                    'infra_unit_location_id': location_id.infra_unit_location_id.id,
                    'no_of_veg': no_of_veg,
                    'no_of_non_veg': no_of_non_veg,
                    'recorded_date':record.date,
                    'meal_type_id':guest_id.id,
                    'meal_price':guest_id.price,
                    'card_punch': 'yes'}
                exist_meal_employee_id.sudo().create(meal_dict)
                pass
            else:
                # print(exist_meal_employee_id)
                exist_meal_employee_id.sudo().write({
                    'infra_unit_location_id': location_id.infra_unit_location_id.id,
                    'meal_price': exist_meal_employee_id.meal_type_id.price,
                    'is_special': exist_regular_meal_employee_id.is_special,
                    'essl_id': record.event_type,
                    'card_punch': 'yes'
                })
                pass
            record.sync_status = 1
        # pass
