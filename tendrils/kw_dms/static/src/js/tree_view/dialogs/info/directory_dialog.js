
odoo.define('muk_dms_dialogs.DocumentDirectoryInfoDialog', function(require) {
"use strict";

var core = require('web.core');

var DocumentInfoDialog = require('muk_dms_dialogs.DocumentInfoDialog');

var _t = core._t;
var QWeb = core.qweb;

var DocumentDirectoryInfoDialog = DocumentInfoDialog.extend({
    init: function (parent, options) {
    	this.options = options || {};
        this._super(parent, _.extend({}, {
            fields: [
            	"name", "count_directories", "count_files",
            	"count_total_directories", "count_total_files", 
            	"size", "write_date", "write_uid"
            ],
            title: _t("Directory"),
            model: "kw_dms.directory",
            qweb: "muk_dms.DocumentDirectoryInfoDialog",
        }, this.options));
    },
});

return DocumentDirectoryInfoDialog;

});