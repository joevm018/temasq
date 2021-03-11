odoo.define('pos_dashboard.Record', function (require) {
"use strict";


var FusionCharts = require('fusioncharts');
var jQueryFusionCharts = require('jquery-fusioncharts');
var Charts = require('fusioncharts/fusioncharts.charts');
var FusionTheme = require('fusioncharts/themes/fusioncharts.theme.fusion')

Charts(FusionCharts);
FusionTheme(FusionCharts);

var kanban_record = require('web_kanban.Record');

var QWeb = core.qweb;
var fields_registry = kanban_widgets.registry;


kanban_record.KanbanRecord.include({
    renderElement: function () {
        this._super();
        this.setup_color_picker();
        this.$el.addClass('o_kanban_record');
        this.$el.data('record', this);
        if (this.$el.hasClass('oe_kanban_global_click') || this.$el.hasClass('oe_kanban_global_click_edit')) {
            this.$el.on('click', this.proxy('on_global_click'));
        }
    }
});

$('.grid-container').removeClass('o_kanban_record');

});
