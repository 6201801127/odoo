

odoo.define('smart_office.header', function (require) {
    "use strict";

    var DocumentsMainView = require('muk_dms_view.DocumentsMainView');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var config = require('web.config');
    var session = require('web.session');
    var web_client = require('web.web_client');
    var framework = require('web.framework');
    var crash_manager = require('web.crash_manager');

    var Widget = require('web.Widget');
    var Dialog = require('web.Dialog');

    var ActionDocumentTreeView = require('muk_dms_view.ActionDocumentTreeView');
    var PreviewManager = require('muk_preview.PreviewManager');
    var PreviewDialog = require('muk_preview.PreviewDialog');

    var _t = core._t;
    var QWeb = core.qweb;

    DocumentsMainView.include({
        _update_cp: function() {
            var self = this;
            if (!this.$buttons) {
                this.$buttons = $(QWeb.render('muk_dms.DocumentTreeViewButtons', {
                    widget: this,
                }));
                this.$buttons.find('.mk_open').on('click', _.bind(this._open_selected_node, this));
                this.$buttons.find('.mk_create').on('click', _.bind(this._create_selected_node, this));
                this.$buttons.find('.mk_incoming_letter').on('click', _.bind(this._create_incoming_letter, this));
                this.$buttons.find('.mk_edit').on('click', _.bind(this._edit_selected_node, this));
                this.$buttons.find('.mk_delete').on('click', _.bind(this._delete_selected_node, this));
            }
            if (!this.$pager) {
                this.$pager = $(QWeb.render('muk_dms.DocumentTreeViewActions', {
                    widget: this,
                }));
                this.$pager.find('.mk_action_help').on('click', _.bind(this._show_help, this));
                this.$pager.find('.mk_refresh').on('click', _.bind(this.refresh, this));
                this.$pager.find('.mk_auto_refresh').on('click', _.bind(this.toggle_refresh, this));
                this.$pager.find('.mk_action_dialog').on('click', _.bind(this.toggle_dialog, this));
            }
            if (!this.$switch_buttons) {
                this.$switch_buttons = $(QWeb.render('muk_dms.DocumentTreeViewOptions', {
                    widget: this,
                }));
                $(this.$switch_buttons[0]).on('click', _.bind(this.show_preview, this));
                $(this.$switch_buttons[2]).on('click', _.bind(this.hide_preview, this));
            }
            if (!this.$searchview) {
                this.$searchview = $(QWeb.render('muk_dms.DocumentTreeViewSearch', {
                    widget: this,
                }));
                this.$searchview.find('#mk_searchview_input').keyup(this._trigger_search.bind(this));
            }
            this.update_control_panel({
                cp_content: {
                    $buttons: this.$buttons,
                    $pager: this.$pager,
                    $searchview: this.$searchview,
                    $switch_buttons: this.$switch_buttons,
                },
                breadcrumbs: this.getParent()._getBreadcrumbs(),
            });


        },
        _create_incoming_letter: function() {
//            self.params['muk_doc_data'] = data;
            var self = this;
            self._rpc({
                model: 'ir.model.data',
                method: 'xmlid_to_res_id',
                kwargs: {xmlid: 'smart_office.view_add_letter_doc_form'},
            }).then(function (res_id) {
//                var muk_res_id = self.params.muk_doc_data.reference.prevObject.selector.split('_').reverse()[0];
                self.do_action({
                    name: _t('Add Document/Letter'),
                    type: 'ir.actions.act_window',
                    res_model: 'muk_dms.file',
                    views: [[res_id, 'form']],
                    target: 'blank',
                    context: {
//                        'default_directory': parseInt(muk_res_id),
                        'smart_office_incoming_letter': 'smart_office',
                    }

                }, {
                    on_reverse_breadcrumb: function() {
                        self.trigger_up('reverse_breadcrumb', {});
                    }
                });
            });
        },
    });

});
