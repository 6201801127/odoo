from datetime import date, timedelta, datetime
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import calendar


class ManageRoaster(models.TransientModel):
    _name = 'kw_roaster_manage_wizard'
    _description = 'Manage Roster wizard'

    _rec_name = 'group_id'

    group_id = fields.Many2one('kw_roaster_group_config', string="Group", required=True)
    employee_id = fields.Many2many('hr.employee', string="Employee", required=True,)
    from_date = fields.Date(string="From", required=True, autocomplete="off")
    to_date = fields.Date(string="To", required=True, autocomplete="off")
    emp_roaster_id = fields.One2many(comodel_name = 'kw_roaster_employee_manage_wizard',inverse_name='roaster_id',compute='_set_employees',store=True,inverse='_get_values')

    @api.onchange('group_id')
    def show_employee_group(self):
        self.employee_id = False
        self.employee_id = self.group_id.group_member_ids.ids
        return {'domain': {'employee_id': ([('id', 'in', self.group_id.group_member_ids.ids)])}} 

    @api.multi
    @api.depends('employee_id')
    def _set_employees(self):
        for record in self:
            if len(record.employee_id) > 0:
                record.emp_roaster_id = [[0, 0,{'employee_id': data.id}] for data in record.employee_id]

    @api.multi
    def _get_values(self):
        for record in self:
            pass

    @api.constrains('from_date', 'to_date')
    def date_duration(self):
        for rec in self:
            if rec.to_date < rec.from_date:
                raise ValidationError('To Date Must be greater than From Date.')
        
    def send_roster_mail(self):
        template = self.env.ref("kw_hr_attendance.kw_roster_assign_email_template")
        body = template.body_html
        if template:
            for record in self:
                for employee in record.emp_roaster_id:
                    day_list = []
                    day_list.append("Sunday") if employee.sun else ''
                    day_list.append("Monday") if employee.mon else ''
                    day_list.append("Tuesday") if employee.tue else ''
                    day_list.append("Wednesday") if employee.wed else ''
                    day_list.append("Thursday") if employee.thu else ''
                    day_list.append("Friday") if employee.fri else ''
                    day_list.append("Saturday") if employee.sat else ''
                    extra_params = {'employee_name': employee.employee_id.name, 
                                    'employee_email': employee.employee_id.work_email,
                                    'employee_ra_email': employee.employee_id.parent_id.work_email,
                                    'from_date': datetime.strftime(record.from_date, "%d-%b-%Y"),
                                    'to_date': datetime.strftime(record.to_date, "%d-%b-%Y"),
                                    'day_list': day_list}
                    template.with_context(extra_params).send_mail(record.id, notif_layout="kwantify_theme.csm_mail_notification_light")



    @api.model
    def create(self, vals):
        new_record = super(ManageRoaster, self).create(vals)
        duration = new_record.to_date - new_record.from_date
        duration_days = duration.days + 1
        roaster_shift_record = []
        for add in range(duration_days):
            week_off = False
            next_dates = new_record.from_date + timedelta(days=add)
            # print(next_dates.weekday())
            for emp_roasters in new_record.emp_roaster_id:
                if emp_roasters.mon == True and next_dates.weekday() == 0:
                    week_off = True
                elif emp_roasters.tue == True and next_dates.weekday() == 1:
                    week_off = True
                elif emp_roasters.wed == True and next_dates.weekday() == 2:
                    week_off = True
                elif emp_roasters.thu == True and next_dates.weekday() == 3:
                    week_off = True
                elif emp_roasters.fri == True and next_dates.weekday() == 4:
                    week_off = True
                elif emp_roasters.sat == True and next_dates.weekday() == 5:
                    week_off = True
                elif emp_roasters.sun == True and next_dates.weekday() == 6:
                    week_off = True
                else:
                    week_off = False

                roaster_shift_record.append({
                        'employee_id': emp_roasters.employee_id.id,
                        'date' : next_dates,
                        'shift_id':emp_roasters.employee_id.resource_calendar_id.id,
                        'week_off_status': week_off})
        roster_set = self.env['kw_employee_roaster_shift'].create(roaster_shift_record)
        if roster_set:
            new_record.send_roster_mail()
            self.env.user.notify_success(message='Roster shift assigned to employees successfully.')
        return new_record


class ManageRoasterEmployee(models.TransientModel):
    _name = 'kw_roaster_employee_manage_wizard'
    _description = 'Manage Employee Roster wizard'

    _rec_name = 'roaster_id'

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    sun = fields.Boolean(string="Sunday") 
    mon = fields.Boolean(string="Monday") 
    tue = fields.Boolean(string="Tuesday") 
    wed = fields.Boolean(string="Wednesday")
    thu = fields.Boolean(string="Thursday")
    fri = fields.Boolean(string="Friday")
    sat = fields.Boolean(string="Saturday")
    roaster_id = fields.Many2one(comodel_name='kw_roaster_manage_wizard',string='Roster ID')
    
    _sql_constraints = [
        ('emp_roaster_uniq', 'unique(employee_id, roaster_id)', 'Please remove duplicate employee records from list.'),
        ]