# start : commit history
# group added in roster
# end : commit history
from odoo import api, fields, models #, tools, _
from odoo.exceptions import ValidationError
# import re
from datetime import datetime,date

class RecruitmentRoster(models.Model):
    _name = "recruitment.roster"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Recruitment Roster"
    _rec_name = 'number'


    # @api.onchange('job_id')
    # def get_roster_line_item(self):
    #     return {'domain': {'roster_line_item': [('job_id', '=', self.job_id.id), ('employee_id', '=', False)]}}

    # sequence_number = fields.Integer('Sequence Number')
    number = fields.Char('Number')
    
    name = fields.Integer(string="Sequence Number",track_visibility='always')
    roster_point_number = fields.Many2one('recruitment.roster', string='Roster  Point Number')#,track_visibility='always'

    job_id = fields.Many2one('hr.job', string='Job Position',required=True)
    roster_point_id = fields.Many2one('roster.point.master','Roster Point Number',required=True)
    category_id = fields.Many2one('employee.category', string='Reserved For')
    state = fields.Many2one('res.country.state', string='State',track_visibility='always',required=True)
    branch_id = fields.Many2one("res.branch","Center",required=True)

    employee_id = fields.Many2one('hr.employee', string='Name of the Person')
    emp_code = fields.Char('Emp Code', related='employee_id.identify_id')
    Name_of_person = fields.Char('Name of the Person')
    Hired_category = fields.Many2one('employee.category', string='Utilised By')
    date_of_apointment = fields.Date('Date of Appointment')
    current_status = fields.Selection([("Suspended", "Suspended"),
                                        ("Resigned", "Resigned"),
                                        ("technical resignation internal","Technical Resignation(Internal)"),
                                        ("technical resignation external","Technical Resignation(External)"),
                                        ("Contract Expired ", "Contract Expired "),
                                        ("Superannuation", "Superannuation"),
                                        ("Deceased","Deceased"),
                                        ("Terminated","Terminated"),
                                        ("Absconding","Absconding"),
                                        ("Transferred","Transferred"),
                                      ('Working', 'Working'),
                                      ('Vacant', 'Vacant'),
                                      ('deputation','Deputation')
                                       ], string='Current Status')
    current_status_date = fields.Date(string='Current Status Date'
    # track_visibility='always'
    )

    remarks = fields.Text('Remarks')
    # added by gouranga kala 06 july 2021
    group_id = fields.Many2one("stpi.group.master","Group")
    is_group_A = fields.Boolean(string='Group A ?',compute="_compute_if_group_A")
    
    is_approved = fields.Boolean(string='Group A ?',compute="_compute_if_approved")
    active = fields.Boolean(string="Active",default=True)
    recruitment_status = fields.Selection(selection=[('draft','Draft'),
                                                        ('in_progress','In Progress'),
                                                        ('completed','Completed')],string="Recruitment Status",compute="_compute_recruitment_status")

    @api.multi
    def _compute_recruitment_status(self):
        for roster in self:
            job_opening_data = self.env['recruitment.jobop'].search([('state','!=','rejected'),('job_pos.roster_line_id','in',[roster.id])])

            advertisement_data = self.env['hr.requisition.application'].search([('state','!=','rejected'),('advertisement_line_ids.job_opening_line_id.roster_line_id','in',[roster.id])])
            if advertisement_data:
                roster.recruitment_status = 'completed'
            elif job_opening_data:
                roster.recruitment_status = 'in_progress'
            else:
                roster.recruitment_status = 'draft'

    # @api.multi
    # def compute_roster_state(self):
    #     employee_data = self.env['hr.employee'].with_context(active_test=False).search(['|',('active','=',True),('active','=',False),('roster_line_item','in',self.ids)],limit=1)
    #     for roster in self:
    #         roster_employee = employee_data.filtered(lambda r:r.roster_line_item==roster)
    #         if roster_employee:
    #             if roster_employee.active:
    #                 roster.current_status = 'Working'
    #                 # roster.current_status_date = 
    #             else:
    #                 roster.current_status = 'not_working'
    #         else:
    #             roster.current_status = 'Vacant'

    @api.onchange('job_id')
    def set_roaster_point_domain(self):
        domain = [('id','in',[])]
        if self.job_id:
            related_roster_point_ids = self.env['roster.point.master'].search([('job_id','=',self.job_id.id)])
            accuired_roster_points = self.search([('roster_point_id','in',related_roster_point_ids.ids)]) - self
            not_accuired_roaster_points = related_roster_point_ids - accuired_roster_points.mapped('roster_point_id') 
            domain = [('id','in',not_accuired_roaster_points.ids)]
        return {
            'domain':{'roster_point_id':domain}
        }

    @api.onchange('roster_point_id')
    def set_related_fields(self):
        if self.roster_point_id:
            # self.job_id = self.roster_point_id.job_id
            self.category_id = self.roster_point_id.category_id 
            self.state = self.roster_point_id.state_id
            self.branch_id = self.roster_point_id.branch_id
        else:
            # self.job_id = False
            self.category_id = False
            self.state = False
            self.branch_id = False

    api.multi
    def name_get(self):
        res = []
        for record in self:
            name = f"{record.name}"
            if record.job_id:
                name += f" ({record.job_id.name})"
            if record.category_id:
                names = ",".join(record.category_id.mapped('name'))
                name += f" ({names})"
            if record.state:
                name += f" ({record.state.name})"
            if record.branch_id:
                name += f' ({record.branch_id.name})'
            res.append((record.id, name))
        return res

    @api.multi
    def _compute_if_approved(self):
        for roster in self:
            if self.env['job.opening.lines'].sudo().search([('job_opening_id.state','=','approved'),('roster_line_id','=',roster.id)]):
                roster.is_approved = True

    @api.multi
    @api.depends('group_id')
    def _compute_if_group_A(self):
        for roster in self:
            if roster.group_id and roster.group_id.code in ['a','A','Group A']:
                roster.is_group_A = True
            else:
                roster.is_group_A = False

    # @api.onchange('group_id')
    # def set_state(self):
    #     if self.group_id and self.group_id.code in ['a','A','Group A']:
    #         self.state = False
    
    # added by gouranga kala 06 july 2021
    @api.onchange('job_id')
    def set_group(self):
        group_id = self.mapped('job_id.pay_level_id.group_id')
        if group_id and not self.group_id:
            self.group_id = group_id.id

    # @api.constrains('roster_point_number','state')
    # def validate_statewise_roaster(self):
    #     for roster in self:
    #         if roster.roster_point_number and roster.state:
    #             if self.search(['|',('active','=',True),('active','=',False),('roster_point_number','=',roster.roster_point_number.id),('state','=',roster.state.id)]) - self:
    #                 raise ValidationError(f'Combination of state {roster.state.name} and Roaster {roster.number} already exists.')

    @api.model
    def create(self, vals):
        if self.env.user.has_group("hr_recruitment.group_hr_recruitment_manager") and 'HQ' in self.env.user.branch_ids.mapped('code'):
            res = super(RecruitmentRoster, self).create(vals)
            res.current_status = 'Vacant'
            state = res.state and res.state.id or False
            branch = res.branch_id and res.branch_id.id or False
            last_state_roster_number = self.search(['|',('active','=',True),('active','=',False),('id','!=',res.id),('job_id','=',res.job_id.id),('state','=',state),('branch_id','=',branch)],limit=1,order="name desc")
            if last_state_roster_number:
                res.name=last_state_roster_number.name + 1
            else:
                res.name = 1
            # last_name_int = self.sudo().search(['|',('active','=',True),('active','=',False),('id','!=',res.id)]).sorted(key=lambda r:r.name,reverse=True)[0:1]
            # if last_name_int:
            #     res.name=last_name_int.name + 1
            # else:
            #     res.name = 1
            res.number = str(res.name) + ' (' + str(res.job_id.name) + ')' + ' (' + str(res.category_id.name) + ')' + ' (' + str(res.state.name) + ')'
            mail_template = self.env.ref('recruitment_up_stpi.recruitment_roster_notify_mail_template')
            mail_template.send_mail(res.id)
            return res
        else:
            raise ValidationError("Only Recruitment Managers From Head Quarter Can Create Roster(s).")
    
    @api.multi
    def write(self,vals):
        if 'active' in vals and vals['active']==False:
            if 'HQ' not in self.env.user.branch_ids.mapped('code'):
                raise ValidationError("Only recruitment managers from head quarter can deactivate roster(s).")

        result = super(RecruitmentRoster, self).write(vals)
        return result

class EmployeeRoster(models.Model):
    _inherit = "hr.employee"

    roster_line_item = fields.Many2one('recruitment.roster', string="Roster line", track_visibility='onchange')

    @api.constrains('roster_line_item')
    def putinto_roster_line_item(self):
        for rec in self:
            if rec.roster_line_item:
                rec.roster_line_item.employee_id = rec.id
                rec.roster_line_item.Hired_category = rec.category.id
                rec.roster_line_item.emp_code = rec.identify_id
                rec.roster_line_item.Name_of_person = rec.name
                rec.roster_line_item.date_of_apointment = rec.date_of_join
                rec.roster_line_item.current_status = 'Working'
                rec.roster_line_item.current_status_date = date.today()