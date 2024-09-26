from ast import literal_eval
from odoo import api, fields, models
from odoo.addons.base.models.res_partner import _tz_get

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_kw_hr_attendance_status = fields.Boolean(string="Enable Portal Attendance")
    late_entry_screen_enable = fields.Boolean(string="Enable Late Entry Screen")
    # exclude_grades_ids= fields.Many2many('kwemp_grade_master',string='Excluded Grades')
    attn_exclude_grade_ids = fields.Many2many('kwemp_grade_master', 'kwemp_grade_master_attendance_rel', string="Excluded Grades")
    hr_core_team_ids = fields.Many2many('hr.employee','kw_attn_employee_rel','employee_id','resource_calendar_id',string='HR Core Team')



    recompute_start_day = fields.Integer(string="Recomputation Start Day")
    recompute_previous_month = fields.Boolean(string="Recompute Previous Month")
    reminder_mail_start_day = fields.Integer(string="Start Day")

    kwantify_atd_sync_url = fields.Char(string="Kwantify Web-Service Url")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        param = self.env['ir.config_parameter'].sudo()
        attn_exclude_grade_ids = param.get_param('kw_hr_attendance.attn_exclude_grade_ids')
        lines = False
        if attn_exclude_grade_ids:
            lines = [(6, 0, literal_eval(attn_exclude_grade_ids))]
        res.update(
            module_kw_hr_attendance_status=param.get_param('kw_hr_attendance.module_kw_hr_attendance_status'),
            late_entry_screen_enable=param.get_param('kw_hr_attendance.late_entry_screen_enable'),
            recompute_start_day=int(param.get_param('kw_hr_attendance.recompute_start_day')),
            recompute_previous_month=param.get_param('kw_hr_attendance.recompute_previous_month'),
            reminder_mail_start_day=int(param.get_param('kw_hr_attendance.reminder_mail_start_day')),
            kwantify_atd_sync_url=param.get_param('kw_hr_attendance.kwantify_atd_sync_url'),
            attn_exclude_grade_ids=lines,
        )
        core_team_ids = param.get_param('kw_hr_attendance.hr_core_team_ids')
        mail_to = False
        if core_team_ids != False:
            mail_to = [(6, 0, literal_eval(core_team_ids))]
        res.update(
            hr_core_team_ids=mail_to,
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()

        param.set_param('kw_hr_attendance.module_kw_hr_attendance_status', self.module_kw_hr_attendance_status or False)
        param.set_param('kw_hr_attendance.late_entry_screen_enable', self.late_entry_screen_enable or False)

        param.set_param('kw_hr_attendance.recompute_start_day', self.recompute_start_day or 25)
        param.set_param('kw_hr_attendance.recompute_previous_month', self.recompute_previous_month or True)
        param.set_param('kw_hr_attendance.reminder_mail_start_day', self.reminder_mail_start_day or 20)

        param.set_param('kw_hr_attendance.kwantify_atd_sync_url', self.kwantify_atd_sync_url or '')
        # param.set_param('kw_hr_attendance.exclude_grades_ids', self.exclude_grades_ids or '')
        param.set_param('kw_hr_attendance.attn_exclude_grade_ids', self.attn_exclude_grade_ids.ids)
        param.set_param('kw_hr_attendance.hr_core_team_ids', self.hr_core_team_ids.ids)


