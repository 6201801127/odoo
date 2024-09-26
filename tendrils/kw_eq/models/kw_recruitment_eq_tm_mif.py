from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.addons import decimal_precision as dp
from datetime import date, datetime


class EQMIFDetails(models.Model):
    _name = 'kw_recruitment_eq_tm_mif'
    _description = 'EQ TM Resource Details'
    _rec_name = 'opp_id'
    
    
    estimation_id = fields.Many2one('kw_eq_estimation')
    skill = fields.Selection(string="Skill",selection=[('technical_expert', 'Technical Expert'), ('functional_expert', 'Functional Expert'),('subject_matter_expert', 'Subject Matter Expert'),('general', 'General')])
    position = fields.Text(string="Position")
    duration_of_engagement = fields.Integer(string="Duration of Engagement(months)")
    days=fields.Integer(string='Duration of Engagement(days)')
    minimum_educational_qualification_id = fields.Many2one('kw_eq_educational_qualification_master')
    detailed_experience = fields.Text(string="Detailed Experience")
    # year_of_experience = fields.Selection(string="Number of Resource",selection=[('1', '1'), ('2', '2'),('3', '3'),('4', '4'),('5', '5'),('6', '6'),('7', '7'),('8', '8'),('9', '9'),('10', '10'),('11', '11'),('12', '12'),('13', '13'),('14', '14'),('15', '15'),('16', '16'),('17', '17'),('18', '18'),('19', '19'),('20', '20')])
    year_of_experience = fields.Integer(string="Year of Experience")
    work_location = fields.Selection(string="Work Location",selection=[('csm_office', 'CSM Office'), ('client_location', 'Client Location')])
    location = fields.Text()
    computer_provision = fields.Selection(string="Computer Provision",selection=[('CSM', 'CSM'), ('Client', 'Client')])
    job_description = fields.Text(string="Job Description")
    eq_category = fields.Selection(string="EQ Category",selection=[('software_support', 'Software Support'), ('social_media_management', 'Social Media Management'),('consultancy_service', 'Consultancy Service'),('staffing_service', 'Staffing Service')])
    skill_description = fields.Text(string="Skill Description")
    # number_of_resource = fields.Selection(string="Number of Resource",selection=[('1', '1'), ('2', '2'),('3', '3'),('4', '4'),('5', '5'),('6', '6'),('7', '7'),('8', '8'),('9', '9'),('10', '10'),('11', '11'),('12', '12'),('13', '13'),('14', '14'),('15', '15'),('16', '16'),('17', '17'),('18', '18'),('19', '19'),('20', '20')])
    number_of_resource = fields.Integer(string="Number of Resource")
    work_location_id = fields.Many2many('kw_recruitment_location','kw_recruitment_location_tm_location','resource_id','branch_id',string='Base Location')
    specialization = fields.Text()
    # lead_details
    opp_code = fields.Char()
    opp_id = fields.Many2one('crm.lead')
    opp_name = fields.Char(related='opp_id.name')
    client_name = fields.Char()
    
    # sales
    acc_manager_id = fields.Many2one('hr.employee')
    csg_head_id = fields.Many2one('hr.employee')
    # presales
    presales_tl_id = fields.Many2one('hr.employee')
    presales_member_id = fields.Many2one('hr.employee')
    # delivery
    pm_id = fields.Many2one('hr.employee')
    sbu_lead_id = fields.Many2one('hr.employee')
    project_reviewer_id = fields.Many2one('hr.employee')
    
    resource_id = fields.Many2one('kw_eq_resources_data')
    mif_created = fields.Boolean(compute='check_mif')
    mif_edit_bool = fields.Boolean(compute='check_mif')
    mif_view_bool = fields.Boolean(compute='check_mif')
    
    mif_id = fields.Many2one('kw_manpower_indent_form')
    mif_code = fields.Char(related='mif_id.code')
    
    month_days = fields.Char(compute="comute_duration")
    eq_ctc = fields.Float()
    sl_no = fields.Integer(compute='compute_sl_no')
    
    
    @api.depends('estimation_id')
    def compute_sl_no(self):
        sorted_records = self.search([('estimation_id','!=',False)], order='id')

        # Assign serial numbers sequentially
        for index, record in enumerate(sorted_records):
            record.sl_no = index + 1
    
    
    @api.depends('duration_of_engagement','days')
    def comute_duration(self):
        for rec in self:
            if rec.duration_of_engagement>0 and rec.days >0:
                rec.month_days = f"{rec.duration_of_engagement} Months and {rec.days} Days"
            elif rec.duration_of_engagement>0 and rec.days == 0:
                rec.month_days = f"{rec.duration_of_engagement} Months"
            elif rec.duration_of_engagement == 0 and rec.days >0:
                rec.month_days = f"{rec.days} Days"
            
  
                
        
                
    @api.depends('mif_id')
    def check_mif(self):
        for rec in self:
            if rec.mif_id:
                rec.mif_created = True
            mif_data = self.env['kw_manpower_indent_form'].sudo().search([('id','=',rec.mif_id.id)])
            print(mif_data,"==================mif_data==============")
            for mif in mif_data:
                if mif.state == 'Draft':
                    rec.mif_edit_bool = True
                if mif.state not in ['Draft',False]:
                    rec.mif_view_bool = True
    # """server action to create data after generating eq resource"""
    # def create_resource(self):
    #     eq_resource = self.env['kw_eq_resources_data'].sudo().search([('resource_material_id','!=',False)])
    #     eq_mif = self.env['kw_recruitment_eq_tm_mif'].sudo().search([]).mapped('resource_id')
    #     for rec in eq_resource:
    #         if rec.id not in eq_mif.ids:
    #             mif = self.env['kw_recruitment_eq_tm_mif'].sudo().create({
    #                 'opp_code':rec.resource_material_id.kw_oppertuinity_id.code,
    #                 'opp_id':rec.resource_material_id.kw_oppertuinity_id.id,
    #                 'resource_id':rec.id,
    #                 'computer_provision':rec.computer_provision,
    #                 'number_of_resource': rec.number_of_resource,
    #                 'year_of_experience': rec.year_of_experience ,
    #                 'estimation_id':rec.resource_material_id.id,
    #                 'eq_category':rec.eq_category,
    #                 'skill':rec.skill,
    #                 'specialization':rec.specialization,
    #                 'skill_description':rec.skill_description,
    #                 'position':rec.position,
    #                 'minimum_educational_qualification_id':rec.minimum_educational_qualification_id.id,
    #                 'work_location':rec.work_location,
    #                 'work_location_id':rec.work_location_id.id,
    #                 'location':rec.location,
    #                 'detailed_experience':rec.detailed_experience,
    #                 'job_description':rec.job_description,
    #                 'csg_head_id': rec.resource_material_id.kw_oppertuinity_id.csg_head_id.id,
    #                 'duration_of_engagement':rec.duration_of_engagement,
    #                 'days':rec.days,
    #                 # self.presales_tl_id = 
    #                 # self.presales_member_id = 
    #                 'pm_id' :rec.resource_material_id.kw_oppertuinity_id.pm_id.id,
    #                 # self.sbu_lead_id = 
    #                 'project_reviewer_id' : rec.resource_material_id.kw_oppertuinity_id.reviewer_id.id,
    #             })
                
    #     tree_view_id = self.env.ref("kw_eq.kw_recruitment_eq_tm_mif_view_tree").id
    #     form_view_id = self.env.ref("kw_eq.kw_recruitment_eq_tm_mif_view_form").id
    #     return {
    #         'name': 'Resourc Details',
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'tree,form',
    #         'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
    #         'res_model': 'kw_recruitment_eq_tm_mif',
    #         'target': 'self',
    #         # 'domain': [('id', 'in', mif_list)],
    #     }
    
    def action_generate_mif(self):
        # self.mif_created = True
        # tree_view_id = self.env.ref("kw_recruitment.view_kw_manpower_indent_form_tree").id
        form_view_id = self.env.ref("kw_recruitment.view_kw_manpower_indent_form").id
        print(self.pm_id.id,"==============pm",self.env.user.employee_ids.id)
        if self.pm_id.id == self.env.user.employee_ids.id:
            return {
                'name': 'Manpower Indent Form',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'views': [(form_view_id, 'form')],
                'res_model': 'kw_manpower_indent_form',
                # 'res_id': mif_rec.id,
                'target': 'self',
                # 'domain': [('id', 'in', mif_list)],
                'flags':{'mode':'edit'},
                'context':{'available_data':'from_eq','default_it_infra_provision':'CSM' if self.computer_provision == 'CSM' else 'Client' if  self.computer_provision == 'Client' else '',
                    'default_req_raised_by_id': self.env.user.employee_ids.id,
                    'default_sbu_id': self.env.user.employee_ids.sbu_master_id.id if self.env.user.employee_ids.sbu_master_id else False,
                    'default_no_of_resource': self.number_of_resource,
                    'default_min_exp_year': str(self.year_of_experience) if self.year_of_experience else '',
                    'default_estimation_id':self.estimation_id.id,
                    'default_eq_category':self.eq_category,
                    'default_skill':self.skill,
                    'default_skill_description':self.skill_description,
                    'default_position':self.position,
                    'default_minimum_educational_qualification_id':self.minimum_educational_qualification_id.id,
                    'default_work_location':self.work_location,
                    'default_branch_id':self.work_location_id.ids,
                    'default_qualification':self.specialization,
                    'default_location':self.location,
                    'default_detailed_experience':self.detailed_experience,
                    'default_job_description':self.job_description,
                    'default_acc_manager_id':self.acc_manager_id.id,
                    'default_csg_head_id':self.csg_head_id.id,
                    'default_presales_tl_id':self.presales_tl_id.id,
                    'default_presales_member_id':self.presales_member_id.id,
                    'default_pm_id':self.pm_id.id,
                    'default_sbu_lead_id':self.sbu_lead_id.id,
                    'default_project_reviewer_id':self.project_reviewer_id.id,
                    'default_months':self.duration_of_engagement,
                    'default_days':self.days,
                    'default_engagement_period':'Specified_period',
                    'default_type_project' : 'opportunity',
                    'default_project': self.opp_id.id,
                    'default_project_code':self.opp_code,
                    # 'default_opp_name':self.opp_name,
                    'default_client_name':self.estimation_id.client_name,
                    'default_from_eq_bool': True,
                    'default_eq_mif_id':self.id,
                    'default_type_recruitment': 'Deployment',
                    'default_from_eq_proposed_ctc':self.eq_ctc,
                    # 'default_eq_ctc':self.eq_ctc
                    
                }
            }
        else:
            raise ValidationError("You have no access to create MIF")
    
    def view_generate_mif(self):
        mif_data = self.env['kw_manpower_indent_form'].sudo().search([('id','=',self.mif_id.id)])
        # tree_view_id = self.env.ref("kw_recruitment.view_kw_manpower_indent_form_tree").id
        form_view_id = self.env.ref("kw_recruitment.view_kw_manpower_indent_form").id
        return {
            'name': 'Manpower Indent Form',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'views': [(form_view_id, 'form')],
            'res_model': 'kw_manpower_indent_form',
            'target': 'self',
            'res_id': mif_data.id,
            # 'domain': [('estimation_id', '=', self.estimation_id.id)],
            'context': {"create": False,"edit": False,"import":True},
            'flags' : {'mode':'readonly'}
        }
        
    def action_edit_mif(self):
        mif_data = self.env['kw_manpower_indent_form'].sudo().search([('id','=',self.mif_id.id)])
        # tree_view_id = self.env.ref("kw_recruitment.view_kw_manpower_indent_form_tree").id
        form_view_id = self.env.ref("kw_recruitment.view_kw_manpower_indent_form").id
        return {
            'name': 'Manpower Indent Form',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'views': [(form_view_id, 'form')],
            'res_model': 'kw_manpower_indent_form',
            'target': 'self',
            'res_id': mif_data.id,
            # 'domain': [('estimation_id', '=', self.estimation_id.id)],
            'context': {"create": False,"edit": True,"import":False},
            'flags' : {'mode':'edit'}
        }


    # def view_eq_resource(self):
    #     form_view_id = self.env.ref("kw_eq.kw_recruitment_eq_tm_mif_view_form").id
    #     return {
    #         'name': 'EQ Resource Details',
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'tree,form',
    #         'views': [(form_view_id, 'form')],
    #         'res_model': 'kw_recruitment_eq_tm_mif',
    #         'res_id': self.id,
    #         'target': 'self',
    #         'context': {"create": False,"edit": True,"import":True},
    #     }