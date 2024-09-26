
odoo.define('muk_preview_markdown.PreviewContentOpenDocument', function (require) {
"use strict";

var core = require('web.core');
var ajax = require('web.ajax');
var utils = require('web.utils');
var session = require('web.session');

var registry = require('muk_preview.registry');

var AbstractPreviewContent = require('muk_preview.AbstractPreviewContent');

var QWeb = core.qweb;
var _t = core._t;

var PreviewContentOpenDocument = AbstractPreviewContent.extend({
	template: "muk_preview.PreviewContentOpenDocument",
	init: function(parent, url, mimetype, filename) {
    	this._super.apply(this, arguments);
        this.viewer_url = '/kw_dms_preview/static/open_document_preview/lib/' + 
        	'viewerjs/index.html#' + this.url; //encodeURIComponent(this.url);
        console.log(this.viewer_url)
    },
    downloadable: false,
    printable: false,
});

_.each([
	'.odt', '.odp', '.ods', '.fodt', '.ott',
	'.fodp', '.otp', '.fods', '.ots'
], function(extension) {
	registry.add(extension, PreviewContentOpenDocument);
});
_.each([
	'odt', 'odp', 'ods', 'fodt', 'ott',
	'fodp', 'otp', 'fods', 'ots'
], function(extension) {
	registry.add(extension, PreviewContentOpenDocument);
});
_.each([
	'application/vnd.oasis.opendocument.text',
	'application/vnd.oasis.opendocument.presentation',
	'application/vnd.oasis.opendocument.spreadsheet'
], function(mimetype) {
	registry.add(mimetype, PreviewContentOpenDocument);
});

return PreviewContentOpenDocument;

});
