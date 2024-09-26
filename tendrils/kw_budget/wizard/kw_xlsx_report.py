from odoo import fields, models, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.float_utils import float_is_zero
from odoo.exceptions import ValidationError
import os
import time
import tempfile
import logging
_logger = logging.getLogger('Budget Report')
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
try:
    import xlwt
    import xlsxwriter
    from xlwt.Utils import rowcol_to_cell
except ImportError:
    _logger.debug('Can not import xlsxwriter`.')
import base64


class BudgetXlsxOutputReport(models.TransientModel):
    _name = 'budget.xlsx.output'
    _description = "XLSX Budget Report Download"

    name = fields.Char('Name')
    xls_output = fields.Binary('Download', readonly=True)