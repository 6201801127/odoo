# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta


class PayrollIncrement(models.Model):
    _name = 'payroll_increment'
    _description = 'Increment list of Employee'

    employee_id = fields.Many2one('hr.employee')
    increment_date = fields.Date()
    remark = fields.Text()
    state = fields.Selection([('open', 'Open'),('close', 'Close')],default='open')
    company_id = fields.Many2one('res.company')
    
    @api.onchange('employee_id')
    def onchange_employee_id(self):
            self.company_id = self.employee_id.company_id.id
    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state in ['close']:
                raise UserError(_('You cannot delete a data that is in %s state.') % (rec.state,))
        return super(PayrollIncrement, self).unlink()
    
    @api.constrains('employee_id', 'increment_date')
    def validate_allowance_allocation(self):
        for rec in self:
            record = self.env['payroll_increment'].sudo().search([]).filtered(lambda x:x.increment_date.year ==  rec.increment_date.year and x.increment_date.month == rec.increment_date.month and x.employee_id.id == rec.employee_id.id)  - self
            if record:
                raise ValidationError(
                    f"Duplicate entry found for {record.employee_id.emp_display_name}")
         
    
    # @api.model
    # def create(self, vals):
    #     record = super(PayrollIncrement, self).create(vals)
    #     if 'employee_id' in vals and 'increment_date' in vals:
    #         employee_id = vals['employee_id']
    #         increment_date =  datetime.strptime((vals['increment_date']), "%Y-%m-%d")
    #         expire_date =  increment_date - relativedelta(days=1)
    #         contract = self.env['hr.contract']
    #         search_contract = contract.search([('employee_id','=',employee_id),('state','=','open')])
    #         search_contract.write({'date_end':expire_date})
    #         create_contract = search_contract.copy()
    #         search_contract.write({'state':'close'})
    #         create_contract.write({'state':'open','date_start':increment_date})
    #         self.env.user.notify_success(message='Old contract is expired and the new one is created !')
    #     return record
    
    
    
class PayrollIncrementWizard(models.TransientModel):
    _name = 'payroll_increment_wizard'
    _description = "Payroll Employee's Increment"

    def _get_increment_data(self):
        employee_details_ids = self.env.context.get('selected_active_ids')
        res = self.env['payroll_increment'].sudo().search([('id', 'in', employee_details_ids),('state','=','open')])
        return res

    increment_ids = fields.Many2many('payroll_increment', 'payroll_increment_payroll_rel', 'payroll_id', 'contract_id', string='Employees',
                                   default=_get_increment_data)

    def btn_update_contract(self):
        if self.increment_ids:
            for val in self.increment_ids:
                if val.increment_date:
                    expire_date =  val.increment_date - relativedelta(days=1)
                    contract = self.env['hr.contract']
                    search_contract = contract.search([('employee_id','=',val.employee_id.id),('state','=','open')])
                    search_contract.write({'date_end':expire_date})
                    create_contract = search_contract.copy()
                    search_contract.write({'state':'close'})
                    create_contract.write({'state':'open','date_start':val.increment_date})
        self.env.user.notify_success(message='Salary computed successfully!.')