from odoo import fields, api, models, _
import pytz
from pytz import timezone
import uuid
from io import BytesIO
import base64
from datetime import datetime
from odoo.exceptions import UserError, RedirectWarning


class MsQuery(models.Model):
    _name = "ms.query"
    _description = "Execute Query"
    _inherit = ['mail.thread']

    title = fields.Char("Name")
    backup = fields.Text('Backup Syntax', help="Backup your query if needed")
    name = fields.Text('Syntax', required=True)
    result = fields.Text('Result', default='[]')
    encoding = fields.Selection(
        [('utf-8', 'utf-8'), ('utf-16', 'utf-16'),
         ('windows-1252', 'windows-1252'), ('latin1', 'latin1'),
         ('latin2', 'latin2'), ('big5', 'big5'), ('gb18030', 'gb18030'),
         ('shift_jis', 'shift_jis'), ('windows-1251', 'windows-1251'),
         ('koir8_r', 'koir8_r')], string='Encoding', required=True,
        default='utf-8')

    def get_real_datetime(self):
        if not self.env.user.tz:
            action = self.env.ref('base.action_res_users')
            msg = _("Please set your timezone in Users menu.")
            raise RedirectWarning(msg, action.id, _("Go to Users menu"))
        return pytz.UTC.localize(datetime.now()).astimezone(timezone(self.env.user.tz))

    @api.multi
    def execute_query(self):
        if not self.name:
            return
        prefix = self.name[:6].upper()
        try:
            self._cr.execute(self.name)
        except Exception as e:
            raise UserError(e)

        if prefix == 'SELECT':
            result = self._cr.dictfetchall()
            if result:
                self.result = '\n\n'.join(str(res) for res in result)
            else:
                self.result = "Data not found"
        elif prefix == 'UPDATE':
            self.result = '%d row(s) affected' % (self._cr.rowcount)
        else:
            self.result = 'Successful'

        msg = '%s<br><br>Executed on %s' % (self.name, str(self.get_real_datetime())[:19])
        self.message_post(body=msg)

    @api.multi
    def export_query(self):
        self.ensure_one()
        wiz = self.env['ms.query.export.wizard'].create({'ms_query_id': self.id})
        return wiz.export_sql()

    @api.model
    def _create_savepoint(self):
        rollback_name = '%s_%s' % (self._name.replace('.', '_'), uuid.uuid1().hex)
        # pylint: disable=sql-injection
        req = "SAVEPOINT %s" % (rollback_name)
        self.env.cr.execute(req)
        return rollback_name

    @api.model
    def _rollback_savepoint(self, rollback_name):
        # pylint: disable=sql-injection
        req = "ROLLBACK TO SAVEPOINT %s" % (rollback_name)
        self.env.cr.execute(req)

    @api.multi
    def _execute_sql_request(
            self, params=None, mode='fetchall', rollback=True,
            view_name=False, copy_options="CSV HEADER DELIMITER ';'"):

        self.ensure_one()
        res = False
        # Check if the request is in a valid state
        # if self.state == 'draft':
        #     raise UserError(_(
        #         "It is not allowed to execute a not checked request."))

        # Disable rollback if a creation of a view is asked
        if mode in ('view', 'materialized_view'):
            rollback = False

        # pylint: disable=sql-injection
        if params:
            query = self.name % params
        else:
            query = self.name
        query = query

        if mode in ('fetchone', 'fetchall'):
            pass
        elif mode == 'stdout':
            query = "COPY (%s) TO STDOUT WITH %s" % (query, copy_options)
        elif mode in 'view':
            query = "CREATE VIEW %s AS (%s);" % (query, view_name)
        # elif mode in 'materialized_view':
        #     self._check_materialized_view_available()
        #     query = "CREATE MATERIALIZED VIEW %s AS (%s);" % (query, view_name)
        else:
            raise UserError(_("Unimplemented mode : '%s'" % mode))

        if rollback:
            rollback_name = self._create_savepoint()
        try:
            if mode == 'stdout':
                output = BytesIO()
                self.env.cr.copy_expert(query, output)
                # print(output)
                res = base64.b64encode(output.getvalue())
                output.close()
            else:
                self.env.cr.execute(query)
                if mode == 'fetchall':
                    res = self.env.cr.dictfetchall()  # fetchall()
                elif mode == 'fetchone':
                    res = self.env.cr.fetchone()
        finally:
            self._rollback_savepoint(rollback_name)

        return res
