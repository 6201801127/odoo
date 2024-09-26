from odoo import models, fields, api, tools

class CourtCaseMangement(models.Model):
    _name = 'court.case.management'
    _description = 'Court Case Management'
    _rec_name = 'case_no'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    job_id = fields.Many2one(comodel_name='hr.job', string='Designation / पद')
    case_type = fields.Many2one('court.case.type', string="Case Type / मामले का प्रकार" )
    case_no = fields.Char(string='Case Number / केस नंबर',size=15 ,required=True)
    case_subject = fields.Char(string='Case Subject / मामला विषय',size=100)
    case_description = fields.Text(string='Case Description / केस विवरण') 
    arising_case = fields.Selection([('yes', 'Yes'), ('no', 'No')], default='no', string="Arising out of the case / मामले से बाहर")
    case_copy = fields.Binary("Upload case copy / केस कॉपी अपलोड करें", attachment=True)
    filed_on = fields.Date(string='Filed on / पर दायर' )
    petitioner_name = fields.Many2one('hr.employee',string='Petition By / याचिका द्वारा',size=100)
    court_location_id = fields.Many2one(comodel_name ='court.location', string='Location / स्थान')
    emp_id = fields.Many2one(comodel_name='hr.employee',string='culprit Name / दोषी का नाम')
    case_sub_type = fields.Many2one('court.case.sub.type', string="Case Sub Type / केस उप प्रकार")
    case_file_no = fields.Char(string='File Number / दस्तावेज संख्या',size=15)
    respondent_name_id = fields.Many2one('hr.employee', string='Respodent / प्रतिवादी',required='1')
    address = fields.Text(string='Address / पता')
    hearing_detail_ids = fields.One2many('case.hearing.details', 'court_case_id', string="Hearing Details")
    status  = fields.Selection([('draft', 'Draft / प्रारूप'),('applied', 'Applied / लागू'),('approved', 'Approved / अनुमत'),('cancel','Cancelled / रद्द'),('confirm', 'Confirmed / पुष्टि'),('reject', 'Rejected / अस्वीकृत')],string="Status / स्थति",default='draft',tracking=True)

#for apply button
    def apply_btn(self):
        self.status = 'applied'

#for approve button                       
    def approve_btn(self):
        self.status = 'approved'

#for cancel button
    def cancel_btn(self):
        self.status = 'cancel'

#for reject button
    def reject_btn(self):
        self.status = 'reject'

#for confirm button
    def confirm_btn(self):
        self.status = 'confirm'

# while selecting Case Type its particular Sub Case Type also coming
    @api.onchange('case_type')
    def onchange_case_type_id(self):
        for rec in self:
            select_sub_case_type = {'domain': {'case_sub_type': [('case_types_id', '=', rec.case_type.id)]}}
            return select_sub_case_type

class CaseHearingDetails(models.Model):
    _name = 'case.hearing.details'
    _description = 'Hearing Details'

    case_hearing_date = fields.Date(string="Case Hearing Date / मामले की सुनवाई की तारीख")
    description = fields.Text(string="Description / विवरण")
    document = fields.Binary(string="Document(PDF) / दस्तावेज़(पीडीएफ)", attachment=True)
    file_name = fields.Char(string="File Name / फ़ाइल का नाम")
    employee_id = fields.Many2one('hr.employee', string="Name / नाम", store=True, compute="_compute_employee")
    court_case_id = fields.Many2one('court.case.management', string="Court Case Id / कोर्ट केस आईडी", ondelete='cascade')

    @api.depends('court_case_id')
    def _compute_employee(self):
        if self.court_case_id:
            self.employee_id = self.court_case_id.respondent_name_id
