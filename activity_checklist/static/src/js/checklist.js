odoo.define('activity_checklist.Checklist', function (require) {
    "use strict";

    var Chatter = require('mail.Chatter');
    var AbstractField = require('web.AbstractField');
    var field_registry = require('web.field_registry');
    var BasicView = require('web.BasicView');
    var rpc = require('web.rpc');
    var core = require('web.core');

    var QWeb = core.qweb;

    function _readChecklist(self) {
        return rpc.query({
            model: 'activity.checklist',
            method: 'search_read',
            fields: ['id', 'name', 'checklist_item_ids'],
            domain: [['res_id', '=', self.res_id],
            ['res_model', '=', self.model]]
        });
    }

    function _readChecklistItens(checklist) {
        if (!checklist) {
            return [];
        }
        return rpc.query({
            model: 'activity.checklist.item',
            method: 'read',
            args: [checklist.checklist_item_ids]
        }).then(function (result) {
            // convert create_date and date_deadline to moments
            // sort activities by due date
            checklist.checklist_item_ids = _.sortBy(result, 'is_done');
            return checklist;
        });
    }


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
        start: function () {
            this._super()
            console.log(this.$topbar)
            this.$topbar.append(QWeb.render('activity_checklist.checklist_button', {
                checklist_btn: !!this.fields.checklist
            }));
        }
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
        events: {
            'click .checklist_checkbox': '_onMarkChecklistItem',
            'click .o_checklist_done': '_onChecklistDone',
            'click .o_checklist_edit': '_onChecklistEdit',
            'click .o_checklist_unlink': '_onChecklistUnlink',
        },
        init: function () {
            this._super.apply(this, arguments);
        },
        _render: function () {
            var self = this
            _readChecklist(this).then(function (clist) {
                if (clist.length) {
                    _readChecklistItens(clist[0]).then(result => {
                        self.$el.html(QWeb.render('activity_checklist.checklist_template', {
                            checklist: result,
                        })).insertAfter($('.o_chatter_topbar'));
                    });
                } else {
                    self.$el.empty();
                }
            });
        },
        createChecklist: function () {
            var callback = this._reload.bind(this, { checklist: true });
            return this._createActivityChecklist(false, callback);
        },
        _reload: function (fieldsToReload) {
            this.trigger_up('reload_mail_fields', fieldsToReload);
        },
        _updateChecklistRecord: function (id, value) {
            return this._rpc({
                model: 'activity.checklist.item',
                method: 'write',
                args: [id, { 'is_done': value }]
            });
        },
        _onMarkChecklistItem: function () {
            _readChecklist(this).then(result => {
                _.each(result[0].checklist_item_ids, (item => {
                    let checkbox = $(`input#${item}`).is(":checked")
                    this._updateChecklistRecord(item, checkbox)
                }))
            })
        },
        _onChecklistEdit: function (event, options) {
            event.preventDefault();
            var self = this;
            var checklist_id = $(event.currentTarget).data('checklist-id');
            var action = _.defaults(options || {}, {
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
                res_id: checklist_id,
            });
            return this.do_action(action, {
                on_close: function () {
                    self._reload({ checklist: true });
                },
            });
        },
        _onChecklistUnlink: function (event, options) {
            event.preventDefault();
            var self = this
            var checklist_id = $(event.currentTarget).data('checklist-id');
            options = _.defaults(options || {}, {
                model: 'activity.checklist',
                args: [[checklist_id]],
            });
            return this._rpc({
                model: options.model,
                method: 'unlink',
                args: options.args,
            }).then(self._reload({ checklist: true }));
        },
        _onChecklistDone: function (event, options) {
            event.preventDefault();
            var checklist_id = $(event.currentTarget).data('checklist-id');
            var self = this
            options = _.defaults(options || {}, {
                model: 'activity.checklist',
                args: [[checklist_id]],
            });
            return this._rpc({
                model: options.model,
                method: 'mark_checklist_done',
                args: options.args,
            }).then(self._reload.bind(self, { checklist: true, thread: true }));
        },
    });

    field_registry.add('activity_checklist', Checklist)

    return Checklist;
});