from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import base64, re
from odoo.tools.mimetypes import guess_mimetype


class InheritEmployee(models.Model):
    _inherit = 'hr.employee'

    discipline_count = fields.Integer(compute="_compute_discipline_count")
    disciplinary_action_id = fields.One2many('disciplinary.action','employee_id','Disciplinary Action')


    def _compute_discipline_count(self):
        all_actions = self.env['disciplinary.action'].read_group([
            ('employee_id', 'in', self.ids),
            ('state', '!=', 'draft'),
        ], fields=['employee_id'], groupby=['employee_id'])
        mapping = dict([(action['employee_id'][0], action['employee_id_count']) for action in all_actions])
        for employee in self:
            employee.discipline_count = mapping.get(employee.id, 0)
    
            



class CategoryDiscipline(models.Model):
    _name = 'discipline.category'
    _description = 'Reason Category'

    # Discipline Categories

    code = fields.Char(string="Code / कोड", required=True, help="Category code")
    name = fields.Char(string="Name / नाम", required=True, help="Category name")
    category_type = fields.Selection([('disciplinary', 'Disciplinary Category'), ('action', 'Action Category')],
                                   string="Category Type / श्रेणी प्रकार", help="Choose the category type disciplinary or action")
    description = fields.Text(string="Details / विवरण", help="Details for this category")



class DisciplinaryAction(models.Model):
    _name = 'disciplinary.action'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Disciplinary Action"

    state = fields.Selection([
        ('draft', 'Draft'),
        ('explain', 'Waiting at Deputy Commissioner'),
        ('submitted', 'Waiting at Manager'),
        ('action', 'Completed'),
        ('cancel', 'Cancelled'),

    ], default='draft', string="Status / स्थिति", track_visibility='onchange')

    name = fields.Char(string='Reference / संदर्भ', required=True, copy=False, readonly=True,
                       default=lambda self: _('New / नया'))

    employee_id = fields.Many2one('hr.employee', string='Employee / कर्मचारी', required=True, help="Employee name")
    department_name = fields.Many2one('hr.department', string='Department / विभाग', required=True, help="Department name",store=True)
    discipline_reason = fields.Many2one('discipline.category', string='Reason / कारण', required=True, help="Choose a disciplinary reason")
    explanation = fields.Text(string="Remarks of Deputy Commissioner / उपायुक्त की टिप्पणी", help='Deputy Commissioner have to give Explanation'
                                                                     'to Commissioner about the violation of discipline')
    action = fields.Many2one('discipline.category', string="Action / कार्रवाई", help="Choose an action for this disciplinary action")
    # read_only = fields.Boolean(compute="get_user", default=True)
    # user_dep_com = fields.Boolean(compute="get_user", default=True)
    # user_comm = fields.Boolean(compute="get_user", default=True)

    warning_letter = fields.Html(string="Warning Letter / चेतावनी पत्र")
    suspension_letter = fields.Html(string="Suspension Letter / निलंबन पत्र")
    termination_letter = fields.Html(string="Termination Letter / बर्खास्तगी पत्र")
    warning = fields.Integer(default=False)
    action_details = fields.Text(string="Remarks of Manager / प्रबंधक की टिप्पणी", help="Give the details for this action")
    attachment_ids = fields.Many2many('ir.attachment', string="Document / दस्तावेज़",
                                      help="Employee can submit any documents which supports their explanation")
    note = fields.Text(string="Description / विवरण")
    joined_date = fields.Date(string="Joined Date / कार्यारंभ तारीख", help="Employee joining date",store=True)

    check_manager = fields.Boolean(default=False, compute="check_user_group")
    check_user = fields.Boolean(default=False, compute="check_user_group")


     # Check the user is a employee's manager or not
    @api.depends('employee_id')
    def check_user_group(self):
        for rec in self:
            if rec.employee_id.parent_id.user_id.id == self.env.user.id and self.env.user.has_group('bsscl_employee.group_hr_ra'):
                rec.check_manager = True
                rec.check_user = False
            if rec.employee_id.user_id.id == self.env.user.id :
                rec.check_manager = False
                rec.check_user = True
        print("manager-----------------------------",rec.check_manager)
        print("check_user-----------------------------",rec.check_user)


    # hr_employee_id = fields.Many2one('hr.employee')

    # assigning the sequence for the record
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('disciplinary.action')
        return super(DisciplinaryAction, self).create(vals)

    # Check the user is a manager or employee
    # @api.depends('employee_id')
    # def get_user(self):
    #     if self.env.user.has_group('hr.group_hr_manager'):
    #         self.read_only = True
    #     else:
    #         self.read_only = False

    #     if self.env.user.has_group('bsscl_employee.deputy_com_id'):
    #         self.user_dep_com = True
    #     else:
    #         self.user_dep_com = False

    #     if self.env.user.has_group('bsscl_employee.commissioner_id'):
    #         self.user_comm = True
    #     else:
    #         self.user_comm = False
            

    # Check the Action Selected
    @api.onchange('action')
    def onchange_action(self):
        if self.action.name == 'Written Warning':
            self.warning = 1
        elif self.action.name == 'Suspend the Employee for one Week':
            self.warning = 2
        elif self.action.name == 'Terminate the Employee':
            self.warning = 3
        elif self.action.name == 'No Action':
            self.warning = 4
        else:
            self.warning = 5

    @api.onchange('employee_id')
    @api.depends('employee_id')
    def onchange_employee_id(self):

        department = self.env['hr.employee'].search([('name', '=', self.employee_id.name)])
        self.department_name = department.department_id.id
        self.joined_date = department.transfer_date

        if self.state == 'action':
            raise ValidationError(_('You Can not edit a Validated Action !!'))

    @api.onchange('discipline_reason')
    @api.depends('discipline_reason')
    def onchange_reason(self):
        if self.state == 'action':
            raise ValidationError(_('You Can not edit a Validated Action !!'))

    def assign_function(self):
        for rec in self:
            rec.state = 'submitted'

    def cancel_function(self):
        for rec in self:
            rec.state = 'cancel'

    def set_to_function(self):
        for rec in self:
            rec.state = 'draft'

    def explanation_function(self):
        for rec in self:
            if not rec.explanation:
                raise ValidationError(_('You must give an explanation !!'))
        self.write({
            'state': 'submitted'
        })

    def action_function(self):
        for rec in self:
            if not rec.action:
                raise ValidationError(_('You have to select an Action !!'))

            if self.warning == 1:
                if not rec.warning_letter or rec.warning_letter == '<p><br></p>':
                    raise ValidationError(_('You have to fill up the Warning Letter in Action Information !!'))

            elif self.warning == 2:
                if not rec.suspension_letter or rec.suspension_letter == '<p><br></p>':
                    raise ValidationError(_('You have to fill up the Suspension Letter in Action Information !!'))

            elif self.warning == 3:
                if not rec.termination_letter or rec.termination_letter == '<p><br></p>':
                    raise ValidationError(_('You have to fill up the Termination Letter in  Action Information !!'))

            elif self.warning == 4:
                self.action_details = "No Action Proceed"

            elif self.warning == 5:
                if not rec.action_details:
                    raise ValidationError(_('You have to fill up the  Action Information !!'))
            rec.state = 'action'

    @api.constrains('attachment_ids')
    def check_uploaded_document(self):
        allowed_file_list = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
        not_allowed_aud_vdo = ['audio/mpeg','audio/mp4','video/mp4','video/webm','video/mkv']
        for record in self:
            for rec in record.attachment_ids:
                if rec.datas:
                    acp_size = ((len(rec.datas) *3/4) /1024) / 1024
                    mimetype = guess_mimetype(base64.b64decode(rec.datas)) 
                    print("================mimetype=========================",mimetype)       
                    if str(mimetype) not in allowed_file_list:
                        raise ValidationError("Only .jpeg, .jpg, .png, .pdf, .doc, .docx format are allowed. / केवल .jpeg, .jpg, .png, .pdf, .doc, .docx प्रारूप की अनुमति है। ")
                    if acp_size > 2:
                        raise ValidationError("Maximum file size is 2 MB / अधिकतम फ़ाइल आकार 2 एमबी है")
                    
    @api.constrains('note')
    @api.onchange('note')
    def _onchange_description(self):
        for rec in self:
            if rec.note and not re.match(r'^[A-Za-z]{1}[A-Za-z\s]*$',str(rec.note)):
                raise ValidationError("Description should be in alphabet / विवरण वर्णमाला में होना चाहिए")
            if rec.note:
                if len(rec.note) > 500:
                    raise ValidationError('Description should contain 500 characters or below / विवरण में 500 वर्ण या उससे कम होने चाहिए')