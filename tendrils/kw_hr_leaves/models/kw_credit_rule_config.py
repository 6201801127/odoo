from odoo import models, fields, api
from odoo.exceptions import ValidationError
from dateutil import relativedelta


class KwCreditRuleConfig(models.Model):
    _name           = 'kw_credit_rule_config'
    _description    = "Credit Rule Configurations"
    _rec_name       = "credit_rule"

    credit_rule     = fields.Char(string="Credit Rule", required=True)
    rule_ids        = fields.One2many('kw_credit_rules', 'credit_rules_ids')
    # leave_type_id   = fields.Many2many(
    #     'hr.leave.type', string="Applicable to", required=True)

    # _sql_constraints = [
    #     ('leave_type_uniq', 'unique(leave_type_id)',
    #      'The leave type must be unique!'),
    # ]


    @api.constrains('rule_ids')
    def validate_day_range(self):
        for record in self:
            if record.rule_ids:
                for rule in record.rule_ids:
                    new_rule = record.rule_ids - rule
                    if rule.from_day and rule.to_day:
                        new_rules = new_rule.filtered(
                            lambda rec: rec.from_day != False and rec.to_day != False)
                        n_rule = new_rule.filtered(
                            lambda r: ((r.from_day <= rule.from_day <= r.to_day) or (r.from_day <= rule.to_day <= r.to_day)))
                        if n_rule:
                            raise ValidationError(
                                "Day duration overlaps with others. Please modify it.")

    
    @api.constrains('credit_rule', 'rule_ids')
    def validate_rule(self):
        for data in self:
            if data.credit_rule and not data.rule_ids:
                raise ValidationError(
                    "The rules should have atleat one record .")


class KwCreditRules(models.Model):
    _name = 'kw_credit_rules'
    _description = 'Leave Credit Rules'

    credit_rules_ids    = fields.Many2one('kw_credit_rule_config', string='rules')
    from_day            = fields.Integer(string='From Day')
    to_day              = fields.Integer(string='To Day')
    percentage          = fields.Float(string='Percentage')


    @api.multi
    def name_get(self):
        result = []
        for record in self:
            record_name = f"{record.from_day} - { record.to_day } : {record.percentage}"
            result.append((record.id, record_name))
        return result

    @api.constrains('from_day')
    def check_from_day(self):
        for record in self:
            if record.from_day > 31:
                raise ValidationError("From day should not be greater than 31.")
            elif record.from_day < 1:
                raise ValidationError("From day should be greater than 0.")

    @api.constrains('to_day')
    def check_to_day(self):
        for record in self:
            if record.to_day > 31 :
                raise ValidationError(
                    "To day should not be greater than 31.")
            elif record.to_day < 1 :
                raise ValidationError(
                    "To day should be greater than 0.")

    @api.constrains('percentage')
    def check_percentage(self):
        for record in self:
            if record.percentage > 100 or record.percentage < 0.00:
                raise ValidationError("Percentage can not be more than 100 or less than 0.")
    @api.constrains('from_day', 'to_day')
    def validate_day(self):
        for record in self:
            if record.from_day > record.to_day:
                raise ValidationError(f'From day should not greater than To Day : {record.from_day} > {record.to_day}.')


    get_quantity = lambda self,lpm,rm : (lpm * rm) + (lpm * self.percentage)
    
  