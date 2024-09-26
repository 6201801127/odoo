from select import select
import string
from odoo import api, fields, models,_
from datetime import datetime

class UpdateUserWizard(models.TransientModel):
    _name = 'kw_update_user_wizard'
    _description = "Update User Wizard"


    # job_id = fields.Many2one('hr.job', string="Designation")
    # employee_ids = fields.Many2many('hr.employee', 'employee_ids_kw_update_user_wizard', 'employee_ids_id', 'rel_employee_ids', string="Employees")
    dept_head_ids = fields.Many2many('hr.employee', 'dept_head_ids_kw_update_user_wizard', 'dept_head_ids_id', 'rel_employee_ids', string="Department Heads")
    sbu_head_ids = fields.Many2many('hr.employee', 'sbu_head_ids_kw_update_user_wizard', 'sbu_head_ids_id', 'rel_employee_ids', string="SBU Representatives")
    update_group = fields.Selection([('sbu_hod', 'SBU/HOD'),('reviewer', 'Reviewer')],default='sbu_hod')
    division_id = fields.Many2one('kw_division_config',string='Division Id', default=lambda self: self._context.get('current_division_id'))
    reviewer = fields.Many2many('hr.employee', 'reviewer_kw_update_user_wizard', 'reviewer_id', 'rel_reviewer_id', string="Select Reviewer")
    existing_reviewer_ids = fields.Many2many('hr.employee', 'existing_reviewer_kw_update_user_wizard', 'existing_reviewer_id', 'rel_existing_reviewer', string="Existing Reviewer")
    existing_dept_head_ids = fields.Many2many('hr.employee', 'existing_dept_head_ids_kw_update_user_wizard', 'existing_dept_head_id', 'rel_dept_head_ids', string="Existing Department Heads in SBU/HOD group")
    existing_sbu_head_ids = fields.Many2many('hr.employee','existing_sbu_head_ids_kw_update_user_wizard', 'existing_sbu_head_id', 'rel_dept_head_ids', string="Existing SBU Representatives in SBU/HOD group")
    
    @api.onchange('update_group')
    def onchange_update_group(self):
        # self.employee_ids = False
        # self.job_id = False
        self.dept_head_ids = False
        self.div_head_ids = False
        employee = self.env['hr.employee']
        emp_ids = False
        department = self.env['hr.department']
        if self.update_group == 'sbu_hod':
            dept_employees = department.sudo().search([('dept_type.code','=','department')]).mapped('manager_id')
            div_employees = department.sudo().search([('dept_type.code','=','division')]).mapped('manager_id')
            sbu_employees = self.env['kw_sbu_master'].sudo().search([('type','=','sbu')]).mapped('representative_id')
            existing_dept =  dept_employees.mapped('user_id')
            existing_sbu =  sbu_employees.mapped('user_id')
            dpt_emp_users = existing_dept.filtered(lambda user: user.has_group('kw_reward_and_recognition.rnr_sbu')==True).mapped('employee_ids')
            sbu_emp_users = existing_sbu.filtered(lambda user: user.has_group('kw_reward_and_recognition.rnr_sbu')==True).mapped('employee_ids')
            self.dept_head_ids = dept_employees.ids
            self.sbu_head_ids = sbu_employees.ids
            self.existing_dept_head_ids = dpt_emp_users.ids
            self.existing_sbu_head_ids = sbu_emp_users.ids
            return {'domain': {'dept_head_ids': ([('id', 'in', dept_employees.ids)]),'sbu_head_ids': ([('id', 'in', sbu_employees.ids)]),'existing_sbu_head_ids': ([('id', 'in', sbu_emp_users.ids)]),'existing_dept_head_ids': ([('id', 'in', dpt_emp_users.ids)])}}
        
        if self.update_group == 'reviewer':
            users = self.env['res.users'].sudo().search([])
            emp_users = users.filtered(lambda user: user.has_group('kw_reward_and_recognition.rnr_reviewer')==True).mapped('employee_ids').ids
            self.existing_reviewer_ids = emp_users
            return {'domain': {'existing_reviewer_ids': [('id', 'in', emp_users)]}}    

            

    @api.multi
    def update_user_group(self):
        # """ for reporting authority/manager add to hr HOD group"""
        # if self.update_group == 'officer':
        #     if self.job_id and self.employee_ids:
        #         officer_group = self.env.ref('kw_reward_and_recognition.rnr_sbu', False)
        #         for emp_rec in self.employee_ids:
        #             if emp_rec.user_id:
        #                 officer_group.write({'users': [(4, emp_rec.user_id.id)]})
        #         self.env.user.notify_success("Users added to the Officer group")

        """ for reporting authority/manager add to hr HOD group"""
        if self.update_group == 'sbu_hod':
            rnr_group = self.env.ref('kw_reward_and_recognition.rnr_sbu', False)
            sbu_representative = self.env['kw_sbu_master'].sudo().search([('type','=','sbu')]).mapped('representative_id')
            dept_head = self.env['hr.department'].sudo().search([]).mapped('manager_id')
            all_users = sbu_representative + dept_head
            # sbu_representative = self.env['kw_sbu_master'].sudo().search([('type','=','sbu')]).mapped('representative_id')
            # dept_head = self.env['hr.department'].sudo().search([]).mapped('manager_id')
            # sbu_representative = self.sbu_head_ids
            # dept_head = self.dept_head_ids
            # all_users = sbu_representative if sbu_representative else [] + dept_head if dept_head else []

            if all_users:
                for emp_rec in all_users:
                    if emp_rec.user_id:
                        rnr_group.write({'users': [(4, emp_rec.user_id.id)]})
                self.env.user.notify_success("Users added to the SBU group")
        
        """ Add to reviewer group """
        if self.update_group == 'reviewer':
            rnr_review_group = self.env.ref('kw_reward_and_recognition.rnr_reviewer', False)
            reviewer = self.reviewer
            if reviewer:
                for rev in reviewer:
                    if rev.user_id:
                        rnr_review_group.write({'users': [(4, rev.user_id.id)]})
                self.env.user.notify_success("Users added to the Reviewer group")





