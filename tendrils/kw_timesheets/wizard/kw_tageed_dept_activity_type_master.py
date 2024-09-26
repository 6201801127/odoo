from odoo import api, models,fields
from odoo.exceptions import UserError,ValidationError
from odoo import exceptions,_

class tagged_dept_activity_master(models.TransientModel):
    _name       ='tagged_dept_activity_master'
    _description= 'Dept tagged wizard'

    # def _get_default_dept(self):
    #     datas   = self.env['project.task'].browse(self.env.context.get('active_ids',[]))
    #     return datas


    dept_tagged = fields.Many2many('hr.department',string='Department Tagged' ,required=True)

    @api.multi
    def action_tag_department(self):
        project_task_ids = self.env['project.task'].browse(self._context.get('active_ids',[]))
    
        if project_task_ids:
            for department in self.dept_tagged:
                project_task_ids.write({'mapped_to': [[4,department.id]]})
            self.env.user.notify_success("Tagged Department successfully.")
        
    @api.multi
    def action_untag_department(self):
        project_task_ids = self.env['project.task'].browse(self._context.get('active_ids',[]))
        if project_task_ids:
            for department in self.dept_tagged:
                project_task_ids.write({'mapped_to': [[3,department.id]]})
            self.env.user.notify_success("Un-tagged Department successfully.")