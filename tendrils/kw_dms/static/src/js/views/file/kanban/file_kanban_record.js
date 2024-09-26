

odoo.define('kw_dms.FileKanbanRecord', function (require) {
"use strict";

var core = require('web.core');
var ajax = require('web.ajax');
var session = require('web.session');

var KanbanRecord = require('web.KanbanRecord');

var _t = core._t;
var QWeb = core.qweb;

var FileKanbanRecord = KanbanRecord.extend({

});

return FileKanbanRecord;

});
