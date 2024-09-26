from odoo import models, fields, api, exceptions


class HealthInsuranceConfiguration(models.Model):
    _name = 'health_insurance_configuration'
    _description = "Health Insurance Configuration"
    _rec_name = 'name'

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    value = fields.Integer(string="Value")

    @api.multi
    def write(self, values):
        res = super(HealthInsuranceConfiguration, self).write(values)
        if self.code == 'EC':
            data = self.env['health_insurance_dependant'].sudo().search([])
            for dataa in data:
                if dataa.state == 'draft' or dataa.state == 'applied':
                    amt = dataa.amount_ - int(values["value"])
                    dataa.sudo().write({
                        'employeer_contribution': int(values["value"]),
                        'employee_contribution': amt,
                        'insurance_amount': amt,
                    })
        if self.code == 'IC':
            recc = self.env['health_insurance_dependant'].sudo().search([])
            for rec in recc:
                if rec.state == 'draft' or rec.state == 'applied':
                    totall = 0
                    amountt = 0
                    for data in rec.family_details_ids:
                        totall += data.insurance_amount
                    rec.total_insurance_amount = False
                    amountt += rec.insurance_amount
                    if values["value"] == 1:
                        rec.total_insurance_amount = totall
                    elif values["value"] == 2:
                        rec.total_insurance_amount = amountt
        return res
