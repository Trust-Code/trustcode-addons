odoo.define('activity_checklist.Checklist', function (require) {
    "use strict";

    var Chatter = require('mail.Chatter');
    var AbstractField = require('web.AbstractField');
    var field_registry = require('web.field_registry');
    var BasicView = require('web.BasicView');
    var rpc = require('web.rpc');
    var core = require('web.core');

    var QWeb = core.qweb;

    BasicView.include({
        init: function (viewInfo) {
            this._super.apply(this, arguments);
            var fieldsInfo = viewInfo.fieldsInfo[this.viewType];
            for (let fieldName in fieldsInfo) {
                let fieldInfo = fieldsInfo[fieldName];
                if ('activity_checklist' == fieldInfo.widget) {
                    this.mailFields['activity_checklist'] = fieldName;
                    fieldInfo.__no_fetch = true;
                }
            }
            this.rendererParams.activeActions = this.controllerParams.activeActions;
            this.rendererParams.mailFields = this.mailFields;
        },
    });

    Chatter.include({
        events: _.defaults({
            'click .o_chatter_button_create_checklist': 'open_create_checklist_view'
        }, Chatter.prototype.events),
        init: function (parent, record, mailFields, options) {
            this._super.apply(this, arguments)
            if (mailFields.activity_checklist) {
                this.fields.checklist = new Checklist(this, mailFields.activity_checklist, record, options);
            }
        },
        open_create_checklist_view: function () {
            this.fields.checklist.createChecklist()
        },
        _onReloadMailFields: function (event) {
            this._super.apply(this, arguments)
            var fieldNames = [];
            if (this.fields.checklist && event.data.checklist) {
                fieldNames.push(this.fields.checklist.name);
            }
            this.trigger_up('reload', {
                fieldNames: fieldNames,
                keepChanges: true,
            });
        },
    });

    var AbstractChecklistField = AbstractField.extend({
        // private
        _createActivityChecklist: function (id, callback) {
            var action = {
                type: 'ir.actions.act_window',
                res_model: 'activity.checklist',
                view_mode: 'form',
                view_type: 'form',
                views: [[false, 'form']],
                target: 'new',
                context: {
                    default_res_id: this.res_id,
                    default_res_model: this.model,
                },
                res_id: id || false,
            };
            return this.do_action(action, { on_close: callback });
        },
    });

    var Checklist = AbstractChecklistField.extend({
        className: 'o_activity_checklist',
        // inherited
        init: function () {
            this._super.apply(this, arguments);
        },
        _render: function () {
                var self = this
                rpc.query({
                model: 'activity.checklist',
                method: 'search_read',
                fields: ['id', 'name', 'checklist_item_ids'],
                domain: [['res_id', '=', this.res_id],
                ['res_model', '=', this.model]],
            }).then(function (clist) {
                if (clist.length) {
                    self.$el.html(QWeb.render('activity_checklist.checklist_template', {
                        checklist: clist[0],
                    }));
                } else {
                    self.$el.empty();
                }
            });
        },
        // public
        createChecklist: function () {
            var callback = this._reload.bind(this, {checklist: true});
            return this._createActivityChecklist(false, callback);
        },
        // private
        _reload: function (fieldsToReload) {
            this.trigger_up('reload_mail_fields', fieldsToReload);
        },

    });

    field_registry.add('activity_checklist', Checklist)

    return Checklist;
});