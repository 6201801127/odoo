from odoo import fields,api,models


class NonDocumentsReport(models.Model):
    _name="non.documents.report"
    _description="Non Documents Report"

    employee_id = fields.Many2one('hr.employee', string='Requested By')
    branch_id = fields.Many2one('res.branch', string="Branch", store=True)
    tds_id = fields.Many2one('hr.declaration', string="Declaration")
    date_range = fields.Many2one('date.range', string='Date Range')

    income_house_ids = fields.Many2many('income.house',string='Income from House Property')
    income_other_ids = fields.Many2many('income.other', string='Income from Other Sources')
    slab_ids = fields.Many2many('declaration.slab', string='Slab 80 Ids')
    med_ins_ids = fields.Many2many('declaration.medical', string='Medical Insurance Premium paid ')
    deduction_saving_ids = fields.Many2many('declaration.deduction', string='Deductions on Interest on Savings Account')
    tax_home_ids = fields.Many2many('declaration.taxhome', string='Tax Benefits on Home Loan')
    tax_education_ids = fields.Many2many('declaration.taxeducation', string='Tax benefit on Education Loan (80E)')
    rgess_ids = fields.Many2many('declaration.rgess', string='Deductions on Rajiv Gandhi Equity Saving Scheme')
    dedmedical_ids = fields.Many2many('declaration.dedmedical', string='Deductions on Medical Expenditure for a Handicapped Relative')
    dedmedical_self_ids = fields.Many2many('declaration.dedmedicalself', string='Deductions on Medical Expenditure on Self or Dependent Relative')


    @api.multi
    def action_view_declaration(self):
        form_view = self.env.ref('tds.hr_declaration_form_view')
        tree_view = self.env.ref('tds.hr_declaration_tree_view')
        value = {
            'domain': str([('id', '=', self.tds_id.id)]),
            'view_type': 'form',
            'view_mode': 'tree, form',
            'res_model': 'hr.declaration',
            'view_id': False,
            'views': [(form_view and form_view.id or False, 'form'),
                      (tree_view and tree_view.id or False, 'tree')],
            'type': 'ir.actions.act_window',
            'res_id': self.tds_id.id,
            'target': 'current',
            'nodestroy': True
        }
        return value
