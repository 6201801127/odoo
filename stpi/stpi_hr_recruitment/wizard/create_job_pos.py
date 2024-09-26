from odoo import fields, models, api

class CreateJobPos(models.TransientModel):
    _name = 'create.jobrecruit.line'
    _description = 'Job Opening'

    advertisement_id = fields.Many2one('hr.requisition.application', invisible=1)
    branch_id = fields.Many2one("res.branch","Branch")
    job_recruit = fields.Many2many('recruitment.jobop', string='Job Openings')

    @api.multi
    def confirm_job_pos(self):
        advertisement_line_ids = []
        for line in self.job_recruit:
            for inline in line.job_pos:
                advertisement_line_ids.append((0, 0, {
                    'job_opening_line_id':inline.id,
                    'allowed_category_id': self.advertisement_id.id,
                    'job_id': inline.job_id.id,
                    'branch_id': inline.branch_id.id,
                    'directorate_id': inline.directorate_id.id,
                    'category_id': inline.category_id.id,
                    'state': inline.state.id,
                    'remarks': inline.remarks,
                    'opening': 1,
                    'employee_type':inline.employee_type
                }))
            line.write({'state': 'published'})
        self.advertisement_id.advertisement_line_ids = advertisement_line_ids