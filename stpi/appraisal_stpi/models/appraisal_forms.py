from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, timedelta

class AppraisalForms(models.Model):
    _name = 'appraisal.main'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Appraisal'


    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    employee_id = fields.Many2one('hr.employee', default=_default_employee, track_visibility='always')
    appraisal_sequence = fields.Char(string='Appraisal Sequence', track_visibility='always')
    abap_period = fields.Many2one('date.range', string='APAR Period', track_visibility='always')
    branch_id = fields.Many2one('res.branch', string='Branch', compute='get_basic_details', store=True, track_visibility='always')
    category_id = fields.Many2one('employee.category', string='Category', compute='get_basic_details', track_visibility='always')
    dob = fields.Date(string='Date of Birth', compute='get_basic_details', track_visibility='always')
    job_id = fields.Many2one('hr.job', string='Functional Designation', compute='get_basic_details', track_visibility='always')
    struct_id = fields.Many2one('hr.payroll.structure', string='Salary Structure', compute='get_basic_details', track_visibility='always')
    pay_level_id = fields.Many2one('hr.payslip.paylevel', string='Pay Level', compute='get_basic_details', track_visibility='always')
    pay_level = fields.Many2one('payslip.pay.level', string='Pay Cell', compute='get_basic_details', track_visibility='always')
    template_id = fields.Many2one('appraisal.template', track_visibility='always', compute='get_basic_details')
    duties_description = fields.Text(string='Duties Description', track_visibility='always')
    targets = fields.Text(string='Targets', track_visibility='always')
    achievement = fields.Text(string='achievement', track_visibility='always')
    sortfalls = fields.Text(string='Short Falls', track_visibility='always')
    # immovatable_property = fields.Text(string='immovatable_property', track_visibility='always')
    immovatable_property = fields.Selection([('yes', 'Yes'),
                                       ('no', 'No'),
                              ], track_visibility='always')
    comment_oa = fields.Text('Please comment on the officer’s accessibility to the public and responsiveness to their needs', track_visibility='always')
    train_gen = fields.Text('Training', track_visibility='always')
    soh = fields.Text('State of Health', track_visibility='always')
    inte_general = fields.Text('Integrity', track_visibility='always')
    pen_picture = fields.Text('Pen Picture', track_visibility='always')
    len_rev = fields.Text('Length Review', track_visibility='always')
    ag_no = fields.Selection([('yes', 'Yes'),
                                       ('no', 'No'),
                              ], 'Ag No', track_visibility='always')
    agree_dis = fields.Selection([('Agreed', 'Agreed'),
                                       ('Disagree', 'Disagree'),
                              ], 'Agreed?', default='Agreed', track_visibility='always')
    dis_mod = fields.Text('Dis Mod', track_visibility='always')
    If_not_happy = fields.Text('If not happy, Query')
    pen_pic_rev = fields.Text('Pen Picture of review officer', track_visibility='always')
    overall_rate_num = fields.Integer('Overall Rate', compute='compue_overal_rate', track_visibility='always')
    overall_grade = fields.Char('Grade')
    kpia_ids = fields.One2many('appraisal.kpi','kpia_id', string='KPIA IDS', track_visibility='always')
    kpia_ids1 = fields.One2many('appraisal.kpi','kpia_id1', string='KPIA IDS', track_visibility='always')
    kpia_ids2 = fields.One2many('appraisal.kpi','kpia_id2', string='KPIA IDS', track_visibility='always')
    average1 = fields.Float(compute='compue_overal_rate')
    average2 = fields.Float(compute='compue_overal_rate')
    average3 = fields.Float(compute='compue_overal_rate')
    app_ids = fields.One2many('targets.achievement','app_id', string='Targets/Achievement', track_visibility='always')
    state = fields.Selection([('draft', 'Draft'), ('self_review', 'Pending'), ('reporting_authority_review', 'Assesst by reporting officer'),
                              ('reviewing_authority_review', 'Assesst by reviewing officer'), ('completed', 'Completed'), ('raise_query', 'Raise Query'), ('rejected', 'Rejected')
                              ], required=True, default='draft', track_visibility='always')
    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")


    @api.depends('kpia_ids','kpia_ids1','kpia_ids2')
    def compue_overal_rate(self):
        for rec in self:
            divisor = len(rec.kpia_ids)
            total_reviewing_auth_weightage = 0
            total_reviewing_auth_weightage1 = 0
            total_reviewing_auth_weightage2 = 0
            total_avg = 0
            overall_weight = 0
            for line in rec.kpia_ids:
                if line.reviewing_auth:
                    total_reviewing_auth_weightage += int(line.reviewing_auth)
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
            # for line in rec.kpia_ids:
            #     line.average = (((int(line.reporting_auth)+int(line.reviewing_auth))/2)/line.weightage_comp)*100
            #     total_avg += int(line.average)
            # overall_weight = (total_avg/13)/10
            # rec.overall_rate_num = int(overall_weight)
            # for line in rec.kpia_ids:
            #     total_reporting_auth_weightage += int(line.reporting_auth)
            #     total_reviewing_auth_weightage += int(line.reviewing_auth)
            #     # avg = (int(line.reporting_auth) + int(line.reviewing_auth))/2
            #     # rec.overall_rate_num = int(avg)
            # if divisor:
            #     weightage = ((total_reporting_auth_weightage / divisor) + (total_reviewing_auth_weightage / divisor)) / 2
                # rec.overall_rate_num = int(weightage)
            over_rate = self.env['overall.rate'].sudo().search([('from_int', '<=', rec.overall_rate_num), ('to_int', '>=', rec.overall_rate_num)], limit=1)
            rec.overall_grade = over_rate.name


    @api.multi
    @api.depends('employee_id')
    def get_basic_details(self):
        for rec in self:
            rec.category_id = rec.employee_id.category.id
            # rec.dob = rec.employee_id.birthday
            rec.job_id = rec.employee_id.job_id.id
            rec.branch_id = rec.employee_id.branch_id.id
            emp_contract = self.env['hr.contract'].sudo().search([('employee_id', '=', rec.employee_id.id), ('state', '=', 'open')], limit=1)
            rec.struct_id = emp_contract.struct_id.id
            rec.pay_level_id = emp_contract.pay_level_id.id
            rec.template_id = rec.employee_id.job_id.template_id.id
            rec.pay_level = emp_contract.pay_level.id
            # kpi_kpa = []
            # for i in rec.template_id.kpi_kpa_ids:
            #     kpi_kpa.append((0, 0, {
            #         'kpia_id': rec.id,
            #         'kpi': i.kpi,
            #         'kra': i.kra,
            #     }))
            # rec.kpia_ids = kpi_kpa    


    @api.multi
    def print_appraisal_form(self):
        if self.agree_dis=='Disagree':
            return self.env.ref('appraisal_stpi.annex_form2_disagreed_id').report_action(self)
        else:
            return self.env.ref('appraisal_stpi.appraisal_form1_agreed_id').report_action(self)


    @api.model
    def create(self, vals):
        kpi_kpa = []
        kpi_kpa1 = []
        kpi_kpa2 = []
        count = 0
        res =super(AppraisalForms, self).create(vals)
        search_id = self.env['appraisal.main'].search(
            [('abap_period', '=', res.abap_period.id),('employee_id', '=', res.employee_id.id),('state', '!=', 'rejected')])
        if search_id:
            for emp in search_id:
                if emp:
                    print('===================emp=========================', emp.id)
                    count+=1
        print('===================count=========================', count)
        if count > 1:
            raise ValidationError(_('Appraisal already made of {name} for ABAP period {abap}').format(
                name=res.employee_id.name,abap=res.abap_period.name))
        if not res.template_id.id:
            pass
            # raise ValidationError(_('Please select Template of {name}').format(
            # name=res.employee_id.name))
        sequence = ''
        seq = self.env['ir.sequence'].next_by_code('appraisal.main')
        sequence = str(res.employee_id.name) + ' - Appraisal - ' + str(seq)
        res.appraisal_sequence = sequence
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
        return res

    @api.multi
    @api.depends('appraisal_sequence')
    def name_get(self):
        res = []
        for record in self:
            if record.appraisal_sequence:
                name = record.appraisal_sequence
            else:
                name = 'Appraisal'
            res.append((record.id, name))
        return res

    @api.multi
    def button_self_reviewed(self):
        for rec in self:
            print("0--------------------", rec.app_ids)
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
                'res_model': 'appraisal.main',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'view_id': self.env.ref('appraisal_stpi.hr_appraisal_main_tree_view').id,
                'domain': [('state','=','draft')],
                }

    @api.multi
    def button_reporting_authority_reviewed(self):
        print("called")
        for rec in self:
            if rec.state == 'self_review':
                for line in rec.kpia_ids:
                    if not line.reporting_auth:
                        raise ValidationError("Please enter the Reviewing Scores before further proceedings.")
                for line1 in rec.kpia_ids1:
                    if not line1.reporting_auth:
                        raise ValidationError("Please enter the  Reviewing Scores before further proceedings.")
                for line2 in rec.kpia_ids2:
                    if not line2.reporting_auth:
                        raise ValidationError("Please enter the  Reviewing Scores before further proceedings.")
            rec.write({'state': 'reporting_authority_review'})
            for line in rec.kpia_ids:
                line.write({'state': 'reporting_authority_review'})
            for line1 in rec.kpia_ids1:
                line1.write({'state': 'reporting_authority_review'})
            for line2 in rec.kpia_ids2:
                line2.write({'state': 'reporting_authority_review'})
            return {
                'name': 'My Appraisal - Self Reviewed',
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'appraisal.main',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'view_id': self.env.ref('appraisal_stpi.hr_appraisal_main_tree_view').id,
                'domain': [('state','=','self_review')],
                }

    @api.multi
    def button_reviewing_authority_reviewed(self):
        for rec in self:
            if rec.state == 'reporting_authority_review':
                for line in rec.kpia_ids:
                    if not line.reviewing_auth:
                        raise ValidationError("Please enter the Reviewing Scores before further proceedings.")
                for line1 in rec.kpia_ids1:
                    if not line1.reviewing_auth:
                        raise ValidationError("Please enter the  Reviewing Scores before further proceedings.")
                for line2 in rec.kpia_ids2:
                    if not line2.reviewing_auth:
                        raise ValidationError("Please enter the  Reviewing Scores before further proceedings.")
            rec.write({'state': 'reviewing_authority_review'})
            for line in rec.kpia_ids:
                line.write({'state': 'reviewing_authority_review'})
                line.write({'reviewing_auth_user': rec.env.uid})
            for line1 in rec.kpia_ids1:
                line1.write({'state': 'reviewing_authority_review'})
                line1.write({'reviewing_auth_user': rec.env.uid})
            for line2 in rec.kpia_ids2:
                line2.write({'state': 'reviewing_authority_review'})
                line2.write({'reviewing_auth_user': rec.env.uid})
            return {
                'name': 'My Appraisal - Reporting Authority Reviewed',
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'appraisal.main',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'view_id': self.env.ref('appraisal_stpi.hr_appraisal_main_tree_view').id,
                'domain': [('state','=','reporting_authority_review')],
                }

    @api.multi
    def button_completed(self):
        for rec in self:
            for line in rec.kpia_ids:
                avg = (int(line.reporting_auth) + int(line.reviewing_auth))/2
                rec.overall_rate_num = int(avg)
            over_rate = self.env['overall.rate'].sudo().search([('from_int', '<=', rec.overall_rate_num), ('to_int', '>=', rec.overall_rate_num)], limit=1)
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
                'res_model': 'appraisal.main',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'view_id': self.env.ref('appraisal_stpi.hr_appraisal_main_tree_view').id,
                'domain': [('state','=','reviewing_authority_review')],
                }

    @api.multi
    def button_reject(self):
        for rec in self:
            rec.write({'state': 'rejected'})
            for line in rec.kpia_ids:
                line.write({'state': 'rejected'})
            for line1 in rec.kpia_ids1:
                line1.write({'state': 'rejected'})
            for line2 in rec.kpia_ids2:
                line2.write({'state': 'rejected'})


    @api.multi
    def button_raised_query(self):
        for rec in self:
            rec.write({'state': 'raise_query'})
            for line in rec.kpia_ids:
                line.write({'state': 'raise_query'})
            for line1 in rec.kpia_ids1:
                line1.write({'state': 'raise_query'})
            for line2 in rec.kpia_ids2:
                line2.write({'state': 'raise_query'})
    @api.multi
    def agreed(self):
        for rec in self:
            rec.agree_dis = 'Agreed'

    @api.multi
    def disagree(self):
        for rec in self:
            rec.agree_dis = 'Disagree'


class KPIForm(models.Model):
    _name = 'appraisal.kpi'
    _description = 'KPI Forms'

    kpia_id = fields.Many2one('appraisal.main', string='KPIA IDS')
    kpia_id1 = fields.Many2one('appraisal.main', string='KPIA IDS')
    kpia_id2 = fields.Many2one('appraisal.main', string='KPIA IDS')
    kpi = fields.Char('KPI')
    kra = fields.Char('KRA')
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
        [('draft', 'Draft'), ('self_review', 'Self Reviewed'), ('reporting_authority_review', 'Reporting Authority Reviewed'),
         ('reviewing_authority_review', 'Reviewing Authority Reviewed'), ('completed', 'Completed'), ('raise_query', 'Raise Query'), ('rejected', 'Rejected')
         ],default='draft', string='Status')
    weightage_comp = fields.Float('weightage', compute='get_kpi_weightage')
    weightage_int = fields.Integer('Weightage',  compute='get_kpi_weightage')
    reviewing_auth_user = fields.Many2one('res.users', store=True)
    average = fields.Integer('Average')


    @api.multi
    def get_kpi_weightage(self):
        for rec in self:
            kpis_ids = self.env['appraisal.template.o2m'].search([('kpi', '=', rec.kpi)], limit=1)
            for rec_line in kpis_ids:
                rec.weightage_comp = rec_line.weigtage
                rec.weightage_int = int(rec_line.weigtage)
            print(rec,rec.weightage_comp)

    @api.onchange('reporting_auth')
    def _onchange_validation_report(self):
        for rec in self:
            print(float(rec.reporting_auth))
            if rec.reporting_auth:
                rec.reviewing_auth = rec.reporting_auth
                
    # @api.onchange('reviewing_auth')
    # def _onchange_validation_review(self):
    #     for rec in self:
    #         print(float(rec.reviewing_auth))
    #         if float(rec.reviewing_auth) > rec.weightage_comp:
    #             raise ValidationError(
    #                 "Reviewing Authority weightage must be as per the weightage defined in the master configuration.")
    
    # @api.depends('reviewing_auth')
    # def get_user_name(self):
    #     for rec in self:
    #         rec.reviewing_auth_user = rec.env.uid



class TargetsAchievement(models.Model):
    _name = 'targets.achievement'
    _description = 'Achievements'

    app_id = fields.Many2one('appraisal.main', string='Appraisal ID')
    targets = fields.Char('Targets')
    achievements = fields.Char('Achievements')



class HrPaySlip(models.Model):
    _inherit='hr.payslip.paylevel'

    template_id = fields.Many2one('appraisal.template')
