# -*- coding: utf-8 -*-
#########################
    # Created On : 20-Apr-2021 , Gouranga Kala
#########################

from datetime import date
from odoo import models,api

from odoo.addons.kw_hr_attendance.models.kw_daily_employee_attendance import WFH_STATUS 


class AttendanceUpdateWFHStatus(models.TransientModel):
    _name           = "kw_attendance_update_wfh_wizard"
    _description    = "Attendance Update WFH Status From WFH Module"

    @api.multi
    def update_wfh_status(self):
        self.ensure_one()
        current_date = date.today()
        try:
            wfh_data = self.env['kw_wfh'].sudo().search([
                                '|',
                                '&', '&', ('state', '=', 'grant'), ('request_from_date', '<=', current_date), ('request_to_date', '>=', current_date),
                                '&', '&', ('state', '=', 'expired'), ('act_from_date', '<=', current_date), ('act_to_date', '>=', current_date),
                                ])
            if wfh_data:
                employee_ids = wfh_data.mapped('employee_id').ids
                attendance_records = self.env['kw_daily_employee_attendance'].sudo().search(
                    [('work_mode', '!=', WFH_STATUS),
                     ('attendance_recorded_date', '=', current_date),
                     ('employee_id', 'in', employee_ids)])
                for atd in attendance_records:
                    try:
                        atd.write({'work_mode':WFH_STATUS})
                    except Exception:
                        continue

        except Exception as e:
            # print(e)
            pass
        self.env.user.notify_success("WFH Status Updated Successfully.")
