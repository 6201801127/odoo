from odoo import models, fields, api,_
from odoo.exceptions import ValidationError

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'


    casual_leave = fields.Float(string="Casual Leave",readonly=True)
    half_pay_leave = fields.Float(string="Half Pay Leave",readonly=True)
#     commuted_leave = fields.Float(string="Commuted Leave",readonly=True)
    earned_leave = fields.Float(string="Earned Leave",readonly=True)
    maternity_leave = fields.Float(string="Maternity Leave",readonly=True)
    special_casual_leave = fields.Float(string="Special Casual Leave",readonly=True)
    extra_ordinary_leave = fields.Float(string="Extra Ordinary Leave",readonly=True)
    paternity_leave = fields.Float(string="Paternity Leave",readonly=True)
    child_care_leave = fields.Float(string="Child Care Leave",readonly=True)
    
    
    @api.constrains('date_from','date_to','employee_id')
    @api.onchange('date_from','date_to','employee_id')
    def _compute_casual_leave(self):
        for t in self:
            if t.employee_id:
                date_from = t.date_from
                date_to = t.date_to
#                 print("///////////////////////////////////",)
                SQL = """
                    select sum(number_of_days)
                    from hr_leave as hl
                    inner join hr_employee as he on he.id = hl.employee_id
                    inner join hr_leave_type as hlt on hlt.id = hl.holiday_status_id
                    
                    where hl.employee_id = %s and hlt.leave_type.code = 'Casual Leave' and hl.state in ('validate') and 
                        hl.request_date_from >= %s and hl.request_date_to <= %s

    
                """
                self.env.cr.execute(SQL,(t.employee_id.id,
                                          t.date_from,
                                          t.date_to,
                                          ))
                res = self.env.cr.fetchall()
                for line in res:
                    t.casual_leave = line[0]
#                     print("?????????????????????????????",res,float(res[0][1]))

    @api.constrains('date_from','date_to','employee_id')
    @api.onchange('date_from','date_to','employee_id')
    def _compute_half_pay_leave(self):
        for t in self:
            if t.employee_id:
                date_from = t.date_from
                date_to = t.date_to
#                 print("///////////////////////////////////",)
                SQL = """
                    select sum(number_of_days)
                    from hr_leave as hl
                    inner join hr_employee as he on he.id = hl.employee_id
                    inner join hr_leave_type as hlt on hlt.id = hl.holiday_status_id
                    
                    where hl.employee_id = %s and hlt.leave_type.code = 'Half Pay Leave' and hl.state in ('validate') and 
                        hl.request_date_from >= %s and hl.request_date_to <= %s

    
                """
                self.env.cr.execute(SQL,(t.employee_id.id,
                                          t.date_from,
                                          t.date_to,
                                          ))
                res = self.env.cr.fetchall()
                for line in res:
                    t.half_pay_leave = line[0]
    
#     @api.constrains('date_from','date_to','employee_id')
#     @api.onchange('date_from','date_to','employee_id')
#     def _compute_commuted_leave(self):
#         for t in self:
#             if t.employee_id:
#                 date_from = t.date_from
#                 date_to = t.date_to
# #                 print("///////////////////////////////////",)
#                 SQL = """
#                     select sum(number_of_days)
#                     from hr_leave as hl
#                     inner join hr_employee as he on he.id = hl.employee_id
#                     inner join hr_leave_type as hlt on hlt.id = hl.holiday_status_id
#                      
#                     where hl.employee_id = %s and hlt.leave_type = 'Commuted Leave' and hl.state in ('validate') and 
#                         hl.request_date_from >= %s and hl.request_date_to <= %s
#  
#      
#                 """
#                 self.env.cr.execute(SQL,(t.employee_id.id,
#                                           t.date_from,
#                                           t.date_to,
#                                           ))
#                 res = self.env.cr.fetchall()
#                 for line in res:
#                     t.commuted_leave = line[0]
                     
    @api.constrains('date_from','date_to','employee_id')
    @api.onchange('date_from','date_to','employee_id')
    def _compute_earned_leave(self):
        for t in self:
            if t.employee_id:
                date_from = t.date_from
                date_to = t.date_to
#                 print("///////////////////////////////////",)
                SQL = """
                    select sum(number_of_days)
                    from hr_leave as hl
                    inner join hr_employee as he on he.id = hl.employee_id
                    inner join hr_leave_type as hlt on hlt.id = hl.holiday_status_id
                    
                    where hl.employee_id = %s and hlt.leave_type.code = 'Earned Leave' and hl.state in ('validate') and 
                        hl.request_date_from >= %s and hl.request_date_to <= %s

    
                """
                self.env.cr.execute(SQL,(t.employee_id.id,
                                          t.date_from,
                                          t.date_to,
                                          ))
                res = self.env.cr.fetchall()
                for line in res:
                    t.earned_leave = line[0]
                    
    @api.constrains('date_from','date_to','employee_id')
    @api.onchange('date_from','date_to','employee_id')
    def _compute_maternity_leave(self):
        for t in self:
            if t.employee_id:
                date_from = t.date_from
                date_to = t.date_to
#                 print("///////////////////////////////////",)
                SQL = """
                    select sum(number_of_days)
                    from hr_leave as hl
                    inner join hr_employee as he on he.id = hl.employee_id
                    inner join hr_leave_type as hlt on hlt.id = hl.holiday_status_id
                    
                    where hl.employee_id = %s and hlt.leave_type.code = 'Maternity Leave' and hl.state in ('validate') and 
                        hl.request_date_from >= %s and hl.request_date_to <= %s

    
                """
                self.env.cr.execute(SQL,(t.employee_id.id,
                                          t.date_from,
                                          t.date_to,
                                          ))
                res = self.env.cr.fetchall()
                for line in res:
                    t.maternity_leave = line[0]
                    
    @api.constrains('date_from','date_to','employee_id')
    @api.onchange('date_from','date_to','employee_id')
    def _compute_special_casual_leave(self):
        for t in self:
            if t.employee_id:
                date_from = t.date_from
                date_to = t.date_to
#                 print("///////////////////////////////////",)
                SQL = """
                    select sum(number_of_days)
                    from hr_leave as hl
                    inner join hr_employee as he on he.id = hl.employee_id
                    inner join hr_leave_type as hlt on hlt.id = hl.holiday_status_id
                    
                    where hl.employee_id = %s and hlt.leave_type.code = 'Special Casual Leave' and hl.state in ('validate') and 
                        hl.request_date_from >= %s and hl.request_date_to <= %s

    
                """
                self.env.cr.execute(SQL,(t.employee_id.id,
                                          t.date_from,
                                          t.date_to,
                                          ))
                res = self.env.cr.fetchall()
                for line in res:
                    t.special_casual_leave = line[0]
                    
    @api.constrains('date_from','date_to','employee_id')
    @api.onchange('date_from','date_to','employee_id')
    def _compute_extra_ordinary_leave(self):
        for t in self:
            if t.employee_id:
                date_from = t.date_from
                date_to = t.date_to
#                 print("///////////////////////////////////",)
                SQL = """
                    select sum(number_of_days)
                    from hr_leave as hl
                    inner join hr_employee as he on he.id = hl.employee_id
                    inner join hr_leave_type as hlt on hlt.id = hl.holiday_status_id
                    
                    where hl.employee_id = %s and hlt.leave_type.code = 'Extra Ordinary Leave' and hl.state in ('validate') and 
                        hl.request_date_from >= %s and hl.request_date_to <= %s

    
                """
                self.env.cr.execute(SQL,(t.employee_id.id,
                                          t.date_from,
                                          t.date_to,
                                          ))
                res = self.env.cr.fetchall()
                for line in res:
                    t.extra_ordinary_leave = line[0]
                    
    @api.constrains('date_from','date_to','employee_id')
    @api.onchange('date_from','date_to','employee_id')
    def _compute_paternity_leave(self):
        for t in self:
            if t.employee_id:
                date_from = t.date_from
                date_to = t.date_to
#                 print("///////////////////////////////////",)
                SQL = """
                    select sum(number_of_days)
                    from hr_leave as hl
                    inner join hr_employee as he on he.id = hl.employee_id
                    inner join hr_leave_type as hlt on hlt.id = hl.holiday_status_id
                    
                    where hl.employee_id = %s and hlt.leave_type.code = 'Paternity Leave' and hl.state in ('validate') and 
                        hl.request_date_from >= %s and hl.request_date_to <= %s

    
                """
                self.env.cr.execute(SQL,(t.employee_id.id,
                                          t.date_from,
                                          t.date_to,
                                          ))
                res = self.env.cr.fetchall()
                for line in res:
                    t.paternity_leave = line[0]
    
    @api.constrains('date_from','date_to','employee_id')
    @api.onchange('date_from','date_to','employee_id')
    def _compute_child_care_leave(self):
        for t in self:
            if t.employee_id:
                date_from = t.date_from
                date_to = t.date_to
#                 print("///////////////////////////////////",)
                SQL = """
                    select sum(number_of_days)
                    from hr_leave as hl
                    inner join hr_employee as he on he.id = hl.employee_id
                    inner join hr_leave_type as hlt on hlt.id = hl.holiday_status_id
                    
                    where hl.employee_id = %s and hlt.leave_type.code = 'Child Care Leave' and hl.state in ('validate') and 
                        hl.request_date_from >= %s and hl.request_date_to <= %s

    
                """
                self.env.cr.execute(SQL,(t.employee_id.id,
                                          t.date_from,
                                          t.date_to,
                                          ))
                res = self.env.cr.fetchall()
                for line in res:
                    t.child_care_leave = line[0]
    
    
    