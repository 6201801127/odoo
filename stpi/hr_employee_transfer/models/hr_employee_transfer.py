from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError, UserError
from datetime import  datetime

class  HrEmployeeTransfer(models.Model):
    _name = "hr.employee.transfer"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'HR Employee Transfer'
    _rec_name='employee_id'

    employee_id =  fields.Many2one('hr.employee',string='Employee', store=True,track_visibility='always')
    job_id = fields.Many2one('hr.job', string="Functional Designation", store=True,track_visibility='always')
    branch_id = fields.Many2one('res.branch', string="Center", store=True,track_visibility='always')
    department_id = fields.Many2one('hr.department', string="Department", store=True,track_visibility='always')
    date_of_join = fields.Date('Date of Joining',track_visibility='always')
    emp_stages = fields.Selection([
        ('test_period', 'Probation'),
        ('employment', 'Employment'),
        ('notice_period', 'Notice Period'),
        ('relieved', 'Resigned'),
        ('terminate', 'Terminated'),
        ('retired', 'Retired'),
        ('suspended', 'Suspended'),
        ('superannuation', 'Superannuation'),
        ('deceased', 'Deceased'),
        ('absconding', 'Absconding'),
    ], string='Emplyement Status',track_visibility='always')

    transfer_to = fields.Many2one('res.branch', string='Transfer To',track_visibility='always')
    order_number = fields.Char(string='Order Number',track_visibility='always')
    order_date =  fields.Date(string='Order Date',track_visibility='always')
    file_number=  fields.Char(string='File Number',track_visibility='always')
    date   =  fields.Date(string='Date', default=datetime.now().date(),track_visibility='always')
    transfer_attach = fields.Binary('Document',track_visibility='always')
    emp_activity = fields.Many2many('mail.activity', string = 'Activity',track_visibility='always')

    state = fields.Selection([
                                ('draft', 'Draft'),
                                ('approval', 'Approval'),
                                ('approved', 'Approved'),
                                ('rejected','Rejected')

                            ], default='draft',track_visibility='always')


    @api.onchange('employee_id')
    @api.constrains('employee_id')
    def onchange_emo_get_basic(self):
        for record in self:
            record.job_id = record.employee_id.job_id
            record.branch_id = record.employee_id.branch_id
            record.department_id = record.employee_id.department_id
            record.date_of_join = record.employee_id.date_of_join
            record.emp_stages = record.employee_id.state
            serch_id = self.env['mail.activity'].search([('user_id', '=', self.employee_id.user_id.id)])
            record.emp_activity = serch_id.ids


    @api.multi
    def button_reset_to_draft(self):
        self.ensure_one()
        compose_form_id = self.env.ref('mail.email_compose_message_wizard_form').id
        ctx = dict(
            default_composition_mode='comment',
            default_res_id=self.id,

            default_model='hr.employee.transfer',
            default_is_log='True',
            custom_layout='mail.mail_notification_light'
        )
        mw = {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
        self.write({'state': 'draft'})
        return mw
    @api.multi
    def button_draft(self):
        for rec in self:
            rec.write({'state': 'approval'})

    @api.multi
    def button_approved(self):
        for rec in self:
            rec.employee_id.branch_id = rec.transfer_to.id
            rec.employee_id.address_id = rec.transfer_to.partner_id.id
            _body = (_(
                (
                    "Transfer has been approved by <b>{0}</b> ").format(self.write_uid.name)))
            rec.employee_id.message_post(body=_body)
            rec.write({'state': 'approved'})


    @api.multi
    def unlink(self):
        for transfer in self:
            if transfer.state != 'draft':
                raise UserError(
                    'You cannot delete a Transfer Order which is not in draft state')
        return super(HrEmployeeTransfer, self).unlink()


    @api.multi
    def button_rejected(self):
        for rec in self:
            rec.write({'state': 'rejected'})


    def button_assign_to(self):
        if self:
            return {
                'name': 'Employee Transfer',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'hr.employee.transfer.approve',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'view_id': self.env.ref('hr_employee_transfer.hr_employee_transfer_approve_form_view').id,
                'context': {
                    'default_employee_transfer_id': self.id,
                    'default_branch_id': self.branch_id.id,
                }
            }



class HrEmployee(models.Model):
    _inherit = 'hr.employee'


    transfers_count = fields.Integer('Transfers count', compute='_compute_transfer_count')


    def _compute_transfer_count(self):
        for line in self:
            comp_model = self.env['hr.employee.transfer'].search([('employee_id', '=', self.id),('state', '=', 'approved')])
            line.transfers_count = len(comp_model)


    def set_employee_transfer(self):
        tree_view_id = self.env.ref('hr_employee_transfer.employeetransfer_show_tree_view')
        return {
            'name': 'Employee Transfer',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'hr.employee.transfer',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'views': [(tree_view_id.id, 'tree')],
            'view_id': tree_view_id.id,
            'domain': [('employee_id', '=', self.id),('state', '=', 'approved')]
        }
