# *******************************************************************************************************************
#  File Name             :   appraisal_form.py
#  Description           :   This is a model which is used to fill all details of appraisal for an employee in BSSCL
#  Created by            :   Ajay Kumar Ravidas
#  Created On            :   10-02-2023
#  Modified by           :
#  Modified On           :
#  Modification History  :
# *******************************************************************************************************************

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
import re


class BssclEmployeeAppraisal(models.Model):
    
    _name = "bsscl.employee.appraisal"
    _description = "BSSCL Appraisal model"
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    _rec_name = "employee_id"

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    # *****************************************All relational ***************************************************
    employee_id = fields.Many2one(comodel_name="hr.employee",default=_default_employee, string="Requested By / द्वारा अनुरोध किया गया")
    branch_id = fields.Many2one(comodel_name="res.branch", string="Branch / शाखा")
    template_id = fields.Many2one('appraisal.template',string="Template / खाका", tracking=True)
    # compute='get_basic_details'
    apar_period_id = fields.Many2one(comodel_name="account.fiscalyear", string="APAR Period / एपीएआर अवधि")
    app_ids = fields.One2many(comodel_name='targets.achievement',inverse_name='app_id', 
                              string='Targets/Achievement / लक्ष्य/उपलब्धि', tracking=True)
    kpia_ids = fields.One2many(comodel_name='appraisal.kpi',inverse_name='kpia_id', string='KPIA IDS / केपीआईए आईडीएस', tracking=True)
    kpia_ids1 = fields.One2many(comodel_name='appraisal.kpi',inverse_name='kpia_id1', string='KPIA IDS / केपीआईए आईडीएस', tracking=True)
    kpia_ids2 = fields.One2many(comodel_name='appraisal.kpi',inverse_name='kpia_id2', string='KPIA IDS / केपीआईए आईडीएस', tracking=True)

    #********************Float Fields ******************************************
    average1 = fields.Float(compute='compue_overal_rate')
    average2 = fields.Float(compute='compue_overal_rate')
    average3 = fields.Float(compute='compue_overal_rate')
    overall_rate_num = fields.Integer(string='Overall Rate / समग्र कीमत', compute='compue_overal_rate', tracking=True)

    # ***********All Selection Fields Start from here *******************************
    # state = fields.Selection([('draft', 'Draft / प्रारूप'), ('self_review', 'Pending / लंबित'), ('reporting_authority_review', 'Assesst by reporting officer / रिपोर्टिंग अधिकारी द्वारा मूल्यांकन करें'),('reviewing_authority_review', 'Assesst by reviewing officer / समीक्षा अधिकारी द्वारा आकलन करें'), ('completed', 'Completed / पुरा होना।'), ('rejected', 'Rejected / अस्वीकार कर दिया')], required=True,string="State / स्थिति", default='draft',tracking=True)
    state = fields.Selection([('draft', 'Draft / प्रारूप'), ('self_review', 'Pending / लंबित'),('completed', 'Completed / पुरा होना।'), ('rejected', 'Rejected / अस्वीकार कर दिया')], required=True,string="State / स्थिति", default='draft',tracking=True)
    immovatable_property = fields.Selection([('yes', 'Yes / हाँ'),
                                       ('no', 'No / नहीं'),
                              ],tracking=True)

    # ********************All Charactor************************
    overall_grade = fields.Char(string='Grade / श्रेणी')


    # ********************All Text fields *********************************
    duties_description = fields.Text(string="Duties Description / कर्तव्य विवरण")
    targets = fields.Text(string='Targets / लक्ष्यों को', tracking=True)
    achievement = fields.Text(string='achievement / उपलब्धि', tracking=True)
    sortfalls = fields.Text(string='Short Falls / शॉर्ट फॉल्स', tracking=True)
    soh = fields.Text('State of Health / सेहत की स्थिति', tracking=True)
    inte_general = fields.Text('Integrity / अखंडता', tracking=True)
    pen_picture = fields.Text('Pen Picture / कलम चित्र', tracking=True)
    pen_pic_rev = fields.Text('Pen Picture of review officer / समीक्षा अधिकारी का पेन चित्र', tracking=True)
    dis_mod = fields.Text('Dis Mod / डिस मॉड', tracking=True)
    # query_remarks = fields.Text(string="Raise Query By Manager / प्रबंधक द्वारा प्रश्न उठाएं")
    len_rev = fields.Text('Length Review / लंबाई समीक्षा', tracking=True)
    comment_oa = fields.Text('Please comment on the officer’s accessibility to the public and responsiveness to their needs / कृपया जनता तक अधिकारी की पहुंच और उनकी जरूरतों के प्रति जवाबदेही पर टिप्पणी करें', tracking=True)
    train_gen = fields.Text('Training / प्रशिक्षण', tracking=True)
    ra_group_bool_check = fields.Boolean("RA Check", compute="_compute_boolean")
    review_group_bool_check = fields.Boolean("Reviewer Check", compute="_compute_boolean")
    manager_group_bool_check = fields.Boolean("Manager Check", compute="_compute_boolean")


    @api.depends()
    def _compute_boolean(self):
        if self.env.user.has_group('bsscl_employee_appraisal.appraisal_reporting_authority_group_id'):
            self.ra_group_bool_check = True
        else: 
            self.ra_group_bool_check = False

        if self.env.user.has_group('bsscl_employee_appraisal.appraisal_reviewing_authority_group_id'):
            self.review_group_bool_check = True
        else: 
            self.review_group_bool_check = False
        if self.env.user.has_group('bsscl_employee_appraisal.appraisal_manager_group_id'):
            self.manager_group_bool_check = True
        else: 
            self.manager_group_bool_check = False


    @api.model
    def create(self, vals):
        kpi_kpa = []
        kpi_kpa1 = []
        kpi_kpa2 = []
        # count = 0
        res =super(BssclEmployeeAppraisal, self).create(vals)
      
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
        template = self.env.ref('bsscl_employee_appraisal.create_appraisal_email_template_id')
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
                if line.reporting_auth:
                    print('reclines', line.reporting_auth)
                    total_reviewing_auth_weightage += int(line.reporting_auth)
            print("total_reviewing_auth_weightage", total_reviewing_auth_weightage)
            # 5/0
            rec.average1 = ((int(total_reviewing_auth_weightage)/4)*0.4)
            for line1 in rec.kpia_ids1:
                if line1.reporting_auth:
                    total_reviewing_auth_weightage1 += int(line1.reporting_auth)
            rec.average2 = ((int(total_reviewing_auth_weightage1)/3)*0.3)
            for line2 in rec.kpia_ids2:
                if line2.reporting_auth:
                    total_reviewing_auth_weightage2 += int(line2.reporting_auth)
            rec.average3 = ((int(total_reviewing_auth_weightage2)/3)*0.3)
            overall_weight = rec.average1 + rec.average2 + rec.average3
            rec.overall_rate_num = int(overall_weight)
            over_rate = self.env['appraisal.rating'].sudo().search([('from_int', '<=', rec.overall_rate_num), ('to_int', '>=', rec.overall_rate_num)], limit=1)
            rec.overall_grade = over_rate.name

    # *********************Call these methods by button click *******************************
    def button_self_reviewed(self):
        for rec in self:
            print("0--------------------", rec.app_ids)
            if not rec.app_ids and rec.state == 'draft':
                raise ValidationError(
                    "Please enter the targets before further proceedings. / आगे की कार्यवाही से पहले कृपया लक्ष्य दर्ज करें।")
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
                'res_model': 'bsscl.employee.appraisal',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'view_id': self.env.ref('bsscl_employee_appraisal.appraisal_view_tree').id,
                'domain': [('state','=','draft')],
                }

    def button_reporting_authority_reviewed(self):
        for rec in self:
            if rec.state == 'self_review':
                for line in rec.kpia_ids:
                    if not line.reporting_auth:
                        raise ValidationError("Please enter the reporting officer Scores before further proceedings. / आगे की कार्यवाही से पहले कृपया रिपोर्टिंग अधिकारी स्कोर दर्ज करें।")
                for line1 in rec.kpia_ids1:
                    if not line1.reporting_auth:
                        raise ValidationError("Please enter the  reporting officer scores before further proceedings. / कृपया आगे की कार्यवाही से पहले रिपोर्टिंग अधिकारी स्कोर दर्ज करें।")
                for line2 in rec.kpia_ids2:
                    if not line2.reporting_auth:
                        raise ValidationError("Please enter the  reporting officer scores before further proceedings. / कृपया आगे की कार्यवाही से पहले रिपोर्टिंग अधिकारी स्कोर दर्ज करें। ")
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
                'res_model': 'bsscl.employee.appraisal',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'view_id': self.env.ref('bsscl_employee_appraisal.appraisal_view_tree').id,
                'domain': [('state','=','self_review')],
                }
    # def button_reviewing_authority_reviewed(self):
    #      for rec in self:
    #         if rec.state == 'reporting_authority_review':
    #             for line in rec.kpia_ids:
    #                 if not line.reviewing_auth:
    #                     raise ValidationError("Please enter the Reviewing Scores before further proceedings. / आगे की कार्यवाही से पहले कृपया समीक्षा स्कोर दर्ज करें।")
    #             for line1 in rec.kpia_ids1:
    #                 if not line1.reviewing_auth:
    #                     raise ValidationError("Please enter the  Reviewing Scores before further proceedings. / आगे की कार्यवाही से पहले कृपया समीक्षा स्कोर दर्ज करें।")
    #             for line2 in rec.kpia_ids2:
    #                 if not line2.reviewing_auth:
    #                     raise ValidationError("Please enter the  Reviewing Scores before further proceedings. / आगे की कार्यवाही से पहले कृपया समीक्षा स्कोर दर्ज करें।")
    #         rec.write({'state': 'reviewing_authority_review'})
    #         for line in rec.kpia_ids:
    #             line.write({'state': 'reviewing_authority_review'})
    #             line.write({'reviewing_auth_user': rec.env.uid})
    #         for line1 in rec.kpia_ids1:
    #             line1.write({'state': 'reviewing_authority_review'})
    #             line1.write({'reviewing_auth_user': rec.env.uid})
    #         for line2 in rec.kpia_ids2:
    #             line2.write({'state': 'reviewing_authority_review'})
    #             line2.write({'reviewing_auth_user': rec.env.uid})
    #         return {
    #             'name': 'My Appraisal - Reporting Authority Reviewed',
    #             'view_type': 'form',
    #             'view_mode': 'tree',
    #             'res_model': 'bsscl.employee.appraisal',
    #             'type': 'ir.actions.act_window',
    #             'target': 'current',
    #             'view_id': self.env.ref('bsscl_employee_appraisal.appraisal_view_tree').id,
    #             'domain': [('state','=','reporting_authority_review')],
    #             }

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
                'res_model': 'bsscl.employee.appraisal',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'view_id': self.env.ref('bsscl_employee_appraisal.appraisal_view_tree').id,
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
            'view_id': self.env.ref('bsscl_employee_appraisal.appraisal_raisequery_view_form').id,
            }
        return action
    
    # **************** (Duties description and sortfalls validation) ********************************
    @api.constrains('duties_description','sortfalls')
    @api.onchange('duties_description','sortfalls')
    def _onchnage_duties_description(self):
        if self.duties_description and re.match(r'^[\s]*$', str(self.duties_description)):
            raise ValidationError("Duties description field not allow only white spaces / कर्तव्यों का विवरण फ़ील्ड केवल सफेद रिक्त स्थान की अनुमति नहीं देता है")
        if self.duties_description and not re.match(r'^[A-Za-z ]*$',str(self.duties_description)):
            raise ValidationError("Duties description field not allow special and numeric characters  / कर्तव्यों का विवरण फ़ील्ड विशेष और संख्यात्मक वर्णों की अनुमति नहीं देता है")
        if self.sortfalls and re.match(r'^[\s]*$', str(self.sortfalls)):
            raise ValidationError("Sortfalls field not allow only white spaces / सॉर्टफॉल्स फ़ील्ड केवल सफेद रिक्त स्थान की अनुमति नहीं देता है")
        if self.sortfalls and not re.match(r'^[A-Za-z ]*$',str(self.sortfalls)):
            raise ValidationError("Sortfalls field not allow special and numeric characters / सॉर्टफॉल्स फ़ील्ड विशेष और संख्यात्मक वर्णों की अनुमति नहीं देता है")
    # --------------------end----------------------------------------------------

    #  *****************A new model name Target Achivement ****************
    class TargetsAchievement(models.Model):
        _name = 'targets.achievement'
        _description = 'Achievements'

        app_id = fields.Many2one(comodel_name='bsscl.employee.appraisal', string='Appraisal ID / मूल्यांकन आईडी')
        targets = fields.Text('Targets / लक्ष्यों को')
        achievements = fields.Text('Achievements / उपलब्धियों')

        # ******************** (Validate target details) *****************
        @api.constrains('targets')
        @api.onchange('targets',)
        def _onchnage_targets(self):
            if self.targets and re.match(r'^[\s]*$', str(self.targets)):
                raise ValidationError("Target field not allow only white spaces / लक्षित क्षेत्र केवल सफेद रिक्त स्थान की अनुमति नहीं देता है")
            if self.targets and not re.match(r'^[A-Za-z ]*$',str(self.targets)):
                raise ValidationError("Target field not allow special and numeric characters  / लक्ष्य फ़ील्ड विशेष और अंकीय वर्णों की अनुमति नहीं देता")
       
        # ******************** (Validate achievements details) *****************
        @api.constrains('achievements')
        @api.onchange('achievements')
        def _onchnage_achievements(self):
            if self.achievements and re.match(r'^[\s]*$', str(self.achievements)):
                raise ValidationError("Achievements field not allow only white spaces / उपलब्धि क्षेत्र केवल सफेद रिक्त स्थान की अनुमति नहीं देता है")
            if self.achievements and not re.match(r'^[A-Za-z ]*$',str(self.achievements)):
                raise ValidationError("Achievement field not allow special and numeric characters  / उपलब्धि फ़ील्ड में विशेष और अंकीय वर्णों की अनुमति नहीं है")

    # --------------------------End -----------------------------

    # *****************Appraisal KPIs model ********************
    class KPIForm(models.Model):
        _name = 'appraisal.kpi'
        _description = 'KPI Forms'

        kpia_id = fields.Many2one(comodel_name='appraisal.main', string='KPIA IDS / केपीआईए आईडीएस')
        kpia_id1 = fields.Many2one(comodel_name='appraisal.main', string='KPIA IDS / केपीआईए आईडीएस')
        kpia_id2 = fields.Many2one(comodel_name='appraisal.main', string='KPIA IDS / केपीआईए आईडीएस')
        kpi = fields.Char('KPI / केपीआई')
        kra = fields.Char('KRA / केआरए')
        reporting_auth_remarks = fields.Text(string="Reporting Auth Remarks / रिपोर्टिंग प्रामाणिक टिप्पणी")
        reviewing_auth_remarks = fields.Text(string="Reviewing Auth Remarks / प्रामाणिक टिप्पणियों की समीक्षा करना")
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
                                        ], 'Reporting Authority / रिपोर्टिंग प्राधिकरण')
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
                                    ('10', '10'),], 'Reviewing Authority / समीक्षा प्राधिकरण')
        state = fields.Selection(
            [('draft', 'Draft / प्रारूप'), ('self_review', 'Self Reviewed / स्व समीक्षित'), ('reporting_authority_review', 'Reporting Authority Reviewed / रिपोर्टिंग प्राधिकरण की समीक्षा की'),
            ('reviewing_authority_review', 'Reviewing Authority Reviewed / समीक्षा अधिकारी ने समीक्षा की'), ('completed', 'Completed / पुरा होना।'), ('rejected', 'Rejected / अस्वीकार कर दिया')
            ],default='draft', string='Status / स्थति')
        weightage_comp = fields.Float('weightage / बल भार', compute='get_kpi_weightage')
        weightage_int = fields.Integer('Weightage / बल भार',  compute='get_kpi_weightage')
        reviewing_auth_user = fields.Many2one('res.users', store=True)
        average = fields.Integer('Average / औसत')
        ra_group_bool_check = fields.Boolean("RA Check", compute="_compute_boolean")
        review_group_bool_check = fields.Boolean("Reviewer Check", compute="_compute_boolean")


        @api.depends()
        def _compute_boolean(self):
            if self.env.user.has_group('bsscl_employee_appraisal.appraisal_reporting_authority_group_id'):
                self.ra_group_bool_check = True
            else: 
                self.ra_group_bool_check = False

            if self.env.user.has_group('bsscl_employee_appraisal.appraisal_reviewing_authority_group_id'):
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
                print(rec,rec.weightage_comp)


        # def _onchange_validation_report(self):
        #     for rec in self:
        #         if rec.reporting_auth:
        #             rec.reviewing_auth = rec.reporting_auth
    # --------------------------End -----------------------------