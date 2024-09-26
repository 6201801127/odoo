from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import datetime,date



class GenerateArrear(models.TransientModel):
    _name = 'generate.arrear'
    _description = 'Generate Arrear for all selected employees'

    employee_ids = fields.Many2many('hr.employee', 'arrear_employee_rel', string='Employees')

    
    def compute_batch_arrear(self):
        arrearbatch = self.env["arrear.batch"].browse(self._context.get('active_id'))
        active_id = self.env.context.get('active_id')
        for case in self.employee_ids:
            arrearObj = self.env["arrear.arrear"].create({
                'employee_id' : case.id,
                'centre_id' : case.branch_id.id,
                'confirm_date': arrearbatch.confirm_date,
                'arrear_type':arrearbatch.arrear_type,
                'date_from':arrearbatch.date_from,
                'date_to':arrearbatch.date_to,    
                'batch_id': active_id,  

            })

            if arrearObj:
                arrearObj.compute_arrear()

        return True
      