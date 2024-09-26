from odoo import api, fields, models,_


class NonDocumentsWizard(models.TransientModel):
    _name = 'non.documents.wizard'
    _description = 'Pending Documents'

    date_range = fields.Many2one('date.range', string='Financial Year')
    branch_id = fields.Many2many('res.branch', string='Branch')

    def find_non_doc(self):
        if self:
            non_doc_rep = self.env['non.documents.report'].search([('branch_id', 'in', self.branch_id.ids),('date_range', '=', self.date_range.id)])
            for line in non_doc_rep:
                line.unlink()
            id_dec = self.env['hr.declaration'].search([('branch_id', 'in', self.branch_id.ids),('date_range', '=', self.date_range.id)])
            income_house_ids = []
            income_other_ids = []
            slab_ids = []
            med_ins_ids = []
            deduction_saving_ids = []
            tax_home_ids = []
            tax_education_ids = []
            rgess_ids = []
            dedmedical_ids = []
            dedmedical_self_ids = []
            for declaration in id_dec:
                for line in declaration.income_house_ids:
                    if not line.document:
                        income_house_ids.append(line.id)
                for line in declaration.income_other_ids:
                    if not line.document:
                        income_other_ids.append(line.id)
                for line in declaration.slab_ids:
                    if not line.document:
                        slab_ids.append(line.id)
                for line in declaration.med_ins_ids:
                    if not line.document:
                        med_ins_ids.append(line.id)
                for line in declaration.deduction_saving_ids:
                    if not line.document:
                        deduction_saving_ids.append(line.id)
                for line in declaration.tax_home_ids:
                    if not line.document:
                        tax_home_ids.append(line.id)
                for line in declaration.tax_education_ids:
                    if not line.document:
                        tax_education_ids.append(line.id)
                for line in declaration.rgess_ids:
                    if not line.document:
                        rgess_ids.append(line.id)
                for line in declaration.dedmedical_ids:
                    if not line.document:
                        dedmedical_ids.append(line.id)
                for line in declaration.dedmedical_self_ids:
                    if not line.document:
                        dedmedical_self_ids.append(line.id)
                if income_house_ids or income_other_ids or slab_ids or med_ins_ids or deduction_saving_ids or tax_home_ids or tax_education_ids or rgess_ids or dedmedical_ids or dedmedical_self_ids:
                    self.env['non.documents.report'].create({
                        'tds_id': declaration.id,
                        'employee_id': declaration.employee_id.id,
                        'branch_id': declaration.branch_id.id,
                        'date_range': self.date_range.id,
                        'income_house_ids': [(6,0,income_house_ids)],
                        'income_other_ids': [(6,0,income_other_ids)],
                        'slab_ids': [(6,0,slab_ids)],
                        'med_ins_ids': [(6,0,med_ins_ids)],
                        'deduction_saving_ids': [(6,0,deduction_saving_ids)],
                        'tax_home_ids': [(6,0,tax_home_ids)],
                        'tax_education_ids': [(6,0,tax_education_ids)],
                        'rgess_ids': [(6,0,rgess_ids)],
                        'dedmedical_ids': [(6,0,dedmedical_ids)],
                        'dedmedical_self_ids': [(6,0,dedmedical_self_ids)],
                    })
            return {
                'name': 'Pending Documents',
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'non.documents.report',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'domain': [('branch_id', 'in', self.branch_id.ids),('date_range', '=', self.date_range.id)],
            }