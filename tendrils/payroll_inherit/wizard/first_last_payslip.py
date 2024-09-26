from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, date
from odoo.exceptions import ValidationError
import base64
from io import BytesIO
import openpyxl






class first_last_payslip(models.TransientModel):
    _name = 'first_last_payslip'

    excel_file = fields.Binary(attachment=True)
    employee_ids = fields.Many2many('hr.employee','kw_payslip_emp_rel','employee_id','fl_wizard_id',domain="['|', ('active', '=', False), ('active', '=', True)]")
    select_type = fields.Selection(string="Type",
                                   selection=[('0', 'First/Last'), ('1', 'Date')], default='0')
    date_from = fields.Date()
    date_to = fields.Date()

    def action_button_view_end(self):
        tree_view_id = self.env.ref('payroll_inherit.view_hr_payslip_tree_first_end').id
        form_view_id = self.env.ref('payroll_inherit.hr_payslip_form_inherit').id
        # employee_ids = self.employee_ids.ids
        query = f"select fl_wizard_id from kw_payslip_emp_rel where employee_id = {self.id}"
        self.env.cr.execute(query)
        employee_ids = [row[0] for row in self.env.cr.fetchall()]
        if not employee_ids:
            raise ValidationError('No employees selected')
        elif self.select_type == '0':
            subquery = f"""
                SELECT id FROM (
                    SELECT id, ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY date_from) AS rn 
                    FROM hr_payslip WHERE employee_id IN %s and state='done'
                ) AS subquery_first WHERE rn = 1
                UNION ALL
                SELECT id FROM (
                    SELECT id, ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY date_from DESC) AS rn 
                    FROM hr_payslip WHERE employee_id IN %s and state='done'
                ) AS subquery_last WHERE rn = 1
            """
                
            self.env.cr.execute(subquery, (tuple(employee_ids), tuple(employee_ids)))
            result_ids = [row[0] for row in self.env.cr.fetchall()]
            domain = [('id', 'in', result_ids)]
        elif self.select_type == '1' and self.date_from and self.date_to:
            subquery = f"""
                SELECT id, ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY date_from) AS rn 
                FROM hr_payslip 
                WHERE employee_id IN %s AND state='done' AND date_to BETWEEN %s AND %s
            """

            self.env.cr.execute(subquery, (tuple(employee_ids), self.date_from, self.date_to))
            result_ids = [row[0] for row in self.env.cr.fetchall()]
            domain = [('id', 'in', result_ids)]

            

        action = {
            'type': 'ir.actions.act_window',
            'name': 'First-Last Payslips',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'hr.payslip',
            'target': 'main',
            'domain': domain,
            'context': {'create': False,'edit': False,'delete': False,'import': False}
                }

        return action
    
    @api.onchange('excel_file')
    def _get_employees(self):
        if self.excel_file:
            for rec in self:
                try:
                    excel_data = BytesIO(base64.b64decode(rec.excel_file))
                    work_book = openpyxl.load_workbook(excel_data)
                    worksheet = work_book.active
                    all_data,emp_code = [],[]
                    for row in worksheet.iter_rows(values_only=True):
                        all_data.append(row)
                    
                    for row in all_data:
                        emp_code.append(row[0])
                    employees = self.env['hr.employee'].sudo().search([('emp_code', 'in', emp_code), '|', ('active', '=', False), ('active', '=', True)])
                    rec.employee_ids = [(6, 0, employees.ids)]

                except:
                    raise ValidationError('Please upload a valid Excel file (.xlsx format).')
        else:
            self.employee_ids = False