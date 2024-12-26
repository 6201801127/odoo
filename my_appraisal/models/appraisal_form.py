# *******************************************************************************************************************
#  File Name             :   appraisal_form.py
#  Description           :   This is a model which is used to fill all details of appraisal for an employee
#  Created by            :   Ajay Kumar Ravidas
#  Created On            :   10-02-2023
#  Modified by           :
#  Modified On           :
#  Modification History  :
# *******************************************************************************************************************

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
import re


class EmployeeAppraisal(models.Model):
    
    _name = "employee.appraisal"
    _description = "Appraisal model"
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    _rec_name = "employee_id"

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    employee_id = fields.Many2one(comodel_name="hr.employee",default=_default_employee, string="Requested By")
    branch_id = fields.Many2one(comodel_name="res.branch", string="Branch")
    template_id = fields.Many2one('appraisal.template',string="Template", tracking=True)
    # compute='get_basic_details'
    apar_period_id = fields.Many2one(comodel_name="account.fiscalyear", string="APAR Period")
    app_ids = fields.One2many(comodel_name='targets.achievement',inverse_name='app_id', 
                              string='Targets/Achievement', tracking=True)
    kpia_ids = fields.One2many(comodel_name='appraisal.kpi',inverse_name='kpia_id', string='KPIA IDS', tracking=True)
    kpia_ids1 = fields.One2many(comodel_name='appraisal.kpi',inverse_name='kpia_id1', string='KPIA IDS', tracking=True)
    kpia_ids2 = fields.One2many(comodel_name='appraisal.kpi',inverse_name='kpia_id2', string='KPIA IDS', tracking=True)

    average1 = fields.Float(compute='compue_overal_rate')
    average2 = fields.Float(compute='compue_overal_rate')
    average3 = fields.Float(compute='compue_overal_rate')
    overall_rate_num = fields.Integer(string='Overall Rate', compute='compue_overal_rate', tracking=True)

    state = fields.Selection([('draft', 'Draft'), ('self_review', 'Pending'),('completed', 'Completed'), ('rejected', 'Rejected')], required=True,string="State", default='draft',tracking=True)
    immovatable_property = fields.Selection([('yes', 'Yes'),
                                       ('no', 'No '),
                              ],tracking=True)

    overall_grade = fields.Char(string='Grade')


    duties_description = fields.Text(string="Duties Description")
    targets = fields.Text(string='Targets', tracking=True)
    achievement = fields.Text(string='achievement', tracking=True)
    sortfalls = fields.Text(string='Short Falls', tracking=True)
    soh = fields.Text('State of Health', tracking=True)
    inte_general = fields.Text('Integrity', tracking=True)
    pen_picture = fields.Text('Pen Picture', tracking=True)
    pen_pic_rev = fields.Text('Pen Picture of review officer', tracking=True)
    dis_mod = fields.Text('Dis Mod', tracking=True)
    len_rev = fields.Text('Length Review', tracking=True)
    comment_oa = fields.Text('Please comment on the officer’s accessibility to the public and responsiveness to their needs', tracking=True)
    train_gen = fields.Text('Training ', tracking=True)
    ra_group_bool_check = fields.Boolean("RA Check", compute="_compute_boolean")
    review_group_bool_check = fields.Boolean("Reviewer Check", compute="_compute_boolean")
    manager_group_bool_check = fields.Boolean("Manager Check", compute="_compute_boolean")


    @api.depends()
    def _compute_boolean(self):
        if self.env.user.has_group('my_appraisal.appraisal_reporting_authority_group_id'):
            self.ra_group_bool_check = True
        else: 
            self.ra_group_bool_check = False

        if self.env.user.has_group('my_appraisal.appraisal_reviewing_authority_group_id'):
            self.review_group_bool_check = True
        else: 
            self.review_group_bool_check = False
        if self.env.user.has_group('my_appraisal.appraisal_manager_group_id'):
            self.manager_group_bool_check = True
        else: 
            self.manager_group_bool_check = False


    @api.model
    def create(self, vals):
        kpi_kpa = []
        kpi_kpa1 = []
        kpi_kpa2 = []
        # count = 0
        res =super(EmployeeAppraisal, self).create(vals)
      
        for i in res.template_id.kpi_kpa_ids:
            kpi_kpa.append((0, 0, {
                'kpia_id': res.id,
                'kpi': i.kpi,
                'kra': i.kra,
            }))
        for j in res.template_id.kpi_kpa_ids1:
            kpi_kpa1.append((0, 0, {
                'kpia_id1': res.id,
                'kpi': j.kpi,
                'kra': j.kra,
            }))
        for k in res.template_id.kpi_kpa_ids2:
            kpi_kpa2.append((0, 0, {
                'kpia_id2': res.id,
                'kpi': k.kpi,
                'kra': k.kra,
            }))
        res.kpia_ids = kpi_kpa
        res.kpia_ids1 = kpi_kpa1
        res.kpia_ids2 = kpi_kpa2
        email1 = res.employee_id.work_email
        name = res.employee_id.name
        template = self.env.ref('my_appraisal.create_appraisal_email_template_id')
        template.with_context(email_to=email1,names=name).send_mail(res.id)
        return res
    

    @api.depends('kpia_ids','kpia_ids1','kpia_ids2')
    def compue_overal_rate(self):
        for rec in self:
            divisor = len(rec.kpia_ids)
            total_reviewing_auth_weightage = 0
            total_reviewing_auth_weightage1 = 0
            total_reviewing_auth_weightage2 = 0
            total_avg = 0
            overall_weight = 0
            print("rec.kpia_idsrec.kpia_ids", rec.kpia_ids)
            for line in rec.kpia_ids:
                if line.reviewing_auth:
                    print('reclines', line.reviewing_auth)
                    total_reviewing_auth_weightage += int(line.reviewing_auth)
            print("total_reviewing_auth_weightage", total_reviewing_auth_weightage)
            # 5/0
            rec.average1 = ((int(total_reviewing_auth_weightage)/4)*0.4)
            for line1 in rec.kpia_ids1:
                if line1.reviewing_auth:
                    total_reviewing_auth_weightage1 += int(line1.reviewing_auth)
            rec.average2 = ((int(total_reviewing_auth_weightage1)/3)*0.3)
            for line2 in rec.kpia_ids2:
                if line2.reviewing_auth:
                    total_reviewing_auth_weightage2 += int(line2.reviewing_auth)
            rec.average3 = ((int(total_reviewing_auth_weightage2)/3)*0.3)
            overall_weight = rec.average1 + rec.average2 + rec.average3
            rec.overall_rate_num = int(overall_weight)
            over_rate = self.env['appraisal.rating'].sudo().search([('from_int', '<=', rec.overall_rate_num), ('to_int', '>=', rec.overall_rate_num)], limit=1)
            rec.overall_grade = over_rate.name

    def button_self_reviewed(self):
        for rec in self:
            # print("0--------------------", rec.app_ids)
            if not rec.app_ids and rec.state == 'draft':
                raise ValidationError(
                    "Please enter the targets before further proceedings.")
            rec.write({'state': 'self_review'})
            for line in rec.kpia_ids:
                line.write({'state': 'self_review'})
            for line1 in rec.kpia_ids1:
                line1.write({'state': 'self_review'})
            for line2 in rec.kpia_ids2:
                line2.write({'state': 'self_review'})
            return {
                'name': 'My Appraisal - Draft',
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'employee.appraisal',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'view_id': self.env.ref('my_appraisal.appraisal_view_tree').id,
                'domain': [('state','=','draft')],
                }

    def button_reporting_authority_reviewed(self):
        for rec in self:
            if rec.state == 'self_review':
                for line in rec.kpia_ids:
                    if not line.reporting_auth:
                        raise ValidationError("Please enter the reporting officer Scores before further proceedings.")
                for line1 in rec.kpia_ids1:
                    if not line1.reporting_auth:
                        raise ValidationError("Please enter the  reporting officer scores before further proceedings.")
                for line2 in rec.kpia_ids2:
                    if not line2.reporting_auth:
                        raise ValidationError("Please enter the  reporting officer scores before further proceedings.")
            rec.write({'state': 'completed'})
            for line in rec.kpia_ids:
                line.write({'state': 'completed'})
            for line1 in rec.kpia_ids1:
                line1.write({'state': 'completed'})
            for line2 in rec.kpia_ids2:
                line2.write({'state': 'completed'})
            return {
                'name': 'My Appraisal - Self Reviewed',
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'employee.appraisal',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'view_id': self.env.ref('my_appraisal.appraisal_view_tree').id,
                'domain': [('state','=','self_review')],
                }
    def button_completed(self):
         for rec in self:
            for line in rec.kpia_ids:
                avg = (int(line.reporting_auth) + int(line.reviewing_auth))/2
                rec.overall_rate_num = int(avg)
            over_rate = self.env['appraisal.rating'].sudo().search([('from_int', '<=', rec.overall_rate_num), ('to_int', '>=', rec.overall_rate_num)], limit=1)
            rec.overall_grade = over_rate.name
            rec.write({'state': 'completed'})
            for line in rec.kpia_ids:
                line.write({'state': 'completed'})
            for line1 in rec.kpia_ids1:
                line1.write({'state': 'completed'})
            for line2 in rec.kpia_ids2:
                line2.write({'state': 'completed'})
            return {
                'name': 'My Appraisal - Reviewing Authority Reviewed',
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'employee.appraisal',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'view_id': self.env.ref('my_appraisal.appraisal_view_tree').id,
                'domain': [('state','=','reviewing_authority_review')],
                }
    def button_reject(self):
        for rec in self:
            rec.write({'state': 'rejected'})
            for line in rec.kpia_ids:
                line.write({'state': 'rejected'})
            for line1 in rec.kpia_ids1:
                line1.write({'state': 'rejected'})
            for line2 in rec.kpia_ids2:
                line2.write({'state': 'rejected'})

    def button_raised_query(self):
        action = {
            'name': 'My Appraisal - Raise Query',
            # 'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'appraisal.raisequery',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'view_id': self.env.ref('my_appraisal.appraisal_raisequery_view_form').id,
            }
        return action
    
    @api.constrains('duties_description','sortfalls')
    @api.onchange('duties_description','sortfalls')
    def _onchnage_duties_description(self):
        if self.duties_description and re.match(r'^[\s]*$', str(self.duties_description)):
            raise ValidationError("Duties description field not allow only white spaces")
        if self.duties_description and not re.match(r'^[A-Za-z ]*$',str(self.duties_description)):
            raise ValidationError("Duties description field not allow special and numeric characters")
        if self.sortfalls and re.match(r'^[\s]*$', str(self.sortfalls)):
            raise ValidationError("Sortfalls field not allow only white spaces")
        if self.sortfalls and not re.match(r'^[A-Za-z ]*$',str(self.sortfalls)):
            raise ValidationError("Sortfalls field not allow special and numeric characters")

    class TargetsAchievement(models.Model):
        _name = 'targets.achievement'
        _description = 'Achievements'

        app_id = fields.Many2one(comodel_name='employee.appraisal', string='Appraisal ID')
        targets = fields.Text('Targets')
        achievements = fields.Text('Achievements')

        @api.constrains('targets')
        @api.onchange('targets',)
        def _onchnage_targets(self):
            if self.targets and re.match(r'^[\s]*$', str(self.targets)):
                raise ValidationError("Target field not allow only white spaces")
            if self.targets and not re.match(r'^[A-Za-z ]*$',str(self.targets)):
                raise ValidationError("Target field not allow special and numeric characters")
       
        @api.constrains('achievements')
        @api.onchange('achievements')
        def _onchnage_achievements(self):
            if self.achievements and re.match(r'^[\s]*$', str(self.achievements)):
                raise ValidationError("Achievements field not allow only white spaces")
            if self.achievements and not re.match(r'^[A-Za-z ]*$',str(self.achievements)):
                raise ValidationError("Achievement field not allow special and numeric characters")


    class KPIForm(models.Model):
        _name = 'appraisal.kpi'
        _description = 'KPI Forms'

        kpia_id = fields.Many2one(comodel_name='appraisal.main', string='KPIA IDS')
        kpia_id1 = fields.Many2one(comodel_name='appraisal.main', string='KPIA IDS')
        kpia_id2 = fields.Many2one(comodel_name='appraisal.main', string='KPIA IDS')
        kpi = fields.Char('KPI')
        kra = fields.Char('KRA')
        reporting_auth_remarks = fields.Text(string="Reporting Auth Remarks")
        reviewing_auth_remarks = fields.Text(string="Reviewing Auth Remarks")
        reporting_auth = fields.Selection([('1', '1'),
                                    ('2', '2'),
                                    ('3', '3'),
                                    ('4', '4'),
                                    ('5', '5'),
                                    ('6', '6'),
                                    ('7', '7'),
                                    ('8', '8'),
                                    ('9', '9'),
                                    ('10', '10'),
                                        ], 'Reporting Authority')
        weightage = fields.Float()
        score = fields.Float()
        reviewing_auth = fields.Selection([('1', '1'),
                                    ('2', '2'),
                                    ('3', '3'),
                                    ('4', '4'),
                                    ('5', '5'),
                                    ('6', '6'),
                                    ('7', '7'),
                                    ('8', '8'),
                                    ('9', '9'),
                                    ('10', '10'),], 'Reviewing Authority')
        state = fields.Selection(
            [('draft', 'Draft'), ('self_review', 'Self Reviewed'), ('reporting_authority_review', 'Reporting Authority Reviewed '),
            ('reviewing_authority_review', 'Reviewing Authority Reviewed'), ('completed', 'Completed'), ('rejected', 'Rejected')
            ],default='draft', string='Status')
        weightage_comp = fields.Float('weightage', compute='get_kpi_weightage')
        weightage_int = fields.Integer('Weightage',  compute='get_kpi_weightage')
        reviewing_auth_user = fields.Many2one('res.users', store=True)
        average = fields.Integer('Average')
        ra_group_bool_check = fields.Boolean("RA Check", compute="_compute_boolean")
        review_group_bool_check = fields.Boolean("Reviewer Check", compute="_compute_boolean")


        @api.depends()
        def _compute_boolean(self):
            if self.env.user.has_group('my_appraisal.appraisal_reporting_authority_group_id'):
                self.ra_group_bool_check = True
            else: 
                self.ra_group_bool_check = False

            if self.env.user.has_group('my_appraisal.appraisal_reviewing_authority_group_id'):
                self.review_group_bool_check = True
            else: 
                self.review_group_bool_check = False


        @api.model
        def get_kpi_weightage(self):
            for rec in self:
                kpis_ids = self.env['appraisal.template.o2m'].search([('kpi', '=', rec.kpi)], limit=1)
                for rec_line in kpis_ids:
                    rec.weightage_comp = rec_line.weigtage
                    rec.weightage_int = int(rec_line.weigtage)
                # print(rec,rec.weightage_comp)