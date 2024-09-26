# start : commit history
# get_branch method added for domain if delhi then show all b ranches
# group field in job opening
# dynamic domain for roster in onchange
# end : commit history
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
import re
from datetime import datetime

class RecruitmentJobOpening(models.Model):
    _name = "recruitment.jobop"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Job Opening"
    # _rec_name = 'name'

    def default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)

    name = fields.Char('Name')
    requested_by = fields.Many2one('hr.employee', string='Requested By', default=default_employee)
    requested_on = fields.Date(string="Requested On", default=fields.Date.today(),track_visibility='always')
    branch_id = fields.Many2one('res.branch', string='Recruiter Branch')
    job_pos = fields.One2many('job.opening.lines', 'job_opening_id', string='Job Openings')
    state = fields.Selection([('draft', 'Draft'), ('to_approve', 'To Approve'), ('approved', 'Approved'), ('published', 'Published'), ('rejected', 'Rejected')], required=True, string='Status', default='draft', track_visibility='always')
    job_ids = fields.Many2many('hr.job',string='Job Openings',compute="_compute_unique_job_openings")

    @api.depends('job_pos')
    @api.multi
    def _compute_unique_job_openings(self):
        for opening in self:
            opening.job_ids = [[6,0,opening.job_pos.mapped('job_id').ids]]

    @api.onchange('requested_by')
    def onchange_get_basic(self):
        for record in self:
            record.branch_id = record.requested_by.branch_id

    @api.onchange('job_pos')
    def show_duplicate_roster_warning(self):
        if self.job_pos:
            for data in self.job_pos:
                if self.job_pos.filtered(lambda r: r.roster_line_id == data.roster_line_id) - data:
                    return {'warning': {'title': ('Validation Error'),'message': ('Duplicate roster added.')}}

    @api.model
    def create(self, vals):
        res = super(RecruitmentJobOpening, self).create(vals)
        sequence = ''
        seq = self.env['ir.sequence'].next_by_code('recruitment.jobop')
        sequence = 'Job Op - ' + str(seq)
        res.name = sequence
        return res

    @api.multi
    def button_draft(self):
        for rec in self:
            rec.write({'state': 'draft'})

    @api.multi
    def button_to_approve(self):
        for rec in self:
            rec.write({'state': 'to_approve'})

    @api.multi
    def button_approved(self):
        for rec in self:
            rec.write({'state': 'approved'})

    @api.multi
    def button_reject(self):
        for rec in self:
            rec.write({'state': 'rejected'})


    @api.multi
    def button_create_advertisemtnt(self):
        for rec in self:
            create_advertisement = self.env['hr.requisition.application'].create(
                {
                    'state': 'draft',
                    'branch_id': rec.branch_id.id,
                    'start_date': datetime.now().date(),
                }
            )
            sql = self._cr.execute("select job_id,branch_id, count(*) from job_opening_lines" \
                  "group_by job_id,branch" \
                  "where job_opening_id = {0}".format(rec.id))
            print('============sql===================', sql)
            for line in rec.job_pos:
                create_advertisement_line = self.env['advertisement.line'].create(
                    {
                        'allowed_category_id': create_advertisement.id,
                        'job_id': line.job_id.id,
                        'branch_id': line.branch_id.id,
                        'opening': int(line.roster_line_id.sc) + int(line.roster_line_id.general) + int(line.roster_line_id.st),
                        'sc': int(line.roster_line_id.sc),
                        'general': int(line.roster_line_id.general),
                        'st': int(line.roster_line_id.st),
                    }
                )

            rec.write({'state': 'published'})


class RecruitmentJobLines(models.Model):
    _name = "job.opening.lines"
    _description = "Job Opening Lines"

    @api.model
    def get_domain(self,for_which):
        domain = [('id','=',0)]
        if self._context.get('default_job_opening_branch') and self._context['default_job_opening_branch']:
            branch = self.branch_id.browse(self._context['default_job_opening_branch'])
            if branch.name in ['New Delhi','Delhi']:
                domain = []
            else:
                if for_which == 'branch':
                    domain = ['|',('id','=',branch.id),('parent_branch_id','=',branch.id)]
                elif for_which == 'group':
                    domain = [('code','not in',['a','A'])]
        return domain

    job_opening_id = fields.Many2one('recruitment.jobop', string='Job Opening')
    # job_opening_branch = fields.Many2one('res.branch', string='Job Opening Branch')
    job_id = fields.Many2one('hr.job', string='Job Position')
    date = fields.Date(string="Date", default=fields.Date.today(),track_visibility='always')
    state_id = fields.Many2one('res.country.state', string='State',domain=[('country_id.code','=','IN')],required=True)
    directorate_id =  fields.Many2one('res.branch',string="Directorate",domain="['|',('parent_branch_id.code','=','HQ'),('code','=','HQ')]")
    branch_id = fields.Many2one('res.branch', string='Center',domain=lambda self: self.get_domain('branch'))
    roster_line_id = fields.Many2one('recruitment.roster', string='Roster')
    category_id = fields.Many2one('employee.category', string='Category')
    state = fields.Many2one('res.country.state', string='State')
    employee_type = fields.Selection([('regular', 'Regular Employee'),('contractual_with_agency', 'Contractual with Agency'),('contractual_with_stpi', 'Contractual with STPI')],string='Employment Type',default="regular",required=True)
    group_id = fields.Many2one("stpi.group.master","Group",domain=lambda self: self.get_domain('group'))
    remarks = fields.Text('Remarks')
    is_group_A = fields.Boolean("Group A ?",compute="_compute_if_group_A")

    @api.depends('group_id')
    @api.multi
    def _compute_if_group_A(self):
        for line in self:
            if line.group_id and line.group_id.code in ['a','A']:
                line.is_group_A = True

    @api.onchange('group_id')      
    def set_job_position(self):
        self.job_id = False
        self.branch_id = False
        group_id = self.group_id and self.group_id.id or 0
        return { 'domain':{'job_id':[('pay_level_id.group_id','=',group_id)]}}

    @api.onchange('roster_line_id')
    def get_basic_details(self):
        for rec in self:
            rec.category_id = rec.roster_line_id.category_id
            rec.state = rec.roster_line_id.state
            rec.remarks = rec.roster_line_id.remarks
            # rec.branch_id = rec.roster_line_id.branch_id
            # added by Gouranga kala 06 july 2021
            # rec.group_id = rec.mapped('roster_line_id.group_id')
    
    # added by gouranga kala 06 july 2021
    # group filter removed suggested by Bibhu sir & nalini sir 16-Dec-2021
    # @api.onchange('group_id','branch_id','job_id','state_id')
    @api.onchange('job_id','state_id','directorate_id')
    def set_roster_domain(self):
        self.roster_line_id = False
        domain = [('id', '=', False)]
        # if group A then no restriction for state he can access all state roster having same group (Previous logic)
        # if self.is_group_A and self.job_id and self.group_id and self.state_id:
        #     domain = [('job_id','=',self.job_id.id),('group_id','=',self.group_id.id),('state','=',self.state_id.id),('employee_id','=',False)]
        # else:
        #     if self.group_id and self.branch_id and self.branch_id.state_id and self.job_id:
        #         domain = [('state','=',self.branch_id.state_id.id),('job_id','=',self.job_id.id),('employee_id','=',False),('group_id','=',self.group_id.id)]
        # if self.job_id and self.group_id and self.state_id:
        if self.job_id and self.state_id:
            # domain = [('job_id','=',self.job_id.id),('group_id','=',self.group_id.id),('state','=',self.state_id.id),('employee_id','=',False)]
            domain = [('job_id', '=', self.job_id.id), ('state', '=', self.state_id.id), ('employee_id', '=', False)]
            if self.directorate_id:
                domain = ['|', ('branch_id', '=', self.directorate_id.id), ('branch_id', '=', False)] + domain
        not_approved_rosters = self.roster_line_id.search(domain).filtered(lambda r: r.is_approved == False)
        print("not approved", not_approved_rosters)
        domain = [('id', 'in', not_approved_rosters.ids)]
        return { 'domain':{'roster_line_id':domain}}