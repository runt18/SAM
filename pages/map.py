import common
import dbaccess


class Map:
    pageTitle = "Map"

    # handle HTTP GET requests here.  Name gets value from routing rules above.
    def GET(self):
        protocols = dbaccess.get_protocol_list()

        return str(common.render._head(self.pageTitle,
                                       stylesheets=['/static/css/map.css',
                                                    '/static/css/timerange.css',
                                                    '/static/nouislider/nouislider.css',
                                                    '/static/nouislider/nouislider.pips.css'],
                                       scripts=['/static/js/map.js',
                                                '/static/js/map_node.js',
                                                '/static/js/map_links.js',
                                                '/static/js/map_data.js',
                                                '/static/js/map_selection.js',
                                                '/static/js/map_ports.js',
                                                '/static/js/map_render.js',
                                                '/static/js/map_events.js',
                                                '/static/js/timerange.js',
												'/static/js/liveUpdate.js',
                                                '/static/nouislider/nouislider.min.js'])) \
               + str(common.render._header(common.navbar, self.pageTitle)) \
               + str(common.render.map(protocols)) \
               + str(common.render._tail())
