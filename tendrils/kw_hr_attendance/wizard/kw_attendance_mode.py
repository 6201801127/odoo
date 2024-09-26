from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AttendanceMode(models.TransientModel):
    _name = 'kw_attendance_mode_wizard'
    _description = 'Attendance Mode Wizard'

    branch_id = fields.Many2one('kw_res_branch',string="Branch/SBU")
    employee_id = fields.Many2many('hr.employee',string="Employee")
    no_attendance = fields.Boolean(string="No Attendance")
    attendance_mode = fields.Many2many('kw_attendance_mode_master', string="Attendance Mode")

    @api.onchange('branch_id')
    def show_employee(self):
        self.employee_id = False
        return {'domain': {'employee_id': ([('user_id.branch_id', '=', self.branch_id.id)])}}

    @api.model
    def create(self, vals):
        new_record = super(AttendanceMode, self).create(vals)
        del_query,update_query,add_query = '','',''
        if new_record.employee_id:
            if new_record.no_attendance:
                for emp in new_record.employee_id:
                    del_query += f"DELETE FROM hr_employee_kw_attendance_mode_master_rel WHERE hr_employee_id={emp.id};"
                    update_query += f"update hr_employee set no_attendance = True WHERE id={emp.id};"
                self._cr.execute(del_query)
                self._cr.execute(update_query)
                # new_record.employee_id.write(
                #     {'no_attendance': True, 'attendance_mode_ids': False})

            else:
                mode_list = []
                for emp in new_record.employee_id:
                    for mode in new_record.attendance_mode.ids:
                        mode_list.append((emp.id,mode))
                    mode_ids = str(mode_list)[1:-1]
                    update_query += f"update hr_employee set no_attendance = False WHERE id={emp.id};"
                    del_query += f"DELETE FROM hr_employee_kw_attendance_mode_master_rel WHERE hr_employee_id={emp.id};"
                    add_query += f"INSERT INTO hr_employee_kw_attendance_mode_master_rel (hr_employee_id, kw_attendance_mode_master_id) VALUES {mode_ids} ON CONFLICT DO NOTHING;"

                self._cr.execute(update_query)
                self._cr.execute(del_query)
                self._cr.execute(add_query)
                # new_record.employee_id.write(
                #     {'no_attendance': False,
                #      'attendance_mode_ids': [[6, False, new_record.attendance_mode.ids]]})
        self.env.user.notify_success(message='Employee Attendance Mode Assigned successfully.')
        return new_record
