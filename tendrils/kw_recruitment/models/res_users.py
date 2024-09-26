from odoo import models, fields,api
from ast import literal_eval

class Users(models.Model):
    _inherit = 'res.users'

    # helper methods

    def in_second_level_approval(self):
        result = False
        Parameters = self.env['ir.config_parameter'].sudo()
        second_approver_list = literal_eval(Parameters.get_param('kw_recruitment.second_level_approver_ids'))
        if self.employee_ids and self.employee_ids[-1] and \
            self.employee_ids[-1].id in second_approver_list:
            result = True
        return result
    
    def in_first_level_approval(self):
        result = False
        Parameters = self.env['ir.config_parameter'].sudo()
        first_approver_list = literal_eval(Parameters.get_param('kw_recruitment.first_level_approver_ids'))
        if self.employee_ids and self.employee_ids[-1] and \
                self.employee_ids[-1].id in first_approver_list:
            result = True
        return result

    def in_first_level_employee(self):
        result = False
        Parameters = self.env['ir.config_parameter'].sudo()
        approver_list = literal_eval(Parameters.get_param('kw_recruitment.employee_first_level_ids'))
        if self.employee_ids and self.employee_ids[-1] and \
            self.employee_ids[-1].id in approver_list:
            result = True
            # print('result', result)
        return result
    
    # def approval_ids_employee(self):
    #     result = False
    #     Parameters = self.env['ir.config_parameter'].sudo()
    #     approver_ids_list = literal_eval(Parameters.get_param('kw_recruitment.approval_ids'))
    #     if self.employee_ids and self.employee_ids[-1] and \
    #         self.employee_ids[-1].id in approver_ids_list:
    #         result = True
    #         print('result', result)
    #     return result
    
    # def notify_cc_employee(self):
    #     result = False
    #     Parameters = self.env['ir.config_parameter'].sudo()
    #     notify_cc_ids_list = literal_eval(Parameters.get_param('kw_recruitment.notify_cc_ids'))
    #     if self.employee_ids and self.employee_ids[-1] and \
    #         self.employee_ids[-1].id in notify_cc_ids_list:
    #         result = True
    #         print('result', result)
    #     return result
