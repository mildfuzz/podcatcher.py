#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# ------------------------------------------------------------------------------
# 
# ------------------------------------------------------------------------------

import codecs
import feedparser
import json
import notify2
import os
import requests
import urlparse

# ------------------------------------------------------------------------------

class Podcatcher(object):
    
    def __init__(self, *args, **kwargs):
        pass
    
    # --------------------------------------------------------------------------
    
    def config(self, *args, **kwargs):
        
        if 'path' in kwargs:
            if os.path.exists(kwargs['path']) is True and os.path.isfile(kwargs['path']) is True:
                handle = codecs.open(kwargs['path'], 'rb', 'utf-8')
                
                status = True, json.load(handle)
                
                handle.close()
            
            else:
                status = False, """There is an error in the given path..."""
        
        else:
            status = False, """Path value isn't available..."""
        
        return status
    
    # --------------------------------------------------------------------------
    
    def feed(self, *args, **kwargs):
        
        if 'path' in kwargs:
            status, response = self.get(path=kwargs['path'])
            
            if hasattr(response, 'status_code') is True and isinstance(response.status_code, int) is True and response.status_code == 200:
                
                if hasattr(response, 'headers') is True and 'Content-Type' in response.headers:
                    
                    content_type = response.headers['Content-Type'].lower().split('; ')[0]
                    
                    if content_type == 'application/rss+xml' or 'text/xml':
                        status = True, response.text
                    
                    else:
                        status = False, """Request payload isn't XML..."""
                
                else:
                    status = False, """Content-Type isn't available..."""
            
            else:
                status = False, """Response code isn't HTTP OK 200..."""
        
        else:
            status = False, """Path value isn't available..."""
        
        return status
    
    # --------------------------------------------------------------------------
    
    def get(self, *args, **kwargs):
        
        if 'path' in kwargs:
            try:
                status = True, requests.get(kwargs['path'], timeout=10)
            
            except:
                status = False, """Request failed..."""
        
        else:
            status = False, """Path value isn't available..."""
        
        return status
    
    # --------------------------------------------------------------------------
    
    def notification(self, *args, **kwargs):
        
        if 'title' in kwargs and 'message' in kwargs:
            notify2.init('Podcatcher.py')
            
            # A number of stock 
            notify = notify2.Notification(kwargs['title'], kwargs['message'], "computer")
            
            status = notify.show(), """Message displayed..."""
        
        else:
            status = False, """Error..."""
        
        return status
    
    # --------------------------------------------------------------------------
    
    def path(self, *args, **kwargs):
        
        if 'path' in kwargs:
            
            if os.path.exists(kwargs['path']) is True and os.path.isdir(kwargs['path']) is True:
                status = True, """Directory exists..."""
            
            elif os.path.exists(kwargs['path']) is True and os.path.isdir(kwargs['path']) is False:
                status = False, """Path exists, and isn't directory..."""
            
            else:
                os.makedirs(kwargs['path'])
                status = True, """Creating directory..."""
        
        else:
            status = False, """Error..."""
        
        return status
    
    # --------------------------------------------------------------------------
    
    def podcast(self, *args, **kwargs):
        
        if 'path' in kwargs and 'podcast' in kwargs:
            
            parsed = urlparse.urlparse(kwargs['podcast'])
            
            path_podcast = '%s/%s' % (kwargs['path'], parsed.path.split('/')[-1])
            
            if os.path.exists(kwargs['path']) is True and os.path.exists(path_podcast) is False:
                
                status, response = self.get(path=kwargs['podcast'])
                
                if status is True:
                    handle = codecs.open(path_podcast, 'wb')
                    
                    handle.write(response.content)
                    
                    handle.close()
                    
                    status = True, """Downloaded... %s""" % (kwargs['podcast'])
                
                else:
                    status = status, response
            
            else:
                status = False, """Skip... %s""" % (kwargs['podcast'])
        
        else:
            status = False, """Error..."""
        
        return status

# ------------------------------------------------------------------------------

def main():
    
    podcatcher = Podcatcher()
    
    status, config = podcatcher.config(path='config.json')
    
    if status is not False and 'sources' in config:
        
        for source in config['sources']:
            
            status, message = podcatcher.path(path=source['path'])
            
            if status is True:
                
                status, response = podcatcher.feed(path=source['feed'])
                
                if status is True:
                    
                    rss = feedparser.parse(response)
                    
                    for item in rss.entries:
                        
                        status, message = podcatcher.podcast(path=source['path'], podcast=item.link)
                        
                        if status is True:
                            
                            status, message = podcatcher.notification(title='Podcatcher.py', message=message)

# ------------------------------------------------------------------------------

if __name__ == '__main__':
    main()