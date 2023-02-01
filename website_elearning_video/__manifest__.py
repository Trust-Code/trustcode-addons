#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

# -*- coding: utf-8 -*-
# © 2016 ONESTEiN BV (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name'          : "Odoo eLearning Video Uploader",
    'version'       : '1.3.1',
    'summary'       : """Website Slides Video Uploader""",
    'author'        : 'Webkul Software Pvt. Ltd.',
    'website'       : 'https://store.webkul.com',
    "license"       :  "Other proprietary",
    'category'      : 'website',
    "live_test_url" : "http://odoodemo.webkul.com/?module=website_elearning_video",
    'description'   : """Odoo eLearning Video Uploader facilitates you upload the video from
     your local hence, you are not dependent upon youtube to upload the video.""",
    'depends'       : [
        'website_slides',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'wizard/attachment_wizard_view.xml',
        'views/website_slides_video_views.xml',
        'views/website_slides.xml',
    ],

    'demo':['demo/demo.xml'],

    'qweb': [
        'static/xml/extend_video_slides.xml',
    ],
    "images"        :  ['static/description/Banner.png'],
    "application"   :  True,
    "installable"   :  True,
    "auto_install"  :  False,
    "price"         :  45,
    "currency"      :  "USD",
    'sequence'      :   1,
    'pre_init_hook' :   'pre_init_check',
}
