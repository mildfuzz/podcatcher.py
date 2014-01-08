#!/usr/bin/python
# -*- coding: UTF-8 -*-

import codecs
import datetime
import feedparser
import json
# import notify2
import os
import requests
import urlparse

# ------------------------------------------------------------------------------

class Podcatcher(object):
    
    def __init__(self, *args, **kwargs):
        pass
    
    # --------------------------------------------------------------------------
    
    def json(self, *args, **kwargs):
        
        if 'path' in kwargs and 'data' in kwargs:
            if os.path.exists(kwargs['path']) is True and os.path.isfile(kwargs['path']) is True:
                handle = codecs.open(kwargs['path'], 'wb', 'utf-8')
                
                payload = True, json.dump(kwargs['data'], handle, indent=2), {'datetime': self.now(), 'action': """Write, %s""" % (kwargs['path'])}
                
                handle.close()
            
            else:
                payload = False, None, {'datetime': self.now(), 'error': """There is an error, could not write file..."""}
        
        elif 'path' in kwargs and 'data' not in kwargs:
            if os.path.exists(kwargs['path']) is True and os.path.isfile(kwargs['path']) is True:
                handle = codecs.open(kwargs['path'], 'rb', 'utf-8')
                
                payload = True, json.load(handle), {'datetime': self.now(), 'action': """Read, %s""" % (kwargs['path'])}
                
                handle.close()
            
            else:
                payload = False, None, {'datetime': self.now(), 'error': """There is an error in the given path..."""}
        
        else:
            payload = False, None, {'datetime': self.now(), 'error': """Path value isn't available..."""}
        
        return payload
    
    # --------------------------------------------------------------------------
    
    def get(self, *args, **kwargs):
        
        if 'path' in kwargs:
            try:
                payload = True, requests.get(kwargs['path'], timeout=10), {'datetime': self.now(), 'action': """Requested, %s""" % (kwargs['path'])}
            
            except:
                payload = False, None, {'datetime': self.now(), 'error': """Request failed, %s""" % (kwargs['path'])}
        
        else:
            payload = False, None, {'datetime': self.now(), 'error': """Path value isn't available, %s""" % (kwargs['path'])}
        
        return payload
    
    # --------------------------------------------------------------------------
    
    def now(self, *args, **kwargs):
        
        return unicode(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # --------------------------------------------------------------------------
    
    # def notification(self, *args, **kwargs):
        
    #     if 'title' in kwargs and 'message' in kwargs:
    #         notify2.init('Podcatcher.py')
            
    #         notify = notify2.Notification(kwargs['title'], kwargs['message'], "computer")
            
    #         status = notify.show(), """Message displayed..."""
        
    #     else:
    #         status = False, """Error..."""
        
    #     return status
    
    # --------------------------------------------------------------------------
    
    def path(self, *args, **kwargs):
        
        if 'path' in kwargs:
            
            if os.path.exists(kwargs['path']) is True and os.path.isdir(kwargs['path']) is True:
                payload = True, None, {'datetime': self.now(), 'action': """Directory exists, %s""" % (kwargs['path'])}
            
            elif os.path.exists(kwargs['path']) is True and os.path.isdir(kwargs['path']) is False:
                payload = False, None, {'datetime': self.now(), 'error': """Path exists, and isn't directory, %s""" % (kwargs['path'])}
            
            else:
                os.makedirs(kwargs['path'])
                payload = True, None, {'datetime': self.now(), 'action': """Creating directory, %s""" % (kwargs['path'])}
        
        else:
            payload = False, None, {'datetime': self.now(), 'action': """Error, %s""" % (kwargs['path'])}
        
        return payload
    
    # --------------------------------------------------------------------------
    
    def podcast(self, *args, **kwargs):
        
        if 'path' in kwargs and 'podcast' in kwargs:
            
            parsed = urlparse.urlparse(kwargs['podcast'])
            
            path_podcast = '%s/%s' % (kwargs['path'], parsed.path.split('/')[-1])
            
            if os.path.exists(kwargs['path']) is True and os.path.exists(path_podcast) is False:
                
                status, response, metrics = self.get(path=kwargs['podcast'])
                
                if status is True:
                    handle = codecs.open(path_podcast, 'wb')
                    
                    handle.write(response.content)
                    
                    handle.close()
                    
                    payload = True, None, {'datetime': self.now(), 'action': """Downloaded, %s""" % (kwargs['podcast'])}
                
                else:
                    payload = status, None, metrics
            
            else:
                payload = False, None, {'datetime': self.now(), 'action': """Skip, %s""" % (kwargs['podcast'])}
        
        else:
            payload = False, {'datetime': self.now(), 'error': """Error, %s""" % (kwargs['podcast'])}
        
        return payload
    
    # --------------------------------------------------------------------------
    
    def rss(self, *args, **kwargs):
        
        if 'path' in kwargs:
            status, response, metrics = self.get(path=kwargs['path'])
            
            if hasattr(response, 'status_code') is True and isinstance(response.status_code, int) is True and response.status_code == 200:
                
                if hasattr(response, 'headers') is True and 'Content-Type' in response.headers:
                    
                    content_type = response.headers['Content-Type'].lower().split('; ')[0]
                    
                    if content_type == 'application/rss+xml' or 'text/xml':
                        payload = True, response.text, metrics
                    
                    else:
                        payload = False, None, {'datetime': self.now(), 'error': """Request payload isn't XML..."""}
                
                else:
                    payload = False, None, {'datetime': self.now(), 'error': """Content-Type isn't available..."""}
            
            else:
                payload = False, None, {'datetime': self.now(), 'error': """Response code isn't HTTP OK 200..."""}
        
        else:
            payload = False, None, metrics
        
        return payload

# ------------------------------------------------------------------------------

def main():
    
    podcatcher = Podcatcher()
    
    # --------------------------------------------------------------------------
    
    # Load the log.json.
    status, log, metrics = podcatcher.json(path='log.json')
    log['records'].append(metrics)
    
    if status is True:
        
        # Load the config.json.
        status, config, metrics = podcatcher.json(path='config.json')
        log['records'].append(metrics)
        
        # ----------------------------------------------------------------------
        
        if status is not False and 'sources' in config:
            
            # foreach source in config.json.
            for source in config['sources']:
                
                # Test the existence of each path, and create new directories.
                status, message, metrics = podcatcher.path(path=source['path'])
                log['records'].append(metrics)
                
                # If the local path exists, and is directory.
                if status is True:
                    
                    # Request the RSS file.
                    status, response, metrics = podcatcher.rss(path=source['feed'])
                    log['records'].append(metrics)
                    
                    if status is True:
                        
                        # Create an object of the RSS file.
                        rss = feedparser.parse(response)
                        
                        # Loop through each item in the RSS file.
                        for item in rss.entries:
                            
                            if 'href' in item.enclosures[0]:
                                
                                # Request the href of the RSS enclosure.
                                status, message, metrics = podcatcher.podcast(path=source['path'], podcast=item.enclosures[0]['href'])
                                log['records'].append(metrics)
    
    # --------------------------------------------------------------------------
    
    # Log process has finished.
    log['records'].append({'datetime': podcatcher.now(), 'action': 'Finished...'})
    
    # Save log.json to disk.
    status, data, metrics = podcatcher.json(path='log.json', data=log)

# ------------------------------------------------------------------------------

if __name__ == '__main__':
    main()