# Copyright 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import os
import tempfile
from io import BytesIO

from odoo import models

import logging
_logger = logging.getLogger(__name__)

try:
    import docx
except ImportError:
    _logger.debug('Can not import docx`.')
from docx import Document


class ReportDocxAbstract(models.AbstractModel):
    _name = 'report.report_docx.abstract'
    _description = 'Abstract Docx Report'

    def _get_objs_for_report(self, docids, data):
        if docids:
            ids = docids
        elif data and 'context' in data:
            ids = data["context"].get('active_ids', [])
        else:
            ids = self.env.context.get('active_ids', [])
        return self.env[self.env.context.get('active_model')].browse(ids)

    def create_docx_report(self, docids, data):
        objs = self._get_objs_for_report(docids, data)
        temporary_files = []
        document = Document()
        doc_file_fd, doc_file_path = tempfile.mkstemp(suffix='.docx', prefix='report.docx.')
        temporary_files.append(doc_file_path)
        self.generate_docx_report(document, data, objs)
        document.save(doc_file_path)
        with open(doc_file_path, 'rb') as document_data:
            doc_content = document_data.read()
        for temporary_file in temporary_files:
            try:
                os.unlink(temporary_file)
            except (OSError, IOError):
                _logger.error('Error when trying to remove file %s' % temporary_file)
        return doc_content, 'docx'

    def get_document_heading(self):
        return ''

    def get_document_options(self):
        return {}

    def generate_docx_report(self, document, data, objs):
        raise NotImplementedError()
