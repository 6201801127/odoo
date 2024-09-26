# -*- coding: utf-8 -*-

from odoo import http
import xlsxwriter
from io import BytesIO
from odoo.http import request
from datetime import datetime
import base64


class KwAuctionReportDownload(http.Controller):
    @http.route('/download-xls-format/', type='http', auth='user')
    def generate_xls(self):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()
        
        bold = workbook.add_format({'bold': True})
        
        header_row = [
            'Auction Duration',
            'Reference ID',
            'Item Name',
            'Item Model',
            'Item Configuration',
            'FA Code',
            'Serial No',
            'Used By',
            'Booked By',
            'Booked On',
            'Auction Reserved Price',
            'Final Bid',
            'State'
        ]
        for col, header in enumerate(header_row):
            worksheet.write(0, col, header, bold)
        
        kw_auction_report_records = request.env['kw_auction_report'].search([])
        for row, record in enumerate(kw_auction_report_records, start=1):
            worksheet.write(row, 0, record.auction_duration)
            worksheet.write(row, 1, record.auction_ref_id)
            worksheet.write(row, 2, record.item_name)
            worksheet.write(row, 3, record.item_model)
            worksheet.write(row, 4, record.item_configuration)
            worksheet.write(row, 5, record.fa_code)
            worksheet.write(row, 6, record.serial_no)
            worksheet.write(row, 7, record.used_by_id.name)
            worksheet.write(row, 8, record.booked_by_id.name)
            if record.booked_on:
                booked_on_str = record.booked_on.strftime("%d-%b-%y")
            else:
                booked_on_str = ""   
            worksheet.write(row, 9, booked_on_str)         
            worksheet.write(row, 10, record.reserve_price)
            worksheet.write(row, 10, record.final_bid)
            worksheet.write(row, 11, record.state)
        
        workbook.close()
        output.seek(0)

        current_date = datetime.now()
        formatted_date = current_date.strftime("%d-%m-%y")

        return request.make_response(
            output.getvalue(),
            headers=[
                ('Content-Disposition', f'attachment; filename = Auction_Report_{formatted_date}.xls'),
                ('Content-Type', 'application/vnd.ms-excel')
            ]
        )
        

    @http.route('/download/image/<int:record_id>', type='http', auth='user')
    def download_image(self, record_id, **kwargs):
        record = request.env['kw_auction_item_photo_master'].browse(record_id)
        if record.photo:
            image_binary = base64.b64decode(record.photo)
            image_name = 'downloaded_image.jpg' 
            return request.make_response(image_binary,
                                         headers=[
                                             ('Content-Type', 'image/jpeg'),
                                             ('Content-Disposition', image_name)
                                         ])
        else:
            return request.not_found()