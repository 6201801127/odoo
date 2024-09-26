from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

class HrRequisition(models.Model):
    _name = "hr.requisition"
    _description = "HR Requisition"
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string='Job Requisition Number', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'),track_visibility='always')
    job_position = fields.Many2one('hr.job',string="Job Position",required=True,
                                   help='Job Title of the employee',track_visibility='always')
    department_id = fields.Many2one('hr.department', string="Department",required=True,related="job_position.department_id",
                                    help='Department of the employee',track_visibility='always')
    requested_by_id = fields.Many2one('res.users',string="Requested By",default=lambda self: self.env.user.id, limit=1,readonly=True,track_visibility='always')
    no_of_employee = fields.Integer(string="Number Of Position",track_visibility='always')
    reason_code_id = fields.Many2one('hr.reason.code',string="Purpose of Recruitment",track_visibility='always')
    
    state = fields.Selection([('draft', 'Draft'), 
                              ('approval', 'Approval Pending'),#added by Sangitarename approval to Approval Pending
                              ('approved','Approved'),
                              ('cancel','Cancel')],
                             string='Status', default='draft',track_visibility='always')
    description = fields.Text(string="Description",track_visibility='always')
    #added by sangita
    branch_id = fields.Many2one('res.branch',string="Center", store=True, default=lambda self: self.env.user.default_branch_id,track_visibility='always')
    
    user_id = fields.Many2one('res.users',string='Requesting Employee' ,default=lambda self: self.env.user.id,track_visibility='always')
    deadline_date =fields.Date(string='Expected Hiring Date',default=datetime.now().date(),track_visibility='always')
    date =fields.Date(string='Requisition Date', default=datetime.now().date(),track_visibility='always')
    # num_of_position = fields.Integer('Num of Position')

    recruitment_team_id = fields.Many2one('recruitment.team', string='Recruitment Team') 
    member_ids = fields.Many2many('res.users', string='Team Member')

    @api.onchange('job_position')
    def job_pos_get_des(self):
        for rec in self:
            rec.description = rec.job_position.description

    @api.onchange('branch_id')
    def set_job_position_domain(self):
        self.job_position = False
        domain = [('pay_level_id.group_id.code','in',['B','C']),('vacant_post', '>=', 1)]
        if self.branch_id and self.branch_id.name in ['New Delhi','Delhi']:
            domain = [('vacant_post', '>=', 1)]
        return {'domain':{'job_position':domain}}

    @api.model
    def create(self, vals):
        # assigning the sequence for the record
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.requisition') or _('New')
        res = super(HrRequisition, self).create(vals)
        return res
    
    @api.one
    def button_send_for_approval(self):
        for s in self:
            if s.no_of_employee <= 0:
                raise UserError(_('No of Employee Should greater then zero'))
            
            if s.state != 'draft':
                raise ValidationError("Requisition must be in Draft State")
            s.write({'state':'approval'})

    @api.one
    def button_approved(self):
        for s in self:
            s.write({'state':'approved'})

    @api.multi
    def cancel(self):
        rc = {
            'name': 'Reason for Revert',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('hr_employee_requisition.view_reason_revert_requisition_wizard').id,
            'res_model': 'revert.requisition.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_res_model': self._name,
                'default_res_id': self.id,
            }
        }
        return rc

class HrReasonCode(models.Model):
    _name = "hr.reason.code"
    _description = "Reason Code"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string="Name")