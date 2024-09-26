import base64,re
from odoo import SUPERUSER_ID
from datetime import datetime, date
from odoo import api, fields, models,tools
from odoo.exceptions import ValidationError,AccessError
from odoo.tools.translate import _
from odoo.modules.module import get_module_resource
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

# class ApplicantRelative(models.Model):
    
#     _name = 'applicant.relative'
#     _description = "Applicant Relatives"
#     _rec_name = 'name'

#     relative_type = fields.Selection([('Aunty', 'Aunty'),
#                                       ('Brother', 'Brother'),
#                                       ('Daughter', 'Daughter'),
#                                       ('Father', 'Father'),
#                                       ('Husband', 'Husband'),
#                                       ('Mother', 'Mother'),
#                                       ('Sister', 'Sister'),
#                                       ('Son', 'Son'), ('Uncle', 'Uncle'),
#                                       ('Wife', 'Wife'), ('Other', 'Other')],
#                                      string='Relative Type')
#     relate_type = fields.Many2one('relative.type', string = "Relative Type")
    
#     name = fields.Char(string='Name', size=128, required=True)
#     birthday = fields.Date(string='Date of Birth')
#     place_of_birth = fields.Char(string='Place of Birth', size=128)
#     occupation = fields.Char(string='Occupation', size=128)
#     gender = fields.Selection(
#         [('Male', 'Male'), ('Female', 'Female')], 
#         required=False)
#     active = fields.Boolean(string='Active', default=True)
#     applicant_id = fields.Many2one(
#         'hr.applicant', 'Applicant Ref', ondelete='cascade')

    # @api.onchange('birthday')
    # def onchange_birthday(self):
    #     if self.birthday and self.birthday >= date.today():
    #         warning = {'title': _('User Alert !'), 'message': _(
    #             'Date of Birth must be less than today!')}
    #         self.birthday = False
    #         return {'warning': warning}

    # @api.onchange('relative_type')
    # def onchange_relative_type(self):
    #     if self.relative_type:
    #         if self.relative_type in ('Brother', 'Father', 'Husband', 'Son',
    #                                   'Uncle'):
    #             self.gender = 'Male'
    #         elif self.relative_type in ('Mother', 'Sister', 'Wife', 'Aunty'):
    #             self.gender = 'Female'
    #         else:
    #             self.gender = ''
    #     if self.applicant_id and not self.relative_type:
    #         warning = {
    #             'title': _('Warning!'),
    #             'message': _('Please select Relative Type!'),
    #         }
    #         return {'gender': False, 'warning': warning}

    # @api.model
    # def create(self, vals):
    #     if (self._context.get('active_model') == 'hr.applicant' and
    #             self._context.get('active_id')):
    #         vals.update({'applicant_id': self._context.get('active_id')})
    #     return super(ApplicantRelative, self).create(vals)


class RelativeType(models.Model):
    _name = 'relative.type'
    _description = 'Relative Type'

    name = fields.Char('Name')
    gender = fields.Selection(
        [('Male', 'Male'), ('Female', 'Female')])


class EmployeeRelative(models.Model):

    _name = 'employee.relative'
    _description = "Employee Relatives"
    _rec_name = 'name'

    relative_type = fields.Selection([('Aunty', 'Aunty'),
                                      ('Brother', 'Brother'),
                                      ('Daughter', 'Daughter'),
                                      ('Father', 'Father'),
                                      ('Husband', 'Husband'),
                                      ('Mother', 'Mother'),
                                      ('Sister', 'Sister'),
                                      ('Son', 'Son'), ('Uncle', 'Uncle'),
                                      ('Wife', 'Wife'), ('Other', 'Other')],
                                     string='Relative Type/रिश्तेदार')
    name = fields.Char(string='Name/नाम', size=128, required=True)
    birthday = fields.Date(string='Date of Birth/जन्म तिथि')
    place_of_birth = fields.Char(string='Place of Birth/जन्म-स्थान', size=128)
    occupation = fields.Char(string='Occupation/पेशा', size=128)
    gender = fields.Selection(
        [('Male', 'Male'), ('Female', 'Female')],string='Gender/लिंग',
        required=False)
    active = fields.Boolean(string='Active', default=True)
    employee_id = fields.Many2one(
        'hr.employee', 'Employee Ref/कर्मचारी', ondelete='cascade')
    
    salutation = fields.Many2one('res.partner.title',string='Salutation/अभिवादन')
    relative_type = fields.Selection([('Aunty', 'Aunty'),
                                      ('Brother', 'Brother'),
                                      ('Daughter', 'Daughter'),
                                      ('Father', 'Father'),
                                      ('Husband', 'Husband'),
                                      ('Mother', 'Mother'),
                                      ('Sister', 'Sister'),
                                      ('Son', 'Son'), ('Uncle', 'Uncle'),
                                      ('Wife', 'Wife'), ('Other', 'Other')],
                                     string='Relative Type/सापेक्ष प्रकार')

    relate_type = fields.Many2one('relative.type', string="Relative Type/रिश्तेदार")
    relate_type_name = fields.Char(related='relate_type.name')


    # name = fields.Char(string = 'Name',)

    medical = fields.Boolean('Medical/चिकित्सा',default=False)
    tuition = fields.Boolean('Tuition/ट्यूशन',default=False)
    hostel = fields.Boolean('Hostel/छात्रावास',default=False)
    ltc = fields.Boolean('LTC/एलटीसी',default=False)
    twins = fields.Boolean('Twins/जुडवा',default=False)
    divyang = fields.Boolean('Divyang/दिव्यांग',default=False)
    status = fields.Selection([('dependant','Dependant'),
                               ('non_dependant','Non-Dependant'),
                               ],string='Status/अवस्था')
    status2 = fields.Selection([('surviving','Surviving'),
                               ('non_surviving', 'Non Surviving')
                               ],string='Status/अवस्था', default='surviving')
    prec_pf =fields.Float('PF/पीएफ%')
    prec_gratuity =fields.Float('Gratuity/ग्रेच्युटी%')
    prec_pension =fields.Float('Pension/पेंशन%')
    date_of_deadth = fields.Date('Date of Death/मृत्यु तिथि')
    age= fields.Float('Age/उम्र')
    
#(wagisha) only alphabets allowed in name field
    @api.constrains('name')
    @api.onchange('name')
    def _validate_name(self):
        for rec in self:
            if rec.name and not re.match(r'^[A-Za-z\s]*$',str(rec.name)):
                raise ValidationError(_("You can only use alphabets in Name"))
            
    @api.constrains('place_of_birth')
    @api.onchange('place_of_birth')
    def _validate_place_of_birth(self):
        for record in self:
            check_alpha=record.place_of_birth.isalpha() if record.place_of_birth else True
            if check_alpha == False :
                raise ValidationError(_("You can only use alphabets in Birth Place"))
            
#(wagisha) only alphabets allowed in occupation field
    @api.constrains('occupation')
    @api.onchange('occupation')
    def _validate_occupation(self):
        for record in self:
            check_alpha=record.occupation.isalpha() if record.occupation else True
            if check_alpha == False :
                raise ValidationError(_("You can only use alphabets in Occupation"))

    @api.constrains('birthday','date_of_deadth')
    # @api.onchange('birthday')
    def _validate_birthday(self):
        for record in self:
            check_today = date.today() 
            if record.birthday:
                
                print("chek-----today------------",check_today)
                if record.birthday >= check_today:
                    raise ValidationError(_("You can only select previous date in Date Of Birth"))
            if record.date_of_deadth:
                if record.date_of_deadth > check_today :
                    raise ValidationError(_("You can only select previous date in Date Of Death"))
            if record.date_of_deadth and record.birthday:
                if record.date_of_deadth < record.birthday :
                    raise ValidationError(_("You can not select less than Date of Birth date"))
    


class EmployeeEducation(models.Model):
    _name = "employee.education"
    _description = "Employee Education"
    _rec_name = "from_date"
    _order = "from_date"
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']

    from_date = fields.Date(string='From Date / आरंभ करने की तिथि',tracking=True)
    to_date = fields.Date(string='To Date / अंतिम तिथि',tracking=True)
    education_rank = fields.Char('Education Rank / शिक्षा रैंक',tracking=True)

    grade = fields.Char('Degree / डिग्री',tracking=True)
    field = fields.Char(string='Exam Passed / परीक्षा उत्तीर्ण', size=128,tracking=True)
    stream = fields.Char("Stream/Discipline /स्ट्रीम/अनुशासन")
    school_name = fields.Char(string='University/Board / विश्वविद्यालय/बोर्ड', size=256,tracking=True)
    passing_year = fields.Char("Year of Passing / उत्तीर्ण होने का वर्ष",tracking=True)
    percentage = fields.Float("Percentage / फ़ीसदी",tracking=True)

    illiterate = fields.Boolean('Illiterate / निरक्षर',tracking=True)
    active = fields.Boolean(string='Active', default=True,tracking=True)
    employee_id = fields.Many2one(
        'hr.employee', string='Employee Ref / कर्मचारी', required=True, help="Employee name",tracking=True)
    edu_type = fields.Selection(
        [('Local', 'Local'), ('Abroad', 'Abroad')], 'School Location / स्कूल का स्थान',
        default="Local",tracking=True)
    country_id = fields.Many2one('res.country', 'Country / देश',tracking=True)
    state_id = fields.Many2one('res.country.state', 'State / राज्य',tracking=True)
    province = fields.Char("Province / प्रांत",tracking=True)

    @api.constrains('from_date','to_date')
    @api.onchange('from_date','to_date')
    def _check_from_date(self):
        for rec in self:
            today=datetime.now().date()
            if rec.from_date and rec.to_date:
                if rec.from_date > today:
                    raise ValidationError(_('Your From date can not be a future date.'))
                if rec.to_date > today:
                    raise ValidationError(_('Your To date can not be a future date.'))
                if rec.from_date > rec.to_date:
                    raise ValidationError(_('Your From date must be less than To date.'))

    @api.constrains('passing_year')
    def _check_passing_year(self):
        for rec in self:
            to_date_year=rec.to_date.strftime("%Y")
            print("++++++++++++++++++++++++++++",to_date_year)
            curr_year=datetime.now().year
            passing_year_int = rec.passing_year.isdigit()
            if passing_year_int == False:
                raise ValidationError(_('Your passing year should be an integer.'))
            if int(rec.passing_year) != int(to_date_year):
                raise ValidationError(_('Please check your year of passing and To date should be the same.'))
            
    @api.constrains('percentage')
    def _check_values(self):
        if self.percentage < 1.0:
            raise ValidationError(_('Values should not be zero.'))
            

    @api.constrains('stream')
    @api.onchange('stream')	
    def _check_stream_name(self):
        for rec in self:
            if rec.stream and not re.match(r'^[A-Za-z\s]*$',str(rec.stream)):
                raise ValidationError(_("Stream  should be an alphabet"))

    @api.constrains('school_name')
    @api.onchange('school_name')	
    def _check_school_name(self):
	    for rec in self:
		    if rec.school_name and not re.match(r'^[A-Za-z\s]*$',str(rec.school_name)):
			    raise ValidationError(_("University name should be an alphabet"))
                    
            



    # @api.onchange('edu_type')
    # def onchange_edu_type(self):
    #     for rec in self:
    #         if rec.edu_type == 'Local':
    #             rec.abroad_country_id = False
    #             return {'domain': {'state_id' : [('country_id.code','=','IN')]}}
    #         else:
    #             rec.local_province_id = False
    #             rec.local_district_id = False

    # @api.onchange('illiterate')
    # def onchange_illiterate(self):
    #     for rec in self:
    #         rec.from_date = False
    #         rec.to_date = False
    #         rec.education_rank = ''
    #         rec.school_name = ''
    #         rec.grade = ''
    #         rec.field = ''
    #         rec.edu_type = ''
    #         rec.country_id = False
    #         rec.state_id = False
    #         rec.province = ''

    # @api.model
    # def create(self, vals):
    #     if (self._context.get('active_model') == 'hr.employee' and
    #             self._context.get('active_id')):
    #         vals.update({'employee_id': self._context.get('active_id')})
    #     return super(EmployeeEducation, self).create(vals)

    # @api.constrains('from_date', 'to_date')
    # def onchange_date(self):
    #     for rec in self:
    #         if rec.to_date and rec.to_date >= date.today():
    #             raise ValidationError('To date must be less than today!')
    #         if rec.from_date and rec.to_date and rec.from_date > rec.to_date:
    #             raise ValidationError('To Date must be greater than From Date!')
    
    # @api.constrains('percentage')
    # def onchange_percentage(self):
    #     for rec in self:
    #         if rec.percentage > 100:
    #             raise ValidationError("Percentage value should be between 0 to 100.")
    #         if rec.percentage < 0:
    #             raise ValidationError("Percentage value should be positive.")
                

    # @api.onchange('to_date')
    # def onchange_passing_year(self):
    #     if self.to_date:
    #         self.passing_year = self.to_date.year

class EmployeeLanguage(models.Model):
    _name = "employee.language"
    _description = "Employee Language"
    _rec_name = "language"
    _order = "id desc"

    language = fields.Char('Language / भाषा', required=True)
    read_lang = fields.Selection(
        [('Excellent', 'Excellent / उत्कृष्ट'), ('Good', 'Good / अच्छा'), ('Poor', 'Poor / खराब')],
        string='Read / पढ़ना' ,default = 'Good')
    write_lang = fields.Selection(
        [('Excellent', 'Excellent / उत्कृष्ट'), ('Good', 'Good / अच्छा'), ('Poor', 'Poor / खराब')],
        string='Write / लिखना' ,default = 'Good')
    speak_lang = fields.Selection(
        [('Excellent', 'Excellent / उत्कृष्ट'), ('Good', 'Good / अच्छा'), ('Poor', 'Poor / खराब')],
        string='Speak / बोलना' ,default = 'Good')
    active = fields.Boolean(string='Active', default=True)
    employee_id = fields.Many2one(
        'hr.employee', 'Employee Ref', ondelete='cascade')
    mother_tongue = fields.Boolean('Mother Tongue / मातृ भाषा')

    @api.constrains('language')
    def _check_language(self):
        for rec in self:
            x = rec.language.isalpha()
        if x == False:
            raise ValidationError("Language should be in Alphabet / भाषा वर्णमाला में होनी चाहिए")
        
    # @api.constrains('mother_tongue')
    # def _check_mother_tongue(self):
    #     self.ensure_one()
    #     if self.mother_tongue and self.employee_id:
    #         language_rec = self.search([
    #             ('employee_id', '=', self.employee_id.id),
    #             ('mother_tongue', '=', True), ('id', '!=', self.id)],
    #             limit=1)
    #         if language_rec:
    #             raise ValidationError(_("If you want to set '%s' \
    #                 as a mother tongue, first you have to uncheck mother \
    #                 tongue in '%s' language.") % (
    #                 self.language, language_rec.language))

    # @api.model
    # def create(self, vals):
    #     if self._context.get('active_model') == 'hr.employee' and \
    #             self._context.get('active_id'):
    #         vals.update({'employee_id': self._context.get('active_id')})
    #     return super(EmployeeLanguage, self).create(vals)