odoo.define('kw_dms.FileListView', function (require) {
"use strict";

var core = require('web.core');
var registry = require('web.view_registry');

var ListView = require('web.ListView');

var FileListController = require('kw_dms.FileListController');

var _t = core._t;
var QWeb = core.qweb;

var FileListView = ListView.extend({
	config: _.extend({}, ListView.prototype.config, {
        Controller: FileListController,
    }),
});

registry.add('file_list', FileListView);

return FileListView;

});
