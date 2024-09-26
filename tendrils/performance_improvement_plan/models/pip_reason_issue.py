from odoo import models, fields, api


class PerformanceImprovementPlanReason(models.Model):
    _name = 'pip_reason_issue_config'
    _description = 'pip_reason_issue_config'
    _rec_name = "name"

    name = fields.Char(string="Reason", required=True)
    code = fields.Char(string="Code")
    status_active = fields.Boolean(string="Active",default=True)


class PIPUserAccess(models.Model):
    _name = 'pip_user_access'
    _description = 'PIP Raise User Access'

    designation_id = fields.Many2one('hr.job', string='Designation')
    grade_id = fields.Many2one('kwemp_grade_master', string='Grade')
    empl_id = fields.Many2many('hr.employee',string="Employee")

    def give_user_group_access(self, *args):
        record = self.env['pip_user_access'].search([])
        for rec in record:
            # emp_env_data = self.env['hr.employee'].sudo().search([('job_id','=',rec.designation_id.id)])
            emp_env_data = self.env['hr.employee'].sudo().search([('grade', '=', rec.grade_id.id)])
            emp_access_user = self.env['hr.employee'].sudo().search([('id','in',rec.empl_id.ids)])
            user_groups = self.env.ref('performance_improvement_plan.group_pip_user')
            if emp_env_data:
                for user in emp_env_data:
                    user = user.user_id
                    user.sudo().write({'groups_id': [(4, user_groups.id)]})
            if emp_access_user:
                for emp in emp_access_user:
                    user = emp.user_id
                    user.sudo().write({'groups_id': [(4, user_groups.id)]})
        return


class PIPManagerAccess(models.Model):
    _name = 'pip_manager_access'
    _description = 'PIP Manager Access'

    employee_id = fields.Many2one('hr.employee', string='Employee')

    def give_manager_group_access(self, *args):
        record = self.env['pip_manager_access'].search([])
        user_groups = self.env.ref('performance_improvement_plan.group_pip_manager')

        existing_users = user_groups.users
        mapped_users = record.mapped('employee_id')
        for usr in existing_users:
            # print('>>>>>>>>>>>>>>>>>>>  ', existing_users, mapped_users, usr.employee_ids)
            if usr.employee_ids.exists() and usr.employee_ids not in mapped_users:
                self.env['pip_manager_access'].sudo().create({'employee_id': usr.employee_ids.id})

        for rec in record:
            user = rec.employee_id.user_id
            if user.exists() and not user.has_group('performance_improvement_plan.group_pip_manager'):
                user.sudo().write({'groups_id': [(4, user_groups.id)]})
        return

    @api.multi
    def unlink(self):
        user_groups = self.env.ref('performance_improvement_plan.group_pip_manager')

        for rec in self:
            user = rec.employee_id.user_id
            # print('user >>>> ', user)
            if user.exists() and user.has_group('performance_improvement_plan.group_pip_manager'):
                user.sudo().write({'groups_id': [(3, user_groups.id)]})

        return super(PIPManagerAccess, self).unlink()
    
    
    
class PIPReportAccess(models.Model):
    _name = 'pip_report_access'
    _description = 'PIP Report Access'

    employee_id = fields.Many2one('hr.employee', string='Employee')

    def give_report_group_access(self, *args):
        record = self.env['pip_report_access'].search([])
        user_groups = self.env.ref('performance_improvement_plan.group_pip_mis_user')

        existing_users = user_groups.users
        mapped_users = record.mapped('employee_id')
        for usr in existing_users:
            if usr.employee_ids.exists() and usr.employee_ids not in mapped_users:
                self.env['pip_report_access'].sudo().create({'employee_id': usr.employee_ids.id})

        for rec in record:
            user = rec.employee_id.user_id
            if user.exists() and not user.has_group('performance_improvement_plan.group_pip_mis_user'):
                user.sudo().write({'groups_id': [(4, user_groups.id)]})
        return

    @api.multi
    def unlink(self):
        user_groups = self.env.ref('performance_improvement_plan.group_pip_mis_user')
        for rec in self:
            user = rec.employee_id.user_id
            if user.exists() and user.has_group('performance_improvement_plan.group_pip_mis_user'):
                user.sudo().write({'groups_id': [(3, user_groups.id)]})
        return super(PIPReportAccess, self).unlink()

class PIPnotifyOfficerAccess(models.Model):
    _name = 'pip_notify_officer_access'
    _description = 'PIP Officer Access'

    employee_id = fields.Many2one('hr.employee', string='Employee')

    def give_notify_officer_access(self, *args):
        record = self.env['pip_notify_officer_access'].search([])
        user_groups = self.env.ref('performance_improvement_plan.group_pip_officer')

        existing_users = user_groups.mapped('users')
        mapped_users = record.mapped('employee_id')
        for rec in existing_users:
            emp = self.env['hr.employee'].sudo().search([('user_id','=',rec.id)])
            if emp not in mapped_users:
                record.sudo().create({'employee_id':emp.id})
        # if existing_users :
        #     user_groups.users = [(3, user.id) for user in existing_users]
        if record :
            for rec in record:
                user = rec.employee_id.user_id
                if user.exists() and not user.has_group('performance_improvement_plan.group_pip_officer'):
                    user.sudo().write({'groups_id': [(4, user_groups.id)]})
        return
    # mapped_users = record.mapped('employee_id')
        # for usr in existing_users:
        #     if usr.employee_ids.exists() and usr.employee_ids not in mapped_users:
        #         self.env['pip_notify_officer_access'].create({'employee_id': usr.employee_ids.id})


    @api.multi
    def unlink(self):
        user_groups = self.env.ref('performance_improvement_plan.group_pip_officer')

        for rec in self:
            user = rec.employee_id.user_id
            # print('user >>>> ', user)
            if user.exists() and user.has_group('performance_improvement_plan.group_pip_officer'):
                user.sudo().write({'groups_id': [(3, user_groups.id)]})

        return super(PIPnotifyOfficerAccess, self).unlink()
    
    
    
class PIPnotifyLKAccess(models.Model):
    _name = 'pip_l_k_training_access'
    _description = 'PIP L&k  Access'

    employee_id = fields.Many2one('hr.employee', string='Employee')

    def give_notify_lk_access(self, *args):
        record = self.env['pip_l_k_training_access'].search([])
        user_groups = self.env.ref('performance_improvement_plan.group_pip_l_and_k')

        existing_users = user_groups.mapped('users')
        mapped_users = record.mapped('employee_id')
        
        if existing_users:
            for rec in existing_users:
                emp = self.env['hr.employee'].sudo().search([('user_id','=',rec.id)])
                if emp not in mapped_users:
                    record.sudo().create({'employee_id':emp.id})
        if record :
            for rec in record:
                user = rec.employee_id.user_id
                if user.exists() and not user.has_group('performance_improvement_plan.group_pip_l_and_k'):
                    user.sudo().write({'groups_id': [(4, user_groups.id)]})
        return
    
    @api.multi
    def unlink(self):
        user_groups = self.env.ref('performance_improvement_plan.group_pip_l_and_k')

        for rec in self:
            user = rec.employee_id.user_id
            # print('user >>>> ', user)
            if user.exists() and user.has_group('performance_improvement_plan.group_pip_l_and_k'):
                user.sudo().write({'groups_id': [(3, user_groups.id)]})

        return super(PIPnotifyLKAccess, self).unlink()
    
