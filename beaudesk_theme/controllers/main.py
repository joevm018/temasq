# -*- coding: utf-8 -*-

import datetime
from itertools import islice
import json
import xml.etree.ElementTree as ET

import logging
import re

import werkzeug.utils
import urllib2
import werkzeug.wrappers


import odoo
from odoo.addons.web.controllers.main import WebClient, Binary
import functools
from odoo import api
from odoo import http
from odoo.http import request
from odoo import http as http1
from odoo.modules import get_resource_path

from cStringIO import StringIO

logger = logging.getLogger(__name__)

# Completely arbitrary limits
MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT = IMAGE_LIMITS = (1024, 768)
LOC_PER_SITEMAP = 45000
SITEMAP_CACHE_TIME = datetime.timedelta(hours=12)


class Backend(odoo.addons.web.controllers.main.Home):
    #------------------------------------------------------
    # View
    #------------------------------------------------------

    @http.route('/backend/customize_template_get', type='json', auth='user', website=True)
    def backend_customize_template_get(self, key, full=False, bundles=False):
        """ Get inherit view's informations of the template ``key``. By default, only
        returns ``customize_show`` templates (which can be active or not), if
        ``full=True`` returns inherit view's informations of the template ``key``.
        ``bundles=True`` returns also the asset bundles
        """
        return request.env["ir.ui.view"].customize_template_get(key, full=full, bundles=bundles)

    def get_view_ids(self, xml_ids):
        ids = []
        for xml_id in xml_ids:
            if "." in xml_id:
                xml = xml_id.split(".")
                view_model = request.env.ref(xml_id).id
            else:
                view_model = int(xml_id)
            ids.append(view_model)
        return ids

    @http.route(['/backend/theme_customize_get'], type='json', auth="public", website=True)
    def backend_theme_customize_get(self, xml_ids):
        enable = []
        disable = []
        ids = self.get_view_ids(xml_ids)
        for view in request.env['ir.ui.view'].with_context(active_test=True).browse(ids):
            if view.active:
                enable.append(view.xml_id)
            else:
                disable.append(view.xml_id)
        return [enable, disable]

    @http.route(['/backend/theme_customize'], type='json', auth="public", website=True)
    def backend_theme_customize(self, enable, disable, get_bundle=False):
        """ enable or Disable lists of ``xml_id`` of the inherit templates
        """
        def set_active(ids, active):
            if ids:
                real_ids = self.get_view_ids(ids)
                request.env['ir.ui.view'].with_context(
                    active_test=True).browse(real_ids).write({'active': active})

        set_active(disable, False)
        set_active(enable, True)

        if get_bundle:
            context = dict(request.context, active_test=True)
            return request.env["ir.qweb"]._get_asset('web.assets_backend', options=context)
        return True

    @http.route(['/backend/theme_customize_reload'], type='http', auth="public", website=True)
    def backend_theme_customize_reload(self, href, enable, disable):
        self.backend_theme_customize(enable and enable.split(
            ",") or [], disable and disable.split(",") or [])
        redirect_path = href + ("&theme=true" if "#" in href else "#theme=true")
        return request.redirect(redirect_path)

    @http.route(['/website/multi_render'], type='json', auth="public", website=True)
    def multi_render(self, ids_or_xml_ids, values=None):
        res = {}
        for id_or_xml_id in ids_or_xml_ids:
            res = request.env["ir.ui.view"].render(id_or_xml_id, values=values, engine='ir.qweb')
        return res