from datetime import datetime
import base64
from io import BytesIO

from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT ,pycompat


class SqlFileWizard(models.TransientModel):
    _name = "ms.query.export.wizard"
    _description = "Allow the user to save the file with sql request's data"

    binary_file = fields.Binary('File', readonly=True)
    file_name = fields.Char('File Name', readonly=True)
    ms_query_id = fields.Many2one(comodel_name='ms.query', required=True)

    def export_sql(self):
        self.ensure_one()
        sql_export      = self.ms_query_id

        # Manage Params
        variable_dict   = {}
        now_tz          = fields.Datetime.context_timestamp(sql_export, datetime.now())
        date            = now_tz.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        
        # Execute Request
        res = sql_export._execute_sql_request(
            params=variable_dict, mode='fetchall',
             copy_options="CSV HEADER DELIMITER ';'"
            )
        
        fp      = BytesIO()
        writer  = pycompat.csv_writer(fp, quoting=1)
        
        count=1
        for data in res:
            row     = []
            keys    = []
            # print(data[key])
            
            for key in data:
                # print(key)
                # print(data[key])
                if count== 1:
                    keys.append(pycompat.to_text(key))

                # Spreadsheet apps tend to detect formulas on leading =, + and -
                val = data[key]
                if isinstance(val, pycompat.string_types) and val.startswith(('=', '-', '+')):
                    val = "'" + val

                row.append(pycompat.to_text(val))

                
            if count== 1:
                writer.writerow(keys)
                count+=1
            writer.writerow(row)


        self.write({
            'binary_file': base64.b64encode(fp.getvalue()),
            'file_name': '%(name)s_%(date)s.csv' % {
            'name': 'export_query', 'date': date}
        })
        return {
            'view_mode': 'form',
            'res_model': 'ms.query.export.wizard',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': self.env.context,
            'nodestroy': True,
        }
