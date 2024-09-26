odoo.define('tree_button_confirm.confirm_dialog', function (require) {
    "use strict";


    var ListRenderer = require('web.ListRenderer');
    var viewUtils = require('web.viewUtils');
    var Dialog = require('web.Dialog');



    ListRenderer.include({
        _renderButton: function (record, node) {
            var self = this;
            var nodeWithoutWidth = Object.assign({}, node);
            delete nodeWithoutWidth.attrs.width;

            let extraClass = '';
            if (node.attrs.icon) {
                // if there is an icon, we force the btn-link style, unless a btn-xxx
                // style class is explicitely provided
                const btnStyleRegex = /\bbtn-[a-z]+\b/;
                if (!btnStyleRegex.test(nodeWithoutWidth.attrs.class)) {
                    extraClass = 'btn-link o_icon_button';
                }
            }
            var $button = this._renderButtonFromNode(nodeWithoutWidth, {
                extraClass: extraClass,
            });
            this._handleAttributes($button, node);
            this._registerModifiers(node, record, $button);

            if (record.res_id) {
                // TODO this should be moved to a handler
                var attrs = node.attrs;
                $button.on("click", function (e) {
                    e.stopPropagation();
                    if (attrs.confirm){
                        new Promise(function (resolve, reject) {
                            Dialog.confirm(self, attrs.confirm, {
                                confirm_callback: function (){
                                    self.trigger_up('button_clicked', {
                                        attrs: node.attrs,
                                        record: record,
                                    });
                                },
                            }).on("closed", null, resolve);
                        });
                    }else{
                        self.trigger_up('button_clicked', {
                            attrs: node.attrs,
                            record: record,
                        });
                    }

                });
            } else {
                if (node.attrs.options.warn) {
                    $button.on("click", function (e) {
                        e.stopPropagation();
                        self.do_warn(false, _t('Please click on the "save" button first'));
                    });
                } else {
                    $button.prop('disabled', true);
                }
            }
            return $button;
        },
    })


});