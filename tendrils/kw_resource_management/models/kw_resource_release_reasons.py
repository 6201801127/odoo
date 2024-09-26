# -*- coding: utf-8 -*-
from odoo import fields, models, api, tools
from odoo.exceptions import ValidationError


class ResourceReleaseRemarkWizard(models.TransientModel):
    _name = 'resource_release_remark_wizard'
    _description = 'Remark wizard'

    reason = fields.Text(string="Remark")
    # permission  = fields.Selection([
    #     ('no', 'No'),
    #     ('yes', 'Yes'),
    #     ],  default='no')
    release_reason = fields.Selection([
        ('Resignation', 'Resignation'),
        ('Illness', 'Illness'),
        ('Other Assignments', 'Other Assignments'),
        ('Task Completed', 'Task Completed'),
        ],required=True,string="Reason")
    discipline_adherence_ratings = fields.Selection([('0','0'),('1','1'),('2','2'),('3','3'),('4','4'),('5','5')], string="Discipline and Process adherence" )
    enhanced_roles = fields.Selection([('yes', 'Yes'),('no', 'No')],required=True,  default='yes',string="Would you recommend him for similar or enhanced roles that he/ she can perform. ")
    @api.constrains('reason')
    def _check_remark(self):
        if self.reason and len(self.reason) > 200:
            raise ValidationError('Maximum 200 characters required.')
           

    def action_confirm_btn(self):
        employee_id = self.env.context.get('employee_id')
        emp_rec = self.env['hr.employee'].sudo().search([('id','=',employee_id)])
        old_sbu_id = emp_rec.sbu_master_id.id
        old_sbu_name = emp_rec.sbu_master_id.name
        if emp_rec:
            if not self.discipline_adherence_ratings:
                raise ValidationError('Kindly provide rating for Discipline and Process adherence.')
            emp_rec.write({
                'sbu_master_id':False,
                'sbu_type':False
            })
            self.env['kw_resource_release_log'].sudo().create({
                'release_reason':self.release_reason if self.release_reason else '',
                'reason':self.reason if self.reason else f"Released from unit bench ({old_sbu_name})",
                'release_emp_id':emp_rec.id,
                'release_by':self.env.user.employee_ids.id,
                'release_from':old_sbu_id,
                'discipline_adherence_ratings':self.discipline_adherence_ratings if self.discipline_adherence_ratings else ' ',
                'enhanced_roles':self.enhanced_roles if self.enhanced_roles else ' ',
            })

class ResourceReleaseLog(models.Model):
    _name = 'kw_resource_release_log'
    _description = 'Release Log'


    reason = fields.Char(string='Reason')
    release_emp_id = fields.Many2one('hr.employee',string='Released Employee')
    release_emp_code = fields.Char(related='release_emp_id.emp_code',string="Released Employee's Code")
    release_emp_name = fields.Char(related='release_emp_id.name',string="Released Employee's Name")
    release_by = fields.Many2one('hr.employee',string='Released By')
    release_from = fields.Many2one('kw_sbu_master',string='Released From')
    short_text = fields.Text(string="Remarks",compute="_compute_short_text")
    release_reason = fields.Selection([
        ('Resignation', 'Resignation'),
        ('Illness', 'Illness'),
        ('Other Assignments', 'Other Assignments'),
        ('Task Completed', 'Task Completed'),
        ],string="Release Reason")
    discipline_adherence_ratings = fields.Selection([('0','0'),('1','1'),('2','2'),('3','3'),('4','4'),('5','5')], string="Discipline and Process adherence" )
    enhanced_roles = fields.Selection([('yes', 'Yes'),('no', 'No')],string="Would you recommend him for similar or enhanced roles that he/ she can perform.")


    @api.depends('reason')
    def _compute_short_text(self):
        for record in self:
            record.short_text = ' '.join(record.reason.split()[:20])        