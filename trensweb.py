#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

"""

"""

import os
import trens
import cherrypy
from datetime import datetime
import time
import threading
from mako.template import Template

lastdata = {}

def update(src, dst):
    if src not in lastdata:
        lastdata[src] = {}
    newdata = {}
    lastdata[src][dst] = newdata
    date = datetime.today()
    newdata["date"] = date
    trains = trens.get_trains(date, src, dst)
    newdata["trains"] = sorted(list(trains))

update("SC", "PC")
update("SC", "UN")

def updater():
    while True:
        time.sleep(60*5)
        update()

#t = threading.Thread(target=updater)
#t.start()

stations_template = """<!doctype html>
<meta charset="UTF-8">
<title>Horaris FGC</title>
<link rel="stylesheet" href="/jaume/css/trens.css">
<h1>Tria una estació</h1>
<ul class="llista-estacions">
% for station in stations:
<li><a href="${base}/${station}">${station}</a>
% endfor
</ul>
"""

template = """<!doctype html><% title = "Trens de " + src + " a " + dst %>
<meta charset="UTF-8">
<title>${title}</title>
<link rel="stylesheet" href="/jaume/css/trens.css">
<h1>${title}</h1>
Llista actualitzada el ${updated.strftime("%d/%m/%Y a les %H:%M:%S")}
<ul class="llista-trens">
% for train in trains:
<li>
  <span class="linia ${train.linia}">${train.linia}</span>
  <time>${train.hora_sortida()}</time> -
  <time>${train.hora_arribada()}</time>
% endfor
</ul>
"""

class WebSite:
    exposed = True
    def GET(self, src=None, dst=None):
        if src is None:
            return Template(stations_template).render(
                base="",
                stations=sorted(lastdata.keys()))
        if src not in lastdata:
            return "404 here"
        if dst is None:
            return Template(stations_template).render(
                base="/"+src,
                stations=sorted(lastdata[src].keys()))
        if dst not in lastdata[src]:
            return "404 here"
        data = lastdata[src][dst]
        date = data["date"]
        trains = data["trains"]
        return Template(template).render(
            src=src,
            dst=dst,
            trains=trains,
            updated=date)
    #@cherrypy.expose
    #def index(self):
    #    date = lastdata["date"]
    #    trains = lastdata["trains"]
    #    return Template(template).render(
    #        src=src,
    #        dst=dst,
    #        trains=lastdata["trains"],
    #        updated=lastdata["date"])
        #return "{}<br>{}".format(date, "<br>".join(str(t) for t in trains))

if __name__ == "__main__":
    cherrypy.config.update({
        'server.socket_port': 8092,
        #'tools.proxy.on': True,
        #'tools.proxy.base': 'http://www.example.com',
    })
    conf = {
        '/' : {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
        },
        '/jaume/css/trens.css' : {
            'tools.staticfile.on': True,
            'tools.staticfile.filename': os.path.abspath("./trens.css")
        },
        '/favicon.ico':
        {
            'tools.staticfile.on': True,
            'tools.staticfile.filename': os.path.abspath("./icon.ico")
        }
    }
    #cherrypy.quickstart(WebSite(), "/", conf)
    cherrypy.tree.mount(WebSite(), '/', conf)
    cherrypy.engine.start()
    cherrypy.engine.block()