# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrContract(models.Model):
    """
    Employee contract based on the visa, work permits
    allows to configure different Salary structure
    """
    _inherit = 'hr.contract'
    _description = 'Employee Contract'

    struct_id = fields.Many2one('hr.payroll.structure', string='Salary Structure / वेतन संरचना')
    schedule_pay = fields.Selection([
        ('monthly', 'Monthly / मासिक'),
        ('quarterly', 'Quarterly / त्रैमासिक'),
        ('semi-annually', 'Semi-annually / अर्द्ध वार्षिक'),
        ('annually', 'Annually / प्रतिवर्ष'),
        ('weekly', 'Weekly / साप्ताहिक'),
        ('bi-weekly', 'Bi-weekly / द्वि-साप्ताहिक'),
        ('bi-monthly', 'Bi-monthly / द्विमासिक'),
    ], string='Scheduled Pay / अनुसूचित वेतन', index=True, default='monthly',
    help="Defines the frequency of the wage payment. / मजदूरी भुगतान की आवृत्ति को परिभाषित करता है।")
    resource_calendar_id = fields.Many2one(required=True, help="Employee's working schedule. / कर्मचारी के काम का शेड्यूल।")
    hra = fields.Monetary(string='HRA / मकान किराया भत्ता', help="House rent allowance. / मकान किराया भत्ता।")
    travel_allowance = fields.Monetary(string="Travel Allowance / यात्रा भत्ता", help="Travel allowance / यात्रा भत्ता")
    da = fields.Monetary(string="DA / महंगाई भत्ता", help="Dearness allowance / महंगाई भत्ता")
    meal_allowance = fields.Monetary(string="Meal Allowance / भोजन भत्ता", help="Meal allowance / भोजन भत्ता")
    medical_allowance = fields.Monetary(string="Medical Allowance / चिकित्सा भत्ता", help="Medical allowance / चिकित्सा भत्ता")
    other_allowance = fields.Monetary(string="Other Allowance / अन्य भत्ता", help="Other allowances / अन्य भत्ते")
    city_tier = fields.Selection([('a', 'A'),
                                  ('a1', 'A1'),
                                  ('other', 'Other'),
                                  ], string='City Tier',  store=True)
    employee_hra_cat = fields.Selection([('x', 'X'),
                                         ('y', 'Y'),
                                         ('z', 'Z'),
                                         ], string='HRA Category', store=True)
    pay_level_id = fields.Many2one('hr.payslip.paylevel', string='Pay Level')
    pay_level = fields.Many2one('payslip.pay.level', string='Pay Cell', track_visibility='onchange')

    # @api.depends('employee_id')
    # def compute_hra_tier(self):
    #     for rec in self:
    #         # rec.city_id = rec.employee_id.branch_id.city_id.id
    #         rec.employee_hra_cat = rec.employee_id.branch_id.city_id.employee_hra_cat
    #         rec.city_tier = rec.employee_id.branch_id.city_id.city_tier

    def get_all_structures(self):
        """
        @return: the structures linked to the given contracts, ordered by hierachy (parent=False first,
                 then first level children and so on) and without duplicata
        """
        structures = self.mapped('struct_id')
        if not structures:
            return []
        # YTI TODO return browse records
        return list(set(structures._get_parent_structure().ids))

    def get_attribute(self, code, attribute):
        return self.env['hr.contract.advantage.template'].search([('code', '=', code)], limit=1)[attribute]

    def set_attribute_value(self, code, active):
        for contract in self:
            if active:
                value = self.env['hr.contract.advantage.template'].search([('code', '=', code)], limit=1).default_value
                contract[code] = value
            else:
                contract[code] = 0.0

    def write(self, values):
        if 'state' in values:
            previous_state = self.state
            new_state = values.get('state')
            if (new_state in ['draft','open','close','cancel']) and (not self.env.user.has_group('hr.group_hr_manager')):
                raise ValidationError(_("Only Managers can change contract stage!"))
        return super(HrContract, self).write(values)

class HrContractAdvantageTemplate(models.Model):
    _name = 'hr.contract.advantage.template'
    _description = "Employee's Advantage on Contract"

    name = fields.Char('Name / नाम', required=True)
    code = fields.Char('Code / कोड', required=True)
    lower_bound = fields.Float('Lower Bound / निम्न परिबंध', help="Lower bound authorized by the employer for this advantage / इस लाभ के लिए नियोक्ता द्वारा अधिकृत निचली सीमा")
    upper_bound = fields.Float('Upper Bound / ऊपरी सीमा', help="Upper bound authorized by the employer for this advantage / इस लाभ के लिए नियोक्ता द्वारा अधिकृत ऊपरी सीमा")
    default_value = fields.Float('Default value for this advantage / इस लाभ के लिए डिफ़ॉल्ट मान')
