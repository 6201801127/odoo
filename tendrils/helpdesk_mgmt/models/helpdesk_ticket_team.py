"""
Module for Helpdesk Ticket Team Model.

This module contains the model definition for managing teams of helpdesk tickets in Odoo.

"""
from odoo import api, fields, models


class HelpdeskTeam(models.Model):
    """
    Model for Helpdesk Ticket Team.

    This class represents the model for managing teams of helpdesk tickets in Odoo.

    Attributes:
        _name (str): The technical name of the model ('helpdesk.ticket.team').
        _description (str): Description of the model ('Helpdesk Ticket Team').
        _inherit (list): List of inherited models ('mail.thread', 'mail.alias.mixin').

    """
    _name = 'helpdesk.ticket.team'
    _description = 'Helpdesk Ticket Team'
    _inherit = ['mail.thread', 'mail.alias.mixin']

    

    name = fields.Char(string='Name', required=True)
    user_ids = fields.Many2many(comodel_name='res.users', relation="rel1", column1="a", column2="b", string='L1',
                                domain=lambda self: [("groups_id", "=",
                                                      self.env.ref("helpdesk_mgmt.group_helpdesk_user").id)])
    second_level_ids = fields.Many2many(comodel_name='res.users', string='L2',
                                        domain=lambda self: [("groups_id", "=",
                                                              self.env.ref("helpdesk_mgmt.group_helpdesk_user").id)])
    # third_level_ids = fields.Many2many(comodel_name='res.users', relation="rel3", column1="e", column2="f", string='L3')

    active = fields.Boolean(default=True)
    category_ids = fields.Many2many(comodel_name='helpdesk.ticket.category',
                                    string='Category')
    company_id = fields.Many2one('res.company',
                                 string="Company",
                                 default=lambda self: self.env['res.company']._company_default_get('helpdesk.ticket')
                                 )
    alias_id = fields.Many2one(help="The email address associated with "
                                    "this channel. New emails received will "
                                    "automatically create new tickets assigned "
                                    "to the channel.")
    color = fields.Integer("Color Index", default=0)

    ticket_ids = fields.One2many('helpdesk.ticket', 'team_id',
                                 string="Tickets")

    todo_ticket_ids = fields.One2many('helpdesk.ticket', 'team_id',
                                      string="Todo tickets", domain=[("closed", '=', False)])

    todo_ticket_count = fields.Integer(string="Number of tickets",
                                       compute='_compute_todo_tickets')

    onhold_ticket_count = fields.Integer(string="Number of Onhold tickets",
                                       compute='_compute_onhold_ticket_count')
    inprogress_ticket_count = fields.Integer(string="Number of In Progress tickets",
                                    compute='_compute_inprogress_ticket_count')                                    
    completed_ticket_count = fields.Integer(string="Number of Done tickets",
                                       compute='_compute_completed_ticket_count')
    cancelled_ticket_count = fields.Integer(string="Number of Cancel tickets",
                                       compute='_compute_cancelled_ticket_count')

    todo_ticket_count_unassigned = fields.Integer(
        string="Number of tickets unassigned",
        compute='_compute_todo_tickets')

    todo_ticket_count_unattended = fields.Integer(
        string="Number of tickets unattended",
        compute='_compute_todo_tickets')

    todo_ticket_count_high_priority = fields.Integer(
        string="Number of tickets in high priority",
        compute='_compute_todo_tickets')

    todo_ticket_count_close_total = fields.Integer(
        string="Number of tickets Closed",
        compute='_compute_todo_ticket_count_close_total')
    random_assign = fields.Boolean(string="Is Randomly Assign")

    @api.depends()
    def _compute_onhold_ticket_count(self):
        for record in self:
            ticket_count_onhold = self.env["helpdesk.ticket"].search_count([('stage_id','=','Hold'),('team_id','=',record.id)])
            if ticket_count_onhold:
                record.onhold_ticket_count = ticket_count_onhold    

    @api.depends('ticket_ids', 'ticket_ids.stage_id')
    def _compute_inprogress_ticket_count(self):
        for record in self:
            ticket_count_inprogress = self.env["helpdesk.ticket"].search_count([('stage_id','=','In Progress'),('team_id','=',record.id)])
            if ticket_count_inprogress:
                record.inprogress_ticket_count = ticket_count_inprogress
    @api.depends('ticket_ids', 'ticket_ids.stage_id')
    def _compute_completed_ticket_count(self):
        for record in self:
            ticket_count_done = self.env["helpdesk.ticket"].search_count([('stage_id','=','Done'),('team_id','=',record.id)])
            if ticket_count_done:
                record.completed_ticket_count = ticket_count_done
    @api.depends('ticket_ids', 'ticket_ids.stage_id')
    def _compute_cancelled_ticket_count(self):
        for record in self:
            ticket_count_cancelled = self.env["helpdesk.ticket"].search_count([('stage_id','=','Cancelled'),('team_id','=',record.id)])
            if ticket_count_cancelled:
                record.cancelled_ticket_count = ticket_count_cancelled
    @api.depends('ticket_ids', 'ticket_ids.stage_id')
    def _compute_todo_ticket_count_close_total(self):
        for record in self:
            ticket_count_done = self.env["helpdesk.ticket"].search_count([('stage_id','=','Done'),('team_id','=',record.id)])
            if ticket_count_done:
                record.todo_ticket_count_close_total = ticket_count_done



    @api.depends('ticket_ids', 'ticket_ids.stage_id')
    def _compute_todo_tickets(self):
        ticket_model = self.env["helpdesk.ticket"]
        fetch_data = ticket_model.read_group(
            [("team_id", "in", self.ids), ("closed", "=", False)],
            ["team_id", "user_id", "unattended", "priority"],
            ["team_id", "user_id", "unattended", "priority"],
            lazy=False,
        )
        result = [
            [
                data["team_id"][0],
                data["user_id"] and data["user_id"][0],
                data["unattended"],
                data["priority"],
                data["__count"]
            ] for data in fetch_data
        ]
        for team in self:
            team.todo_ticket_count = sum([
                r[4] for r in result
                if r[0] == team.id
            ])
            team.todo_ticket_count_unassigned = sum([
                r[4] for r in result
                if r[0] == team.id and not r[1]
            ])
            team.todo_ticket_count_unattended = sum([
                r[4] for r in result
                if r[0] == team.id and r[2]
            ])
            team.todo_ticket_count_high_priority = sum([
                r[4] for r in result
                if r[0] == team.id and r[3] == "3"
            ])

    def get_alias_model_name(self, vals):
        return 'helpdesk.ticket'

    def get_alias_values(self):
        values = super(HelpdeskTeam, self).get_alias_values()
        values['alias_defaults'] = {'team_id': self.id}
        return values
