odoo.define('kw_dms.FileListController', function (require) {
"use strict";

var core = require('web.core');
var ajax = require('web.ajax');
var session = require('web.session');

var ListController = require('web.ListController');

var _t = core._t;
var QWeb = core.qweb;

var FileListController = ListController.extend({});

return FileListController;

});
