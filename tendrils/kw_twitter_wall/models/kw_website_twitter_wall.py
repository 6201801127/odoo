# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import logging

import requests
from odoo import api, fields, models

API_ENDPOINT = 'https://api.twitter.com'
API_VERSION = '1.1'
REQUEST_TOKEN_URL = '%s/oauth2/token' % API_ENDPOINT
REQUEST_WALL_LIST_URL = '%s/%s/statuses/user_timeline.json' % (API_ENDPOINT, API_VERSION)
URLOPEN_TIMEOUT = 10

_logger = logging.getLogger(__name__)


class KwWebsiteTwitterWall(models.Model):
    _inherit = 'website'

    twitter_api_key = fields.Char(string='Twitter API key', help='Twitter API Key')
    twitter_api_secret = fields.Char(string='Twitter API secret', help='Twitter API Secret')
    twitter_screen_name = fields.Char(string='Get favorites from this screen name')

    @api.model
    def _request_twitter(self, website, url, params=None):
        """Send an authenticated request to the Twitter API."""
        access_token = self._get_twitter_access_token(website)
       
        try:
            request = requests.get(url, params=params, headers={'Authorization': 'Bearer %s' % access_token}, timeout=URLOPEN_TIMEOUT)
            request.raise_for_status()
            return request.json()
        except requests.HTTPError as e:
            _logger.debug("Twitter API request failed with code: %r, msg: %r, content: %r",
                          e.response.status_code, e.response.reason, e.response.content)
            raise

    @api.model
    def _refresh_wall_tweets(self):
        ''' called by cron job '''
        website = self.env['website'].search([('twitter_api_key', '!=', False),
                                          ('twitter_api_secret', '!=', False),
                                          ('twitter_screen_name', '!=', False)])
        _logger.debug("Refreshing tweets for website IDs: %r", website.ids)
        website.fetch_wall_tweets()

    @api.multi
    def fetch_wall_tweets(self):
        WebsiteTweets = self.env['kw_website_twitter_wall_tweet']
        tweet_ids = []

        
        for website in self:
            if not all((website.twitter_api_key, website.twitter_api_secret, website.twitter_screen_name)):
                _logger.debug("Skip fetching favorite tweets for unconfigured website %s", website)
                continue
            # params = {'screen_name': website.twitter_screen_name} tweet_mode='extended'
            params = {'screen_name': website.twitter_screen_name,'tweet_mode':'extended'}
            last_tweet = WebsiteTweets.search([('website_id', '=', website.id),
                                                     ('screen_name', '=', website.twitter_screen_name)],
                                                     limit=1, order='tweet_id desc')

            

            if last_tweet:
                params['since_id'] = int(last_tweet.tweet_id)
            _logger.debug("Fetching favorite tweets using params %r", params)
            response = self._request_twitter(website, REQUEST_WALL_LIST_URL, params=params)

            #print(response)

            for tweet_dict in response:

              
                tweet_id = tweet_dict['id']  # unsigned 64-bit snowflake ID
                tweet_ids = WebsiteTweets.search([('tweet_id', '=', tweet_id)]).ids
                if not tweet_ids:
                    new_tweet = WebsiteTweets.create(
                            {
                              'website_id': website.id,
                              'tweet': json.dumps(tweet_dict),
                              'tweet_id': tweet_id,  # stored in NUMERIC PG field
                              'screen_name': website.twitter_screen_name,
                            })
                    _logger.debug("Found new favorite: %r, %r", tweet_id, tweet_dict)
                    tweet_ids.append(new_tweet.id)
        return tweet_ids

    def _get_twitter_access_token(self, website):
        """Obtain a bearer token."""
        r = requests.post(
            REQUEST_TOKEN_URL,
            data={'grant_type': 'client_credentials',},
            auth=(website.twitter_api_key, website.twitter_api_secret),
            timeout=URLOPEN_TIMEOUT,
        )
        r.raise_for_status()
        data = r.json()
        access_token = data['access_token']
        return access_token



    