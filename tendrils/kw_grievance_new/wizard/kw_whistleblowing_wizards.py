from odoo import models, fields, api
from multiprocessing import managers
from ast import literal_eval
from datetime import datetime, date

# Assign spoc persion wizards.......

class IncidentWizard(models.TransientModel):
    _name = 'whistle.incident.wizard'
    _description = 'Incident Wizard'

    team_id = fields.Many2one('grievance.ticket.team',default=lambda self: self._context.get("category_id"))
    user_id = fields.Many2one('res.users', string='Team Members')
    user_ids = fields.Many2many(
        comodel_name='res.users',
        related='team_id.user_ids',
        string='Users')

    def update_incident(self):
        context = dict(self._context)
        intObj = self.env["kw_whistle_blowing"]
        int_details = intObj.browse(context.get("active_id"))
        int_details.team_id = self.team_id
        int_details.user_id = self.user_id
        grievance_desk_users = self.env.user.email
        to_name = self.user_id.name
        to_eamil = self.user_id.email
        if int_details.request == 'self':
            template = self.env.ref('kw_grievance_new.email_template_assigned_whistle_ticket')
            template.with_context(to_name=to_name, email_to=to_eamil, email_from=grievance_desk_users).send_mail(
                int_details.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        else:
            pass
    @api.multi
    @api.onchange('team_id')
    def _onchange_team_id(self):
        context = dict(self._context)
        intObj = self.env["kw_whistle_blowing"]
        int_details = intObj.browse(context.get("active_id"))
        if self.team_id:
            user_var = {'domain': {'user_id': [('id', 'in', self.team_id.user_ids.ids)]}}

            return user_var

    @api.onchange('team_id')
    def get_team_id(self):
        # print('------------------------------------->>>>>>>>>')
        return {'domain': {'team_id': [('code', '=', 'WB')]}}

#  awaiting remarks

class AwaitingRemarksWizard(models.TransientModel):
    _name = 'whistle.awaiting.remarks.wizard'
    _description = 'Awaiting Remarks Wizard'

    remarks_for_awaiting = fields.Text(string="Awaiting Remarks")
    stage_id = fields.Many2one('grievance.ticket.stage')

    def action_awaiting_remarks(self):
        context = dict(self._context)
        intObj = self.env["kw_whistle_blowing"]
        int_details = intObj.browse(context.get("active_id"))
        int_details.remarks_for_awaiting = self.remarks_for_awaiting
        stage = self.env['grievance.ticket.stage'].sudo().search([('code', '=', 'H')], limit=1)
        int_details.stage_id = stage.id
        if int_details.request == 'self':
            grievance_desk_users = self.env.user
            user1 = int_details.users_id.name
            user=self.env['hr.employee'].sudo().search([('user_id', '=', user1)], limit=1)
            users = self.env['res.users'].sudo().search([])
            admin = users.filtered(lambda user1: user1.has_group('kw_grievance_new.group_grievance_manager')==True)
            template = self.env.ref('kw_grievance_new.email_template_for_awaiting_whistle_remarks')
            from_emails = ','.join(grievance_desk_users.mapped('email'))
            to_email = ','.join(user.mapped('work_email'))
            param = self.env['ir.config_parameter'].sudo()
            mail_group = literal_eval(param.get_param('kw_grievance_new.mail_to_users'))
            mail_to = []
            if mail_group:
                emp = self.env['hr.employee'].sudo().search([('id', 'in', mail_group)])
                mail_to += emp.filtered(lambda r: r.work_email != False).mapped('work_email')
            email_cc = ",".join(mail_to) or ''
            cc_emails = ','.join(admin.mapped('email'))
            managers = ','.join(admin.mapped('name'))

            template.with_context(email_to=to_email, email_cc= email_cc,from_email=from_emails, names=int_details.users_id.name,
                                remarks=self.remarks_for_awaiting, name_manager=managers).send_mail(int_details.id,
                                                                            notif_layout="kwantify_theme.csm_mail_notification_light")

# inprogress wizard


class RemarksWizard(models.TransientModel):
    _name = 'whistle.remarks.wizard'
    _description = 'Remarks Wizard'

    remarks_for_inprogress = fields.Text(string="Inprogress Remarks")
    stage_id = fields.Many2one('grievance.ticket.stage')

    def action_remarks(self):
        context = dict(self._context)
        intObj = self.env["kw_whistle_blowing"]
        int_details = intObj.browse(context.get("active_id"))
        int_details.remarks_for_inprogress = self.remarks_for_inprogress
        stage = self.env['grievance.ticket.stage'].sudo().search([('code', '=', 'IP')], limit=1)
        int_details.stage_id = stage.id
        if int_details.request == 'self':
            if stage:
                grievance_desk_users = self.env.user
                employee_email = int_details.users_id.name
                user=self.env['hr.employee'].sudo().search([('user_id', '=', employee_email)], limit=1)
                users = self.env['res.users'].sudo().search([])
                admin = users.filtered(lambda user: user.has_group('kw_grievance_new.group_grievance_manager') == True)
                template = self.env.ref('kw_grievance_new.email_template_for_inprogress_whistle_remarks')
                from_emails = ','.join(grievance_desk_users.mapped('email'))
                to_email = ','.join(user.mapped('work_email'))
                param = self.env['ir.config_parameter'].sudo()
                mail_group = literal_eval(param.get_param('kw_grievance_new.mail_to_users'))
                mail_to = []
                if mail_group:
                    emp = self.env['hr.employee'].sudo().search([('id', 'in', mail_group)])
                    mail_to += emp.filtered(lambda r: r.work_email != False).mapped('work_email')
                email_cc = ",".join(mail_to) or ''
                cc_emails = ','.join(admin.mapped('email'))
                name = ','.join(admin.mapped('name'))
                template.with_context(email_to=to_email, email_cc=email_cc,from_email=from_emails, names=int_details.users_id.name,
                                    remarks=self.remarks_for_inprogress, name_manager=name).send_mail(int_details.id,
                                                                                    notif_layout="kwantify_theme.csm_mail_notification_light")

            return True


# new team assign

class NewtemAssignWizard(models.TransientModel):
    _name = 'whistle.new.team.assign.wizard'
    _description = 'New Team Assign Wizard'

    team_id = fields.Many2one(string="Category", comodel_name='grievance.ticket.team', compute="_compute_category")
    spoc_persion = fields.Selection([('1', 'SPOC (Level-2)'), ('2', 'SPOC (Level-3)')], string='SPOC',
                                    compute="_compute_category")
    second_level_id = fields.Many2one(comodel_name='res.users', string='SPOC Name')
    # domain=lambda self: [
    #     ("groups_id", "=", self.env.ref("kw_grievance_new.group_grievance_user").id)])

    second_level_ids = fields.Many2many(
        comodel_name='res.users',
        related='team_id.second_level_ids',
        string='Users')
    comment = fields.Text('Comment', track_visibility="1")

    def action_new_teamassign_wiz(self):
        # print('-------------------------->>>>>>11')
        context = dict(self._context)
        # print('-------------------------->>>>>>33')
        int_details = self.env["kw_whistle_blowing"].browse(context.get("active_id"))
        # print('-------------------------->>>>>>22', int_details, int_details.approver_user_ids, [[4, int_details.user_id.id]])
        int_details.approver_user_ids = [[4, int_details.user_id.id]]
        int_details.team_id = self.team_id
        int_details.user_id = self.second_level_id
        int_details.forward_reason = self.comment
        if int_details.request == 'self':
            template = self.env.ref('kw_grievance_new.email_template_reassigned_ticket_whistle')
            email_to = self.second_level_id.email
            to_name = self.second_level_id.name
            admin = self.env['res.users'].sudo().search([])
            manager = admin.filtered(lambda user: user.has_group('kw_grievance_new.group_grievance_manager') == True)
            cc_email = ','.join(manager.mapped('email'))
            template.with_context(email_to=email_to, to_name=to_name).send_mail(int_details.id,
                                                                                notif_layout="kwantify_theme.csm_mail_notification_light")
        else:
            pass    

    """ ------- Forward grievance to SPOC Level-2 from SPOC Level-1 and and SPOC Level-3 from SPOC Level-2 & default   assign category----------"""

    @api.depends('team_id')
    def _compute_category(self):
        context = dict(self._context)
        act_id = self.env["kw_whistle_blowing"].browse(context.get("active_id"))
        self.team_id = act_id.team_id
        team = self.env['grievance.ticket.team'].sudo().search([])
        for rec in team:
            if rec == act_id.team_id:
                if act_id.user_id in rec.user_ids:
                    self.spoc_persion = '1'
                else:
                    self.spoc_persion = '2'

    # -----------------------------------------End--------------------------------------------------------------------

    @api.onchange('team_id', 'spoc_persion')
    def _onchange_team_id(self):
        # spoc_persion_id = []
        if self.team_id:
            if self.spoc_persion == '1':
                return {'domain': {'second_level_id': [('id', 'in', self.team_id.second_level_ids.ids)]}}
                # spoc_persion_id.extend(self.team_id.second_level_ids.ids)
                # user_var = {'domain': {'second_level_id': [('id', 'in', self.second_level_ids.ids)]}}
            # elif self.spoc_persion == '2':
            #     # user_var = {'domain': {'second_level_id': [('id', 'in', self.second_level_ids.ids)]}}
            #     spoc_persion_id.extend(self.team_id.third_level_ids.ids)



# done wizard or close buttom wizard

class WbDoneRemarksWizard(models.TransientModel):
    _name = 'whistle.done.remarks.wizard'
    _description = 'Done Remarks Wizard'

    remarks_for_done = fields.Text(string="Close Remarks")
    word_limit = fields.Integer(string="Limit", default=100)
    stage_id = fields.Many2one('grievance.ticket.stage')

    @api.onchange('remarks_for_done')
    def _check_remarks_description(self):
        if self.remarks_for_done:
            self.word_limit = 500 - len(self.remarks_for_done)

    def action_done_remarks(self):
        for rec in self:
            context = dict(rec._context)
            intObj = rec.env["kw_whistle_blowing"]
            int_details = intObj.browse(context.get("active_id"))
            int_details.remarks_for_done = rec.remarks_for_done
            stage = rec.env['grievance.ticket.stage'].sudo().search([('code', '=', 'D')], limit=1)
            int_details.stage_id = stage.id
            int_details.done_date = date.today()

            if int_details.request == 'self':
                grievance_desk_users = rec.env.user
                employee_email = int_details.users_id.name
                user=self.env['hr.employee'].sudo().search([('user_id', '=', employee_email)], limit=1)
                # res config user
                param = self.env['ir.config_parameter'].sudo()
                mail_group = literal_eval(param.get_param('kw_grievance_new.mail_to_users'))
                mail_to = []
                if mail_group:
                    emp = self.env['hr.employee'].sudo().search([('id', 'in', mail_group)])
                    mail_to += emp.filtered(lambda r: r.work_email != False).mapped('work_email')
                email = ",".join(mail_to) or ''
                users = rec.env['res.users'].sudo().search([])
                admin = users.filtered(lambda user: user.has_group('kw_grievance_new.group_grievance_manager') == True)
                template1 = rec.env.ref('kw_grievance_new.email_template_for_whistle_done')
                from_emails = ','.join(grievance_desk_users.mapped('email'))
                to_emails = ','.join(user.mapped('work_email'))
                cc_email = ','.join(admin.mapped('email'))
                name = ','.join(admin.mapped('name'))
                template1.with_context(email_to=to_emails, email_from=from_emails, email_cc=email, names=int_details.users_id.name,
                                    remarks=rec.remarks_for_done, name_manager=name).send_mail(int_details.id,
                                                                            notif_layout="kwantify_theme.csm_mail_notification_light")
        return True


#     cancel wizard.....................

class CancelledRemarksWizard(models.TransientModel):
    _name = 'whistle.cancelled.remarks.wizard'
    _description = 'Remarks Wizard'

    remarks_for_cancelled = fields.Text(string="Reject Remarks")
    stage_id = fields.Many2one('grievance.ticket.stage')

    def action_cancelled_remarks(self):
        context = dict(self._context)
        intObj = self.env["kw_whistle_blowing"]
        int_details = intObj.browse(context.get("active_id"))
        int_details.remarks_for_cancelled = self.remarks_for_cancelled
        stage = self.env['grievance.ticket.stage'].sudo().search([('code', '=', 'C')], limit=1)
        int_details.stage_id = stage.id
        grievance_desk_users = self.env.user
        employee_email = int_details.users_id.name
        user=self.env['hr.employee'].sudo().search([('user_id', '=', employee_email)], limit=1)
        users = self.env['res.users'].sudo().search([])
        admin = users.filtered(lambda user: user.has_group('kw_grievance_new.group_grievance_manager') == True)
        template = self.env.ref('kw_grievance_new.email_template_for_cancelled_whistle_remarks')
        template1 = self.env.ref('kw_grievance_new.email_template_for_cancelled_whistle')
        from_emails = ','.join(grievance_desk_users.mapped('email'))
        to_email = ','.join(user.mapped('work_email'))
        cc_emails = ','.join(admin.mapped('email'))
        name = ','.join(admin.mapped('name'))
        template.with_context(email_to=cc_emails, email_from=from_emails, names=int_details.users_id.name,
                              remarks=self.remarks_for_cancelled, name_manager=name).send_mail(int_details.id,
                                                                            notif_layout="kwantify_theme.csm_mail_notification_light")

        template1.with_context(email_to=to_email, email_from=from_emails, names=int_details.users_id.name,
                                  remarks=self.remarks_for_cancelled, name_manager=name).send_mail(int_details.id,
                                                                          notif_layout="kwantify_theme.csm_mail_notification_light")

