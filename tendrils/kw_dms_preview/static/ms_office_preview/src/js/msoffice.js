/**********************************************************************************
*
*    Copyright (c) 2017-2019 MuK IT GmbH.
*
*    This file is part of MuK Preview MS Office 
*    (see https://mukit.at).
*
*    This program is free software: you can redistribute it and/or modify
*    it under the terms of the GNU Lesser General Public License as published by
*    the Free Software Foundation, either version 3 of the License, or
*    (at your option) any later version.
*
*    This program is distributed in the hope that it will be useful,
*    but WITHOUT ANY WARRANTY; without even the implied warranty of
*    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*    GNU Lesser General Public License for more details.
*
*    You should have received a copy of the GNU Lesser General Public License
*    along with this program. If not, see <http://www.gnu.org/licenses/>.
*
**********************************************************************************/

odoo.define('muk_preview_markdown.PreviewContentMSOffice', function (require) {
"use strict";

var core = require('web.core');
var ajax = require('web.ajax');
var utils = require('web.utils');
var session = require('web.session');

var registry = require('muk_preview.registry');

var AbstractPreviewContent = require('muk_preview.AbstractPreviewContent');

var QWeb = core.qweb;
var _t = core._t;

var PreviewContentMSOffice = AbstractPreviewContent.extend({
	template: "muk_preview.PreviewContentMSOffice",    
	willStart: function() { 
		var def = $.Deferred();
		this._downloadFile().done(function(file) {
			this._createAttachment(file).done(function(data) {
				this.attachment = data;
				def.resolve();
			}.bind(this));
		}.bind(this));
		return $.when(this._super.apply(this, arguments), def);
    },
    renderPreviewContent: function() {
		// var viewer = 'https://view.officeapps.live.com/op/embed.aspx?src=';
		var viewer = 'https://docs.google.com/gview?url=';
		// this.$('iframe').attr('src', viewer + encodeURIComponent(this.attachment.url));

		this.$('iframe').attr('src', viewer +this.attachment.url+'&embedded=true');
		
		console.log(viewer + encodeURIComponent(this.attachment.url))

		console.log(this.attachment.url)
		return this._super.apply(this, arguments);
		

// 		<iframe src="https://docs.google.com/gview?url=http://ieee802.org/secmail/docIZSEwEqHFr.doc&embedded=true" frameborder="0">
// </iframe>
		// https://view.officeapps.live.com/op/embed.aspx?src=http%3A%2F%2Fieee802%2Eorg%3A80%2Fsecmail%2FdocIZSEwEqHFr%2Edoc
    },
    destroy: function () {
        if (this.attachment) {
        	this._rpc({
                model: 'ir.attachment',
                method: 'unlink',
                args: [this.attachment.id],
                context: session.user_context,
            }, {
            	shadow: true,
            });
        }
        return this._super.apply(this, arguments);
    },
    _downloadFile: function() {
		return $.ajax({
			url: this.url,
			dataType: "binary",
		}).fail(function(jqXHR, textStatus) {
			console.error(textStatus);
		});
    },
    _createAttachment: function(file) {
    	var form = new FormData();
		form.append('temporary', true);
		form.append('ufile', file, this.filename);
		form.append('csrf_token', core.csrf_token);
		return $.ajax({
		    data: form,
		    type: 'POST',
            dataType: 'json',
		    url: '/utils/attachment/add',
		    enctype: 'multipart/form-data',
		    processData: false,
		    contentType: false
		}).fail(function(jqXHR, textStatus) {
			console.error(textStatus);
		});
    },
    downloadable: false,
    printable: false,
});

_.each([
	'doc', 'docx', 'docm', 'ppt', 'pptx', 'pptm', 'xls', 'xlsx', 'xlsm', 'xlsb'
], function(extension) {
	registry.add(extension, PreviewContentMSOffice);
	registry.add("." + extension, PreviewContentMSOffice);
});
_.each([
	'application/msword', 'application/ms-word', 'application/vnd.ms-word.document.macroEnabled.12',
	'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/vnd.mspowerpoint',
	'application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
	'application/vnd.ms-powerpoint.presentation.macroEnabled.12', 'application/vnd.ms-excel',
	'application/vnd.msexcel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
	'application/vnd.ms-excel.sheet.binary.macroEnabled.12', 'application/vnd.ms-excel.sheet.macroEnabled.12'
], function(mimetype) {
	registry.add(mimetype, PreviewContentMSOffice);
});

return PreviewContentMSOffice;

});
