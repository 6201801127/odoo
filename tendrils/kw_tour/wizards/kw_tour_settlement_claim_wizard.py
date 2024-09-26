from datetime import date
import pytz
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class TourSettlementClaimWizard(models.TransientModel):
    _name                   = 'kw_tour_settlement_claim_wizard'
    _description            = "Tour Settlement Claim Wizard"

    def _default_tour_id(self):
        return self.env['kw_tour_settlement'].browse(self._context.get('active_id')).tour_id

    def _default_settlement_id(self):
        return self.env['kw_tour_settlement'].browse(self._context.get('active_id'))

    tour_id                 = fields.Many2one("kw_tour", string="Tour for Claim Settlement",default=_default_tour_id)
    
    employee_id             = fields.Many2one("hr.employee", string="Applied By",related="tour_id.employee_id")

    settlement_id           = fields.Many2one('kw_tour_settlement', string="Settlement",default=_default_settlement_id)

    status                  = fields.Selection(string="Status",
                                            selection=[('Draft', 'Draft'),
                                                        ('Applied', 'Applied'),
                                                        ('Forwarded', 'Forwarded'),
                                                        ('Approved', 'Approved'),
                                                        ('Paid', 'Paid'),
                                                        ('Rejected', 'Rejected')
                                                        ], related="settlement_id.state")
                                         
    date                    = fields.Date(string="Date", related="settlement_id.applied_date")

    department_id           = fields.Many2one('hr.department', string="Department", related="tour_id.employee_id.department_id")
    child_id                = fields.Many2one('hr.department',string="Section")

    tour_type_id            = fields.Many2one('kw_tour_type',string="Type Of Tour",related="tour_id.tour_type_id")
    project_id              = fields.Many2one('project.project', string='Project', related="tour_id.project_id")

    tour_detail_ids         = fields.One2many(string="Tour Details", related="tour_id.tour_detail_ids")
    settlement_detail_ids   = fields.One2many(string="Expenditure Details", related="settlement_id.settlement_detail_ids")

    total_domestic          = fields.Float(string="Total Domestic",compute="compute_total")
    total_international     = fields.Float(string="Total International",compute="compute_total")

    advance_domestic        = fields.Float(string="Advance Domestic",related="tour_id.advance")
    advance_international   = fields.Float(string="Advance International",related="tour_id.advance_usd")
    
    paid_domestic           = fields.Float(string="Total Domestic",compute="compute_total")
    paid_international      = fields.Float(string="Total International",compute="compute_total")

    action_log_ids          = fields.One2many(string="Action Logs", related="settlement_id.action_log_ids")

    @api.depends('settlement_detail_ids')
    @api.multi
    def compute_total(self):
        for claim in self:

            domestic        = claim.settlement_detail_ids.filtered(lambda r:r.currency_id.name=="INR")
            international   = claim.settlement_detail_ids.filtered(lambda r:r.currency_id.name=="USD")

            claim.total_domestic        = domestic and sum(domestic.mapped('amount_claiming')) or 0
            claim.total_international   = international and sum(international.mapped('amount_claiming')) or 0

            claim.paid_domestic         = claim.total_domestic - claim.advance_domestic
            claim.paid_international    = claim.total_international - claim.advance_international