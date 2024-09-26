odoo.define('muk_preview_markdown.PreviewContentImage', function (require) {
"use strict";

var core = require('web.core');
var ajax = require('web.ajax');
var utils = require('web.utils');
var session = require('web.session');

var registry = require('muk_preview.registry');

var AbstractPreviewContent = require('muk_preview.AbstractPreviewContent');

var QWeb = core.qweb;
var _t = core._t;

var PreviewContentImage = AbstractPreviewContent.extend({
	template: "muk_preview.PreviewContentImage",    
	cssLibs: [
    ],
    jsLibs: [
    ],
    renderPreviewContent: function() {
    	this.$('.mk_preview_image').css({
            "background-size": "contain",
            "background-repeat": "no-repeat",
            "background-position": "center",
            "background-image": "url(" + this.url + ")"
        });
    },
    downloadable: true,
    printable: true,
});

_.each([
	'cod', 'ras', 'fif', 'gif', 'ief', 'jpeg', 'jpg', 'jpe', 'png', 'tiff',
    'tif', 'mcf', 'wbmp', 'fh4', 'fh5', 'fhc', 'ico', 'pnm', 'pbm', 'pgm',
    'ppm', 'rgb', 'xwd', 'xbm', 'xpm'
], function(extension) {
	registry.add(extension, PreviewContentImage);
	registry.add("." + extension, PreviewContentImage);
});
_.each([
	'image/cis-cod', 'image/cmu-raster', 'image/fif', 'image/gif', 'image/ief',
	'image/png', 'image/tiff', 'image/vasa', 'image/vnd.wap.wbmp', 'image/x-freehand',
	'image/x-portable-anymap', 'image/x-portable-bitmap', 'image/x-portable-graymap',
	'image/x-portable-pixmap', 'image/x-rgb', 'image/x-windowdump', 'image/x-xbitmap', 
	'image/jpeg', 'image/x-icon', 'image/x-xpixmap'
], function(mimetype) {
	registry.add(mimetype, PreviewContentImage);
});

return PreviewContentImage;

});
