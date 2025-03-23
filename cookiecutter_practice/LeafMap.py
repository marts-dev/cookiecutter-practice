import ipyleaflet
import logging
import geopandas as gpd


class Map(ipyleaflet.Map):
    __layer_control = None
    __layers = {}

    def __init__(self, center=(20, 0), zoom=2, height="600px", **kwargs):
        """
        Create a LeafMap Map instance.

        Parameters
        ----------
        **center** (tuple): The center of the map (latitude, longitude)

        **zoom** (int): The initial zoom level of the map

        **height** (str): The height of the map

        **kwargs** (dict): Additional keyword arguments

        """
        super().__init__(center=center, zoom=zoom, scroll_wheel_zoom=True, **kwargs)
        self.layout.height = height

    def add_basemap(self, basemap="OpenTopoMap"):
        """
        Add a basemap/layer to the map.

        Parameters
        ----------
        **basemap** (str, default="OpenTopoMap"): The name of the basemap/layer to add. Can be one of the following: 'OpenStreetMap.Mapnik', 'OpenStreetMap.BlackAndWhite', 'OpenStreetMap.DE', 'OpenStreetMap.France', 'OpenStreetMap.HOT', 'OpenStreetMap.Mapnik', 'OpenStreetMap.CH', 'OpenStreetMap.BZH', 'OpenStreetMap.Land', 'OpenStreetMap.HYB', 'OpenStreetMap.OSM

        Returns
        ------
        None
        """
        try:
            url = eval(f"ipyleaflet.basemaps.{basemap}").build_url()
            layer = ipyleaflet.TileLayer(name=basemap, url=url)
            self.__layers[basemap] = layer
            self.add(item=layer)
        except AttributeError:
            logging.warning(f"Basemap {basemap} not found. Using OpenTopoMap instead.")
            self.add(ipyleaflet.basemaps.OpenTopoMap)

    def remove_basemap(self, basemap):
        """
        Remove a basemap/layer from the map.

        Parameters
        ----------
        **basemap** (str): The name of the basemap/layer to remove. Can be one of the following: 'OpenStreetMap.Mapnik', 'OpenStreetMap.BlackAndWhite', 'OpenStreetMap.DE', 'OpenStreetMap.France', 'OpenStreetMap.HOT', 'OpenStreetMap.Mapnik', 'OpenStreetMap.CH', 'OpenStreetMap.BZH', 'OpenStreetMap.Land', 'OpenStreetMap.HYB', 'OpenStreetMap.OSM

        Returns
        ------
        None
        """
        try:
            if basemap in self.__layers:
                self.remove(self.__layers[basemap])
                self.__layers.pop(basemap)
            else:
                logging.warning(f"Basemap {basemap} not found.")
        except AttributeError:
            logging.warning(f"There was an error removing the basemap {basemap}.")

    def add_layer_control(self, position="topright"):
        """
        Add a layer control to the map.

        Parameters
        ----------
        **position** (str, default="topright"): The position of the control (one of the map corners), can be 'topleft', 'topright', 'bottomleft' or 'bottomright'

        Returns
        ------
        None
        """
        if position not in ["topleft", "topright", "bottomleft", "bottomright"]:
            logging.warning(f"Position {position} not valid. Using topright instead.")
            self.__layer_control = ipyleaflet.LayersControl(position="topright")
            self.add(self.__layer_control)
        else:
            self.__layer_control = ipyleaflet.LayersControl(position=position)
            self.add(self.__layer_control)

    def remove_layer_control(self):
        """
        Remove the layer control from the map.

        Parameters
        ----------
        None

        Returns
        ------
        None
        """
        try:
            self.remove(self.__layer_control)
            del self.__layer_control
        except AttributeError:
            logging.warning(f"Layer control does not exist")

    def add_vector(self, name, url=None, geo_data=None, **kwargs):
        """
        Add a vector layer to the map.

        Parameters
        ----------
        **name** (str): The name of the vector layer

        **url** (str, path object or file-like object): Either the absolute or relative path to the file or URL to be opened, or any object with a read() method (such as an open file or StringIO)

        **geo_data** (geopandas.GeoDataFrame): A GeoDataFrame containing the vector data

        **style** (dict): A dictionary of Leaflet Path options

        **hover_style** (dict): A dictionary of Leaflet Path options

        **point_style** (dict): A dictionary of Leaflet Path options

        Returns
        ------
        None

        Examples
        --------
        ```python
        m = LeafMap.Map()
        m.add_vector(name='countries', url='https://ipyleaflet.readthedocs.io/en/latest/_downloads/countries.geo.json', style={'color': 'black', 'fillColor': '#3366cc', 'opacity':0.05, 'weight':1.9, 'dashArray':'2', 'fillOpacity':0.6}, hover_style={'fillColor': 'red' }, point_style={'radius': 5, 'color': 'red', 'fillOpacity': 0.8, 'fillColor': 'blue', 'weight': 3, 'type':'circle'})
        ```
        """

        if url is None and geo_data is None:
            logging.warning(f"Please provide either a URL or a GeoDataFrame.")
            return
        if url is not None and geo_data is not None:
            logging.warning(f"Please provide only one of URL or GeoDataFrame.")
            return

        if url is not None:
            try:
                gdf = gpd.read_file(url)
                geo_data = ipyleaflet.GeoData(geo_dataframe=gdf, name=name, **kwargs)
                self.__layers[name] = geo_data
                self.add(geo_data)
                return
            except Exception:
                logging.warning(f"There was an error adding the vector layer.")
        if geo_data is not None:
            try:
                geo_data = ipyleaflet.GeoData(
                    geo_dataframe=geo_data, name=name, **kwargs
                )
                self.__layers[name] = geo_data
                self.add(geo_data)
                return
            except Exception:
                logging.warning(f"There was an error adding the vector layer.")
