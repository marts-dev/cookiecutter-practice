"""Main module."""

import ipyleaflet


class LeafMap(ipyleaflet.Map):
    def __init__(self, *args, **kwargs):
        super(LeafMap, self).__init__(*args, **kwargs)
        self.add_control(ipyleaflet.LayersControl())
