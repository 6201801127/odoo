

odoo.define('muk_dms_dialogs.DocumentFileInfoDialog', function(require) {
"use strict";

var core = require('web.core');

var DocumentInfoDialog = require('muk_dms_dialogs.DocumentInfoDialog');

var _t = core._t;
var QWeb = core.qweb;

var DocumentFileInfoDialog = DocumentInfoDialog.extend({
    init: function (parent, options) {
    	this.options = options || {};
        this._super(parent, _.extend({}, {
            fields: [
            	"name", "mimetype", "size",
            	"write_date", "write_uid"
            ],
            title: _t("File"),
            model: "kw_dms.file",
            qweb: "muk_dms.DocumentFileInfoDialog",
        }, this.options));
    },
});

return DocumentFileInfoDialog;

});