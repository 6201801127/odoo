# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
from odoo import _
from odoo import http
from odoo.http import request


class Twitter(http.Controller):

    @http.route(['/website_twitter_wall/reload'], type='json', auth="user", website=True)
    def twitter_reload(self):
        return request.website.fetch_wall_tweets()

    @http.route(['/website_twitter_wall/get_wall_list'], type='json', auth="public", website=True)
    def get_tweets(self, limit=20):
        key = request.website.twitter_api_key
        secret = request.website.twitter_api_secret
        screen_name = request.website.twitter_screen_name
        debug = request.env['res.users'].has_group('website.group_website_publisher')
        if not key or not secret:
            if debug:
                return {"error": _("Please set the Twitter API Key and Secret in the Website Settings.")}
            return []
        if not screen_name:
            if debug:
                return {"error": _("Please set a Twitter screen name to load favorites from, "
                                   "in the Website Settings (it does not have to be yours)")}
            return []
        TwitterTweets = request.env['kw_website_twitter_wall_tweet']
        tweets = TwitterTweets.search(
                [('website_id', '=', request.website.id),
                 ('screen_name', '=', screen_name)],
                limit=int(limit), order="tweet_id desc")
        if len(tweets) < 12:
            if debug:
                return {"error": _("Twitter user @%(username)s has less than 12 favorite tweets. "
                                   "Please add more or choose a different screen name.") % \
                                      {'username': screen_name}}
            else:
                return []
        return tweets.mapped(lambda t: json.loads(t.tweet))



    
    # @http.route('/', auth='public', website=True,type='http', methods=['GET'])
    # def load_homepage_twitter(self):

    #         print(self.get_tweets(limit=20))
       
    #     return http.request.render('kw_twitter_wall.kwantify_homepage_twitter_section')