from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime


class SBUProjectMapping(models.Model):
    _name = 'kw_sbu_project_mapping'
    _description = "Mapping SBU Project budget"
    _rec_name = 'sbu_id'

    sbu_id = fields.Many2one(comodel_name="kw_sbu_master", string="SBU", required=True)
    level_1_approver = fields.Many2many('hr.employee','kw_sbu_approver_l1_rel','employee_id','sbu_emp_id',string="1st Level Compiler", required=True)
    level_2_approver = fields.Many2many('hr.employee','kw_sbu_approver_l2_rel','employee_id','sbu_emp_id',string="2nd Level Finalization", required=True)
    active = fields.Boolean(string='Active', default=True)
    fiscal_year_id = fields.Many2one('account.fiscalyear', string="Fiscal Year")

  
    @api.constrains('sbu_id')
    def _check_duplicate_sbu_id(self):
        current_fiscal = self.env['account.fiscalyear'].search(
            [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
        for record in self:
            duplicate_records = self.search([
                ('sbu_id', '=', record.sbu_id.id),
                ('id', '!=', record.id),
                ('fiscal_year_id', '=', current_fiscal.id),
            ])
            if duplicate_records:
                raise ValidationError("Duplicate  SBU name is not allowed!")

    @api.model
    def _update_project_group_users(self):
        user_ids = set()  # Use a set to store unique user IDs
        current_fiscal = self.env['account.fiscalyear'].search(
            [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])

        sbu_projects = self.env['kw_sbu_project_mapping'].search([('fiscal_year_id', '=', current_fiscal.id)])

        for rec in sbu_projects:
            user_ids.update(emp.user_id.id for emp in rec.level_1_approver)
            user_ids.update(emp.user_id.id for emp in rec.level_2_approver)

        user_ids_list = list(user_ids)  # Convert set back to list for group updates

        # Update both groups in a single call each
        group_department_head = self.env.ref('kw_budget.group_department_head_kw_budget').sudo()
        group_department_head.write({'users': [(6, 0, user_ids_list)]})

        group_sbu_user = self.env.ref('kw_budget.group_sbu_budget_user_kw_budget').sudo()
        group_sbu_user.write({'users': [(6, 0, user_ids_list)]})

    @api.model
    def create(self, vals):
        record = super(SBUProjectMapping, self).create(vals)
        self._update_project_group_users()
        return record

    @api.multi
    def write(self, vals):
        res = super(SBUProjectMapping, self).write(vals)
        print(vals, 'ppppppppppppppppp')
        self._update_project_group_users()
        return res

    # @api.multi
    # def unlink(self):
    #     res = super(SBUProjectMapping, self).unlink()
    #     self._update_project_group_users()
    #     return res
