odoo.define('kw_twitter_wall.editor', function (require) {
'use strict';

var core = require('web.core');
var dom = require('web.dom');
var sOptions = require('web_editor.snippets.options');

var _t = core._t;

sOptions.registry.twitter_wall = sOptions.Class.extend({
    /**
     * @override
     */
    start: function () {
        var self = this;
        var $configuration = dom.renderButton({
            attrs: {
                class: 'btn-primary d-none',
                contenteditable: 'false',
            },
            text: _t("Reload"),
        });
        $configuration.appendTo(document.body).on('click', function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            self._rpc({route: '/website_twitter_wall/reload'});
        });
        this.$target.on('mouseover.kw_twitter_wall', function () {
            var $selected = $(this);
            var position = $selected.offset();
            $configuration.removeClass('d-none').offset({
                top: $selected.outerHeight() / 2
                        + position.top
                        - $configuration.outerHeight() / 2,
                left: $selected.outerWidth() / 2
                        + position.left
                        - $configuration.outerWidth() / 2,
            });
        }).on('mouseleave.kw_twitter_wall', function (e) {
            var current = document.elementFromPoint(e.clientX, e.clientY);
            if (current === $configuration[0]) {
                return;
            }
            $configuration.addClass('d-none');
        });
        this.$target.on('click.kw_twitter_wall', '.lnk_configure', function (e) {
            window.location = e.currentTarget.href;
        });
        this.trigger_up('animation_stop_demand', {
            $target: this.$target,
        });
        return this._super.apply(this, arguments);
    },
    /**
     * @override
     */
    cleanForSave: function () {
        this.$target.find('.twitter_wall_timeline').empty();
    },
    /**
     * @override
     */
    destroy: function () {
        this._super.apply(this, arguments);
        this.$target.off('.kw_twitter_wall');
    },
});
});
