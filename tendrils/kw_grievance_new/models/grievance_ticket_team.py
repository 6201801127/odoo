from odoo import api, fields, models
from odoo.exceptions import ValidationError


class GrievanceTeam(models.Model):
    _name = 'grievance.ticket.team'
    _description = 'Grievance Ticket Team'
    _rec_name = "name"
    _inherit = ['mail.thread', 'mail.alias.mixin']

    
    _sql_constraints = [
        ('name_uniq', 'unique (name)','Category Already Exist!')
    ]
    name = fields.Many2one(string='Category Name',comodel_name="grievance.ticket.category",required=True)
    code = fields.Char(string='Code')
    user_ids = fields.Many2many(comodel_name='res.users', relation="rel", column1="ab", column2="bc",
                                string='SPOC (Level-1)',
                                domain=lambda self: [("groups_id", "=",
                                                      self.env.ref("kw_grievance_new.group_grievance_user").id)])
    second_level_ids = fields.Many2many(comodel_name='res.users', string='SPOC (Level-2)',
                                domain=lambda self: [("groups_id", "=",
                                                      self.env.ref("kw_grievance_new.group_grievance_user").id)])
    third_level_ids = fields.Many2many(comodel_name='res.users', relation="grievance_ticket_team_grievance_ticket_rel", column1="grievance_ticket_team_id",
                                       column2="hr_employee_id", string='SPOC (Level-3)')
    # third_level_ids = fields.Many2many(comodel_name='res.users', relation="rel3", column1="e", column2="f", string='L3')

    # state = fields.Selection([('draft', 'Draft'),
    #     ('assigned', 'Assigned'),
    #     ('approved','Approved'),
    # ], string="State", default='draft')
    active = fields.Boolean(default=True)
    category_ids = fields.Many2many(comodel_name='grievance.ticket.category',
                                    string='Category')
    sub_category_ids = fields.One2many(comodel_name='kw_sub_category_relation', inverse_name="team_id",
                                    string='Sub-Category')
    company_id = fields.Many2one('res.company',
                                 string="Company",
                                 default=lambda self: self.env['res.company']._company_default_get('grievance.ticket')
                                 )

    # alias_id = fields.Many2one(help="The email address associated with "
    #                                 "this channel. New emails received will "
    #                                 "automatically create new tickets assigned "
    #                                 "to the channel.")
    color = fields.Integer("Color Index", default=0)

    ticket_ids = fields.One2many('grievance.ticket', 'team_id',
                                 string="Tickets")

    ticket_wb_ids = fields.One2many('kw_whistle_blowing', 'team_id',
                                 string="Tickets")

    todo_ticket_ids = fields.One2many('grievance.ticket', 'team_id',
                                      string="Todo tickets", domain=[("closed", '=', False)])

    todo_wb_ticket_ids = fields.One2many('kw_whistle_blowing', 'team_id',
                                      string="Todo tickets", domain=[("closed", '=', False)])

    todo_ticket_count = fields.Integer(string="Number of tickets",
                                       compute='_compute_todo_grievances')

    todo_wb_ticket_count = fields.Integer(string="Number of tickets",
                                       compute='_compute_todo_wb')

    onhold_ticket_count = fields.Integer(string="Number of Onhold tickets",
                                       compute='_compute_onhold_grievance_count')

    onhold_wb_ticket_count = fields.Integer(string="Number of Onhold tickets",
                                       compute='_compute_onhold_wb_count')

    inprogress_ticket_count = fields.Integer(string="Number of In Progress tickets",
                                    compute='_compute_inprogress_grievance_count')  

    inprogress_wb_ticket_count = fields.Integer(string="Number of In Progress tickets",
                                    compute='_compute_inprogress_wb_count')                                    
    completed_ticket_count = fields.Integer(string="Number of Done tickets",
                                       compute='_compute_completed_grievance_count')

    completed_wb_ticket_count = fields.Integer(string="Number of Done tickets",
                                       compute='_compute_completed_wb_count')
    cancelled_ticket_count = fields.Integer(string="Number of Cancel tickets",
                                       compute='_compute_cancelled_grievance_count')

    cancelled_wb_ticket_count = fields.Integer(string="Number of Cancel tickets",
                                       compute='_compute_cancelled_wb_count')

    todo_ticket_count_unassigned = fields.Integer(
        string="Number of tickets unassigned",
        compute='_compute_todo_grievances')

    todo_wb_ticket_count_unassigned = fields.Integer(
        string="Number of tickets unassigned",
        compute='_compute_todo_wb')

    todo_ticket_count_unattended = fields.Integer(
        string="Number of tickets unattended",
        compute='_compute_todo_grievances')

    todo_wb_ticket_count_unattended = fields.Integer(
        string="Number of tickets unattended",
        compute='_compute_todo_wb')

    todo_ticket_count_high_priority = fields.Integer(
        string="Number of tickets in high priority",
        compute='_compute_todo_grievances')

    todo_wb_ticket_count_high_priority = fields.Integer(
        string="Number of tickets in high priority",
        compute='_compute_todo_wb')

    todo_ticket_count_close_total = fields.Integer(
        string="Number of tickets Closed",
        compute='_compute_todo_grievance_count_close_total')

    todo_wb_ticket_count_close_total = fields.Integer(
        string="Number of tickets Closed",
        compute='_compute_todo_wb_count_close_total')

    random_assign = fields.Boolean(string="Is Randomly Assign")
    escalation_days = fields.Integer(string="Escalation Days")

    #----------- Same name allowed restriction in SPOC Level-1 and SPOC Level-2 ------------
    @api.constrains('second_level_ids')
    @api.onchange('second_level_ids')
    def _ceck_second_level_ids(self):
        for rec in self.second_level_ids:
            if rec in self.user_ids:
                raise ValidationError('Same name not allowed in both field SPOC Level-2 and SPOC Level-1')
                
    @api.constrains('user_ids')
    @api.onchange('user_ids')
    def _ceck_first_level_ids(self):
        for record in self.user_ids:
            if record in self.second_level_ids:
                raise ValidationError('Same name not allowed in both field SPOC Level-1 and SPOC Level-2')
    # ----------------------------------end---------------------------------------------
      
    @api.onchange('name')
    def _onchange_name(self):
        self.code = self.name.category_code

    @api.constrains('sub_category_ids')
    def _check_name(self):
        team= self.sub_category_ids
        record = self.env['grievance.ticket.team'].sudo().search([]) - self
        for rec in record:
            for data in rec.sub_category_ids:
                if data in team:
                    raise ValidationError("The Sub category {} is already exists , try a different one.".format(data.name))

    @api.onchange('user_ids')
    def _onchange_user_ids(self):
        sec_lv_data = {'domain':{'second_level_ids':[('id', 'not in', self.user_ids.ids),("groups_id", "=",
                                                              self.env.ref("kw_grievance_new.group_grievance_user").id)]}}
        return sec_lv_data

            
    @api.depends()
    def _compute_onhold_grievance_count(self):
        for record in self:
            ticket_count_onhold = self.env["grievance.ticket"].search_count([('stage_id','=','Hold'),('team_id','=',record.id)])
            if ticket_count_onhold:
                record.onhold_ticket_count = ticket_count_onhold  

    @api.depends()
    def _compute_onhold_wb_count(self):
        for record in self:
            ticket_count_onhold = self.env["kw_whistle_blowing"].search_count([('stage_id','=','Hold'),('team_id','=',record.id)])
            if ticket_count_onhold:
                record.onhold_wb_ticket_count = ticket_count_onhold    

    @api.depends('ticket_ids', 'ticket_ids.stage_id')
    def _compute_inprogress_grievance_count(self):
        for record in self:
            ticket_count_inprogress = self.env["grievance.ticket"].search_count([('stage_id','=','In Progress'),('team_id','=',record.id)])
            if ticket_count_inprogress:
                record.inprogress_ticket_count = ticket_count_inprogress


    @api.depends('ticket_ids', 'ticket_ids.stage_id')
    def _compute_inprogress_wb_count(self):
        for record in self:
            ticket_count_inprogress = self.env["kw_whistle_blowing"].search_count([('stage_id','=','In Progress'),('team_id','=',record.id)])
            if ticket_count_inprogress:
                record.inprogress_wb_ticket_count = ticket_count_inprogress

    @api.depends('ticket_ids', 'ticket_ids.stage_id')
    def _compute_completed_grievance_count(self):
        for record in self:
            ticket_count_done = self.env["grievance.ticket"].search_count([('stage_id','=','Closed'),('team_id','=',record.id)])
            if ticket_count_done:
                record.completed_ticket_count = ticket_count_done
                
    @api.depends('ticket_ids', 'ticket_ids.stage_id')
    def _compute_completed_wb_count(self):
        for record in self:
            ticket_count_done = self.env["kw_whistle_blowing"].search_count([('stage_id','=','Closed'),('team_id','=',record.id)])
            if ticket_count_done:
                record.completed_wb_ticket_count = ticket_count_done


    @api.depends('ticket_ids', 'ticket_ids.stage_id')
    def _compute_cancelled_grievance_count(self):
        for record in self:
            ticket_count_cancelled = self.env["grievance.ticket"].search_count([('stage_id','=','Rejected'),('team_id','=',record.id)])
            if ticket_count_cancelled:
                record.cancelled_ticket_count = ticket_count_cancelled

    @api.depends('ticket_ids', 'ticket_ids.stage_id')
    def _compute_cancelled_wb_count(self):
        for record in self:
            ticket_count_cancelled = self.env["kw_whistle_blowing"].search_count([('stage_id','=','Rejected'),('team_id','=',record.id)])
            if ticket_count_cancelled:
                record.cancelled_wb_ticket_count = ticket_count_cancelled


    @api.depends('ticket_ids', 'ticket_ids.stage_id')
    def _compute_todo_grievance_count_close_total(self):
        for record in self:
            ticket_count_done = self.env["grievance.ticket"].search_count([('stage_id','=','Closed'),('team_id','=',record.id)])
            if ticket_count_done:
                record.todo_ticket_count_close_total = ticket_count_done


    @api.depends('ticket_ids', 'ticket_ids.stage_id')
    def _compute_todo_wb_count_close_total(self):
        for record in self:
            ticket_count_done = self.env["kw_whistle_blowing"].search_count([('stage_id','=','Closed'),('team_id','=',record.id)])
            if ticket_count_done:
                record.todo_wb_ticket_count_close_total = ticket_count_done



    @api.depends('ticket_ids', 'ticket_ids.stage_id')
    def _compute_todo_wb(self):
        ticket_model = self.env["kw_whistle_blowing"]
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
            team.todo_wb_ticket_count = sum([
                r[4] for r in result
                if r[0] == team.id
            ])
            team.todo_wb_ticket_count_unassigned = sum([
                r[4] for r in result
                if r[0] == team.id and not r[1]
            ])
            team.todo_wb_ticket_count_unattended = sum([
                r[4] for r in result
                if r[0] == team.id and r[2]
            ])
            team.todo_wb_ticket_count_high_priority = sum([
                r[4] for r in result
                if r[0] == team.id and r[3] == "3"
            ])


    @api.depends('ticket_ids', 'ticket_ids.stage_id')
    def _compute_todo_grievances(self):
        ticket_model = self.env["grievance.ticket"]
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
        return 'grievance.ticket'


    def get_alias_values(self):
        values = super(GrievanceTeam, self).get_alias_values()
        values['alias_defaults'] = {'team_id': self.id}
        return values


class griavanceSubCategory(models.Model):
    _name = "kw_sub_category_relation"
    _description = "kw_sub_category_relation"

    sub_category_id = fields.Many2one('grievance.ticket.subcategory', string="Sub Category", required=True)
    team_id = fields.Many2one('grievance.ticket.team')

    @api.onchange('sub_category_id')
    def get_sub_category(self):
        sub_list = []
        for rec in self.env['kw_sub_category_relation'].sudo().search([]):
            sub_list.append(rec.sub_category_id.id)
        return {'domain': {'sub_category_id': [('id', 'not in',sub_list)]}}
    