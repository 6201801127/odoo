
odoo.define('kw_dms.FileSearchPanel', function (require) {
"use strict";

var core = require('web.core');
var ajax = require('web.ajax');
var session = require('web.session');

//modified by T Ketaki
var SearchPanel = require('kw_web_searchpanel.SearchPanel');

var _t = core._t;
var QWeb = core.qweb;

var FileSearchPanel = SearchPanel.extend({
	getSelectedDirectory: function () {
        var category = _.findWhere(this.categories, {
    		fieldName: 'directory'
    	});
        return category.activeValueId;
    },
});

return FileSearchPanel;

});