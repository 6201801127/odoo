# -*- coding: utf-8 -*-
import werkzeug
import re
from datetime import date, datetime
from odoo import models, fields, api
from odoo.exceptions import ValidationError, AccessError


class ApplyCard(models.Model):
    _name = 'kw_visiting_card_apply'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Business Card'
    _rec_name = 'emp_name'

    visiting_card_for = fields.Selection(string="Card Apply For", selection=[('self', 'Self'), ('others', 'Others')],
                                         required=True, default='self')
    card_for = fields.Char("Employee Name", compute="_compute_applied")
    create_employee_id = fields.Many2one("hr.employee", string="Applied By")
    emp_name = fields.Many2one('hr.employee', string='Employee Name', default=lambda self: self.env.user.employee_ids,
                               required=True)
    emp_code = fields.Char('Employee Code', readonly=True, default=lambda self: self.get_selfEmpCodeDetails())
    applied_date = fields.Date('Applied On', readonly=True, default=fields.Date.context_today)
    date_when_required = fields.Date('Required On', required=True, help='Mention the Date, when the cards required')
    no_of_cards_required = fields.Integer('No of cards required', required=True, size=3,
                                          help='mention the number of cards required')
    card_details = fields.Text('Card Details', default=lambda self: self.get_login_userDetails())
    state = fields.Selection(selection=[('Applied', 'Applied'),
                                        ('Approved', 'Approved'),
                                        ('Granted', 'Granted'),
                                        ('Sent For Printing', 'Sent For Printing'),
                                        ('Delivered to User', 'Delivered to User'),
                                        ('Rejected', 'Rejected')],
                             string="Status", default="Applied")
    to_be_taken_by = fields.Char(string='Action to be taken by', compute='_compute_group_members')
    remark = fields.Text('Remarks', required=True, )
    admin_remark = fields.Text('Remarks', )
    action_ids = fields.One2many(string='Action Details', comodel_name='kw_visiting_card_details',
                                 inverse_name='card_id', )
    action_count = fields.Boolean('Action Count', compute='_compute_action_ids')
    manager_access = fields.Boolean(string="Manager Access", compute="_compute_approve")
    ra_access = fields.Boolean("RA Access", compute="compute_ra_access")
    active = fields.Boolean(string="Active", default=True)
    pending_time = fields.Float("Pending Time", default=0.0, compute="_compute_time")
    vendor_name = fields.Many2one('res.partner', string='Vendor')
    vendor_email = fields.Char(string='Vendor Email', readonly=True, )
    time_expired = fields.Boolean('Time Expired', default=False)

    # @api.constrains('no_of_cards_required')
    # def _check_no_of_cards_required(self):
    #     for record in self:
    #         if len(int(record.no_of_cards_required)) <=3:
    #             raise ValidationError("Maximum 999 number can enter.")
    @api.multi
    def _compute_applied(self):
        for card in self:
            if card.visiting_card_for == "others":
                card.card_for = card.emp_name.name
            else:
                card.card_for = card.create_employee_id and card.create_employee_id.name or 'NA'

    @api.model
    def action_forward_card(self):
        apply_state_cards = self.env['kw_visiting_card_apply'].search([('state', '=', 'Applied')])
        pending_time_over_cards = apply_state_cards.filtered(lambda r: r.pending_time > 24)
        if pending_time_over_cards:
            template = self.env.ref('kw_visiting_card.kw_ra_approve_visiting_card_email_template')
            ra_template = self.env.ref('kw_visiting_card.kw_ra_auto_escalted_visiting_card_email_template')
            manager_group = self.env.ref('kw_visiting_card.group_kw_visiting_card_manager')
            manager_employees = manager_group.users.mapped('employee_ids') or False
            email_ids = manager_employees and ','.join(manager_employees.mapped('work_email')) or ''
            # template.with_context(manager_email=email_ids).send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light") 
            for card in pending_time_over_cards:
                card.write({
                    'time_expired': True,
                    'state': 'Approved',
                    'admin_remark': 'Auto Escalated',
                    'action_ids': [[0, 0, {'remarks': 'Auto Escalated',
                                           'action_status': 'Approved'}
                                    ]]
                })
                template.with_context(manager_email=email_ids, message="auto escalated by \
                    Kwantifybot due to pending time exceeded 24 hours.").send_mail(card.id,
                                                                                   notif_layout="kwantify_theme.csm_mail_notification_light")
                ra_template.send_mail(card.id, notif_layout="kwantify_theme.csm_mail_notification_light")

    @api.onchange('vendor_name')
    def set_vendor_email(self):
        if self.vendor_name:
            self.vendor_email = self.vendor_name.email
        else:
            self.vendor_email = False

    @api.multi
    def _compute_time(self):
        for rec in self:
            if rec.state == 'Applied':
                pending_time = datetime.now() - rec.create_date
                seconds_in_day = 24 * 60 * 60
                total_seconds = (pending_time.days * seconds_in_day) + pending_time.seconds
                time_hour = total_seconds / 3600
                rec.pending_time = time_hour

    @api.model
    def check_groups(self, vals):
        status = False
        if vals.get('user_id'):
            user = self.env['res.users'].browse(int(vals['user_id']))
            if user.has_group('kw_visiting_card.group_kw_visiting_card_manager'):
                status = True
        return status

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):

        if self._context.get('ra_access_check'):
            ids = []
            if self.env.user.has_group('kw_visiting_card.group_kw_visiting_card_manager'):
                query = "select id from kw_visiting_card_apply where active=True"
                self._cr.execute(query)
                ids = self._cr.fetchall()
                if len(ids) > 0:
                    cards = self.env['kw_visiting_card_apply'].browse([c[0] for c in ids])
                    ra_cards = cards.filtered(
                        lambda r: r.create_uid.id != self._uid and len(r.create_uid.employee_ids) > 0 and len(
                            r.create_uid.employee_ids.child_ids) > 0 and r.create_uid.employee_ids.parent_id == 0)
                    # print("ra_cards are",ra_cards)
                    approved_cards = cards.filtered(lambda r: r.state != 'Applied')
                    approved_cards |= cards.filtered(lambda r: r.time_expired == True)
                    approved_cards |= ra_cards
                    ids = approved_cards.ids
                args += [('id', 'in', ids)]
            else:
                args += [('time_expired', '=', False), ('state', '=', 'Applied'), ('create_uid', '!=', self._uid)]
        return super(ApplyCard, self)._search(args, offset=offset, limit=limit, order=order, count=count,
                                              access_rights_uid=access_rights_uid)

    @api.onchange('visiting_card_for')
    def _change_respected_field_values(self):
        if self.visiting_card_for in ['self']:
            self.emp_name = self.env.user.employee_ids
        else:
            self.emp_name = False

    @api.multi
    def _compute_group_members(self):
        for record in self:
            group_users = self.env.ref('kw_visiting_card.group_kw_visiting_card_manager').users
            group_users = ', '.join(group_users.mapped('name'))
            if record.state == 'Applied':
                record.to_be_taken_by = record.create_employee_id.parent_id and record.create_employee_id.parent_id.name or group_users
            elif record.state in ['Delivered to User', 'Rejected']:
                record.to_be_taken_by = ''
            else:
                # settlement_users = ''
                record.to_be_taken_by = group_users
                # for members in group_users:
            #     settlement_users += members.name +', '
            #     record.to_be_taken_by = settlement_users.rstrip(', ')

    def get_manager_name(self):
        group = self.env.ref('kw_visiting_card.group_kw_visiting_card_manager')
        if group.users:
            manager_emp = self.env['hr.employee'].sudo().search([('user_id', '=', group.users[0].id)], limit=1)
            if manager_emp:
                return manager_emp.name
            else:
                return ""
        else:
            return ""

    def get_employee_email(self):
        name_emp = self.env['hr.employee'].sudo().search([('user_id', '=', self.create_uid.id)], limit=1)
        if name_emp:
            return name_emp.work_email
        else:
            return ""

    def get_ra_email(self):
        emp_cc_mail_list=[]
        if self.emp_name and self.emp_name.parent_id and self.emp_name.parent_id.parent_id:
            emp_cc_mail_list += self.emp_name.parent_id.mapped('work_email')
        if self.emp_name.coach_id:
            emp_cc_mail_list += self.emp_name.coach_id.mapped('work_email')    
        return ','.join(set(emp_cc_mail_list))

    def get_employee_name(self):
        create_uid = self.create_uid
        employee = self.env['hr.employee'].sudo().search([('user_id', '=', create_uid.id)], limit=1)
        username = employee and employee.name or create_uid.name
        return username

    @api.multi
    def _compute_action_ids(self):
        for record in self:
            if len(record.action_ids) > 0:
                record.action_count = True
            else:
                record.action_count = False

    @api.multi
    def compute_ra_access(self):
        for record in self:
            if self.env.user.employee_ids.mapped('child_ids'):
                record.ra_access = True

    @api.multi
    def _compute_approve(self):
        for record in self:
            if self.env.user.has_group('kw_visiting_card.group_kw_visiting_card_manager'):
                record.manager_access = True
            else:
                record = False

    def get_root_departments(self, departments):
        parent_departments = departments.mapped('parent_id')
        root_departments = departments.filtered(lambda r: r.parent_id.id == 0)
        if parent_departments:
            root_departments |= self.get_root_departments(parent_departments)
        return root_departments

    @api.onchange('emp_name')
    def set_card_details(self):
        if self.emp_name:
            self.get_login_userDetails(self.emp_name)

    @api.multi
    def get_login_userDetails(self, employee_id=False):
        uid = self.env.user.id
        emp_name = self.env['hr.employee'].sudo().search([('user_id', '=', self._uid)])
        if employee_id:
            emp_name = employee_id
        emp_job = emp_name.job_id.name if emp_name.job_id else False
        emp_work_email = emp_name.work_email if emp_name.work_email else False
        emp_mobile = emp_name.mobile_phone if emp_name.mobile_phone else False
        emp_dept_name = self.get_root_departments(emp_name.department_id) if emp_name.department_id else False
        emp_loc_name = emp_name.work_location if emp_name.work_location else False

        user_details = str(emp_name.name) + "\n"
        if emp_job:
            user_details += "Designation : " + emp_job + "\n"
        if emp_dept_name:
            user_details += "Department : " + emp_dept_name.name + "\n"
        if emp_loc_name:
            user_details += "Location : " + emp_loc_name + "\n"
        if emp_work_email:
            user_details += "Email ID : " + emp_work_email + "\n"
        if emp_mobile:
            user_details += "Mobile : " + emp_mobile + "\n"
        if employee_id:
            self.card_details = user_details
        return user_details

    @api.multi
    def button_take_action(self):
        view_id = self.env.ref('kw_visiting_card.kw_apply_card_take_action_form_view').id
        target_id = self.id
        return {
            'name': 'Take Action',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_visiting_card_apply',
            'res_id': target_id,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(view_id, 'form')],
            'target': 'self',
            'view_id': view_id,
        }

    @api.multi
    def get_selfNameDetails(self):
        uid = self.env.user.id
        emp_name = self.env['hr.employee'].sudo().search([('user_id', '=', self._uid)])
        return emp_name.name

    @api.multi
    def get_selfEmpCodeDetails(self):
        uid = self.env.user.id
        emp_name = self.env['hr.employee'].sudo().search([('user_id', '=', self._uid)])
        return emp_name.emp_code

    def give_remark(self):
        if self.admin_remark.strip() == '':
            raise ValidationError("White space(s) not allowed in first place")
        self.write({
            'state': 'Approved',
            'admin_remark': self.admin_remark.strip(),
            'action_ids': [[0, 0, {'remarks': self.admin_remark,
                                   'action_status': 'Approved'}]]

        })
        current_employee = self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1)
        emp_name = current_employee and current_employee.name or self.env.user.name
        manager_group = self.env.ref('kw_visiting_card.group_kw_visiting_card_manager')
        manager_employees = manager_group.users.mapped('employee_ids') or False
        email_ids = manager_employees and ','.join(manager_employees.mapped('work_email')) or ''
        template = self.env.ref('kw_visiting_card.kw_ra_approve_visiting_card_email_template')
        template.with_context(manager_email=email_ids, user_name=emp_name).send_mail(self.id,
                                                                                     notif_layout="kwantify_theme.csm_mail_notification_light")
        action_id = self.env.ref('kw_visiting_card.kw_apply_card_take_action_act_window').id
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web#action={action_id}&model=kw_visiting_card_apply&view_type=list',
            'target': 'self',
        }

    def printing_remark(self):
        if self.admin_remark.strip() == '':
            raise ValidationError("White space(s) not allowed in first place")
        self.write({
            'state': 'Sent For Printing',
            'admin_remark': self.admin_remark.strip(),
            'action_ids': [[0, 0, {'remarks': self.admin_remark,
                                   'action_status': 'Sent For Printing'}]]
        })

        employee = self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1)
        manager_group = self.env.ref('kw_visiting_card.group_kw_visiting_card_manager')
        manager_employees = manager_group.users.mapped('employee_ids') or False
        email_ids = manager_employees and ','.join(manager_employees.mapped('work_email')) or ''
        template = self.env.ref('kw_visiting_card.kw_send_for_print_visiting_card_email_template')
        template.with_context(manager_email=email_ids, employee=employee).send_mail(self.id, force_send=True,
                                                                                    notif_layout="kwantify_theme.csm_mail_notification_light")
        # template.send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light")
        self.env.user.notify_success(message='Business Card Send For printing .')
        action_id = self.env.ref('kw_visiting_card.kw_apply_card_take_action_act_window').id
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web#action={action_id}&model=kw_visiting_card_apply&view_type=list',
            'target': 'self',
        }

    def granted_remark(self):
        if self.admin_remark.strip() == '':
            raise ValidationError("White space(s) not allowed in first place")
        self.write({
            'state': 'Granted',
            'admin_remark': self.admin_remark.strip(),
            'action_ids': [[0, 0, {'remarks': self.admin_remark,
                                   'action_status': 'Granted'}]]

        })
        # template = self.env.ref('kw_visiting_card.kw_status_visiting_card_email_template')
        # self.env['mail.template'].browse(template.id).send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light")
        self.env.user.notify_success(message='Business Card Granted successfully.')
        action_id = self.env.ref('kw_visiting_card.kw_apply_card_take_action_act_window').id
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web#action={action_id}&model=kw_visiting_card_apply&view_type=list',
            'target': 'self',
        }

    def deliver_user_remark(self):
        if self.admin_remark.strip() == '':
            raise ValidationError("White space(s) not allowed in first place")

        self.write({'state': 'Delivered to User',
                    'active': False,
                    'admin_remark': self.admin_remark.strip(),
                    'action_ids': [[0, 0, {'remarks': self.admin_remark, 'action_status': 'Delivered to User'}]]})

        template = self.env.ref('kw_visiting_card.kw_status_visiting_card_email_template')
        user = self.env.user
        uname = user.employee_ids and user.employee_ids[-1].name or user.name
        template.with_context(user_name=uname).send_mail(self.id,
                                                         notif_layout="kwantify_theme.csm_mail_notification_light")
        self.env.user.notify_success(message='Business Card Delivered to User successfully.')
        # self.env['mail.template'].browse(template.id).send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light")
        action_id = self.env.ref('kw_visiting_card.kw_apply_card_take_action_act_window').id
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web#action={action_id}&model=kw_visiting_card_apply&view_type=list',
            'target': 'self',
        }

    def reject_remark(self):
        if self.admin_remark.strip() == '':
            raise ValidationError("White space(s) not allowed in first place")

        self.write({'state': 'Rejected', 'active': False,
                    'admin_remark': self.admin_remark.strip(),
                    'action_ids': [[0, 0, {'remarks': self.admin_remark, 'action_status': 'Rejected'}]]})

        template = self.env.ref('kw_visiting_card.kw_status_visiting_card_email_template')
        user = self.env.user
        uname = user.employee_ids and user.employee_ids[-1].name or user.name
        template.with_context(user_name=uname).send_mail(self.id,
                                                         notif_layout="kwantify_theme.csm_mail_notification_light")
        self.env.user.notify_success(message='Business Card Application Rejected.')
        action_id = self.env.ref('kw_visiting_card.kw_apply_card_status_act_window').id
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web#action={action_id}&model=kw_visiting_card_apply&view_type=list',
            'target': 'self',
        }

    @api.constrains('date_when_required')
    def validate_data(self):
        current_date = datetime.now().date()
        if self.date_when_required < current_date:
            raise ValidationError("Required date should not be less than current date.")

    @api.constrains('no_of_cards_required')
    def _check_no_of_cards(self):
        if self.no_of_cards_required < 50:
            raise ValidationError("Number of Cards Required Minimum 50.")

    @api.model
    def create(self, vals):
        user = self.env['hr.employee'].sudo().search([('user_id', '=', self._uid)], limit=1)
        # current_employee = self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1)
        current_employee = user
        if self.env.user.has_group('kw_visiting_card.group_kw_visiting_card_manager') \
                or (user and user.child_ids and 'emp_name' in vals and vals['emp_name'] \
                    and vals['emp_name'] in user.child_ids.ids) or not user.parent_id:
            # or (user and user.child_ids):
            vals['state'] = 'Approved'

        vals['create_employee_id'] = user and user.id or False
        new_record = super(ApplyCard, self).create(vals)
        if new_record.visiting_card_for == 'self':
            status = self.env['kw_visiting_card_apply'].sudo().search(
                [('emp_name', '=', current_employee.id),
                 ('state', 'in', ['Applied', 'Approved', 'Sent For Printing'])]) - new_record
        else:
            status = self.env['kw_visiting_card_apply'].sudo().search(
                [('emp_name', '=', new_record.emp_name.id),
                 ('state', 'in', ['Applied', 'Approved', 'Sent For Printing'])]) - new_record
        if status:
            raise ValidationError("You are already applied for Business card")
        self.env.user.notify_success(message='Business card apply request submitted.')

        group = self.env.ref('kw_visiting_card.group_kw_visiting_card_manager')
        user_ids = group.users.mapped('id')
        emp_ids = self.env['hr.employee'].sudo().search([('user_id', 'in', user_ids)])
        template = self.env.ref('kw_visiting_card.kw_apply_visiting_card_email_template')
        ch_obj = self.env['mail.channel']
        if emp_ids:
            for manager in emp_ids:
                # template.with_context(manager_email=manager.work_email, manager_name=manager.name).send_mail(
                #         new_record.id,notif_layout="kwantify_theme.csm_mail_notification_light")
                channel1 = manager.user_id.name + ', ' + self.env.user.name
                channel2 = self.env.user.name + ', ' + manager.user_id.name
                channel = ch_obj.sudo().search(
                    ["|", ('name', 'ilike', str(channel1)), ('name', 'ilike', str(channel2))])
                if not channel:
                    channel_id = ch_obj.channel_get([manager.user_id.partner_id.id])
                    channel = ch_obj.browse([channel_id['id']])
                channel[0].message_post(
                    body=f"New Business card Application applied by {user.name}",
                    message_type='comment',
                    subtype='mail.mt_comment',
                    author_id=self.env.user.partner_id.id,
                    notif_layout='mail.mail_notification_light')

        if new_record.visiting_card_for == 'self':
            ra = new_record.create_employee_id and new_record.create_employee_id.parent_id or False
            emp_without_ra = new_record.create_employee_id and not (new_record.create_employee_id.parent_id) or False

            if ra and emp_without_ra:
                template.with_context(manager_email=','.join(emp_ids.mapped('work_email')),
                                      manager_name='Admin').send_mail(new_record.id)
            elif ra and not emp_without_ra:
                template.with_context(manager_email=ra.work_email, manager_name=ra.name).send_mail(
                    new_record.id, notif_layout="kwantify_theme.csm_mail_notification_light")
            elif emp_without_ra and not ra:
                template.with_context(manager_email=','.join(emp_ids.mapped('work_email')),
                                      manager_name='Admin').send_mail(
                    new_record.id, notif_layout="kwantify_theme.csm_mail_notification_light")

        else:
            if emp_ids:
                email_ids = ','.join(emp_ids.mapped('work_email')) or ''
                template.with_context(manager_email=email_ids, manager_name='Admin').send_mail(
                    new_record.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                # visiting_card_records = self.env['kw_visiting_card_apply'].sudo().search([])
                # for record in visiting_card_records:
                #     record.activity_schedule('kw_visiting_card.mail_visiting_card_activity', fields.Date.today() , user_id=manager.user_id.id)
        return new_record
