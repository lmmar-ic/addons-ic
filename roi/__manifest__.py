# -*- coding: utf-8 -*-
##############################################################################
#    License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
#    Copyright (C) 2020 Comunitea Servicios Tecnológicos S.L. All Rights Reserved
#    Vicente Ángel Gutiérrez Fernández <vicente@comunitea.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "ROI",
    "version": "14.0.1.0.0",
    "category": "Sales",
    "author": "www.serincloud.com",
    "maintainer": "Pedroguirao",
    "website": "www.serincloud.com",
    "license": "AGPL-3",
    "depends": [
        'sale_management',
        'contract',
        'base_automation',
    ],
    "data": [
        "views/roi_set.xml",
        "views/menu_views.xml",
        "views/roi.xml",
        #"data/action_server.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
}
