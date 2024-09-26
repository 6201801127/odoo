from odoo import SUPERUSER_ID
from odoo import models,fields,api

class RosterPointMasterJob(models.Model):
    _inherit = "hr.job"

    application_count = fields.Integer("No.Of Applications",compute="compute_no_of_applications")
    application_fee_details = fields.Text("Application Fee Details")
    expected_employees = fields.Integer(compute='_compute_expected_employees', string='Total Forecasted Employees', store=False,
        help='Expected number of employees for this job position after new recruitment.')

    @api.multi
    def compute_no_of_applications(self):
        applicant_data = self.env['hr.applicant'].sudo().search([('job_id','in',self.ids)])
        for job in self:
            job.application_count = len(applicant_data.filtered(lambda r: r.job_id == job))
    
    @api.multi
    def _compute_expected_employees(self):
        for job in self:
            job.expected_employees = self.env['hr.applicant'].search_count([
                                    ('stage_id.name','=','Contract Proposal'),
                                    ('job_id','=',job.id),
                                    ('active','=',True),
                                    ('emp_id','=',False)])

    @api.multi
    def view_job_applicants(self):
        # employee_type = False
        # if self.employee_type:
        #     emp_type = self.employee_type[0]
        #     if emp_type.code =='regular':
        #         employee_type = 'regular'

        #     elif emp_type.code =='contract_agency':
        #         employee_type = 'contractual_with_agency'

        #     elif emp_type.code =='contract_stpi':
        #         employee_type = 'contractual_with_stpi'
        # ,'default_employee_type':employee_type
        return {
            'model': 'ir.actions.act_window',
            'name': 'Applications',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'kanban,tree,form,graph,calendar,pivot',
            'res_model': 'hr.applicant',
            'domain': [('branch_id', 'in', self.env.user.branch_ids.ids)] if self._uid != SUPERUSER_ID else [],
            'context': {'search_default_job_id': [self.id], 'default_job_id': self.id}
        }
        

    # @api.model
    # def create(self, vals):
    #     res = super(RosterPointMasterJob, self).create(vals)
    #     sanctioned_post = res.sanctionedpost
    #     roster_point_masters = self.env["roster.point.master"]
    #     if sanctioned_post > 0:
    #         for i in range(1,sanctioned_post+1):
    #             roster_point_masters.create({
    #                 'name': i,
    #                 'job_id':res.id,
    #             })
    #     return res

    # @api.multi
    # def write(self, vals):
    #     res = super(RosterPointMasterJob, self).write(vals)
    #     for job in self:
    #         sanctioned_post = job.sanctionedpost
    #         roster_point_masters = self.env["roster.point.master"].search([('job_id','=',job.id)]).sorted(lambda r:r.name,reverse=True)
    #         if len(roster_point_masters) < sanctioned_post:
    #             for i in range(1,(sanctioned_post - len(roster_point_masters))+1):
    #                 roster_point_masters.create({
    #                     'name':roster_point_masters and roster_point_masters[0].name + i or i,
    #                     'job_id':job.id,
    #                 })
    #     return res
