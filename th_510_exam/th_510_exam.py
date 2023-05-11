"""Main module."""
import spatialcsv
import ipyleaflet
from ipyleaflet import Map, Marker, MarkerCluster
import pandas
import geopandas
import ipywidgets as widgets

class Map(Map):                                                      
                                                                                
    def __init__(self, center=[20, 0], zoom=2, **kwargs) -> None:               
                                                                                
        if "scroll_wheel_zoom" not in kwargs:                                   
            kwargs["scroll_wheel_zoom"] = True                                  
                                                                                
        super().__init__(center=center, zoom=zoom, **kwargs)                    
                                                                                
        if "layers_control" not in kwargs:                                      
            kwargs["layers_control"] = True                                     
                                                                                
        if kwargs["layers_control"]:                                            
            self.add_layers_control()                                           
                                                                                
        if "fullscreen_control" not in kwargs:                                  
            kwargs["fullscreen_control"] = True                                 
                                                                                
        if kwargs["fullscreen_control"]:                                        
            self.add_fullscreen_control()                                       
                                                                                
        if "height" in kwargs:                                                  
            self.layout.height = kwargs["height"]                               
        else:                                                                   
            self.layout.height = "600px"
    
    def add_layers_control(self, position='topright'):                          
        """Adds a layers control to the map.                                    
                                                                                
        Args:                                                                   
            kwargs: Keyword arguments to pass to the layers control.            
        """                                                                     
        layers_control = ipyleaflet.LayersControl(position=position)            
        self.add_control(layers_control)                                        
                                                                                
    def add_fullscreen_control(self, position="topleft"):                       
        """Adds a fullscreen control to the map.                                
                                                                                
        Args:                                                                   
           kwargs: Keyword arguments to pass to the fullscreen control.         
       """                                                                      
        fullscreen_control = ipyleaflet.FullScreenControl(position=position)    
        self.add_control(fullscreen_control) 

    def add_geojson(self, data, name='GeoJSON', **kwargs):                      
        """Adds a GeoJSON layer to the map.                                     
                                                                                
        Args:                                                                   
            data (dict): The GeoJSON data.                                      
        """                                                                     
                                                                                
        if isinstance(data, str):                                               
            import json                                                         
            with open(data, "r") as f:                                          
                data = json.load(f)                                             
                                                                                
        geojson = ipyleaflet.GeoJSON(data=data,name=name, **kwargs)             
        self.add_layer(geojson) 


    def add_shp(self, data, name='Shapefile', **kwargs):                        
        """Adds a Shapefile layer to the map.                                   
                                                                                
        Args:                                                                   
            data (str): The path to the Shapefile.                              
        """                                                                     
        import geopandas as gpd                                                 
        gdf = gpd.read_file(data)                                               
        geojson = gdf.__geo_interface__                                         
        self.add_geojson(geojson, name=name, **kwargs) 

    def points_from_xy(data, x="longitude", y="latitude", z=None, crs=None, **kwargs):
        """Create a GeoPandas GeoDataFrame from a csv or Pandas DataFrame containing x, y, z values.

        Args:
        data (str | pd.DataFrame): A csv or Pandas DataFrame containing x, y, z values.
        x (str, optional): The column name for the x values. Defaults to "longitude".
        y (str, optional): The column name for the y values. Defaults to "latitude".
        z (str, optional): The column name for the z values. Defaults to None.
        crs (str | int, optional): The coordinate reference system for the GeoDataFrame. Defaults to None.

        Returns:
            geopandas.GeoDataFrame: A GeoPandas GeoDataFrame containing x, y, z values.
        """
        import geopandas as gpd
        import pandas as pd
        
        """
        if crs is None:
            crs = "epsg:4326"
        if isinstance(data, pd.DataFrame):
            df = data
        elif isinstance(data, str):
            if not data.startswith("http") and (not os.path.exists(data)):
                raise FileNotFoundError("The specified input csv does not exist.")
            else:
                df = pd.read_csv(data, **kwargs)
        else:
            raise TypeError("The data must be a pandas DataFrame or a csv file path.")
        """
        gdf = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(data[x], data[y]))

        return gdf


    def csv_to_shp(self, data, out_shp, x="longitude", y="latitude"):
        """ Converts a csv to a shapefile.

        Args:
            data (str): Path to the input csv
            out_shp (str): Path to save the shapefile
            x (str): longitude
            y (str): latitude
        """
        gdf = geopandas.GeoDataFrame(pandas.read_csv(data))
        gdf.set_geometry(
            geopandas.points_from_xy(gdf[x], gdf[y]),
            inplace=True, crs='EPSG:4326')
        gdf.to_file(out_shp)
        self.add_shp(out_shp)
        return out_shp



    def choose_file(self):
        box = widgets.Text(
            value='Type a filepath',
            placeholder='Type something',
            description='String:',
            disabled=False
        )
        basemap_ctrl = ipyleaflet.WidgetControl(widget=box, position='bottomright')
        self.add_control(basemap_ctrl)

        def change_box(change):                                             
            if change['new']:                                                   
                self.add_points_from_csv(box.value)                                 
                                                                                
        box.observe(change_box, names='value')


    def add_points_from_csv(self, in_csv, x="longitude", y="latitude", label=None, layer_name="Marker cluster"):
        import geopandas as gpd
        import pandas as pd
        data = pandas.read_csv(in_csv)
        gdf = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(data[x], data[y]))

        #df = self.points_from_xy(in_csv, x, y)
        gdf["x"] = gdf.geometry.x
        gdf["y"] = gdf.geometry.y
        markers = []
        points = list(zip(gdf["y"], gdf["x"]))
        for point in points:
            marker = ipyleaflet.Marker(
                    location=point
                )
            markers.append(marker)
        marker_cluster = ipyleaflet.MarkerCluster(
            markers=markers,
            name=layer_name,
        )
        self.add_layer(marker_cluster)
       
