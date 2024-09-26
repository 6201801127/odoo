# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    
# Create By: T Ketaki Debadrashini, On -01 Feb 2021                          #
###############################################################################
from datetime import datetime, date, timedelta
from odoo import models, fields, api


class KwHRLeaveAllocationRequest(models.Model):
    _inherit = 'hr.leave'

    related_comp_aloc_ids = fields.Many2many(
        string='Related Comp off Allocation Records',
        comodel_name='hr.leave.allocation',
        relation='hr_leave_comp_off_allocation_rel',
        column1='leave_id',
        column2='comp_off_allocation_id',
        # compute='_compute_maintain_comp_off_status',store=True
    )

    # ------------------------------------------------------------
    # Activity methods
    # overriding odoo methods
    # ------------------------------------------------------------

    def _get_responsible_for_approval(self):

        config_param = self.env['ir.config_parameter'].sudo()

        escallate_on_leave = config_param.get_param('kw_hr_leaves.on_leave')
        # print(escallate_on_leave)     

        # escallate_on_tour        = config_param.get_param('kw_hr_leaves.on_tour')
        # print(escallate_on_tour)

        approver = self.env.user
        if self.state == 'confirm' and self.manager_id.user_id:
            approver = self.manager_id.user_id
        elif self.state == 'confirm' and self.employee_id.parent_id.user_id:
            approver = self.employee_id.parent_id.user_id
        elif self.department_id.manager_id.user_id:
            approver = self.department_id.manager_id.user_id
        else:
            approver = self.env.user
        # print('---------------------------------------')

        try:
            # #call the attendance leave approval update method
            if escallate_on_leave:
                daily_attendance = self.env['kw_daily_employee_attendance'].sudo()
                on_leave = daily_attendance.search([('attendance_recorded_date', '=', datetime.now().date()),
                                                    ('employee_id', '=', approver.employee_ids[:1].id),
                                                    ('leave_day_value', '>', 0)])
                # print("escalation check ",on_leave)
                if on_leave:
                    parent_on_leave = daily_attendance.search([('attendance_recorded_date', '=', datetime.now().date()),
                                                               ('employee_id', '=', approver.employee_ids[:1].parent_id.id),
                                                               ('leave_day_value', '>', 0)])
                    # print("escalation check of approver on leave",parent_on_leave)
                    if not parent_on_leave and approver.employee_ids[:1].parent_id and approver.employee_ids[:1].parent_id.parent_id:
                        approver = approver.employee_ids[:1].parent_id.user_id

        except Exception as e:
            # print(str(e))
            pass

        return approver

    @api.model
    def check_forward_leave_on_tour(self):
        try:
            config_param = self.env['ir.config_parameter'].sudo()
            escallate_on_tour = config_param.get_param('kw_hr_leaves.on_tour')
            if escallate_on_tour:
                daily_attendance = self.env['kw_daily_employee_attendance'].sudo()
                yesterday = date.today() - timedelta(days=1)
                leave_records = self.env['hr.leave'].search(
                    [('state', 'in', ['confirm']), ('create_date', '>=', yesterday),
                     ('create_date', '<', date.today())])
                # print("Leave records ",leave_records)
                # leave_records       = leave_records.filtered(lambda leave:leave.create_date.date() == last_date)
                second_approvers = leave_records.mapped('second_approver_id')
                # print("Second approvers ",second_approvers)
                on_tour = daily_attendance.search([('attendance_recorded_date', '=', datetime.now().date()),
                                                   ('employee_id', 'in', second_approvers.ids if second_approvers else []),
                                                   ('is_on_tour', '=', True)])
                # print("On tour ",on_tour)
                if on_tour:
                    for tour in on_tour:

                        parent_on_tour = daily_attendance.search(
                            [('attendance_recorded_date', '=', datetime.now().date()),
                             ('employee_id', '=', tour.employee_id.parent_id.id if tour.employee_id.parent_id else False),
                             ('is_on_tour', '=', True)])
                        # print("Parent on tour ",parent_on_tour)
                        approver = tour.employee_id.parent_id if not parent_on_tour and tour.employee_id.parent_id and tour.employee_id.parent_id.parent_id else tour.employee_id
                        # print("New approver ",approver)
                        existing_approver = leave_records.filtered(lambda res: res.second_approver_id == tour.employee_id)
                        # print("Exisiting Approver ",existing_approver)
                        if existing_approver:
                            for leaves in existing_approver:
                                lm = leaves.second_approver_id

                                if approver and lm != approver:
                                    # print("Not same", leaves.second_approver_id , approver)
                                    leaves.sudo().write({
                                        'second_approver_id': approver.id,
                                        'state': 'forward',
                                        'authority_remark': 'Auto Escalation Forwarded By System.',
                                        'action_taken_on': datetime.now(),
                                    })
                                    self.env['kw_leave_approval_log'].sudo().create_approval_log(False, leaves, False,
                                                                                                 approver,
                                                                                                 "Auto Escalation Forwarded By System.",
                                                                                                 self.env.user.employee_ids.id,
                                                                                                 '4')
                                    template = self.env.ref('kw_hr_leaves.kw_hr_leave_escallation_forward_mail')
                                    template.with_context(lm_email=lm.work_email, lm=lm.name).send_mail(leaves.id,
                                                                                                        notif_layout="kwantify_theme.csm_mail_notification_light")
            else:
                pass
        except Exception as e:
            # print("Leave tour cron error : ", str(e))
            pass

    @api.multi
    def write(self, values):
        """
            Update all record(s) in recordset, with new value comes as {values}
            return True on success, False otherwise
    
            @param values: dict of new values to be set
    
            @return: True on success, False otherwise
        """

        result = super(KwHRLeaveAllocationRequest, self).write(values)
        # # if state or holiday type or no of holidays modified then recalculate comp off details
        if 'state' in values or 'holiday_status_id' in values or 'number_of_days' in values:
            self._compute_maintain_comp_off_status()

        return result

    # # For comp-off leave type ,after approval , update the leave taken and keep track of related leave and entitlement records
    # @api.depends('state','holiday_status_id','number_of_days')
    def _compute_maintain_comp_off_status(self):
        for leave_rec in self:
            # print('--------------------------------')

            if leave_rec.holiday_status_id.is_comp_off:

                no_of_days = leave_rec.number_of_days
                # print("Days ", no_of_days)

                if leave_rec.state == 'validate':

                    # get allocation records in asc order      
                    hr_allocations = self.env['hr.leave.allocation'].sudo().search(
                        [('state', '=', 'validate'), ('holiday_status_id.is_comp_off', '=', True),
                         ('cmp_leave_taken', '<', 1), ('validity_end_date', '>=', datetime.now().date())],
                        order="validity_end_date asc")
                    comp_off_allocations = []
                    # print(hr_allocations)
                    for alc_rec in hr_allocations:
                        if no_of_days > 0:
                            if no_of_days >= 1:
                                leave_taken = 0.5 if alc_rec.cmp_leave_taken == 0.5 else 1
                            else:
                                leave_taken = 0.5

                            # print('cmp_leave_taken ---- ')
                            cmp_leave_taken = alc_rec.cmp_leave_taken if alc_rec.cmp_leave_taken else 0

                            # print(1 if no_of_days >= 1 else cmp_leave_taken + 0.5)
                            comp_off_allocations.append(alc_rec.id)
                            alc_rec.write({'cmp_leave_taken': (1.0 if no_of_days >= 1 else cmp_leave_taken + 0.5)})
                            # print(alc_rec.cmp_leave_taken)
                            no_of_days = no_of_days - leave_taken

                            if no_of_days <= 0:
                                break

                    if comp_off_allocations:
                        # print(comp_off_allocations)
                        leave_rec.related_comp_aloc_ids = comp_off_allocations
                        # print("Related Record ", leave_rec.related_comp_aloc_ids)
