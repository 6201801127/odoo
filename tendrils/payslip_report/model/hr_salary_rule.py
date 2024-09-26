# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval

from odoo.addons import decimal_precision as dp

class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    appear_in_allowance = fields.Boolean(string="Appear in Allowance")


    @api.multi
    def _compute_rule(self, localdict):
        if self.amount_select not in  ('fix','percentage'):
            try:
                safe_eval(self.amount_python_compute, localdict, mode='exec', nocopy=True)
                return float(localdict['result']), 'result_qty' in localdict and localdict['result_qty'] or 1.0, 'result_rate' in localdict and localdict['result_rate'] or 100.0
            except:
                raise UserError(_('Wrong python code defined for salary rule %s (%s) for %s.') % (self.name, self.code,(localdict['employee']).name))
        res = super(HrSalaryRule, self)._compute_rule(localdict)
        return res