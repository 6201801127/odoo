from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError, Warning
from datetime import datetime

class Employeefamily(models.Model):
    _inherit='employee.relative'
    _description = 'Employee Relative'

    salutation = fields.Many2one('res.partner.title',string='Salutation')
    relative_type = fields.Selection([('Aunty', 'Aunty'),
                                      ('Brother', 'Brother'),
                                      ('Daughter', 'Daughter'),
                                      ('Father', 'Father'),
                                      ('Husband', 'Husband'),
                                      ('Mother', 'Mother'),
                                      ('Sister', 'Sister'),
                                      ('Son', 'Son'), ('Uncle', 'Uncle'),
                                      ('Wife', 'Wife'), ('Other', 'Other')],
                                     string='Relative Type')

    relate_type = fields.Many2one('relative.type', string="Relative Type")
    relate_type_name = fields.Char(related='relate_type.name')


    name = fields.Char(string = 'Name',)

    medical = fields.Boolean('Medical',default=False)
    tuition = fields.Boolean('Tuition',default=False)
    hostel = fields.Boolean('Hostel',default=False)
    ltc = fields.Boolean('LTC',default=False)
    twins = fields.Boolean('Twins',default=False)
    divyang = fields.Boolean('Divyang',default=False)
    status = fields.Selection([('dependant','Dependant'),
                               ('non_dependant','Non-Dependant'),
                               ],string='Status')
    status2 = fields.Selection([('surviving','Surviving'),
                               ('non_surviving', 'Non Surviving')
                               ],string='Status', default='surviving')
    prec_pf =fields.Float('PF%')
    prec_gratuity =fields.Float('Gratuity%')
    prec_pension =fields.Float('Pension%')
    date_of_deadth = fields.Date('Date of Death')
    age= fields.Float('Age')

    # @api.multi
    # def write(self, vals):
    #     for rec in self:
    #         if vals.get('twins'):
    #             self.env['employee.relative'].sudo().create({
    #                 'name': 'Twin Name',
    #                 'birthday': rec.birthday,
    #                 'place_of_birth': rec.place_of_birth,
    #                 'employee_id': rec.employee_id.id,
    #                 })
    #     res = super(Employeefamily, self).write(vals)
    #     return res

    @api.onchange('twins')
    def onchange_twins_type(self):
        if self.twins == True:
            self.env['employee.relative'].sudo().create({
                'name': 'Twin Name',
                'birthday': self.birthday,
                'place_of_birth': self.place_of_birth,
                'employee_id': self.employee_id.id,
                })


    @api.onchange('prec_pf')
    def check_pf_prect(self):
        prect = self.env['employee.relative'].search([('employee_id','=',self.employee_id.id)]).mapped('prec_pf')
        total = 0
        print('-------------------prect',prect,self.employee_id.name)
        for val in prect:
            total+=val
        total+=self.prec_pf
        print("---------total-",total)
        if total>100 and self.prec_pf > 0:
            self.update({'prec_pf':0})
            raise UserError(_('you have already distributed your PF out of 100%'))

    @api.onchange('prec_gratuity')
    def check_gratuity(self):
        prect = self.env['employee.relative'].search([('employee_id','=',self.employee_id.id)]).mapped('prec_gratuity')
        total =0
        for val in prect:
            total+=val
        total +=self.prec_gratuity
        if total>100 and self.prec_gratuity > 0:
            self.update({'prec_pf':0})
            raise UserError(_('you have already distributed your Gratuity out of 100%'))

    @api.onchange('prec_pension')
    def check_pension(self):
        prect = self.env['employee.relative'].search([('employee_id','=',self.employee_id.id)]).mapped('prec_pension')
        total =0
        for val in prect:
            total+=val
        total +=self.prec_pension
        if total>100 and self.check_pension > 0:
            self.update({'prec_pf':0})
            raise UserError(_('you have already distributed your Pension out of 100%'))


    @api.onchange('birthday')
    def get_age(self):
        if self.birthday:
            day=(datetime.now().date() - self.birthday).days
            self.age = day/365
            self.tuition =False


    @api.onchange('tuition')
    def tuition_child_count(self):
        child_ids = self.env['employee.relative'].sudo().search([('employee_id', '=', self._context.get('active_id')),
                                                                    ('relate_type.name', 'in', ['Son', 'Daughter'])])
        twins_child_ids = child_ids.filtered(lambda x: x.twins and x.tuition).sorted(key=lambda x: x.id)
        twin_child_pos = child_ids.mapped('id').index(twins_child_ids.mapped('id')[0])\
                                        if len(twins_child_ids) > 0 else None
        # if self.hostel:
        #     raise UserError(_('You can not have both hostel and tuition for a child'))
        if twin_child_pos in  [0, None] and self.tuition and len(child_ids.filtered(lambda x: x.tuition)) == 2:
            raise UserError(_('Only two children are allowed for tuition'))

    @api.onchange('hostel')
    def hostel_child_count(self):
        child_ids = self.env['employee.relative'].sudo().search([('employee_id', '=', self._context.get('active_id')),
                                                                    ('relate_type.name', 'in', ['Son', 'Daughter'])])
        twins_child_ids = child_ids.filtered(lambda x: x.twins and x.hostel).sorted(key=lambda x: x.id)
        twin_child_pos = child_ids.mapped('id').index(twins_child_ids.mapped('id')[0])\
                                        if len(twins_child_ids) > 0 else None
        # if self.tuition:
        #     raise UserError(_('You can not have both tuition and hostel for a child'))
        if twin_child_pos in  [0, None] and self.hostel and len(child_ids.filtered(lambda x: x.hostel)) == 2:
            raise UserError(_('Only two children are allowed for hostel'))
        if self.hostel:
            self.tuition = True

    @api.onchange('relative_type')
    def onchange_relative_type(self):
        pass

    @api.onchange('relate_type')
    def onchange_relate_type(self):
        for record in self:
            if record.relate_type:
                record.gender = record.relate_type.gender if record.relate_type.gender else False

    @api.multi
    @api.depends('name','relate_type','age')
    def name_get(self):
        res = []
        for record in self:
            if record.name and record.relate_type and record.age:
                name = str(record.name) + ' [' + str(record.relate_type.name) + ':' + str(int(record.age)) + ']'
            else:
                name = str(record.name)
            res.append((record.id, name))
        return res
