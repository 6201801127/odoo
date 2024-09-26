from odoo import models, fields, api
from odoo.exceptions import ValidationError

class AssignAppraisalRatio(models.TransientModel):
    _name           = 'assign_appraisal_ratio'
    _description    = "Appraisal Ratio Assign"
    _rec_name       = 'department'
    
    department      = fields.Many2one(comodel_name='hr.department', string="Department")
    
    division        = fields.Many2one(comodel_name='hr.department', string="Division")    
    section         = fields.Many2one(comodel_name='hr.department', string="Practice")    
    practice        = fields.Many2one(comodel_name='hr.department', string="Section")    
    per_appraisal   = fields.Integer(string='Appraisal Percentage')
    per_kra         = fields.Integer(string='KRA Percentage')
    per_inc         = fields.Integer(string='Increment Percentage')
    
    child_id        = fields.One2many('assign_appraisal_ratio','parent_id',string='Department Wise Ratio')
    parent_id       = fields.Many2one('assign_appraisal_ratio')
    
    dep_emp         = fields.Many2many('hr.employee','hr_emp_dep_rel',string='Department Employees',compute='filter_dept_employee')
    count_emp       = fields.Integer(compute='_count_employees',string='No. of Employees')
    
    @api.onchange('per_appraisal','per_kra')
    def _validate_total(self):
        for record in self:
            if (record.per_appraisal > 0 and record.per_kra > 0) and (record.per_appraisal + record.per_kra) != 100:
                raise ValidationError("Sum of Appraisal Pecentage and KRA Percentage must be 100.")
    
    @api.multi
    def _count_employees(self):
        for record in self:
            record.count_emp = len(record.dep_emp) if record.dep_emp else 0
    
    @api.depends('department')
    def filter_dept_employee(self):
        for record in self:
            record.dep_emp = False
            if record.department:
                period_master = self.env['kw_assessment_period_master'].search([],order='id desc')
                appraisal_record = self.env['hr.appraisal'].search([('appraisal_year_rel','=',period_master[0].id or False)])
                enrolled_emp = appraisal_record.mapped('emp_id')
                domain = [
                    ('department_id','=',record.department.id if record.department else False),
                    ('division','=',record.division.id if record.division else False),
                    ('section','=',record.section.id if record.section else False),
                    ('practise','=',record.practice.id if record.practice else False)
                    
                ]
                if enrolled_emp:
                    domain += [('id','in',enrolled_emp.ids)]
                employee_records = self.env['hr.employee'].search(domain)
                record.dep_emp = [(4, emp.id) for emp in employee_records]
            else:
                pass

    @api.onchange('department')
    def _add_child_records(self):
        for record in self:
            vals = []
            record.child_id = False
            if record.department:
                division = record.department.mapped('child_ids')
                vals.append([0, 0,{
                                'department': record.department.id, 
                                'division': False,
                                'section': False,
                                'practice': False
                                }
                            ])
                if division:
                    for div in division:
                        sections = div.mapped('child_ids')
                        vals.append([0, 0,{
                                'department': record.department.id, 
                                'division': div.id,
                                'section': False,
                                'practice': False
                            }
                        ])
                        if sections:
                            for sec in sections:
                                practice = sec.mapped('child_ids')
                                vals.append([0, 0,{
                                                        'department': record.department.id, 
                                                        'division': div.id,
                                                        'section': sec.id,
                                                        'practice': False
                                                    }
                                                ])
                                if practice:
                                    for prac in practice:
                                        vals.append([0, 0,{
                                                            'department': record.department.id, 
                                                            'division': div.id,
                                                            'section': sec.id,
                                                            'practice': prac.id
                                                        }
                                                    ])
                                # else:
                                #     vals.append([0, 0,{
                                #                         'department': record.department.id, 
                                #                         'division': div.id,
                                #                         'section': sec.id,
                                #                         'practice': False
                                #                     }
                                #                 ])
                        # else:
                        #     vals.append([0, 0,{
                        #                         'department': record.department.id, 
                        #                         'division': div.id,
                        #                         'section': False,
                        #                         'practice': False
                        #                     }
                        #                 ])
            if vals:
                record.child_id = vals
                ratio_model = self.env['kw_appraisal_ratio']
                for rec in record.child_id:
                    # print(rec.department.id,rec.division.id,rec.section.id,rec.practice.id)
                    ratio_data = ratio_model.sudo().search([
                            ("department",'=',rec.department.id if rec.department else False),
                            ("division",'=',rec.division.id if rec.division else False),
                            ("section",'=',rec.section.id if rec.section else False),
                            ("practice",'=',rec.practice.id if rec.practice else False)
                            ],limit=1)
                    # print(ratio_data)
                    try:
                        if ratio_data:
                            rec.update({
                                'per_appraisal':ratio_data.per_appraisal if ratio_data.per_appraisal else 0,
                                'per_kra':ratio_data.per_kra if ratio_data.per_kra else 0,
                                'per_inc':ratio_data.per_inc if ratio_data.per_inc else 0,
                            })
                    except Exception as e:
                        continue

                
    @api.multi
    def assign_ration(self):
        self.ensure_one()
        # print(self.child_id)
        ratio_model = self.env['kw_appraisal_ratio']
        if self.child_id:
            for record in self.child_id:
                try:
                    ratio_data = ratio_model.sudo().search([
                            ("department",'=',record.department.id if record.department else False),
                            ("division",'=',record.division.id if record.division else False),
                            ("section",'=',record.section.id if record.section else False),
                            ("practice",'=',record.practice.id if record.practice else False)
                            ],limit=1) 
                    if not ratio_data:
                        ratio_model.create({
                            'department': record.department.id if record.department else False, 
                            'division': record.division.id if record.division else False,
                            'section': record.section.id if record.section else False,
                            'practice': record.practice.id if record.practice else False,
                            'per_appraisal':record.per_appraisal,
                            'per_kra':record.per_kra,
                            'per_inc':record.per_inc,
                        })
                    else:
                        ratio_data.write({
                            'per_appraisal':record.per_appraisal if record.per_appraisal != ratio_data.per_appraisal else ratio_data.per_appraisal,
                            'per_kra':record.per_kra if record.per_kra != ratio_data.per_kra else ratio_data.per_kra,
                            'per_inc':record.per_inc if record.per_inc != ratio_data.per_inc else ratio_data.per_inc,
                        })
                except Exception as e:
                    continue
        return {
        'type': 'ir.actions.client',
        'tag': 'reload',
        }