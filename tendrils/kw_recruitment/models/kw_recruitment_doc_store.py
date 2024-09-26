# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import hashlib
import itertools
import logging
import mimetypes
import os
import io
import re
from collections import defaultdict
import uuid

from odoo import api, fields, models, tools, SUPERUSER_ID, exceptions, _
from odoo.exceptions import AccessError, ValidationError
from odoo.tools import config, human_size, ustr, html_escape
from odoo.tools.mimetypes import guess_mimetype
from odoo.tools import crop_image, image_resize_image
from PyPDF2 import PdfFileWriter, PdfFileReader


class RecruitmentAttachment(models.Model):
    """Attachments are used to link binary files or url to any document.
    """
    _name = 'recruitment_attachment'
    _description = 'Attachment'
    _order = 'id desc'

    name = fields.Char('Name', required=True)
    datas_fname = fields.Char('Filename')
    description = fields.Text('Description')
    res_field = fields.Char('Resource Field', readonly=True)
    res_model = fields.Char('Resource Model', readonly=True, help="The database object this attachment will be attached to.")
    res_id = fields.Integer('Resource ID', readonly=True, help="The record id this is attached to.")
    type = fields.Selection([('url', 'URL'), ('binary', 'File')],
                            string='Type', required=True, default='binary', change_default=True,
                            help="You can either upload a file from your computer or copy/paste an internet link to your file.")
    url = fields.Char('Url', index=True, size=1024)
    db_datas = fields.Binary('Database Data')
    store_fname = fields.Char('Stored Filename')
    mimetype = fields.Char('Mime Type', readonly=True)
    applicant_id = fields.Many2one('hr.applicant', string="Applicant ID")


    # the field 'datas' is computed and may use the other fields below
    datas = fields.Binary(string='File Content', compute='_compute_datas', inverse='_inverse_datas')


    @api.depends('store_fname', 'db_datas')
    def _compute_datas(self):
        bin_size = self._context.get('bin_size')
        for attach in self:
            if attach.store_fname:
                attach.datas = self._file_read(attach.store_fname, bin_size)
            else:
                attach.datas = attach.db_datas
    @api.model
    def _file_read(self, fname, bin_size=False):
        full_path = self._full_path(fname)
        r = ''
        try:
            if bin_size:
                r = human_size(os.path.getsize(full_path))
            else:
                r = base64.b64encode(open(full_path,'rb').read())
        except (IOError, OSError):
            _logger.info("_read_file reading %s", full_path, exc_info=True)
        return r

    @api.model
    def _storage(self):
        return self.env['ir.config_parameter'].sudo().get_param('recruitment_attachment.location', 'file')
    @api.model
    def _filestore(self):
        return config.filestore(self._cr.dbname)


    def _compute_checksum(self, bin_data):
        """ compute the checksum for the given datas
            :param bin_data : datas in its binary form
        """
        # an empty file has a checksum too (for caching)
        return hashlib.sha1(bin_data or b'').hexdigest()

    @api.model
    def _index(self, bin_data, datas_fname, file_type):
        """ compute the index content of the given filename, or binary data.
            This is a python implementation of the unix command 'strings'.
            :param bin_data : datas in binary form
            :return index_content : string containing all the printable character of the binary data
        """
        index_content = False
        if file_type:
            index_content = file_type.split('/')[0]
            if index_content == 'text': # compute index_content only for text type
                words = re.findall(b"[\x20-\x7E]{4,}", bin_data)
                index_content = b"\n".join(words).decode('ascii')
        return index_content

    
    @api.model
    def _full_path(self, path):
        # sanitize path
        path = re.sub('[.]', '', path)
        path = path.strip('/\\')
        return os.path.join(self._filestore(), path)

    @api.model
    def _get_path(self, bin_data, sha):
        # retro compatibility
        fname = sha[:3] + '/' + sha
        full_path = self._full_path(fname)
        if os.path.isfile(full_path):
            return fname, full_path        # keep existing path

        # scatter files across 256 dirs
        # we use '/' in the db (even on windows)
        fname = sha[:2] + '/' + sha
        full_path = self._full_path(fname)
        dirname = os.path.dirname(full_path)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        return fname, full_path

    @api.model
    def _file_write(self, value, checksum):
        bin_value = base64.b64decode(value)
        fname, full_path = self._get_path(bin_value, checksum)
        if not os.path.exists(full_path):
            try:
                with open(full_path, 'wb') as fp:
                    fp.write(bin_value)
                # add fname to checklist, in case the transaction aborts
                self._mark_for_gc(fname)
            except IOError:
                _logger.info("_file_write writing %s", full_path, exc_info=True)
        return fname

    def _mark_for_gc(self, fname):
        """ Add ``fname`` in a checklist for the filestore garbage collection. """
        # we use a spooldir: add an empty file in the subdirectory 'checklist'
        full_path = os.path.join(self._full_path('checklist'), fname)
        if not os.path.exists(full_path):
            dirname = os.path.dirname(full_path)
            if not os.path.isdir(dirname):
                with tools.ignore(OSError):
                    os.makedirs(dirname)
            open(full_path, 'ab').close()

    def _inverse_datas(self):
        location = self._storage()
        for attach in self:
            # compute the fields that depend on datas
            value = attach.datas
            bin_data = base64.b64decode(value) if value else b''
            vals = {
                'file_size': len(bin_data),
                'checksum': self._compute_checksum(bin_data),
                'index_content': self._index(bin_data, attach.datas_fname, attach.mimetype),
                'store_fname': False,
                'db_datas': value,
            }
            if value and location != 'db':
                # save it to the filestore
                vals['store_fname'] = self._file_write(value, vals['checksum'])
                vals['db_datas'] = False

            # take current location in filestore to possibly garbage-collect it
            fname = attach.store_fname
            # write as superuser, as user probably does not have write access
            super(RecruitmentAttachment, attach.sudo()).write(vals)
            if fname:
                self._file_delete(fname)

    #  def _make_pdf(self, output, name_ext):
    #     """
    #     :param output: PdfFileWriter object.
    #     :param name_ext: the additional name of the new attachment (page count).
    #     :return: the id of the attachment.
    #     """
    #     self.ensure_one()
    #     try:
    #         stream = io.BytesIO()
    #         output.write(stream)
    #         return self.copy({
    #             'name': self.name+'-'+name_ext,
    #             'datas_fname': os.path.splitext(self.datas_fname or self.name)[0]+'-'+name_ext+".pdf",
    #             'datas': base64.b64encode(stream.getvalue()),
    #         })
    #     except Exception:
    #         raise Exception