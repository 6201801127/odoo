from odoo import api, fields, models, _


class TotalResourceWizard(models.TransientModel):
    _name = 'total.resouce.wizard'
    _description = 'Total Resource Wizard'

    financial_year_id = fields.Many2one('account.fiscalyear', 'Fiscal Year')

    @api.multi
    def wizard_fiscal_year(self):
        name = str('Total Resource vs CTC') + '(' + str(self.financial_year_id.name) + ')'
        list_name = ['CSM Technologies', 'Contractual', 'Outsourced Other', 'Outsourced kwantify']
        resource = self.env['hr.mis.total.resource.vs.ctc']
        resource_rec = resource.sudo().search([])
        # print('resourceresource', resource, resource_rec)
        res_list = []
        if resource_rec:
            for rec in resource_rec:
                res_list.append(rec.name)
        # print('res_list', res_list)
        for rec_name in list_name:
            # print('rec_name',rec_name, res_list)
            if rec_name not in res_list:
                resource.create({'name': rec_name,
                    'financial_year_id': self.financial_year_id.id})

        return {
            'type': 'ir.actions.act_window',
            'name': name,
            'res_model': 'hr.mis.total.resource.vs.ctc',
            'domain': [('financial_year_id', '=', self.financial_year_id.id)],
            'view_mode': 'tree',
            'target': 'main',
            'context': {'default_financial_year_id': self.financial_year_id.id}
        }
