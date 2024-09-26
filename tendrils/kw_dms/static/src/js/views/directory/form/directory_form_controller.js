
odoo.define('kw_dms.DirectoryFormController', function (require) {
"use strict";

var core = require('web.core');
var ajax = require('web.ajax');
var session = require('web.session');

var FormController = require('web.FormController');

var _t = core._t;
var QWeb = core.qweb;

var DirectoryFormController = FormController.extend({
	createRecord: function (parentID) {
        var record = this.model.get(this.handle, {raw: true});
        var context = _.extend({}, record.getContext(), {
        	default_parent_directory: record.data.id,
        });
        return this.model.load({
            context: context,
            fields: record.fields,
            fieldsInfo: record.fieldsInfo,
            modelName: this.modelName,
            parentID: parentID,
            res_ids: record.res_ids,
            type: 'record',
            viewType: 'form',
        }).then(function (handle) {
        	this.handle = handle;
            this._updateEnv();
            return this._setMode('edit');
        }.bind(this));
    },
});

return DirectoryFormController;

});
