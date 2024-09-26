

odoo.define('kw_dms.FileKanbanController', function (require) {
"use strict";

var core = require('web.core');
var session = require('web.session');

var utils = require('kw_dms_utils.files');
var async = require('kw_dms_utils.async');

var Domain = require('web.Domain');
var KanbanController = require('web.KanbanController');

var FileUpload = require('kw_dms_mixins.FileUpload');

var _t = core._t;
var QWeb = core.qweb;

var FileKanbanController = KanbanController.extend(FileUpload, {
	custom_events: _.extend({}, KanbanController.prototype.custom_events, {
		upload_files: '_onUploadFiles',
    }),
    _getSelectedDirectory: function () {
        var record = this.model.get(this.handle, {raw: true});
        var directoryID = this._searchPanel.getSelectedDirectory();
    	var context = record.getContext();
    	if (directoryID) {
    		return directoryID;
    	} else if (context.active_model === "kw_dms.directory") {
    		return context.active_id;
    	}
    },
	_onUploadFiles: function(event) {
		var directoryID = this._getSelectedDirectory();
		if (directoryID) {
			utils.getFileTree(event.data.items, true).then(
				this._uploadFiles.bind(this, directoryID) 
			);
		} else {
			this.do_warn(_t("Upload Error"), _t("No Directory has been selected!"));
		}
	},
});

return FileKanbanController;

});
