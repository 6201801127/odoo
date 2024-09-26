from odoo import models,fields,api
from odoo.exceptions import ValidationError


class TourCancellation(models.Model):
    _name = 'kw_tour_cancellation'
    _description = 'Tour Cancellation'
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
    reason = fields.Text("Cancellation Reason", required=True)
    state = fields.Selection(string="Status",
                             selection=[('Applied', 'Cancellation Applied'), ('Approved', 'Cancellation Approved'), ('Rejected', 'Cancellation Rejected')])
    ra_access = fields.Boolean("RA Access", compute="compute_ra_access")
    pending_at = fields.Char("Pending At", compute="compute_pending_at")
    remark = fields.Text("Remark")
    dept_id = fields.Many2one('hr.department', string="Department Name", related="employee_id.department_id")
    job_id = fields.Many2one('hr.job', string="Designation", related="employee_id.job_id")
    travel_arrangement = fields.Selection(related='tour_id.travel_arrangement', string="Travel Arrangement", store=True)

    # def cancel_approval_flow(self):
    #     # print('-----------check---------------')
    #     if self.tour_id.tour_type_id.name == 'Project' and self.tour_id.project_type == '70':
    #         pass
    #     else:
    #         # print(self.tour_id.total_budget_expense, '=======================else runned=======', self.tour_id.department_id.id)
    #         t_value = self.env['kw_tour_treasury_budget'].sudo().search([('department_id', '=', self.tour_id.department_id.id)])
    #         t_value.write({
    #             'spent_amount': t_value.spent_amount - self.tour_id.total_budget_expense,
    #         })


    def _get_tour_approver(self):
        approver = self.employee_id and self.employee_id.parent_id or False
        if self.tour_type_id.code == 'project':
            if self.tour_id.actual_project_id:
                if self.tour_id.actual_project_id.emp_id.id == self.tour_id.employee_id.id \
                        and self.tour_id.actual_project_id.reviewer_id.id != self.tour_id.employee_id.id:
                    approver = self.tour_id.actual_project_id.reviewer_id or False
                elif self.tour_id.actual_project_id.emp_id.id != self.tour_id.employee_id.id \
                        and self.tour_id.actual_project_id.reviewer_id.id != self.tour_id.employee_id.id:
                    approver = self.tour_id.actual_project_id.emp_id or False
        return approver

    def return_to_cancellation_take_action(self):
        tree_view_id = self.env.ref('kw_tour.view_kw_tour_cancellation_tree').id
        form_view_id = self.env.ref('kw_tour.view_kw_tour_cancellation_form').id
        current_employee = self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1)
        query = f'''select ktc.id from kw_tour_cancellation ktc
                    join kw_tour kt on kt.id = ktc.tour_id
                    join project_project pj on pj.id = kt.actual_project_id
                    where pj.emp_id = kt.employee_id 
                    and pj.reviewer_id = {current_employee.id}::integer '''
        self._cr.execute(query)
        query_result = self._cr.fetchall()
        tour_reviewer_ids = [id_tuple[0] for id_tuple in query_result]
        return {
            'name': 'Take Action',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'view_id': False,
            'res_model': 'kw_tour_cancellation',
            'type': 'ir.actions.act_window',
            'target': 'main',
            'domain': [('state', '=', 'Applied'),
                       '|', '|',
                       '&', ('employee_id.parent_id.user_id', '=', self.env.user.id),
                       ('tour_id.tour_type_id.code', '!=', 'project'),

                       '&', '&',
                       ('tour_id.tour_type_id.code', '=', 'project'),
                       ('create_uid', '!=', self.env.user.id),
                       ('tour_id.actual_project_id.emp_id.user_id', '=', self.env.user.id),

                       '&',
                       ('tour_id.tour_type_id.code', '=', 'project'),
                       ('id', 'in', tour_reviewer_ids)
                       ],
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
        }

    @api.multi
    def action_approve_cancellation(self):
        remark = self.remark.strip()
        if not remark:
            raise ValidationError("White space(s) not allowed in first place.")

        self.write({'state': 'Approved'})
        tour_state = self.tour_id.state
        self.tour_id.write({'state': 'Cancelled'})
        # if tour_state in ['Finance Approved','Posted']:
        # Start : update attendance related records to False
        tour_dates = self.env['kw_tour'].generate_days_with_from_and_to_date(self.tour_id.date_travel,self.tour_id.date_return)
        attendance_records = self.env['kw_daily_employee_attendance'].sudo().search([('employee_id','=',self.tour_id.employee_id.id),
                                                                                    ('attendance_recorded_date', 'in', tour_dates)])
        for record in attendance_records:
            if record.is_on_tour != False:
                try:
                    record.write({
                        'is_on_tour':False,
                    })
                except Exception as e:
                    # print(e)
                    continue
        # End : update attendance related recors to False


        template = self.env.ref('kw_tour.kw_tour_cancellation_approved_email_template')
        template.send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light")

        self.env.user.notify_success("Tour cancellation approved successfully.")
        # action_id = self.env.ref('kw_tour.action_kw_tour_cancellation_act_window').id

        # return {
        #     'type': 'ir.actions.act_url',
        #     'url': f'/web#action={action_id}&model=kw_tour_cancellation&view_type=list',
        #     'target': 'self',
        # }
        return self.return_to_cancellation_take_action()
    
    @api.multi
    def action_reject_cancellation(self):
        remark = self.remark.strip()
        if not remark:
            raise ValidationError("White space(s) not allowed in first place.")

        self.write({'state':'Rejected'})
        approver = self._get_tour_approver()
        # template = self.env.ref('kw_tour.kw_tour_cancellation_approved_email_template')
        template = self.env.ref('kw_tour.kw_tour_cancellation_reject_email_template')
        template.with_context(email=approver.work_email, name=approver.name).send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light")

        self.env.user.notify_success("Tour cancellation rejected successfully.")
        # action_id = self.env.ref('kw_tour.action_kw_tour_cancellation_act_window').id

        # return {
        #     'type': 'ir.actions.act_url',
        #     'url': f'/web#action={action_id}&model=kw_tour_cancellation&view_type=list',
        #     'target': 'self',
        # }
        return self.return_to_cancellation_take_action()
        
    @api.multi
    def compute_pending_at(self):
        for record in self:
            if record.state == 'Applied':
                approver = record._get_tour_approver()
                record.pending_at = record.employee_id and approver and approver.name or ''

    @api.multi
    def compute_ra_access(self):
        for cancellation in self:
            approver = cancellation._get_tour_approver()
            if cancellation.employee_id and approver and approver.user_id == self.env.user:
                cancellation.ra_access = True
            if self._context.get('hr_tour_canceelaion'):
                cancellation.ra_access = True

    @api.multi
    def take_action(self):
        form_view_id = self.env.ref('kw_tour.view_kw_tour_cancellation_form').id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'kw_tour_cancellation',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view_id,
            'res_id': self.ids[0],
            'target': 'self',
        }
    
    @api.model
    def create(self, values):
        result = super(TourCancellation, self).create(values)
        
        if 'active_model' in self._context and 'active_id' in self._context and self._context['active_model'] == 'kw_tour':
            tour = self.env['kw_tour'].browse(self._context['active_id'])
            # if not tour.cancellation_id:
            tour.cancellation_id = result.id

        if result.employee_id.parent_id:
            approver = result._get_tour_approver()
            template = self.env.ref('kw_tour.kw_tour_cancellation_applied_email_template')
            template.with_context(email=approver.work_email, name=approver.name).send_mail(result.id, notif_layout="kwantify_theme.csm_mail_notification_light")

            self.env.user.notify_success("Tour cancellation applied successfully.")
        else:
            result.write({'state': 'Approved'})
            result.tour_id.write({'state': 'Cancelled'})

            ''' Start : update attendance related records '''
            tour_dates = self.env['kw_tour'].generate_days_with_from_and_to_date(result.tour_id.date_travel, result.tour_id.date_return)
            attendance_records = self.env['kw_daily_employee_attendance'].sudo().search([('employee_id', '=', result.tour_id.employee_id.id),
                                                                                        ('attendance_recorded_date', 'in', tour_dates)])
            for record in attendance_records:
                if record.is_on_tour != False:
                    try:
                        record.write({'is_on_tour': False})
                    except Exception as e:
                        # print(e)
                        continue

            self.env.user.notify_success("Tour cancelled successfully.")
        return result  

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('access_check'):
            if not self.env.user.has_group('kw_tour.group_kw_tour_admin'):
                args += [('create_uid', '=', self._uid)]

        current_employee = self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1)
        query = f'''select ktc.id from kw_tour_cancellation ktc
                    join kw_tour kt on kt.id = ktc.tour_id
                    join project_project pj on pj.id = kt.actual_project_id
                    where pj.emp_id = kt.employee_id 
                    and pj.reviewer_id = {current_employee.id}::integer '''
        self._cr.execute(query)
        query_result = self._cr.fetchall()
        tour_reviewer_ids = [id_tuple[0] for id_tuple in query_result]

        query = f'''select ktc.id from kw_tour_cancellation ktc
                    join kw_tour kt on kt.id = ktc.tour_id
                    join project_project pj on pj.id = kt.actual_project_id
                    where pj.reviewer_id = kt.employee_id '''
        self._cr.execute(query)
        query_result = self._cr.fetchall()
        tour_ra_ids = [id_tuple[0] for id_tuple in query_result]

        query = f'''select ktc.id from kw_tour_cancellation ktc
                    join kw_tour kt on kt.id = ktc.tour_id
                    join project_project pj on pj.id = kt.actual_project_id
                    where pj.reviewer_id != kt.employee_id and pj.emp_id != kt.employee_id 
                    and pj.emp_id = {current_employee.id}::integer '''
        self._cr.execute(query)
        query_result = self._cr.fetchall()
        tour_pm_ids = [id_tuple[0] for id_tuple in query_result]
        if self._context.get('filter_tour_cancellation'):
            if self.env.user.has_group('kw_tour.group_kw_tour_travel_desk') \
                    or self.env.user.has_group('kw_tour.group_kw_tour_finance'):
                args += [('state', '!=', 'Applied')]
            else:
                args += ['|', '|', '|', ('create_uid', '=', self.env.user.id),
                         '&', ('employee_id.parent_id.user_id', '=', self.env.user.id),
                             '|',
                             ('tour_id.tour_type_id.code', '!=', 'project'),
                             '&',
                             ('tour_id.tour_type_id.code', '=', 'project'),
                             '|',
                             ('id', 'in', tour_ra_ids),
                             ('tour_id.project_type', '=', '3'),

                         '&', '&',
                         ('tour_id.tour_type_id.code', '=', 'project'),
                         ('create_uid', '!=', self.env.user.id),
                         ('id', 'in', tour_pm_ids),

                         '&',
                         ('tour_id.tour_type_id.code', '=', 'project'),
                         ('id', 'in', tour_reviewer_ids)]
        if self._context.get('take_action_tour_cancellation'):
            args += ['&',('state', '=', 'Applied'),
                     '|', '|',
                     '&', ('employee_id.parent_id.user_id', '=', self.env.user.id),
                             '|',
                             ('tour_id.tour_type_id.code', '!=', 'project'),
                             '&',
                             ('tour_id.tour_type_id.code', '=', 'project'),
                             '|',
                             ('id', 'in', tour_ra_ids),
                             ('tour_id.project_type', '=', '3'),

                     '&', '&',
                     ('tour_id.tour_type_id.code', '=', 'project'),
                     ('create_uid', '!=', self.env.user.id),
                     ('id', 'in', tour_pm_ids),

                     '&',
                     ('tour_id.tour_type_id.code', '=', 'project'),
                     ('id', 'in', tour_reviewer_ids)]

        return super(TourCancellation, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
