from odoo import models, fields, api
from ast import literal_eval


class NewtemAssignWizard(models.TransientModel):
    _name = 'grievance.new.team.assign.wizard'
    _description = 'New Team Assign Wizard'

    team_id = fields.Many2one(string="Category",comodel_name='grievance.ticket.team',compute="_compute_category")
    spoc_persion = fields.Selection([('1', 'SPOC (Level-2)'), ('2', 'SPOC (Level-3)')], string='SPOC',compute="_compute_category")
    second_level_id = fields.Many2one(comodel_name='res.users', string='SPOC Name')
                                       # domain=lambda self: [
                                       #     ("groups_id", "=", self.env.ref("kw_grievance_new.group_grievance_user").id)])
    
    second_level_ids = fields.Many2many(
        comodel_name='res.users',
        related='team_id.second_level_ids',
        string='Users')
    comment = fields.Text('Comment', track_visibility="1")

    def action_new_teamassign_wiz(self):
        context = dict(self._context)
        int_details = self.env["grievance.ticket"].browse(context.get("active_id"))
        int_details.approver_user_ids = [[4, int_details.user_id.id]]
        int_details.team_id = self.team_id
        int_details.user_id = self.second_level_id
        int_details.forward_reason = self.comment
        if int_details.request == 'self':
            template = self.env.ref('kw_grievance_new.email_template_reassigned_ticket_grievance')
            email_to = self.second_level_id.email
            to_name = self.second_level_id.name
            admin = self.env['res.users'].sudo().search([])
            manager = admin.filtered(lambda user: user.has_group('kw_grievance_new.group_grievance_manager') == True)
            cc_email = ','.join(manager.mapped('email'))
            template.with_context(email_to=email_to,to_name=to_name).send_mail(int_details.id,
                                                                                              notif_layout="kwantify_theme.csm_mail_notification_light")
        else:
            pass

    """ ------- Forward grievance to SPOC Level-2 from SPOC Level-1 and and SPOC Level-3 from SPOC Level-2 & default   assign category----------"""

    @api.depends('team_id')
    def _compute_category(self):
        context = dict(self._context)
        act_id = self.env["grievance.ticket"].browse(context.get("active_id"))
        self.team_id = act_id.team_id
        team = self.env['grievance.ticket.team'].sudo().search([])
        for rec in team:
            if rec == act_id.team_id:
                if act_id.user_id in rec.user_ids:
                    self.spoc_persion = '1'
                else:
                    self.spoc_persion = '2'
    #-----------------------------------------End--------------------------------------------------------------------

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


   