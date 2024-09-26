import math, random, string
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError



class PayslipOTPvalidation(models.TransientModel):
    _name = 'payslip_otp'
    _description = 'Payslip OTP Validation'

    user_otp = fields.Char(string="OTP")

    @api.multi
    def validate_payslip_otp(self):
        exist_otp = self.env['payslip_otp_log'].sudo().search([('employee_id','=',self.env.user.employee_ids.id)],order="id desc",limit=1)
        # print('otp=========>',exist_otp.otp,self.user_otp)
        if exist_otp:
            if exist_otp.otp != self.user_otp:
                raise ValidationError("Invalid OTP.")
            else:
                action = {
                    'name':'My Payslip',
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'tree',
                    'res_model': 'hr.payslip',
                    'domain': [('employee_id.user_id','=',self.env.uid),('state','=','done')],
                    'context': {'create': False, 'edit': False, 'delete': False,'import':False},
                    'target': 'self',
                }
                # print('self.env.user.company_id.parent_id==============',self.env.user.company_id.parent_id.name)
                if not self.env.user.company_id.parent_id:
                    view_id = self.env.ref('payroll_inherit.user_payroll_tree_view').id
                    action['views'] = [(view_id, 'tree')]
                    action['view_id'] = view_id
                    return action
                else:
                    sub_view_id = self.env.ref('payroll_inherit.kenya_user_payroll_tree_view').id
                    action['views'] = [(sub_view_id, 'tree')]
                    action['view_id'] = sub_view_id
                    return action
                    
        else:
            pass
class PayslipOTPLog(models.Model):
    _name = 'payslip_otp_log'
    _description = 'Payslip OTP Log Report'

    employee_id = fields.Many2one('hr.employee', string="Employee")
    otp = fields.Char(string="OTP")

