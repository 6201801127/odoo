from datetime import date
from odoo import fields, models, api
from odoo.exceptions import ValidationError


class NotifyWizardApproved(models.TransientModel):
    _name = 'notify_wizard_approved'
    _description = 'notify_wizard_approved'

    mif_id = fields.Many2one("kw_manpower_indent_form", string="MIF",
                             default=lambda self: self._context.get('current_id'))
    remarks = fields.Text(string="Remark", required=True)

    def approve_confirm_action(self):
        if self._context.get('button') == 'Approve_SBU':
            self.mif_id.sudo().write({'state': 'Approved',
                                      'description': self.remarks,
                                      'pending_at': self.mif_id.approved_user_id.id,
                                      'approval_date': date.today(),
                                      'approved_user_id': False})

            template = self.env.ref("kw_recruitment.mail_notify_to_approve_action")
            if template:
                # users = self.env['res.users'].sudo().search([])
                # manager_emp = users.filtered(lambda user: user.has_group('kw_resource_management.group_budget_manager') == True)
                # mail_to = ",".join(manager_emp.mapped('email')) or ''
                notify_emp = self.env.ref('kw_recruitment.group_kw_mif_user_notify').users
                mail_to = ",".join(notify_emp.mapped('employee_ids.work_email')) or ''
                mail = self.env['mail.template'].browse(template.id).with_context(mail_for="Approval",
                                                                                  email_from=self.env.user.employee_ids.work_email,
                                                                                  email_to=mail_to).sudo().send_mail(
                    self.mif_id.id, notif_layout='kwantify_theme.csm_mail_notification_light')
            tree_view_id = self.env.ref("kw_recruitment.view_kw_manpower_indent_form_tree").id
            return {
                'type': 'ir.actions.act_window',
                'name': 'Manpower Indent Form',
                'res_model': 'kw_manpower_indent_form',
                'view_mode': 'tree',
                'view_type': 'form',
                'view_id': tree_view_id,
                'target': 'main',
            }

        elif self._context.get('button') == 'Approve_HOD':
            self.mif_id.sudo().write({'state': 'Approved',
                                      'approval_date': date.today(),
                                      'description': self.remarks,
                                      'approved_user_id': False})

            template = self.env.ref("kw_recruitment.mail_notify_to_approve_action")
            if template:
                # users = self.env['res.users'].sudo().search([])
                # manager_emp = users.filtered(lambda user: user.has_group('kw_resource_management.group_budget_manager') == True)
                # mail_to = ",".join(manager_emp.mapped('email')) or ''
                notify_emp = self.env.ref('kw_recruitment.group_kw_mif_user_notify').users
                mail_to = ",".join(notify_emp.mapped('employee_ids.work_email')) or ''
                mail = self.env['mail.template'].browse(template.id).with_context(mail_for="Approval",
                                                                                  email_from=self.env.user.employee_ids.work_email,
                                                                                  email_to=mail_to).sudo().send_mail(
                    self.mif_id.id, notif_layout='kwantify_theme.csm_mail_notification_light')
            tree_view_id = self.env.ref("kw_recruitment.view_kw_manpower_indent_form_tree").id
            return {
                'type': 'ir.actions.act_window',
                'name': 'Manpower Indent Form',
                'res_model': 'kw_manpower_indent_form',
                'view_mode': 'tree',
                'view_type': 'form',
                'view_id': tree_view_id,
                'target': 'main',
            }

        elif self._context.get('button') == 'Approve_RCM':
            name = self.env.user.employee_ids.name
            self.mif_id.write({
                'state': 'Grant',
                'approved_user_id': False,
                'pending_at': self.env.user.employee_ids.id,
                'rcm_comment': self.remarks})
            template = self.env.ref("kw_recruitment.mail_notify_to_grant_action")
            if template:
                # users = self.env['res.users'].sudo().search([])
                # manager_emp = users.filtered(lambda user: user.has_group('kw_recruitment.group_kw_mif_user_notify') == True)
                # mail_cc = ",".join(manager_emp.mapped('email')) or ''
                manager_emp = self.env.ref('kw_recruitment.group_kw_mif_user_notify').users
                mail_cc = ",".join(manager_emp.mapped('employee_ids.work_email')) or ''
                mail_cc += f",{self.env.user.employee_ids.work_email}"

                if self.mif_id.req_raised_by_id.sbu_master_id.representative_id:
                    mail_to = [self.mif_id.req_raised_by_id.sbu_master_id.representative_id.work_email] or []
                else:
                    mail_to = [self.mif_id.req_raised_by_id.department_id.manager_id.work_email] or []
                mail_to.append(self.mif_id.req_raised_by_id.work_email)
                # mail_to.append(self.env.user.employee_ids.work_email)
                mail_to = ','.join(list(set(mail_to)))
                mail = self.env['mail.template'].browse(template.id).with_context(email_cc=mail_cc,
                                                                                  mail_to=mail_to).send_mail(self.mif_id.id, notif_layout='kwantify_theme.csm_mail_notification_light')
            tree_view_id = self.env.ref("kw_recruitment.view_kw_manpower_indent_form_tree").id
            return {
                'type': 'ir.actions.act_window',
                'name': 'Manpower Indent Form',
                'res_model': 'kw_manpower_indent_form',
                'view_mode': 'tree',
                'view_type': 'form',
                'view_id': tree_view_id,
                'target': 'main',
            }

        elif self._context.get('button') == 'Rejected':
            self.sudo().mif_id.write({
                'state': 'Rejected',
                'approved_user_id': False,
                'description': self.remarks})
            template = self.env.ref("kw_recruitment.mail_notify_to_reject_action")
            if template:
                # users = self.env['res.users'].sudo().search([])
                # manager_emp = users.filtered(lambda user: user.has_group('kw_recruitment.group_kw_mif_user_notify') == True)
                # mail_cc = ",".join(manager_emp.mapped('email')) or ''
                notify_emp = self.env.ref('kw_recruitment.group_kw_mif_user_notify').users
                mail_cc = ",".join(notify_emp.mapped('employee_ids.work_email')) or ''
                email_from = self.env.user.employee_ids.work_email
                mail = self.env['mail.template'].browse(template.id).with_context(email_cc=mail_cc,
                                                                                  email_from=email_from).sudo().send_mail(self.mif_id.id, notif_layout='kwantify_theme.csm_mail_notification_light')
            tree_view_id = self.env.ref("kw_recruitment.view_kw_manpower_indent_form_tree").id
            return {
                'type': 'ir.actions.act_window',
                'name': 'Manpower Indent Form',
                'res_model': 'kw_manpower_indent_form',
                'view_mode': 'tree',
                'view_type': 'form',
                'view_id': tree_view_id,
                'target': 'main',
            }
