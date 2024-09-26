from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date, datetime, timedelta


class kw_adv_relaxation_wiz(models.TransientModel):
    _name = 'kw_advance_relaxation_wizard'
    _description = 'Relaxation period Wizard'

    salary_adv_id = fields.Many2one('kw_advance_apply_salary_advance', string="salary Adv Id", default=lambda self: self.env.context.get('current_rec_id'))
    relaxation_period = fields.Many2one('kw_advance_buffer_period_master',string='Relaxation Period')
    description = fields.Char(string='Description')
   
    @api.multi
    def get_relaxation(self):
        """ Add relaxation period and re-calculate EMI """
        # if not self.salary_adv_id.buffer_period:
        #     print("111111111111111111111111111111111111111111111111111111111111")
        #     self.salary_adv_id.delete_deduction_lines()
        unpaid_emi_list = []
        for line in self.salary_adv_id.deduction_line_ids:
            if line.principal_amt == 0.00 and line.status == 'draft':
                unpaid_emi_list.append(line.id)
        # print("unpaid_emi_list===",unpaid_emi_list)
        if len(unpaid_emi_list) > 0:
            raise ValidationError(f"You cannot apply for buffer as {len(unpaid_emi_list)} month's buffer interest is unpaid")

        self.salary_adv_id.sudo().write({
                    'buffer_period':self.relaxation_period.id,
                })
        self.salary_adv_id.calculate_emi()
        """ log for relaxation period """
        log = self.env['kw_advance_log_relaxation_period'].sudo().create({
                                    'relaxation_period': self.relaxation_period.id,
                                    'approved_on': date.today(),
                                    'salary_adv_id': self.salary_adv_id.id,
                                    'description': self.description,
                                    'approve_by':self.env.user.employee_ids.id,
                                    })