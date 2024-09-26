from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.addons import decimal_precision as dp
from datetime import date, datetime


class ResourcesMaterial(models.Model):
    _name = 'kw_eq_resources_data'
    _description = 'Resources'
    _rec_name = 'skill'



    resource_material_id = fields.Many2one('kw_eq_estimation', string="Estimation")
    resource_material_replica_id = fields.Many2one('kw_eq_replica')
    skill = fields.Selection(string="Skill",selection=[('technical_expert', 'Technical Expert'), ('functional_expert', 'Functional Expert'),('subject_matter_expert', 'Subject Matter Expert'),('general', 'General')])
    position = fields.Text(string="Position")
    duration_of_engagement = fields.Integer(string="Duration of Engagement(months)")
    days=fields.Integer(string='Duration of Engagement(days)')
    minimum_educational_qualification_id = fields.Many2one('kw_eq_educational_qualification_master')
    detailed_experience = fields.Text(string="Detailed Experience")
    year_of_experience = fields.Integer(string="Year of Experience")
    work_location = fields.Selection(string="Work Location",selection=[('csm_office', 'CSM Office'), ('client_location', 'Client Location')])
    location = fields.Char()
    computer_provision = fields.Selection(string="Computer Provision",selection=[('CSM', 'CSM'), ('Client', 'Client')])
    job_description = fields.Text(string="Job Description")
    eq_category = fields.Selection(string="EQ Category",selection=[('software_support', 'Software Support'), ('social_media_management', 'Social Media Management'),('consultancy_service', 'Consultancy Service'),('staffing_service', 'Staffing Service')])
    skill_description = fields.Text(string="Skill Description")
    number_of_resource = fields.Integer(string="Number of Resource")
    work_location_id = fields.Many2many('kw_recruitment_location','kw_recruitment_location_eq_location','resource_id','branch_id',string='Base Location')
    specialization = fields.Text()
    resource_deploy_duration = fields.Selection(string="Resource Deployment Duration",selection=[('1', '1 Yrs'), ('2', '2 Yrs'),('3', '3 Yrs'),('4', '4 Yrs'),('5', '5 Yrs'),('6', '6 Yrs'),('7', '7 Yrs')])
    # ctc = fields.Float(compute='change_years_amt')  
    # average_percentage  = fields.Integer('Average Percentage')
    first_year = fields.Integer('Quote Per Resource')
    month_days = fields.Char(compute="comute_duration")
    
    @api.constrains('duration_of_engagement','days')
    def _check_duration_of_engagement(self):
        for rec in self:
            if rec.duration_of_engagement > 84:
                raise ValidationError('Man month should be less than 84 in Time and Material Resources!')
            if rec.duration_of_engagement < 0:
                raise ValidationError('Man month can not be negative in Time and Material Resources!')
            if rec.days < 0:
                raise ValidationError('Man month can not be negative in Time and Material Resources!')
            if rec.days > 31:
                raise ValidationError('Man month can not be more than 31 in Time and Material Resources!')
                
        
    
    @api.depends('duration_of_engagement','days')
    def comute_duration(self):
        for rec in self:
            if rec.duration_of_engagement>0 and rec.days >0:
                rec.month_days = f"{rec.duration_of_engagement} Months and {rec.days} Days"
            elif rec.duration_of_engagement>0 and rec.days == 0:
                rec.month_days = f"{rec.duration_of_engagement} Months"
            elif rec.duration_of_engagement == 0 and rec.days >0:
                rec.month_days = f"{rec.days} Days"
    
    # @api.depends('resource_deploy_duration','average_percentage','first_year')
    # def change_years_amt(self):
    #     for rec in self:
    #         if rec.resource_deploy_duration:
    #             percentage = rec.average_percentage/100
    #             sec_year = ((percentage * rec.first_year)) if rec.resource_deploy_duration in ('2','3','4','5','6','7') else  0
    #             third_year =((percentage * sec_year)) if rec.resource_deploy_duration in ('3','4','5','6','7') else  0
    #             forth_year = ((percentage * third_year)) if rec.resource_deploy_duration in ('4','5','6','7') else  0
    #             fifth_year = ((percentage * forth_year)) if rec.resource_deploy_duration in ('5','6','7') else  0
    #             sixth_year = ((percentage * fifth_year)) if rec.resource_deploy_duration in ('6','7') else  0
    #             seventh_year = ((percentage  * sixth_year)) if rec.resource_deploy_duration in ('7') else  0 
    #             average = ((sec_year+third_year+forth_year+fifth_year+sixth_year+seventh_year+rec.first_year)/int(rec.resource_deploy_duration))
    #             rec.ctc = (average)
                
    # @api.onchange('id')
    # def compute_sl_no(self):
    #     for rec in self:
    #         rec.sl_no = rec.id

    @api.onchange('duration_of_engagement')
    def get_year_values(self):
        self.first_year = False
        if self.duration_of_engagement :
            if self.duration_of_engagement <= 12 and self.duration_of_engagement > 0:
                self.resource_deploy_duration = '1'
            elif self.duration_of_engagement <= 24 and self.duration_of_engagement > 12:
                self.resource_deploy_duration = '2'
            elif self.duration_of_engagement <= 36 and self.duration_of_engagement > 24:
                self.resource_deploy_duration = '3'
            elif self.duration_of_engagement <= 48 and self.duration_of_engagement > 36:
                self.resource_deploy_duration = '4'
            elif self.duration_of_engagement <= 60 and self.duration_of_engagement > 48:
                self.resource_deploy_duration = '5'
            elif self.duration_of_engagement <= 72 and self.duration_of_engagement > 60:
                self.resource_deploy_duration = '6'
            elif self.duration_of_engagement <= 84 and self.duration_of_engagement > 72:
                self.resource_deploy_duration = '7'