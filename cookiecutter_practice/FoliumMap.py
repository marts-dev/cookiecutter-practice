import folium
import logging
import geopandas as gpd


class Map(folium.Map):
    def __init__(self, location=(20, 0), zoom_start=2, height="100%", **kwargs):
        """
        Create a FoliumMap Map instance.

        Parameters
        ----------
        center : tuple\n The center of the map (latitude, longitude)
        zoom_start : int\n The initial zoom level of the map
        height : str\n The height of the map
        **kwargs : dict\n Additional keyword arguments
        """
        super().__init__(
            location=location, zoom_start=zoom_start, height=height, **kwargs
        )
        # self.add_control(ipyleaflet.LayersControl())

    def add_basemap(self, basemap="OpenStreetMap"):
        """
        Add a basemap/layer to the map.

        Parameters
        ----------
        basemap : str, default="OpenStreetMap\n The name of the basemap/layer to add. Can be one of the following: 'OpenStreetMap', 'Stamen Terrain', 'Stamen Toner', 'Stamen Watercolor', 'CartoDB positron', 'CartoDB dark_matter', 'OpenTopoMap'.
        You may refer here for other basemaps to use: https://leaflet-extras.github.io/leaflet-providers/preview/

        Returns
        ------
        None
        """
        try:
            folium.TileLayer(basemap).add_to(self)
        except ValueError:
            logging.warning(f"Basemap {basemap} not found. No basemap added.")
            folium.TileLayer("OpenStreetMap").add_to(self)

    def add_layer_control(self, position="topright"):
        """
        Add a layer control to the map.

        Parameters
        ----------
        position : str, default="topright"\n The position of the control (one of the map corners), can be 'topleft', 'topright', 'bottomleft' or 'bottomright' default: 'topright'

        Returns
        ------
        None
        """
        if position not in ["topleft", "topright", "bottomleft", "bottomright"]:
            logging.warning(f"Position {position} not valid. Using topright instead.")
            folium.LayerControl(position="topright").add_to(self)
        else:
            folium.LayerControl(position=position).add_to(self)

    def add_vector(self, name, url=None, geo_data=None, **kwargs):
        """
        Add a vector layer to the map.

        Parameters
        ----------
        name : str\n The name of the vector layer
        url : str, path object or file-like object\n Either the absolute or relative path to the file or URL to be opened, or any object with a read() method (such as an open file or StringIO)
        geo_data : geopandas.GeoDataFrame\n A GeoDataFrame containing the vector data
        style : dict, function\n A dictionary of Folium Path options or a function defining the style of the vector layer
        highlight_style : dict, function\n A dictionary of Folium Path options or a function defining the style of the vector layer when highlighted

        Returns
        ------
        None

        Examples
        --------
        >>> m = FoliumMap.Map()
        >>> m.add_vector(name='countries', url='https://ipyleaflet.readthedocs.io/en/latest/_downloads/countries.geo.json', style={'color': 'black', 'fillColor': '#3366cc', 'opacity':0.05, 'weight':1.9, 'dashArray':'2', 'fillOpacity':0.6}, highlight_style={'fillColor': 'red' })
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
                folium.GeoJson(
                    gdf,
                    name=name,
                    style_function=style_function,
                    highlight_function=highlight_function,
                    **kwargs,
                ).add_to(self)
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
