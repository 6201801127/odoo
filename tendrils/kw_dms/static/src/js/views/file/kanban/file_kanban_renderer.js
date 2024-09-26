

odoo.define('kw_dms.FileKanbanRenderer', function (require) {
"use strict";

var core = require('web.core');
var config = require('web.config');
var session = require('web.session');

var dropzone = require('kw_dms_utils.dropzone');

var KanbanRenderer = require('web.KanbanRenderer');
var FileKanbanRecord = require('kw_dms.FileKanbanRecord');

var _t = core._t;
var QWeb = core.qweb;

var FileKanbanRenderer = KanbanRenderer.extend(dropzone.FileDropzoneMixin, {
	config: _.extend({}, KanbanRenderer.prototype.config, {
        KanbanRecord: FileKanbanRecord,
    }),
	start: function () {
    	var res = this._super.apply(this, arguments);
		this._startDropzone(this.$el);
        return res;
    },
	destroy: function () {
		var res = this._super.apply(this, arguments);
		this._destroyDropzone(this.$el);
        return res;
    },
    _handleDrop: function(event) {
    	var dataTransfer = event.originalEvent.dataTransfer;
    	if (dataTransfer.items && dataTransfer.items.length > 0) {
    		this.trigger_up('upload_files', {
            	items: dataTransfer.items
            });
    	}
	},
});

return FileKanbanRenderer;

});
