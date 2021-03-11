odoo.define('customer_dob.customer_date_of_birth', function (require){"use strict"

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var utils = require('web.utils');
    var Model = require('web.DataModel');
    var round_pr = utils.round_precision;
    var core = require('web.core');
    var QWeb = core.qweb;
    var _t = core._t;
    models.load_fields('res.partner','dob_month');
    models.load_fields('res.partner','dob_day');
    screens.ClientListScreenWidget.include({
        save_client_details: function(partner) {
            var self = this;

            var fields = {};
            this.$('.client-details-contents .detail').each(function(idx,el){
                fields[el.name] = el.value || false;
            });

            if (!fields.name) {
                this.gui.show_popup('error',_t('A Customer Name Is Required'));
                return;
            }

            if (this.uploaded_picture) {
                fields.image = this.uploaded_picture;
            }

            fields.id           = partner.id || false;
            fields.country_id   = fields.country_id || false;


            var customer_new_dob_month = document.getElementById('customer_dob_month');
            var customer_new_dob_monthValue = customer_new_dob_month.options[customer_new_dob_month.selectedIndex].value;
            var customer_new_dob_day = document.getElementById('customer_dob_day');
            var customer_new_dob_dayValue = customer_new_dob_day.options[customer_new_dob_day.selectedIndex].value;

            fields.dob_day   = String(customer_new_dob_dayValue) || false;
            fields.dob_month   = String(customer_new_dob_monthValue) || false;

            new Model('res.partner').call('create_from_ui',[fields]).then(function(partner_id){
                self.saved_client_details(partner_id);
            },function(err,event){
                event.preventDefault();
                self.gui.show_popup('error',{
                    'title': _t('Error: Could not Save Changes'),
                    'body': _t('Your Internet connection is probably down.'),
                });
            });
        },
    });
});
