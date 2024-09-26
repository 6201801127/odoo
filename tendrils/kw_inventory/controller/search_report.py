from odoo import http
from odoo.http import request


class SearchReport(http.Controller):

    @http.route('/search-filter-report', type='json', auth="user", website=True)
    def filter_report(self, **args):
        query = "SELECT req_num AS Requisition_Number,pr_create_date AS PR_Create_Date,requisition_Department AS Requisition_Department,\
        requisition_status AS Requisition_Status,pr_approved_by AS PR_Approved_By,ind_num AS Indent_Number,indent_date AS Indent_Date,\
        indent_department AS Indent_Department,indent_status AS Indent_Status,indent_approved_by AS Indent_Approved_By, quo_no AS Quotation_Number,\
        quotation_date AS Quotation_Date,quotation_state AS Quotation_State,quotation_approved_by AS Quotation_Approved_By FROM get_inventory2()"
        request.cr.execute(query)
        data = request.cr.fetchall()
        inventory_data = []
        for record in data:
            # print(record)
            inventory_data.append({'req_no': record[0],
                                   'pr_create_date': record[1],
                                   'requisition_Department': record[2],
                                   'requisition_status': record[3],
                                   'pr_approved_by': record[4],
                                   'indent_no': record[5],
                                   'indent_date': record[6],
                                   'indent_department': record[7],
                                   'indent_status': record[8],
                                   'indent_approved_by': record[9],
                                   'quo_no': record[10],
                                   'quotation_date': record[11],
                                   'quotation_state': record[12],
                                   'quotation_approved_by': record[13]})
        infodict = dict(report_inventory=inventory_data)
        return infodict
