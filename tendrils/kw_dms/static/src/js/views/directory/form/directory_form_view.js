

odoo.define('kw_dms.DirectoryFormView', function (require) {
"use strict";

var core = require('web.core');
var registry = require('web.view_registry');

var FormView = require('web.FormView');

var DirectoryFormController = require('kw_dms.DirectoryFormController');

var _t = core._t;
var QWeb = core.qweb;

var DirectoryFormView = FormView.extend({
	config: _.extend({}, FormView.prototype.config, {
        Controller: DirectoryFormController,
    }),
});

registry.add('directory_form', DirectoryFormView);

return DirectoryFormView;

});
