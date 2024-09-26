from odoo import fields, models, api, _

class InheritBank(models.Model):
    _inherit = 'hr.employee.document'

    name = fields.Selection([('me', 'Medical Examination'), ('ca', 'Character & Antecedents'), ('atc', 'Allegiance to the Constitution'), ('os', 'Oath of secrecy'), ('cps', 'Confirmation in post after successful completion of probation period')], string='Document Number', required=True, copy=False, help='You can give your'
                                                                                 'Document number.')

    @api.constrains('name')
    @api.onchange('name')
    def onchange_name_get_description(self):
        for record in self:
            if record.name == 'me':
                record.description = 'The employee was medically examined on _______________ and found fit. The original medical certificate has been kept in safe custody vide Sl. No. _____ & Page No. _____ of Vol. II of the Service Book.'
            elif record.name == 'ca':
                record.description = 'His/her'
            elif record.name == 'atc':
                record.description = ''
            elif record.name == 'os':
                record.description = ''
            elif record.name == 'cps':
                record.description = ''
            else:
                record.description = ''