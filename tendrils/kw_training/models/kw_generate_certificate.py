from odoo import models, fields,api
from odoo.exceptions import UserError, ValidationError




class TrainingcertificateGenerate(models.Model):
    _name = 'kw_training_certificate_generate'
    _description = 'Training Completion and Certificate'
    _rec_name = 'training_id'

   
    course_type_id = fields.Many2one('kw_skill_type_master',string="Course Type",required=True,store= True)
    course_id = fields.Many2one('kw_skill_master',string="Course",required=True ,store= True)
    financial_year = fields.Many2one("account.fiscalyear",string='Financial Year', store= True)
    training_id = fields.Many2one("kw_training",string='Training',ondelete="restrict", store= True)
    start_date =  fields.Date('Start Date', store= True)
    end_date = fields.Date('End Date',store= True)
    instructor_type = fields.Char('Instructor Type',store= True)

    skill_answer_id = fields.Many2one('kw_skill_answer_master', string='Skill Answer', store=True)
    score_percentage = fields.Float(string='Score Percentage', store=True)

    trainee_id = fields.Many2one('hr.employee',string="Trainee", store=True)


    status = fields.Selection([('1', 'Sent'), ('0', 'Draft')], string="Status",default='0')




    @api.depends('skill_answer_id.percentage_scored')
    def _compute_score_percentage(self):
        for record in self:
            if record.skill_answer_id:
                record.score_percentage = record.skill_answer_id.percentage_scored


    @api.model
    def create(self, vals):
        if 'skill_answer_id' in vals:
            skill_answer = self.env['kw_skill_answer_master'].browse(vals['skill_answer_id'])
            if skill_answer:
                vals['score_percentage'] = skill_answer.percentage_scored
        
        return super(TrainingcertificateGenerate, self).create(vals)

    def generated_certificate_download(self):
        return {
            'type': 'ir.actions.act_url',
            'url': f'/get-generated-certificate-details/{self.id}/{self.trainee_id.id}',
            'target': 'new',
        }

    def send_certificate_email(self):
        if self.status == '1':
            raise UserError("You have already sent the email for this certificate.")
        template_id = self.env.ref('kw_training.training_certification_mail_template')
        if template_id :
            # manager_group = self.env.ref('kw_training.group_kw_training_manager').users
            # email_cc = ','.join(manager_group.mapped('email'))
            template_id.with_context(record_id=self.id,employee_id=self.trainee_id.id,training_name=self.training_id.name).send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light")
            self.status = "1"
            self.env.user.notify_success("Mail Sent successfully.")

   
    
   

    