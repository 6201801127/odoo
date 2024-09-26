import datetime

from odoo import fields, models, api

class ForwordModuleLeadWizards(models.TransientModel):
    _name = 'kw_forword_bug_wizards'
    _description = 'Kwantify Forword Module Lead Wizards'

    def get_module_lead_id(self):
        record = self.env.context.get('current_record')
        data = self.env['kw_raise_defect'].sudo().search([('id', '=', record)])
        emp_list = []
        if data.project_id:
            for recc in data.bug_con_id.user_ids:
                if recc.user_type in ['Module Lead']:
                    emp_list.append(recc.employee_id.id)
            emp_li = [('id', 'in', emp_list)]
            return emp_li
    
    project_id = fields.Many2one('project.project' , string='Project')
    defect_id = fields.Many2one('kw_raise_defect', default=lambda self: self._context.get('current_record'))
    module_lead_id = fields.Many2one('hr.employee', string="Module Lead Name", domain=get_module_lead_id, track_visibility='always', required=True)
    description = fields.Text(string='Description')

    def forword_bug(self):
        context = dict(self._context)
        int_details = self.env["kw_raise_defect"].browse(context.get("active_id"))
        for rec in self.env['kw_raise_defect'].sudo().search([('id', '=', int_details.id)]):
            rec.pending_at = False
            rec.pending_at = [(4, self.module_lead_id.id, False)]
            rec.forward_to = self.module_lead_id.id
            rec.assigned_by = self.env.user.employee_ids.id
            rec.developer_id = self.module_lead_id.id
            rec.developer_assign_boolean = False
            rec.forward_bug_date = datetime.datetime.now()
            user_designation = self.env['kw_bug_life_cycle_conf_user_field'].sudo().search([('employee_id', '=', self.env.user.employee_ids.id),('cycle_bug_conf_id.project_id', '=', rec.project_id.id)])
            rec.write({'action_log_table_ids':[[0, 0, {'state':'Forwarded',
                                                       'action_taken_by': self.env.user.employee_ids.name,
                                                       'designation':user_designation.user_type,
                                                       'remark':self.description
                                                        }]]})



