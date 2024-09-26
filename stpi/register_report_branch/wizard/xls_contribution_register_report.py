
from datetime import datetime,date
from xlsxwriter.utility import xl_rowcol_to_cell
from time import strftime
from odoo import models

def change_date_format(date_string):
    return datetime.strptime(date_string, '%Y-%m-%d').strftime('%m/%d/%Y')

def empty_string_if_none(k):
    if not k:
        return ''
    else:
        return k


class register_report_xls(models.AbstractModel):
    _name = 'report.register_report_branch.register_report_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, obj):
        print("----------------------------ok---------------------------obj",obj)

        ws = workbook.add_worksheet('Register Report')
        heading_format = workbook.add_format({'align': 'left',
                                              'valign': 'vcenter',
                                              'bold': True, 'size': 14,
                                              })
        bold = workbook.add_format({'bold': True})
        align_center = workbook.add_format({'align': 'center'})
        cell_format = workbook.add_format({ 'size': 11,})
        #background_color = cell_format.set_bg_color('#FF6600')

        cell_text_format_for_total = workbook.add_format({'align': 'left',
                                                          'bold': True,
                                                          'size': 16,

                                                          })

        #         colour = workbook.add_format({'align':'center'})
        ws.set_column('A:A', 20)
        ws.set_column('B:N', 18)

        ws.merge_range('B1:D1', 'Register Report On', heading_format)
        today_date = change_date_format(str(date.today()))
        ws.write_string('C1', today_date, bold)

        ws.write('A2', 'From', bold)
        ws.write_string('B2', change_date_format(str(obj.from_date)), bold)
        ws.write('C2', 'To', align_center)
        ws.write_string('D2', change_date_format(str(obj.to_date)), bold)

        ws.add_table('A5:N5', {'data': data, 'style': 'Table Style Light 11',
                               'columns': [
                                           {'header': 'Employee'},
                                           {'header': 'Payslip From Date'},
                                           {'header': 'Payslip To Date'},
                                           {'header': 'Department'},
                                           {'header': 'Manager'},
                                           {'header': 'Contribution Register'},
                                           {'header': 'Job Position'},
                                           {'header': 'Contract'},
                                           {'header': 'Branch'},
                                           {'header': 'Payslip Name'},
                                           {'header': 'Wage'},
                                           {'header': 'Amount'},
                                           {'header': 'Rate'},
                                           {'header': 'Total'},
#                                            {'header': 'Register Info'},
#                                            {'register_name': 'Re'}

                                           ]})
        data = obj.env['contribution.register.report'].search([])
        col = 0
        row = 5
        for obj in data:
            ws.write(row,col,empty_string_if_none(obj.employee_id.name),cell_format)
            ws.write(row,col+1,change_date_format(str(obj.pay_from_date)))
            ws.write(row,col+2,change_date_format(str(obj.pay_to_date)))
            ws.write(row,col+3,empty_string_if_none(obj.dep_id.name),cell_format)
            ws.write(row,col+4,empty_string_if_none(obj.manager_id.name),cell_format)
            ws.write(row,col+5,empty_string_if_none(obj.contib_regi.name),cell_format)
            ws.write(row,col+6,empty_string_if_none(obj.job_position.name),cell_format)
            ws.write(row,col+7,empty_string_if_none(obj.contract_id.name),cell_format)
            ws.write(row,col+8,empty_string_if_none(obj.branch_id.name),cell_format)
            ws.write(row,col+9,obj.payslip_name,cell_format)
            ws.write(row,col+10,obj.wage,cell_format)
            ws.write(row,col+11,obj.amt,cell_format)
            ws.write(row,col+12,obj.rate,cell_format)
            ws.write(row,col+13,obj.total,cell_format)
#             ws.write(row,col+14,obj.register_name,cell_format)
            row+=1

            col = 0
            ws.write(row, col+4, 'Total',cell_text_format_for_total)
#             ws.write_formula(row, col + 5, '{=SUM(F6:F%s)}' % str(row),bold)
#             ws.write_formula(row, col + 6, '{=SUM(G6:G%s)}' % str(row),bold)
#             ws.write_formula(row, col + 7, '{=SUM(H6:H%s)}' % str(row),bold)
#             ws.write_formula(row, col + 8, '{=SUM(I6:I%s)}' % str(row),bold)
#             ws.write_formula(row, col + 9, '{=SUM(J6:J%s)}' % str(row),bold)
            ws.write_formula(row, col + 10, '{=SUM(K6:k%s)}' % str(row),bold)
            ws.write_formula(row, col + 11, '{=SUM(L6:L%s)}' % str(row),bold)
            ws.write_formula(row, col + 12, '{=SUM(M6:M%s)}' % str(row),bold)
            ws.write_formula(row, col + 13, '{=SUM(N6:N%s)}' % str(row),bold)



# sale_performance_xls('report.sales_performance.sale_performance_xls_report.xlsx','sales.performance.wizard')