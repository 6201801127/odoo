

odoo.define('kw_dms.FileFormView', function (require) {
"use strict";

var core = require('web.core');
var registry = require('web.view_registry');

var FormView = require('web.FormView');

var FileFormController = require('kw_dms.FileFormController');

var _t = core._t;
var QWeb = core.qweb;

var FileFormView = FormView.extend({
	config: _.extend({}, FormView.prototype.config, {
        Controller: FileFormController,
    }),
});

registry.add('file_form', FileFormView);

return FileFormView;

});
