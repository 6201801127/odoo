from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ReviseAmountWizard(models.TransientModel):
    _name = 'revise_amount_wizard'
    _description = 'Revise Amount Wizard'

    record_id = fields.Many2one('transfer_project_budget_amounts', string='Record')
    source_month = fields.Selection([
        ('apr', 'Apr'),
        ('may', 'May'),
        ('jun', 'Jun'),
        ('jul', 'Jul'),
        ('aug', 'Aug'),
        ('sep', 'Sep'),
        ('oct', 'Oct'),
        ('nov', 'Nov'),
        ('dec', 'Dec'),
        ('jan', 'Jan'),
        ('feb', 'Feb'),
        ('mar', 'Mar'),
    ], string='Source Month', required=True)
    source_month_amt = fields.Float("Orginal Amount",compute="_compute_sourec_month_amount")
    destination_month = fields.Selection([
        ('apr', 'Apr'),
        ('may', 'May'),
        ('jun', 'Jun'),
        ('jul', 'Jul'),
        ('aug', 'Aug'),
        ('sep', 'Sep'),
        ('oct', 'Oct'),
        ('nov', 'Nov'),
        ('dec', 'Dec'),
        ('jan', 'Jan'),
        ('feb', 'Feb'),
        ('mar', 'Mar'),
    ], string='Destination Month')
    transfer_amount = fields.Float('Reallocation Amount')
    revise_amount_destination_wizard_ids = fields.One2many('revise_amount_destination_wizard', 'revise_amount_wizard_id', string="Destination Months", required=True)

    @api.depends('source_month')
    def _compute_sourec_month_amount(self):
        for rec in self:
            if rec.source_month:
                month_field = rec.source_month + '_budget_org'
                rec.source_month_amt = getattr(rec.record_id, month_field, 0.0)
            else:
                rec.source_month_amt = 0.0

    # @api.onchange('transfer_amount')
    # def onchange_transfer_amount(self):
    #     if self.source_month_amt:
    #         if self.source_month_amt < self.transfer_amount:
    #             raise ValidationError('Transfer amount is higher then the available amount in source month.')
            

    @api.model
    def default_get(self, fields):
        res = super(ReviseAmountWizard, self).default_get(fields)
        if self.env.context.get('active_id'):
            record = self.env['transfer_project_budget_amounts'].browse(self.env.context['active_id'])
            res.update({
                'record_id': record.id,
            })
        return res

    def revise_amount(self):
        if not self.record_id:
            raise ValidationError('Please select a record to revise amounts.')
        check_am = 0.0
        for line in self.revise_amount_destination_wizard_ids:
            if line.destination_month == self.source_month:
                raise ValidationError('Source and destination months cannot be the same.')
            check_am += line.amount
            if check_am > self.source_month_amt:
                raise ValidationError('Reallocation Amount is higher than the available amount in source month.')

        # if self.source_month == self.destination_month:
        #     raise ValidationError('Source and destination months cannot be the same.')
        # if self.transfer_amount > self.source_month_amt:
        #     raise ValidationError('Transfer amount is higher then the available amount in source month. ')

        source_rev_field = self.source_month + '_budget_rev'
        # dest_rev_field = self.destination_month + '_budget_rev'

        transfer_amount =  0.0
        for months in self.revise_amount_destination_wizard_ids:
            dest_rev_field = months.destination_month + '_budget_rev'
            transfer_amount += months.amount

            self.record_id.write({
                'state': 'applied',
                dest_rev_field: months.amount,
                source_rev_field: -transfer_amount
            })

class ReviseAmountDestinationWizard(models.TransientModel):
    _name = 'revise_amount_destination_wizard'
    _description = 'Revise Amount Destinantion Wizard'


    destination_month = fields.Selection([
        ('apr', 'Apr'),
        ('may', 'May'),
        ('jun', 'Jun'),
        ('jul', 'Jul'),
        ('aug', 'Aug'),
        ('sep', 'Sep'),
        ('oct', 'Oct'),
        ('nov', 'Nov'),
        ('dec', 'Dec'),
        ('jan', 'Jan'),
        ('feb', 'Feb'),
        ('mar', 'Mar'),
    ], string='Destination Month')
    amount = fields.Float('Reallocation Amount')
    revise_amount_wizard_id = fields.Many2one('revise_amount_wizard', 'wizard_id')



class ApproveRevisionWizard(models.TransientModel):
    _name = 'approve_revision_wizard'
    _description = 'Approve Revision Wizard'

    record_id = fields.Many2one('transfer_project_budget_amounts', string='Record', required=True)
    remarks = fields.Text('Remarks')

    def approve_revision(self):
        for record in self:
            
            record.record_id.write({
                'state': 'approved',
                'remarks' : self.remarks,
                "has_revised_amounts": False
            })

    def cancel_revision(self):
        for record in self:
            record.record_id.write({
                'state': 'cancel',
                'remarks': self.remarks,
                "has_revised_amounts": False
            })


