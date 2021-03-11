import odoo.addons.web.controllers.main as main
from odoo import http
from odoo.http import request
import odoo
import datetime
from odoo.addons.web.controllers.main import ensure_db
from odoo.tools.translate import _


class Home(main.Home):
    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        ensure_db()
        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return http.redirect_with_hash(redirect)

        if not request.uid:
            request.uid = odoo.SUPERUSER_ID

        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method == 'POST':
            old_uid = request.uid
            uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
            if uid is not False:
                # ***************************Additional*****************************
                restrict_login = request.env['project.shutdown'].search([]).restrict_login
                if restrict_login:
                    shutdown_date = request.env['project.shutdown'].search([]).shutdown_date
                    now = datetime.datetime.now().date()
                    shutdown_date = datetime.datetime.strptime(shutdown_date, '%Y-%m-%d').date()
                    if shutdown_date <= now:
                        values['error'] = _("Please contact Al Kidhma Group for assistance")
                        response = request.render('web.login', values)
                        response.headers['X-Frame-Options'] = 'DENY'
                        return response
                    # ***************************Additional*****************************
                request.params['login_success'] = True
                if not redirect:
                    redirect = '/web'
                return http.redirect_with_hash(redirect)
            request.uid = old_uid
            values['error'] = _("Wrong login/password")
        return request.render('web.login', values)