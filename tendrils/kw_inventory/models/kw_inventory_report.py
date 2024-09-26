import datetime
# import calendar
from odoo import models, fields, api
# from odoo.exceptions import ValidationError


class kw_inventory_report(models.Model):
    _name = "kw_inventory_report"
    _description = "Inventory Report"

    requisition_number = fields.Char(string='Requisition Number')
    indent_number = fields.Integer(string='Indent Number')
    quotation_number = fields.Integer(string='Quotation Number')

    @api.model
    def action_report_inventory(self, args):
        # print(args)
        from_date = args.get('fromdate', False)
        to_date = args.get('todate', False)

        self._cr.execute("SELECT req_num AS Requisition_Number,pr_create_date AS PR_Create_Date,requisition_Department AS Requisition_Department,\
        requisition_status AS Requisition_Status,pr_approved_by AS PR_Approved_By, ind_num AS Indent_Number,indent_date AS Indent_Date,\
        indent_department AS Indent_Department,indent_status AS Indent_Status,indent_approved_by AS Indent_Approved_By, quo_no AS Quotation_Number,\
        quotation_date AS Quotation_Date,quotation_state AS Quotation_State,quotation_approved_by AS Quotation_Approved_By FROM get_inventory2('" + from_date + "','" + to_date + "')")

        result = self._cr.fetchall()
        # print(result)
        return result

    # @api.model
    # def my_custom_function(self):
    #     print('my function called')
    #     req_no_dict=[]
    #     req_no = self.env['kw_purchase_requisition'].search([])
    #     for record in req_no:
    #         req_no_dict.append(record.requisition_number)

    #     indent_number_dict = []
    #     indent_no = self.env['kw_consolidation'].search([])
    #     for record in indent_no:
    #         indent_number_dict.append(record.indent_number)
    #     report_dict = dict(req = req_no_dict, indent = indent_number_dict)

    #     return report_dict
