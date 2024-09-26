# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from ast import literal_eval


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # employee_fla_ids = fields.Many2many('hr.employee', 'employee_fla_rel', 'employee_id', 'approver_id', string='First Level Employees')
    employee_first_level_ids = fields.Many2many('hr.employee', 'hr_recruitment_mrf_first_level_emp_rel', 'emp_id',
                                                'approver_id', string='CEO Office Employees')
    first_level_approver_ids = fields.Many2many('hr.employee', 'hr_recruitment_mrf_first_level_emp_approval_rel',
                                                'emp_id', 'approver_id', string='First Level Approval')
    second_level_approver_ids = fields.Many2many('hr.employee', 'hr_recruitment_mrf_sec_level_emp_approval_rel',
                                                 'emp_id', 'approver_id', string='CEO')
    user_id = fields.Many2one('res.users', "Responsible", )
    # approval_user_ids = fields.Many2many("hr.employee","approval_user_empl_rel","approver_id","empl_id",string="Approval Notification")
    approval_ids = fields.Many2many('hr.employee', 'final_empl_approval_rel', 'emp_id', 'final_approval_id',
                                    string='TAG Managers')
    notify_cc_ids = fields.Many2many('hr.employee', 'cc_emp_approval_rel', 'emp_id', 'cce_id', string='TAG CC Email')
    interview_feedback_check = fields.Boolean(string="Interview Feedback Check")
    rcm_head = fields.Many2many('hr.employee', 'hr_recruitment_mrf_rcm_head_rel', 'emp_id', 'approver_id',
                                string='RCM Head')
    tag_head = fields.Many2many('hr.employee', 'hr_recruitment_mrf_tag_head_rel', 'emp_id', 'approver_id',
                                string='TAG Head')
    interview_feedback_date = fields.Date(string="Check Interview Feedback Date After")
    employee_jd_check = fields.Boolean(string="Employee JD")

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('kw_recruitment.employee_first_level_ids', self.employee_first_level_ids.ids)
        self.env['ir.config_parameter'].set_param('kw_recruitment.first_level_approver_ids', self.first_level_approver_ids.ids)
        self.env['ir.config_parameter'].set_param('kw_recruitment.second_level_approver_ids', self.second_level_approver_ids.ids)
        self.env['ir.config_parameter'].set_param('kw_recruitment.user_id', self.user_id.id)
        # self.env['ir.config_parameter'].set_param('kw_recruitment.approval_user_ids', self.approval_user_ids.ids)
        self.env['ir.config_parameter'].set_param('kw_recruitment.approval_ids', self.approval_ids.ids)
        self.env['ir.config_parameter'].set_param('kw_recruitment.notify_cc_ids', self.notify_cc_ids.ids)
        self.env['ir.config_parameter'].set_param('kw_recruitment.rcm_head', self.rcm_head.ids)
        self.env['ir.config_parameter'].set_param('kw_recruitment.tag_head', self.tag_head.ids)
        self.env['ir.config_parameter'].set_param('kw_recruitment.interview_feedback_check', self.interview_feedback_check or False)
        self.env['ir.config_parameter'].set_param('kw_recruitment.interview_feedback_date', self.interview_feedback_date or False)
        self.env['ir.config_parameter'].set_param('kw_recruitment.employee_jd_check', self.employee_jd_check or False)

        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        employee_first_level_ids = self.env['ir.config_parameter'].sudo().get_param('kw_recruitment.employee_first_level_ids')
        employees = False
        if employee_first_level_ids:
            employees = [(6, 0, literal_eval(employee_first_level_ids))]
        first_level_approver_ids = self.env['ir.config_parameter'].sudo().get_param('kw_recruitment.first_level_approver_ids')
        lines = False
        if first_level_approver_ids:
            lines = [(6, 0, literal_eval(first_level_approver_ids))]
        second_level_approver_ids = self.env['ir.config_parameter'].sudo().get_param('kw_recruitment.second_level_approver_ids')
        sec_lines = False
        if second_level_approver_ids:
            sec_lines = [(6, 0, literal_eval(second_level_approver_ids))]

        final_approver_ids = self.env['ir.config_parameter'].sudo().get_param('kw_recruitment.approval_ids')
        flines = False
        if final_approver_ids:
            flines = [(6, 0, literal_eval(final_approver_ids))]

        notify_cc_ids = self.env['ir.config_parameter'].sudo().get_param('kw_recruitment.notify_cc_ids')
        cclines = False
        if notify_cc_ids:
            cclines = [(6, 0, literal_eval(notify_cc_ids))]
            
        rcm_head = self.env['ir.config_parameter'].sudo().get_param('kw_recruitment.rcm_head')
        rcmlines = False
        if rcm_head:
            rcmlines = [(6, 0, literal_eval(rcm_head))]
        
        tag_head = self.env['ir.config_parameter'].sudo().get_param('kw_recruitment.tag_head')
        taglines = False
        if tag_head:
            taglines = [(6, 0, literal_eval(tag_head))]

        user = self.env['ir.config_parameter'].sudo().get_param('kw_recruitment.user_id', default=False)
        # tag = self.env['ir.config_parameter'].sudo().get_param('kw_recruitment.tag_head', default=False)
        # rcm = self.env['ir.config_parameter'].sudo().get_param('kw_recruitment.rcm_head', default=False)

        res.update(
            employee_first_level_ids=employees,
            first_level_approver_ids=lines,
            second_level_approver_ids=sec_lines,
            user_id=int(user),
            approval_ids=flines,
            notify_cc_ids=cclines,
            rcm_head=rcmlines,
            tag_head=taglines,
            interview_feedback_check=self.env['ir.config_parameter'].sudo().get_param('kw_recruitment.interview_feedback_check'),
            interview_feedback_date=self.env['ir.config_parameter'].sudo().get_param('kw_recruitment.interview_feedback_date'),
            employee_jd_check=self.env['ir.config_parameter'].sudo().get_param('kw_recruitment.employee_jd_check')
        )
        return res
