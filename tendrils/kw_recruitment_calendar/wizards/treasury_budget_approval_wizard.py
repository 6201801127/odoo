from http.client import ImproperConnectionState
from odoo import fields,models,api
from odoo.exceptions import ValidationError
from datetime import date,datetime
from dateutil.relativedelta import relativedelta

def get_years():
    year_list = []
    for i in range((date.today().year), 1997, -1):
        year_list.append((i, str(i)))
    return year_list

class TreasuryBudgetApprovalWizard(models.TransientModel):
    _name = 'treasury_budget_approval_wizard'
    _description = 'treasury_budget_approval_wizard'

    budget_line_status = fields.Char(string='Status', default=lambda self: (', '.join(set(self.env['kw_recruitment_budget_lines'].sudo().browse(self._context.get('budget_approval_ids')).mapped('status')))).title())

    @api.multi
    def approve_budget_ids(self):
        searched_env = self.env['kw_recruitment_budget_lines']
        dept_ids=False
        all_ids=False
        if self._context.get('budget_approval_ids'):
            if not self.env.user.has_group('kw_recruitment.group_tag_budget_user'):
                raise ValidationError("To approve the selected records you should be TAG user.")
            all_ids = searched_env.sudo().browse(self._context.get('budget_approval_ids'))
            dept_ids = all_ids.mapped('dept_id')
            march_budget = all_ids.mapped('mar_budget')
            all_ids.ids.sort(reverse=False)
            approval_data = list(set(all_ids.mapped('status')))
            if len(approval_data) == 1:
                if approval_data[0] == 'publish':
                    raise ValidationError("Budget line is already Published. Please select Budget lines of Draft state to Publish the Budget lines")
                elif approval_data[0] == 'reject':
                    raise ValidationError("Budget line with Reject state are selected. Please select Budget lines of Draft state to Publish the Budget lines")

            elif len(approval_data) >1:
                raise ValidationError("Multiple Budget line of different state are selected. Please select Budget lines of Draft state to Approve the records.")

            if False in march_budget:
                raise ValidationError("Please add the budget in the selected budget lines.")
            
        if dept_ids:
            for dept in dept_ids:
                filtered_data = self.env['kw_recruitment_budget_lines'].sudo().search([('department_sequence','!=','')])
                # print("filtered_data===",filtered_data)
                filtered_records = False
                if filtered_data:
                    filtered_records = filtered_data
                get_data = searched_env.sudo().department_last_sequence(int(dept),filtered_records)
                # print("get_data===",get_data)
                # return
                count = get_data+1 if get_data != 0 else 1 
                # print("count===11=",count)
                budget_ids = all_ids.filtered(lambda x: x.dept_id.id ==int(dept) and x.status != 'publish')
                # print("budget_ids===",budget_ids)
                for budget in budget_ids:
                    query = f""" update kw_recruitment_budget_lines set status = 'publish', name = '{budget.dept_id.display_name + '/' + str(budget.fiscalyr.name) + '/' + str(count)}', department_sequence={count} where id = {budget.id}"""
                    self._cr.execute(query)
                    # budget.write({'status': 'publish','name': budget.dept_id.display_name + "/" + str(budget.fiscalyr.name) + "/" + str(count),'department_sequence':count})
                    count += 1
                    # print("count===22=",count)
                    template_obj = self.env.ref('kw_recruitment_calendar.recruitment_budget_action_template')
                    mail = self.env['mail.template'].browse(template_obj.id).with_context(
                                requester = budget.employee_id.name,
                                # email_cc = tag_cc,
                                action= "Published",
                                email_to=budget.employee_id.work_email).send_mail(budget.id,notif_layout='kwantify_theme.csm_mail_notification_light')
            self.env.user.notify_success("Budget Published successfully.")
            
class TreasuryBudgetDeclineWizard(models.TransientModel):
    _name = 'treasury_budget_decline_wizard'
    _description = 'treasury_budget_decline_wizard'


    budget_line_status = fields.Char(string='Status', default=lambda self: (', '.join(set(self.env['kw_recruitment_budget_lines'].sudo().browse(self._context.get('budget_decline_ids')).mapped('status')))).title())

    @api.multi
    def decline_budget_ids(self):
        budget_ids = False
        if self._context.get('budget_decline_ids'):
            if not self.env.user.has_group('kw_recruitment.group_tag_budget_user'):
                raise ValidationError("To approve the selected records you should have access (Recruitment : TAG User).")
            budget_ids = self.env['kw_recruitment_budget_lines'].sudo().browse(self._context.get('budget_decline_ids'))
            approval_data = list(set(budget_ids.mapped('status')))
            if len(approval_data) == 1:
                if approval_data[0] == 'publish':
                    raise ValidationError("Budget line is Published.You cannot reject the published Budget lines.")
                elif approval_data[0] == 'reject':
                    raise ValidationError("Budget line is already Rejected. Please select Budget lines of Draft state to Reject the Budget lines")
            elif len(approval_data) > 1:
                raise ValidationError("Multiple Budget line of different state are selected. Please select Budget lines of Draft state to reject the record")
        if budget_ids:
            for budget in budget_ids:
                budget.write({'status': 'reject'})
                template_obj = self.env.ref('kw_recruitment_calendar.recruitment_budget_action_template')
                mail = self.env['mail.template'].browse(template_obj.id).with_context(
                            requester = budget.employee_id.name,
                            # email_cc = tag_cc,
                            action= "Declined",
                            email_to=budget.employee_id.work_email).send_mail(budget.id,notif_layout='kwantify_theme.csm_mail_notification_light')
            self.env.user.notify_success("Budget Declined successfully.")
