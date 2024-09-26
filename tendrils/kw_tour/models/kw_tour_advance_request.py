from odoo import models,fields,api
from odoo.exceptions import ValidationError


class TourAdvanceRequest(models.Model):
    _name = 'kw_tour_advance_request'
    _description = 'Tour Advance Request'
    _rec_name = "tour_id"

    def default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    employee_id = fields.Many2one("hr.employee", "Employee", default=default_employee)
    tour_id = fields.Many2one("kw_tour", "Employee Name", required=True,
                              default=lambda self: self.env.context.get('default_tour_id'))
    code = fields.Char(related='tour_id.code', string="Reference No.", )
    purpose = fields.Text(related='tour_id.purpose', string="Purpose", )
    date_travel = fields.Date(related='tour_id.date_travel', string="Date Of Travel", )
    date_return = fields.Date(related='tour_id.date_return', string="Return Date", )
    tour_type_id = fields.Many2one('kw_tour_type', related='tour_id.tour_type_id', string="Type Of Tour")
    city_id = fields.Many2one('kw_tour_city', related='tour_id.city_id', string="Originating Place")
    tour_detail_ids = fields.One2many('kw_tour_details', related='tour_id.tour_detail_ids', required=True)
    travel_expense_details_ids = fields.One2many('kw_tour_travel_expense_details',
                                                 related='tour_id.travel_expense_details_ids',
                                                 string="Travel Expenses", )
    ancillary_expense_ids = fields.One2many('kw_tour_ancillary_expense_details',
                                            related='tour_id.ancillary_expense_ids', string="Ancillary Expenses")

    advance = fields.Float(related='tour_id.advance', string="Advance(In Domestic)")
    advance_usd = fields.Float(related='tour_id.advance_usd', string="Advance(In International)")

    disbursed_inr = fields.Float(related='tour_id.disbursed_inr', string="Amount Disbursed(Domestic)")
    disbursed_usd = fields.Float(related='tour_id.disbursed_usd', string="Amount Disbursed(USD)")

    to_disbursed_inr = fields.Float(related='tour_id.to_disbursed_inr', string="To be Disbursed(Domestic)")
    to_disbursed_usd = fields.Float(related='tour_id.to_disbursed_usd', string="To be Disbursed(USD)")

    exchange_rate = fields.Float(related='tour_id.exchange_rate', string="Exchange Rate")
    new_exchange_rate = fields.Float(string="New Exchange Rate")

    request_inr = fields.Float("New Advance Request(Domestic)")
    request_usd = fields.Float("New Advance Request(USD)")

    to_be_given_inr = fields.Float("Amount To Be Disbursed(Domestic)")
    to_be_given_usd = fields.Float("Amount To Be Disbursed(USD)")

    state = fields.Selection(string="Status",
                             selection=[('Applied', 'Applied'), ('Approved', 'Approved'), ('Grant', 'Grant'),
                                        ('Rejected', 'Rejected')])
    ra_access = fields.Boolean("RA Access", compute="compute_ra_access")
    pending_at = fields.Char("Pending At", compute="compute_pending_at")
    remark = fields.Text("Remarks")

    can_apply_inr = fields.Boolean(related='tour_id.can_apply_inr', string='Can Apply For Advance Domestic ?')
    can_apply_usd = fields.Boolean(related='tour_id.can_apply_usd', string='Can Apply For Advance USD ?', )

    advance_ids = fields.One2many('kw_tour_advance_given_log', related='tour_id.advance_ids',
                                  string="Advance Disbursed Log")

    action_log_ids = fields.One2many('kw_advance_request_action_log', 'tour_id', string="Action Logs")
    dept_id = fields.Many2one('hr.department', string="Department Name", related="employee_id.department_id")
    job_id = fields.Many2one('hr.job', string="Designation", related="employee_id.job_id")
    project_id = fields.Many2one(related='tour_id.project_id', string='Project')
    approver_id = fields.Many2one('hr.employee', 'First Approver')
    travel_arrangement = fields.Selection(related='tour_id.travel_arrangement', string="Travel Arrangement", store=True)

    def _get_tour_approver(self):
        approver = self.employee_id and self.employee_id.parent_id or False
        if self.tour_id.tour_type_id.code == 'project':
            if self.tour_id.actual_project_id:
                if self.tour_id.actual_project_id.emp_id.id == self.employee_id.id \
                        and self.tour_id.actual_project_id.reviewer_id.id != self.employee_id.id:
                    approver = self.tour_id.actual_project_id.reviewer_id or False
                elif self.tour_id.actual_project_id.emp_id.id != self.employee_id.id \
                        and self.tour_id.actual_project_id.reviewer_id.id != self.employee_id.id:
                    approver = self.tour_id.actual_project_id.emp_id or False
        return approver

    def return_to_adv_req_take_action(self):
        tree_view_id = self.env.ref('kw_tour.view_kw_tour_advance_request_take_action_tree').id
        form_view_id = self.env.ref('kw_tour.view_kw_tour_advance_request_take_action_form').id

        return {
            'name': 'Take Action',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'view_id': False,
            'res_model': 'kw_tour_advance_request',
            'type': 'ir.actions.act_window',
            'target': 'main',
            'context': {'access_check': 1},
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
        }

    @api.multi
    def action_approve_advance_request(self):
        remark = self.remark.strip()
        if not remark:
            raise ValidationError("White space(s) not allowed in first place.")
        self.write({'state':'Approved','remark':False})

        user = self.env.user
        uname = user.employee_ids and user.employee_ids[-1].name or user.name

        notify_template = self.env.ref('kw_tour.kw_tour_advance_request_approve_reject_email_template')
        finance_users = self.env.ref('kw_tour.group_kw_tour_finance').users
        finance_users_emails = ','.join(finance_users.mapped("employee_ids.work_email"))

        approver = self._get_tour_approver()
        # cc_employee = self.employee_id | self.employee_id.parent_id
        cc_employee = self.employee_id | approver
        cc_emails = cc_employee and ','.join(cc_employee.mapped('work_email')) or ''
        notify_template.with_context(
            user_name=uname,
            email_users=finance_users_emails,
            email_cc_users=cc_emails).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")

        self.env.user.notify_success("Tour Advance Request approved successfully.")
        # action_id = self.env.ref('kw_tour.action_kw_tour_advance_request_act_window').id

        # return {
        #     'type': 'ir.actions.act_url',
        #     'url': f'/web#action={action_id}&model=kw_tour_advance_request&view_type=list',
        #     'target': 'self',
        # }
        return self.return_to_adv_req_take_action()

    @api.multi
    def action_grant_advance_request(self):
        remark = self.remark.strip()
        if not remark:
            raise ValidationError("White space(s) not allowed in first place.")

        self.write({'state': 'Grant', 'remark': False})
       
        user = self.env.user
        uname = user.employee_ids and user.employee_ids[-1].name or user.name

        notify_template = self.env.ref('kw_tour.kw_tour_advance_request_approve_reject_email_template')

        log = self.env['kw_tour_advance_given_log']
        data = {'tour_id':self.tour_id.id}
        adv_data = {}

        if self.can_apply_inr:
            data['requested_inr'] = self.request_inr
            data['disbursed_amount_inr'] = self.to_be_given_inr
            data['old_amount_inr'] = self.disbursed_inr
            data['new_amount_inr'] = adv_data['disbursed_inr'] = self.disbursed_inr + self.to_be_given_inr

        if self.can_apply_usd:
            data['requested_usd'] = self.request_usd
            data['old_amount_usd'] = self.disbursed_usd
            data['disbursed_amount_usd'] = self.to_be_given_usd
            data['new_amount_usd'] = adv_data['disbursed_usd'] = self.disbursed_usd + self.to_be_given_usd

            data['exchange_rate'] = self.new_exchange_rate

        log.create(data)

        self.tour_id.write(adv_data)
        approver = self._get_tour_approver()
        # ra_email = self.employee_id.parent_id and self.employee_id.parent_id.work_email or ''
        ra_email = ''
        if approver:
            ra_email = approver.work_email
        notify_template.with_context(
            user_name=uname,
            email_users=self.employee_id.work_email,
            email_cc_users=ra_email).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")

        self.env.user.notify_success("Tour advance request granted successfully.")
        # action_id = self.env.ref('kw_tour.action_kw_tour_advance_request_act_window').id

        # return {
        #     'type': 'ir.actions.act_url',
        #     'url': f'/web#action={action_id}&model=kw_tour_advance_request&view_type=list',
        #     'target': 'self',
        # }
        return self.return_to_adv_req_take_action()

    @api.multi
    def action_reject_advance_request(self):
        prev_state = self.state
        remark = self.remark.strip()
        if not remark:
            raise ValidationError("White space(s) not allowed in first place.")

        self.write({'state': 'Rejected', 'remark': False})

        user = self.env.user
        uname = user.employee_ids and user.employee_ids[-1].name or user.name

        notify_template = self.env.ref('kw_tour.kw_tour_advance_request_approve_reject_email_template')

        cc_emails = ''
        if prev_state == 'Approved':
            # if self.employee_id.parent_id and self.employee_id.parent_id.work_email:
            #     cc_emails += self.employee_id.parent_id.work_email
            approver = self._get_tour_approver()
            if approver and approver.work_email:
                cc_emails += approver.work_email
        # cc_emails = cc_employee and ','.join(cc_employee.mapped('work_email')) or ''

        notify_template.with_context(
            user_name=uname,
            email_users=self.employee_id.work_email,
            email_cc_users=cc_emails).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")

        self.env.user.notify_success("Tour advance request rejected successfully.")
        # action_id = self.env.ref('kw_tour.action_kw_tour_advance_request_act_window').id
        # return {
        #     'type': 'ir.actions.act_url',
        #     'url': f'/web#action={action_id}&model=kw_tour_advance_request&view_type=list',
        #     'target': 'self',
        # }
        return self.return_to_adv_req_take_action()

    @api.multi
    def take_action(self):
        form_view_id = self.env.ref('kw_tour.view_kw_tour_advance_request_take_action_form').id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'kw_tour_advance_request',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view_id,
            'res_id': self.ids[0],
            'target': 'self',
        }

    @api.multi
    def compute_ra_access(self):
        for advance in self:
            approver = advance._get_tour_approver()
            # if advance.employee_id and advance.employee_id.parent_id and advance.employee_id.parent_id.user_id == self.env.user:
            if advance.employee_id and approver and approver.user_id == self.env.user:
                advance.ra_access = True
            if self._context.get('eos_ra_takeaction'):
                advance.ra_access = True

    @api.multi
    def compute_pending_at(self):
        for record in self:
            if record.state == 'Applied':
                approver = record._get_tour_approver()
                # record.pending_at = record.employee_id and record.employee_id.parent_id and record.employee_id.parent_id.name or False
                record.pending_at = record.employee_id and approver and approver.name or False
            if record.state == 'Approved':
                record.pending_at = ','.join(self.env.ref('kw_tour.group_kw_tour_finance').users.mapped('name'))

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None, is_integrated=False):
        if not is_integrated:
            current_employee = self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1)
            query = f'''select ka.id from kw_tour_advance_request ka
                        join kw_tour kt on kt.id = ka.tour_id
                        join project_project pj on pj.id = kt.actual_project_id
                        where pj.emp_id = kt.employee_id 
                        and pj.reviewer_id = {current_employee.id}::integer '''
            self._cr.execute(query)
            query_result = self._cr.fetchall()
            tour_reviewer_ids = [id_tuple[0] for id_tuple in query_result]

            query = f'''select ka.id from kw_tour_advance_request ka
                        join kw_tour kt on kt.id = ka.tour_id
                        join project_project pj on pj.id = kt.actual_project_id
                        where pj.reviewer_id = kt.employee_id '''
            self._cr.execute(query)
            query_result = self._cr.fetchall()
            tour_ra_ids = [id_tuple[0] for id_tuple in query_result]

            query = f'''select ka.id from kw_tour_advance_request ka
                        join kw_tour kt on kt.id = ka.tour_id
                        join project_project pj on pj.id = kt.actual_project_id
                        where pj.reviewer_id != kt.employee_id and pj.emp_id != kt.employee_id 
                        and pj.emp_id = {current_employee.id}::integer '''
            self._cr.execute(query)
            query_result = self._cr.fetchall()
            tour_pm_ids = [id_tuple[0] for id_tuple in query_result]

            if self._context.get('access_check'):
                employee_id = self.env.user.employee_ids

                if self.env.user.has_group('kw_tour.group_kw_tour_finance'):
                    args += ['|', '|', '|', ('state', 'in', ['Approved']),

                             '&', '&', ('state', 'in', ['Applied']), ('employee_id.parent_id', 'in', employee_id.ids),
                                     '|',
                                     ('tour_id.tour_type_id.code', '!=', 'project'),
                                     '&',
                                     ('tour_id.tour_type_id.code', '=', 'project'),
                                     '|',
                                     ('id', 'in', tour_ra_ids),
                                     ('tour_id.project_type', '=', '3'),

                             '&', '&', '&', ('state', 'in', ['Applied']),
                             ('tour_id.tour_type_id.code', '=', 'project'),
                             ('create_uid', '!=', self.env.user.id),
                             ('id', 'in', tour_pm_ids),

                             '&', '&', ('state', 'in', ['Applied']),
                             ('tour_id.tour_type_id.code', '=', 'project'),
                             ('id', 'in', tour_reviewer_ids)
                             ]
                else:
                    args += ['|', '|',
                             '&', '&', ('state', 'in', ['Applied']), ('employee_id.parent_id', 'in', employee_id.ids),
                                     '|',
                                     ('tour_id.tour_type_id.code', '!=', 'project'),
                                     '&',
                                     ('tour_id.tour_type_id.code', '=', 'project'),
                                     '|',
                                     ('id', 'in', tour_ra_ids),
                                     ('tour_id.project_type', '=', '3'),

                             '&', '&', '&', ('state', 'in', ['Applied']),
                             ('tour_id.tour_type_id.code', '=', 'project'),
                             ('create_uid', '!=', self.env.user.id),
                             ('id', 'in', tour_pm_ids),

                             '&', '&', ('state', 'in', ['Applied']),
                             ('tour_id.tour_type_id.code', '=', 'project'),
                             ('id', 'in', tour_reviewer_ids)]

            if self._context.get('filter_advance_request'):
                if self.env.user.has_group('kw_tour.group_kw_tour_finance'):
                    args += []
                else:
                    args += ['&', ('state', '!=', 'Draft'),
                             '|', '|', '|', ('create_uid', '=', self.env.user.id),

                             '&', ('employee_id.parent_id.user_id', '=', self.env.user.id),
                                     '|',
                                     ('tour_id.tour_type_id.code', '!=', 'project'),
                                     '&',
                                     ('tour_id.tour_type_id.code', '=', 'project'),
                                     '|',
                                     ('id', 'in', tour_ra_ids),
                                     ('tour_id.project_type', '=', '3'),

                             '&', ('tour_id.tour_type_id.code', '=', 'project'),
                                  ('id', 'in', tour_pm_ids),

                             '&', ('tour_id.tour_type_id.code', '=', 'project'),
                                  ('id', 'in', tour_reviewer_ids)
                             ]

        return super(TourAdvanceRequest, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)

    @api.model
    def create(self, values):
        advance_request = super(TourAdvanceRequest, self).create(values)
        if advance_request.tour_id.employee_id.parent_id:
            ra = advance_request.tour_id.employee_id.parent_id or False
            if advance_request.tour_id.tour_type_id.code == 'project':
                if advance_request.tour_id.actual_project_id:
                    if advance_request.tour_id.actual_project_id.emp_id.id == advance_request.employee_id.id \
                            and advance_request.tour_id.actual_project_id.reviewer_id.id != advance_request.employee_id.id:
                        ra = advance_request.tour_id.actual_project_id.reviewer_id or False
                    elif advance_request.tour_id.actual_project_id.emp_id.id != advance_request.employee_id.id \
                            and advance_request.tour_id.actual_project_id.reviewer_id.id != advance_request.employee_id.id:
                        ra = advance_request.tour_id.actual_project_id.emp_id or False
            template = self.env.ref('kw_tour.kw_tour_apply_advance_request_email_template')
            template.with_context(ra_name=ra.name,emails=ra.work_email,).send_mail(advance_request.id,notif_layout="kwantify_theme.csm_mail_notification_light")
        else:
            advance_request.write({'state': 'Approved', 'remark': False})
            template = self.env.ref('kw_tour.kw_tour_apply_advance_request_without_ra_email_template')
            finance_users = self.env.ref('kw_tour.group_kw_tour_finance').users
            finance_users_emails = ','.join(finance_users.mapped("employee_ids.work_email"))
            template.with_context(
                email_users=finance_users_emails).send_mail(advance_request.id, notif_layout="kwantify_theme.csm_mail_notification_light")

        self.env.user.notify_success("Tour Advance Request applied successfully.")
        return advance_request
