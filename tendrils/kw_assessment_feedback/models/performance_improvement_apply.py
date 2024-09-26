# -*- coding: utf-8 -*-
from datetime import datetime,timedelta
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime,date

class kw_performance_improvement(models.Model):
    _name           = 'kw_feedback_assessment_pip'
    _description    = 'Performance Improvement Plan'
    _rec_name       = 'sequence'

    sequence= fields.Char(string='Code', readonly=True,default='New')
    employee_id = fields.Many2one('hr.employee', 'Employee')
    emp_desgination=fields.Char('Designation',related='employee_id.job_id.name')
    emp_department=fields.Char('Department',related='employee_id.department_id.name')
    emp_project=fields.Char('Project',related='employee_id.emp_project_id.name')
    # emp_project_manager=fields.Many2one('project.project','PM/HOD',related='emp_project.emp_id')
    # emp_sbu=fields.Char('SBU',related='employee_id.sbu_master_id.name')
    comment = fields.Text('Feedback')
    requested_by = fields.Many2one('hr.employee', string="Request Raised By", readonly=True, default=lambda self:  self.env.user.employee_ids)
    requested_on = fields.Datetime(string="Request Raised On", readonly=True, default=lambda self: fields.Datetime.now())
    state = fields.Selection(
        [
        ('draft', 'Draft'), 
        ('submitted', 'Submitted'), 
        ('inprogress', 'In Progress'), 
        ('closed', 'Closed')], string='Status',required=True, default='draft', readonly=True)

    log_ids = fields.One2many('assessment_pip_employee', 'emp_id', string='Approval Details')

    
   


    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('self.kw_feedback_assessment_pip') or '/'
        vals['sequence'] = seq
        return super(kw_performance_improvement, self).create(vals)

    def action_submit(self):
        form_view_id = self.env.ref("kw_assessment_feedback.performance_submit_remarks_wizard_form_view").id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Submit Confirmation Wizard',
            'res_model': 'performance_submit_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view_id,
            'target': 'new',
        }    

    @api.multi
    def action_approve(self):
        form_view_id = self.env.ref("kw_assessment_feedback.performance_approve_remarks_wizard_form_view").id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Approve Remark Wizard',
            'res_model': 'performance_approve_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view_id,
            'target': 'new',
        }

    def action_close(self):
        form_view_id = self.env.ref("kw_assessment_feedback.performance_close_remarks_wizard_form_view").id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Clsoe Remark Wizard',
            'res_model': 'performance_close_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view_id,
            'target': 'new',
        }  


    def action_update(self):
        form_view_id = self.env.ref("kw_assessment_feedback.performance_update_remarks_wizard_form_view").id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Update Remark Wizard',
            'res_model': 'performance_update_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view_id,
            'target': 'new',
        }  


        


class PerformanceSubmitWizard(models.TransientModel):
    _name = "performance_submit_wizard"
    _description = "Performance Submit Wizard"

    # remark = fields.Text('Remark',track_visibility='onchange')
    current_datetime = datetime.now()


    @api.multi
    def action_done(self):
        a = self.env['kw_feedback_assessment_pip'].browse(self.env.context.get('active_id'))
        
        template_id = a.env.ref('kw_assessment_feedback.performance_submit_mail_template')
        users = self.env['res.users'].sudo().search([])
        manager = users.filtered(lambda user: user.has_group('kw_assessment_feedback.group_assessment_feedback_manager') == True)
        email_to = ','.join(manager.mapped('email'))
        email_cc = a.requested_by.work_email
        name = ','.join(manager.mapped('name'))
        template_id.with_context(email_to=email_to,email_cc=email_cc,name=name).send_mail(a.id,notif_layout="kwantify_theme.csm_mail_notification_light")
        a.write({'state': 'submitted'})
        a.log_ids = [[0,0,{
            'employee_name': a.env.user.employee_ids.id,
            'comment': a.comment,
            'state': a.state,
            'date': self.current_datetime,
        }
        ]]
        


class PerformanceApproveWizard(models.TransientModel):
    _name = "performance_approve_wizard"
    _description = "Performance Approve Wizard"

    remark = fields.Text('Remark',track_visibility='onchange')
    current_datetime = datetime.now()


    @api.multi
    def action_done(self):
        a = self.env['kw_feedback_assessment_pip'].browse(self.env.context.get('active_id'))

        template_id = a.env.ref('kw_assessment_feedback.performance_approve_mail_template')
        users = self.env['res.users'].sudo().search([])
        manager = users.filtered(lambda user: user.has_group('kw_assessment_feedback.group_assessment_feedback_manager') == True)
        email_to = ','.join(manager.mapped('email'))
        email_cc = a.requested_by.work_email
        name = ','.join(manager.mapped('name'))
        template_id.with_context(email_to=email_to,email_cc=email_cc,name=name).send_mail(a.id,notif_layout="kwantify_theme.csm_mail_notification_light")
        a.write({'state': 'inprogress'})
        a.log_ids = [[0,0,{
            'employee_name': a.env.user.employee_ids.id,
            'comment': self.remark,
            'state': a.state,
            'date': self.current_datetime,
        }
        ]]


class PerformanceCloseWizard(models.TransientModel):
    _name = "performance_close_wizard"
    _description = "Performance Close Wizard"

    remark = fields.Text('Remark',track_visibility='onchange')
    current_datetime = datetime.now()
    


    @api.multi
    def action_done(self):

        a = self.env['kw_feedback_assessment_pip'].browse(self.env.context.get('active_id'))
        
        template_id = a.env.ref('kw_assessment_feedback.performance_submit_mail_template')
        users = self.env['res.users'].sudo().search([])
        manager = users.filtered(lambda user: user.has_group('kw_assessment_feedback.group_assessment_feedback_manager') == True)
        email_to = ','.join(manager.mapped('email'))
        email_cc = a.requested_by.work_email
        name = ','.join(manager.mapped('name'))
        template_id.with_context(email_to=email_to,email_cc=email_cc,name=name).send_mail(a.id,notif_layout="kwantify_theme.csm_mail_notification_light")
        a.write({'state': 'closed'})
        a.log_ids = [[0,0,{
            'employee_name': a.env.user.employee_ids.id,
            'comment': self.remark,
            'state': a.state,
            'date': self.current_datetime,
        }
        ]]


class PerformanceUpdateWizard(models.TransientModel):
    _name = "performance_update_wizard"
    _description = "Performance Update Wizard"

    remark = fields.Text('Remark',track_visibility='onchange')
    current_datetime = datetime.now()


    @api.multi
    def action_done(self):
        a = self.env['kw_feedback_assessment_pip'].browse(self.env.context.get('active_id'))
        
        a.log_ids = [[0,0,{
            'employee_name': a.env.user.employee_ids.id,
            'comment': self.remark,
            'state': a.state,
            'date': self.current_datetime,
        }
        ]]



    


        