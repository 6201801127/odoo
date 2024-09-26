"""
Module: Helpdesk Ticket Team Assignment Wizard

Summary:
    This module provides a wizard for assigning helpdesk tickets to teams.

Description:
    This module defines a wizard used for assigning helpdesk tickets to teams. It contains functionalities
    for selecting a team to assign tickets to. This wizard is part of the helpdesk ticket management system
    within the Odoo platform.

"""
from odoo import models, fields, api
from ast import literal_eval


class NewtemAssignWizard(models.TransientModel):
    """
    Wizard for assigning helpdesk tickets to teams.

    Attributes:
        _name (str): The technical name of the model.
        _description (str): Description of the model.
        team_id (Many2one): Reference field for selecting the helpdesk ticket team.
    """
    _name = 'new.team.assign.wizard'
    _description = 'New Team Assign Wizard'

    team_id = fields.Many2one('helpdesk.ticket.team')
    second_level_id = fields.Many2one(comodel_name='res.users', string='L2',
                                       domain=lambda self: [
                                           ("groups_id", "=", self.env.ref("helpdesk_mgmt.group_helpdesk_user").id)])
    
    second_level_ids = fields.Many2many(
        comodel_name='res.users',
        related='team_id.second_level_ids',
        string='Users')
    comment = fields.Text('Comment', track_visibility="1")

    def action_new_teamassign_wiz(self):
        context = dict(self._context)
        int_details = self.env["helpdesk.ticket"].browse(context.get("active_id"))
        int_details.approver_user_ids = [[4, int_details.user_id.id]]
        int_details.team_id = self.team_id
        int_details.user_id = self.second_level_id
        int_details.forward_reason = self.comment
        template = self.env.ref('helpdesk_mgmt.email_template_reassigned_ticket')
        email_to = self.second_level_id.email
        to_name = self.second_level_id.name
        admin = self.env['res.users'].sudo().search([])
        manager = admin.filtered(lambda user: user.has_group('helpdesk_mgmt.group_helpdesk_manager') == True)
        cc_email = ','.join(manager.mapped('email'))

        param = self.env['ir.config_parameter'].sudo()
        mail_group = literal_eval(param.get_param('helpdesk_mgmt.mail_to_user'))
        mail_to = []
        if mail_group:
            emp = self.env['hr.employee'].sudo().search([('id', 'in', mail_group)])
            mail_to += emp.filtered(lambda r: r.work_email != False).mapped('work_email')
        email_cc = ",".join(mail_to) or ''
        template.with_context(email_to=email_to, email_cc=email_cc, to_name=to_name).send_mail(int_details.id,
                                                                                              notif_layout="kwantify_theme.csm_mail_notification_light")

    @api.onchange('team_id')
    def _onchange_team_id(self):
        if self.team_id:
            user_var = {'domain': {'second_level_id': [('id', 'in', self.second_level_ids.ids)]}}
            return user_var