import folium
import logging
import geopandas as gpd


class Map(folium.Map):
    def __init__(self, center=(20, 0), zoom=2, height="100%", **kwargs):
        """Create a FoliumMap Map instance.

        Params:
            center (tuple): The center of the map (latitude, longitude)
            zoom (int): The initial zoom level of the map
            height (str): The height of the map
            **kwargs (dict): Additional keyword arguments

        """
        super().__init__(location=center, zoom_start=zoom, height=height, **kwargs)
        # self.add_control(ipyleaflet.LayersControl())

    def add_basemap(self, basemap="OpenStreetMap"):
        """Add a basemap/layer to the map.

        Params:
            basemap (str): The name of the basemap/layer to add. Can be one of the following: 'OpenStreetMap', 'Stamen Terrain', 'Stamen Toner', 'Stamen Watercolor', 'CartoDB positron', 'CartoDB dark_matter', 'OpenTopoMap'

        You may refer here for other basemaps to use: [Leaflet Providers](https://leaflet-extras.github.io/leaflet-providers/preview/)

        """
        try:
            folium.TileLayer(basemap).add_to(self)
        except ValueError:
            logging.warning(f"Basemap {basemap} not found. No basemap added.")
            folium.TileLayer("OpenStreetMap").add_to(self)

    def add_layer_control(self, position="topright"):
        """Add a layer control to the map.

        Params:
            position (str): The position of the control (one of the map corners), can be 'topleft', 'topright', 'bottomleft' or 'bottomright'

        """
        if position not in ["topleft", "topright", "bottomleft", "bottomright"]:
            logging.warning(f"Position {position} not valid. Using topright instead.")
            folium.LayerControl(position="topright").add_to(self)
        else:
            folium.LayerControl(position=position).add_to(self)

    def add_vector(self, name, url=None, geo_data=None, **kwargs):
        """Add a vector layer to the map.

        Params:
            name (str): The name of the vector layer
            url (str, path object or file-like object): Either the absolute or relative path to the file or URL to be opened, or any object with a read() method (such as an open file or StringIO)
            geo_data (geopandas.GeoDataFrame): A GeoDataFrame containing the vector data
            style (dict, function): A dictionary of Folium Path options or a function defining the style of the vector layer
            highlight_style (dict, function): A dictionary of Folium Path options or a function defining the style of the vector layer when highlighted

        Examples:
            ```python
            m = FoliumMap.Map()
            m.add_vector(name='countries', url='https://ipyleaflet.readthedocs.io/en/latest/_downloads/countries.geo.json', style={'color': 'black', 'fillColor': '#3366cc', 'opacity':0.05, 'weight':1.9, 'dashArray':'2', 'fillOpacity':0.6}, highlight_style={'fillColor': 'red' })
            ```
        """

        def style_function(feature):
            default = style
            return default

        def highlight_function(feature):
            default = highlight_style
            return default

        if "style" in kwargs:
            style = kwargs["style"]
            kwargs.pop("style")
            if callable(style):
                style_function = style
        else:
            style = {
                "color": "black",
                "fillColor": "green",
                "opacity": 0.05,
                "weight": 1.9,
                "dashArray": "2",
                "fillOpacity": 0.6,
            }

        if "highlight_style" in kwargs:
            highlight_style = kwargs["highlight_style"]
            kwargs.pop("highlight_style")
            if callable(highlight_style):
                highlight_function = highlight_style
        else:
            highlight_style = {"fillColor": "red"}

        if url is None and geo_data is None:
            logging.warning(f"Please provide either a URL or a GeoDataFrame.")
            return
        if url is not None and geo_data is not None:
            logging.warning(f"Please provide only one of URL or GeoDataFrame.")
            return

        if url is not None:
            try:
                gdf = gpd.read_file(url)
                gj = folium.GeoJson(
                    gdf,
                    name=name,
                    style_function=style_function,
                    highlight_function=highlight_function,
                    **kwargs,
                )

                fg = folium.FeatureGroup(name=name, show=True)
                fg.add_to(self)
                gj.add_to(fg)
                return
            except Exception:
                logging.warning(f"There was an error adding the vector layer.")
        if geo_data is not None:
            try:
                folium.GeoJson(
                    geo_data,
                    name=name,
                    style_function=style_function,
                    highlight_function=highlight_function,
                    **kwargs,
                ).add_to(self)
                return
            except Exception:
                logging.warning(f"There was an error adding the vector layer.")

    def add_raster(self, url, name, colormap=None, opacity=1.0, **kwargs):
        """Add a raster layer to the map.

        Params:
            url (str): The URL of the raster layer
            name (str): The name of the raster layer
            colormap (str): The colormap to use for the raster layer
            opacity (float): The opacity of the raster layer
            **kwargs: Additional keyword arguments

        Examples:
            ```python
            m = FoliumMap.Map()
            m.add_raster(url='https://example.com/raster.tif', name='raster', colormap='viridis', opacity=0.5)
            ```
        """
        from localtileserver import TileClient, get_folium_tile_layer

        if url is None:
            logging.warning(f"Please provide a URL.")
            return

        try:
            client = TileClient(url)
            raster_layer = get_folium_tile_layer(
                client, name=name, colormap=colormap, opacity=opacity, **kwargs
            )
            fg = folium.FeatureGroup(name=name, show=True)
            fg.add_to(self)
            raster_layer.add_to(fg)
            north, south, west, east = client.bounds()
            self.fit_bounds(((south, west), (north, east)))
            return
        except Exception as e:
            logging.warning(f"There was an error adding the raster layer: {e}")

    def add_image(self, url, bounds=None, opacity=1.0, **kwargs):
        """Add an image layer to the map.

        Params:
            url (str): The URL of the image layer
            bounds (tuple): The bounds of the image layer ((south, west), (north, east))
            opacity (float): The opacity of the image layer
            **kwargs: Additional keyword arguments

        Examples:
            ```python
            m = FoliumMap.Map()
            m.add_image(url='https://example.com/image.png', bounds=((40, -100), (30, -90)), opacity=0.5)
            ```
        """
        if url is None:
            logging.warning(f"Please provide a URL.")
            return
        if bounds is None:
            bounds = ((-90, -180), (90, 180))

        try:
            folium.raster_layers.ImageOverlay(
                image=url, bounds=bounds, opacity=opacity, **kwargs
            ).add_to(self)
            self.fit_bounds(bounds)
        except Exception as e:
            logging.warning(f"There was an error adding the image layer: {e}")

    def add_video(self, url, bounds=None, opacity=1.0, **kwargs):
        """Add a video layer to the map.

        Params:
            url (str): The URL of the video layer
            bounds (tuple): The bounds of the video layer ((south, west), (north, east))
            opacity (float): The opacity of the video layer
            **kwargs: Additional keyword arguments

        Examples:
            ```python
            m = FoliumMap.Map()
            m.add_video(url='https://example.com/video.mp4', bounds=((40, -100), (30, -90)), opacity=0.5)
            ```
        """
        if url is None:
            logging.warning(f"Please provide a URL.")
            return
        if bounds is None:
            bounds = ((-90, -180), (90, 180))

        try:
            folium.raster_layers.VideoOverlay(
                video_url=url, bounds=bounds, opacity=opacity, **kwargs
            ).add_to(self)
            self.fit_bounds(bounds)
        except Exception as e:
            logging.warning(f"There was an error adding the video layer: {e}")

    def add_wms_layer(
        self, url, layers, name, format="image/png", transparent=True, **kwargs
    ):
        """Add a WMS layer to the map.

        Params:
            url (str): The URL of the WMS layer
            layers (str): The layers of the WMS layer
            name (str): The name of the WMS layer
            format (str): The format of the WMS layer
            transparent (bool): Whether the WMS layer is transparent
            **kwargs: Additional keyword arguments

        Examples:
            ```python
            m = FoliumMap.Map()
            m.add_wms_layer(url="https://ows.terrestris.de/osm/service",
                layers="OSM-WMS",
                name="WMS Layer",
                format="image/png",
                transparent=True,
            )
            ```
        """
        if url is None:
            logging.warning(f"Please provide a URL.")
            return

        try:
            folium.WmsTileLayer(
                url=url,
                layers=layers,
                name=name,
                fmt=format,
                transparent=transparent,
                **kwargs,
            ).add_to(self)
        except Exception as e:
            logging.warning(f"There was an error adding the WMS layer: {e}")
