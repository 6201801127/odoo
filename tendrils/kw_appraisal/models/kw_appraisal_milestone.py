from odoo import models, fields, api
from odoo.exceptions import  ValidationError,UserError
from datetime import datetime,date

class kw_appraisal_milestone(models.Model):
    _name = 'kw_appraisal_milestone'
    _description = 'Appraisal milestone'
    _rec_name = 'name'

    name = fields.Char('Milestone Name',required=True)
    milestone_date = fields.Date('Target Date')
    goal_id = fields.Many2one('kw_appraisal_goal','milestone_id',ondelete='cascade')
    status = fields.Boolean('Achievement Status',default=False,help='If status is True then Milestone completed else not-completed.')
    state = fields.Text(string='Status',selection=[('rejected','Rejected'),('approved','Approved')])
    remark = fields.Text(string='Remarks')
    action_remark = fields.Text(string='Action Remark')
    active = fields.Boolean(default=True)
    make_readonly = fields.Boolean(compute='_compute_readonly')

    @api.multi
    def _compute_readonly(self):
        for record in self:
            if record.goal_id:
                record.make_readonly = True
            else:
                record.make_readonly = False

    @api.onchange('milestone_date')
    def _validate_back_date(self):
        for record in self:
            if record.milestone_date and record.milestone_date < date.today():
                raise UserError(f"Back date not allowed.")

    # @api.multi
    # def unlink(self):
    #     for rec in self:
    #         if rec.goal_id.employee_id.user_id.id == self._uid:
    #             self.env['kw_appraisal_updated_milestone'].create({
    #                 'goal_id':rec.goal_id.id,
    #                 'milestone_name':rec.name,
    #                 'milestone_status':rec.status,
    #                 'milestone_remark':rec.remark,
    #                 'status':'2',
    #             })
    #     return super(kw_appraisal_milestone, self).unlink()

    # @api.multi
    # def write(self,vals):
    #     for rec in self:
    #         if rec.goal_id.employee_id.user_id.id == self._uid and ('name' in vals or 'status' in vals or 'remark' in vals):
    #             self.env['kw_appraisal_updated_milestone'].create({
    #                 'goal_id':rec.goal_id.id,
    #                 'milestone_name':rec.name,
    #                 'milestone_status':rec.status,
    #                 'milestone_remark':rec.remark,
    #                 'status':'3',
    #                 'milestone_id':rec.id,
    #             })
    #     return super(kw_appraisal_milestone, self).write(vals)

class kw_appraisal_updated_milestone(models.Model):
    _name = 'kw_appraisal_updated_milestone'
    _description = 'Appraisal updated milestone'
    _rec_name = 'goal_id'

    goal_id = fields.Many2one('kw_appraisal_goal',string='Goal')
    milestone_id = fields.Integer()
    milestone_name = fields.Char(string='Milestone Name')
    milestone_date = fields.Date('Target Date')
    milestone_status = fields.Boolean('Achievement Status',default=False,help='If status is True then Milestone completed else not-completed.')
    milestone_remark = fields.Text(string='Remarks')
    status = fields.Selection(string='Updated Status',selection=[('1','Created'),('2','Deleted'),('3','Updated')])
    remark = fields.Text(string='Remark')

    @api.multi
    def reject_updated_milestone(self):
        
        form_res = self.env['ir.model.data'].get_object_reference('kw_appraisal', 'kw_appraisal_updated_milestone_approval_form')
        form_id = form_res and form_res[1] or False

        actions = {
            'name': 'Reject Remark',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'res_model': 'kw_appraisal_updated_milestone',
            'res_id':self.id,
            'views': [(form_id, 'form')],
            'target':'new'
            }

        return actions

    @api.multi
    def action_reject(self):
        self.ensure_one()
        self.env['kw_appraisal_milestone'].browse(self.milestone_id).sudo().write({
            'action_remark':self.remark,
            'state':'rejected',
            'active':False,
        })
        milestone_record = self.env['kw_appraisal_milestone'].browse(self.milestone_id)
        self.env['goal_action_log'].create({
            'goal_id':milestone_record.goal_id.id,
            'who':self.env.user.employee_ids.id,
            'when':date.today(),
            'what':'Rejected.',
            'remark':milestone_record.action_remark if milestone_record.action_remark else False,
            'milestone':milestone_record.name
        })
        self.unlink()
        self.env.user.notify_info("Milestone rejected.")



class goal_action_log(models.Model):
    _name           = 'goal_action_log'
    _description    = 'Goal Log'
    
    goal_id = fields.Many2one(comodel_name='kw_appraisal_goal')
    who = fields.Many2one('hr.employee',string='Authority Name')
    when = fields.Date(string='Action Taken On')
    what = fields.Char(string='Approval Status')
    remark = fields.Text(string='Remark')
    milestone = fields.Text(string='Milestone')
