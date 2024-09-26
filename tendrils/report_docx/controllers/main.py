from odoo.addons.web.controllers import main as report
from odoo.http import content_disposition, route, request

import json


class ReportController(report.ReportController):

    @route()
    def report_routes(self, reportname, docids=None, converter=None, **data):
        if converter == 'docx':
            report = request.env['ir.actions.report']._get_report_from_name(reportname)
            context = dict(request.env.context)
            if docids:
                docids = [int(i) for i in docids.split(',')]
            if data.get('options'):
                data.update(json.loads(data.pop('options')))
            if data.get('context'):
                # Ignore 'lang' here, because the context in data is the one
                # from the webclient *but* if the user explicitely wants to
                # change the lang, this mechanism overwrites it.
                data['context'] = json.loads(data['context'])
                if data['context'].get('lang'):
                    del data['context']['lang']
                context.update(data['context'])
            docx = report.with_context(context).render_docx(docids, data=data)[0]
            docxhttpheaders = [
                ('Content-Type', 'application/vnd.openxmlformats-'
                                 'officedocument.wordprocessingml.document'),
                ('Content-Length', len(docx)),
                (
                    'Content-Disposition',
                    content_disposition(report.report_file + '.docx')
                )
            ]
            return request.make_response(docx, headers=docxhttpheaders)
        # if converter == 'pdf':
        #     print("in elif==================",report)
        #     pdf = report.with_context(context).render_qweb_pdf(docids, data=data)[0]
        #     print(pdf,"pdf======================================")
        #     pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
        #     print(pdfhttpheaders,"pdfhttpheaders======================")
        #     return request.make_response(pdf, headers=pdfhttpheaders)
        return super(ReportController, self).report_routes(reportname, docids, converter, **data)
