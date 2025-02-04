# -*- coding: utf-8 -*-
##############################################################################
#    License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
#    Copyright (C) 2021 Serincloud S.L. All Rights Reserved
#    Antonio Cánovas <antonio.canovas@ingenieriacloud.com>
#    Pedro josé Baños Guirao <pedro@serincloud.com>
##############################################################################

{
    "name": "Partner Default Journal",
    "version": "14.0.1.0.0",
    "category": "Partners",
    "author": "www.serincloud.com",
    "maintainer": "Pedroguirao",
    "website": "www.serincloud.com",
    "license": "AGPL-3",
    "depends": [
        'account',
        'base_automation',
    ],
    "data": [
        "views/res_partner_journal.xml",
        "data/action_server.xml",
    ],
    "installable": True,
    "application": True,
}
