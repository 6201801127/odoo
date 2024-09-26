odoo.define('kw_dms.FileKanbanView', function (require) {
"use strict";

var core = require('web.core');
var registry = require('web.view_registry');

var KanbanView = require('web.KanbanView');

var FileKanbanModel = require('kw_dms.FileKanbanModel');
var FileKanbanRenderer = require('kw_dms.FileKanbanRenderer');
var FileKanbanController = require('kw_dms.FileKanbanController');
var FileSearchPanel = require('kw_dms.FileSearchPanel');

var _t = core._t;
var QWeb = core.qweb;

var FileKanbanView = KanbanView.extend({
	config: _.extend({}, KanbanView.prototype.config, {
		Renderer: FileKanbanRenderer,
        Controller: FileKanbanController,
        Model: FileKanbanModel,
		SearchPanel: FileSearchPanel,
    }),
});

registry.add('file_kanban', FileKanbanView);

return FileKanbanView;

});
