# -*- coding: utf-8 -*-
"""
Created on Tue May  2 17:16:02 2017

@author: Aoshuo-wj
"""

from autohome01.user_agents import agents
import random

class UserAgentMiddleware(object):
    """ 换User-Agent """
    def process_request(self, request, spider):
        agent = random.choice(agents)
        request.headers["User-Agent"] = agent

