from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date, timedelta
import requests
import json

class EmployeeActionSelection(models.TransientModel):
    _name = 'employee.action.selection'
    _description = 'Wizard of Employee Selection'


    def show_my_profile(self):
        if self:
            my_ids = []
            employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)], limit=1)
            for emp in employee:
                my_ids.append(emp.id)
            print('==================my_ids========================', my_ids)
            form_view = self.env.ref('hr.view_employee_form')
            tree_view = self.env.ref('hr.view_employee_tree')
            value = {
                'domain': str([('id', 'in', my_ids)]),
                'view_type': 'form',
                'view_mode': 'tree, form',
                'res_model': 'hr.employee',
                'view_id': False,
                'views': [(form_view and form_view.id or False, 'form'),
                          (tree_view and tree_view.id or False, 'tree')],
                'type': 'ir.actions.act_window',
                'res_id': employee.id,
                'target': 'current',
                'nodestroy': True,
                'context':{'create':False,'edit':False}
            }
            return value



    def show_subordinates_profile(self):
        if self:
            my_ids = []
            employee = self.env['hr.employee'].sudo().search([])
            for emp in employee:
                if emp.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.parent_id.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.parent_id.parent_id.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.user_id.id == self.env.user.id or emp.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.parent_id.user_id.id == self.env.user.id:
                    my_ids.append(emp.id)
            print('==================my_ids========================', my_ids)
            return {
                'name': 'Subordinates Profile',
                'view_type': 'form',
                'view_mode': 'kanban,tree,form',
                'res_model': 'hr.employee',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'domain': [('id', 'in', my_ids)],
                }


    def employee_directory_branch(self):
        if self:
            my_ids = []
            my_employee_id = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)], limit=1)
            employee = self.env['hr.employee'].sudo().search([('branch_id', '=', my_employee_id.branch_id.id)])
            for emp in employee:
                my_ids.append(emp.id)
            print('==================my_ids========================', my_ids)
            return {
                'domain': [('id', 'in', my_ids)],
                'name': 'Employees Directory(Branch)',
                'view_type': 'form',
                'view_mode': 'kanban,tree,form',
                'res_model': 'hr.employee',
                'view_id': False,
                'views': [(self.env.ref('hr.hr_kanban_view_employees').id, 'kanban'),
                          (self.env.ref('groups_inherit.view_add_employee_doc_tree').id, 'tree'),
                          (self.env.ref('groups_inherit.view_add_Employee_doc_form').id, 'form')],
                'type': 'ir.actions.act_window'
            }


    def employee_directory_all(self):
        if self:
            my_ids = []
            employee = self.env['hr.employee'].sudo().search([])
            for emp in employee:
                my_ids.append(emp.id)
            # print('==================my_ids========================', my_ids)
            return {
                'name': 'Employees Directory',
                'view_type': 'form',
                'view_mode': 'kanban,tree,form',
                'res_model': 'hr.employee',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'domain': [('id', 'in', my_ids)],
                }


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):

        if self._context.get('branch_check'):
            args += [('branch_id','in',self.env.user.branch_ids.ids)]
                
        elif self._context.get('directory_all'):
            query = "select id from hr_employee"
            self._cr.execute(query)
            emp_records = self._cr.dictfetchall()
            datas = [record['id'] for record in emp_records]

            if datas:
                args += [('id','in',datas)]
        
        return super(HrEmployeeInherit, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
    
    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):

        if self._context.get('branch_check'):
            domain += [('branch_id','in',self.env.user.branch_ids.ids)]

        elif self._context.get('directory_all'):
            query = "select id from hr_employee"
            self._cr.execute(query)
            emp_records = self._cr.dictfetchall()
            datas = [record['id'] for record in emp_records]

            if datas:
                domain += [('id','in',datas)]

        return super(HrEmployeeInherit, self).read_group(domain, fields, groupby, offset=offset, limit=limit,orderby=orderby, lazy=lazy)
