from odoo import models, fields, api, exceptions
from datetime import  datetime

class  HrEmployeeTransfer(models.Model):
    _name = "hr.employee.transfer"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Hr Employee Transfer'
    _rec_name='employee_id'

    employee_id = fields.Many2one('hr.employee',string='Employee')
    # from_location = fields.Many2one('res.partner', string='From Location', related ='employee_id.address_id')
    from_location = fields.Many2one('res.partner', string='From Location')
    to_location = fields.Many2one('res.partner', string='To Location')
    order_number = fields.Char(string='Order Number')
    order_date = fields.Date(string='Order Date')
    file_number = fields.Many2one('muk_dms.file', string='File Number')
    date = fields.Date(string='Date', default=datetime.now().date())
    transfer_attach = fields.Binary('Document',attachment=True)
    transfer_attach_filename = fields.Char('Document Filename')
    state = fields.Selection([
                                ('draft', 'Draft'),
                                ('approval', 'Approval'),
                                ('approved', 'Approved'),
                                ('rejected','Rejected')

                            ], default='draft')


    @api.multi
    def button_draft(self):
        for rec in self:
            rec.write({'state': 'approval'})

    @api.multi
    def button_approved(self):
        for rec in self:
            rec.write({'state': 'approved'})

    @api.multi
    def button_rejected(self):
        for rec in self:
            rec.write({'state': 'rejected'})



    @api.onchange('employee_id')
    def location_change(self):
        if self.employee_id:
            self.from_location = self.employee_id.address_id

