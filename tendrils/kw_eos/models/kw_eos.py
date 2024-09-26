# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import ValidationError
import requests, json


class EndofService(models.Model):
    _name = "kw_end_of_service"
    _description = "End of Service"
    _rec_name = 'create_uid'
    _order = 'id'

    @api.depends('user_id')
    def _get_current_user(self):
        for res in self:
            res.logged_user = self.env.user.id
            if res.user_id.id == res.create_uid.id:
                res.show_approval = True

    def _compute_manager_groups(self):
        for res in self:
            if res.state == 'apply' and res.logged_user.id == res.action_to_be_taken_by.user_id.id:
                res.show_btn_apply = True
            if res.state == 'forward' and res.logged_user.id == res.action_to_be_taken_by.user_id.id:
                res.show_btn_foward = True
            if res.state == 'confirm' and res.logged_user.id == res.action_to_be_taken_by.user_id.id:
                res.show_btn_confirm = True
            if res.state == 'hold' and res.logged_user.id == res.action_to_be_taken_by.user_id.id:
                res.show_btn_hold = True

    service_from = fields.Datetime(string="Service From")
    service_to = fields.Datetime(string="Service To")
    address = fields.Text('Communication Address')
    email = fields.Char('Personal Email')
    phone = fields.Char('Contact No')
    remark = fields.Text('Remarks')
    state = fields.Selection([
        ('apply', 'Applied'),
        ('forward', 'Forwarded'),
        ('hold', 'Hold'),
        ('confirm', 'Approved'),
        ('reject', 'Rejected'), ], string="Status", default='apply', store=True)

    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    logged_user = fields.Many2one('res.users', compute='_get_current_user')
    is_RA = fields.Boolean(compute='_compute_manager_groups')
    is_forward = fields.Boolean(compute='_compute_manager_groups')

    forward_to = fields.Many2one('hr.employee', string="Forwardto")
    forward_reason = fields.Text(string="Forward Reason")
    approval_sent = fields.Boolean('Approval Sent', default=False)
    show_approval = fields.Boolean(compute='_get_current_user')
    eos_qa_lines = fields.One2many('kw_eos_qa', 'eos_id', string="Question & Answer")

    show_btn_foward = fields.Boolean(compute='_compute_manager_groups')
    show_btn_confirm = fields.Boolean(compute='_compute_manager_groups')
    show_btn_apply = fields.Boolean(compute='_compute_manager_groups')
    show_btn_hold = fields.Boolean(compute='_compute_manager_groups')

    # # Manager
    forward_by = fields.Many2one('hr.employee', string="Forwarded By", track_visibility='onchange')
    action_to_be_taken_by = fields.Many2one('hr.employee', string="Action to be taken by", track_visibility='onchange')
    kw_id = fields.Integer('KW ID', default=0)
    applicant_id = fields.Many2one('hr.employee', string="Subordinate")
    resignation_id = fields.Many2one('kw_resignation', string="Resignation Ref")
    prev_state = fields.Char('Prev State')

    @api.multi
    def take_action_button(self):
        view_id = self.env.ref('kw_eos.eos_take_action_form_view').id
        return {
            'name': 'EOS',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_end_of_service',
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(view_id, 'form')],
            'target': 'self',
            'view_id': view_id,
        }

    @api.model
    def create(self, values):
        if values.get('user_id'):
            # values['ra_id'] = self.env.user.employee_ids.parent_id.id
            values['action_to_be_taken_by'] = self.env.user.employee_ids.parent_id.id

        res = super(EndofService, self).create(values)
        template_obj = self.env.ref('kw_eos.eos_approval_mail_template')
        mail = self.env['mail.template'].browse(template_obj.id).send_mail(res.id,
                                                                           notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                           force_send=False)
        self.env.user.notify_success("EOS request applied successfully.")
        return res

    @api.multi
    def write(self, values):
        if values.get('state') == 'confirm':
            self._sync_ex_emp()
        res = super(EndofService, self).write(values)
        return res

    @api.multi
    def _sync_ex_emp(self):
        parameterurl = self.env['ir.config_parameter'].sudo().get_param('kwantify_eos_url')
        EOSurl = parameterurl + 'MoveEOSExEmp'
        header = {'Content-type': 'application/json', 'Accept': 'text/plain'}

        LeavingDate = self.service_to.strftime('%Y-%m-%d')
        userId = str(self.applicant_id.kw_id)

        EmpDict = {
            "userId": userId,
            "LeavingDate": LeavingDate
        }
        resp = requests.post(EOSurl, headers=header, data=json.dumps(EmpDict))
        j_data = json.dumps(resp.json())
        json_record = json.loads(j_data)
        if json_record.get('status') == 1:
            self.applicant_id.user_id.sudo().write({'active': False})
            # self.applicant_id.sudo().write({'active': False})
            self.resignation_id.sudo().write({'hide_btn_cancel': True})
        self.env['kw_eos_log'].sudo().create({'req_data': EmpDict, 'response_res': json_record, 'type': 'MoveEOSExEmp'})

    @api.multi
    def get_cc(self):
        param = self.env['ir.config_parameter'].sudo()
        cc_group = literal_eval(param.get_param('kw_eos.notify_cc'))
        # all_jobs = self.env['hr.job'].browse(cc_group)
        email_list = []
        if cc_group:
            empls = self.env['hr.employee'].search([('id', 'in', cc_group)])
            # empls = self.env['hr.employee'].search([('job_id', 'in', all_jobs.ids)])
            if empls:
                email_list = [empls.work_email for emp in empls if emp.work_email]

        hrd_cc_group = self.env.ref('kw_eos.group_kw_eos_cc_notify').mapped('users')
        if hrd_cc_group:
            email_list += [user.email for user in hrd_cc_group if user.email]

        return ",".join(email_list)

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('ra_eos'):
            employee = self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1)
            child_users = employee.child_ids
            args += ['|', '|', '|', ('applicant_id.user_id', '=', self._uid),
                     ('create_uid', '=', self._uid),
                     ('action_to_be_taken_by', 'in', child_users.ids),
                     ('action_to_be_taken_by', '=', employee.id)]
        return super(EndofService, self)._search(args, offset=offset, limit=limit, order=order, count=count,
                                                 access_rights_uid=access_rights_uid)

    @api.model
    def default_get(self, fields):
        result = super(EndofService, self).default_get(fields)
        qa_lines = []
        qas = self.env['kw_eos_qa'].search([])
        for qa in qas:
            qa_lines.append(qa.id)
        result.update({
            'eos_qa_lines': [(6, 0, qa_lines)],
        })
        return result


class RelievingLetter(models.Model):
    _name = "kw_reliving_letter"
    _description = "Relieving Letter"
    _order = 'id'

    employee_id = fields.Many2one('hr.employee', string="Name")
    date_joining = fields.Date('Date of Joining')
    date_resignation = fields.Date('Resignation Date')
    date_last = fields.Date('Last Date')
    communication_address = fields.Text('Communication Address')
    phone = fields.Char('Phone')
    email = fields.Char('Email')
    actual_leaving_date = fields.Date('Actual Leaving Date')
    reg_type = fields.Many2one('kw_resignation_master', string="Resignation Type")
    reason = fields.Text(string="Reason For Resignation")
    attachment_id = fields.Binary(string="Upload Release Letter")
    file_name = fields.Char('File name')
    remark = fields.Text('Remarks')
    status = fields.Selection([('granted', 'Granted')], string="Status")
