# Libraries
from obspy import read, read_inventory, read_events
import os
from obspy.core.inventory import Inventory, Network, Station, Channel
from obspy.core.stream import Stream
from obspy.core.event import Catalog, Event, Origin, FocalMechanism, MomentTensor, Tensor
from obspy.geodetics import FlinnEngdahl
from obspy import UTCDateTime
import yaml
import numpy as np


# In house files
from axisem3d_output.core.handlers.element_output import ElementOutput
from .wavefield_db import WavefieldDatabase
from .elements_db import ElementsDatabase


class Model:
    
    def __init__(self, controller):
        self.controller = controller
        self.wavefield_database = None
        self.elements_database = None


    def create_database(self):
        self.wavefield_database = WavefieldDatabase()


    def create_elements_database(self):
        self.elements_database = ElementsDatabase()


    def load_wavefield(self, wavefield_path, cat_path, inv_path, data_type):
        name = wavefield_path.split('/')[-1]
        stream = read(wavefield_path)
        cat = read_events(cat_path)
        inv = read_inventory(inv_path)
        self.wavefield_database.add_to_database(name, stream, cat, 
                                                inv, data_type)


    def load_elements(self, elements_path):
        name = elements_path.split('/')[-1]
        element_object = ElementOutput(elements_path)
        # We need to crate a catalogue on the spot for element outputs
        cat = element_object.catalogue
        self.elements_database.add_to_database(elements_path, name, 
                                               element_object, cat)

    
    def auto_load_wavefield(self, wavefield_path, data_type):
        name = wavefield_path.split('/')[-1]
        stream = read(wavefield_path)
        
        # find dir path
        dir_path = os.path.dirname(wavefield_path)
        # Read events catalogue
        for file in os.listdir(dir_path):
            if file.endswith('cat.xml'):
                cat = read_events(os.path.join(dir_path, file))
                break
        # Read inventory
        for file in os.listdir(dir_path):
            if file.endswith('inv.xml'):
                inv = read_inventory(os.path.join(dir_path, file))
                break

        self.wavefield_database.add_to_database(name, stream, cat, inv, data_type)


    def add_selection(self, name):
        self.wavefield_database.add_to_selected_database(name)


    def add_elements_selection(self, name):
        self.elements_database.add_to_selected_database(name)


    def remove_selection(self, name):
        self.wavefield_database.remove_from_selected_database(name)


    def remove_elements_selection(self, name):
        self.elements_database.remove_from_selected_database(name)


    def remove_wavefield(self, name):
        self.wavefield_database.remove_from_database(name)


    def get_times_and_streams(self):
        times = []
        streams = []
        for element in self.wavefield_database.selected_database:
            inv_selection = Inventory()
            stream = self.wavefield_database.database[element]['stream']
            cat = self.wavefield_database.database[element]['cat']
            inv = self.wavefield_database.database[element]['inv']
            data_type = self.wavefield_database.database[element]['type']

            # Geographical choice
            if len(self.controller.view.min_lat.get()) == 0:
                minlatitude = [-90]
            else:
                minlatitude = [float(elem) for elem in self.controller.view.min_lat.get().split(',')]
            if len(self.controller.view.max_lat.get()) == 0:
                maxlatitude = [90]
            else:
                maxlatitude = [float(elem) for elem in self.controller.view.max_lat.get().split(',')]
            if len(self.controller.view.min_lon.get()) == 0:
                minlongitude = [-180]
            else:
                minlongitude = [float(elem) for elem in self.controller.view.min_lon.get().split(',')]
            if len(self.controller.view.max_lon.get()) == 0:
                maxlongitude = [180]
            else:
                maxlongitude = [float(elem) for elem in self.controller.view.max_lon.get().split(',')]

            for index in range(len(minlatitude)):
                inv_selection.__iadd__(inv.select(minlatitude=minlatitude[index],
                                    maxlatitude=maxlatitude[index],
                                    minlongitude=minlongitude[index],
                                    maxlongitude=maxlongitude[index]))
            stream_geo_selection = stream.select(inventory=inv_selection)
            
            stream_net_selection = Stream()
            # Net choice
            if len(self.controller.view.networks.get()) == 0:
                stream_net_selection = stream_geo_selection.copy()
            else:
                network_choice = self.controller.view.networks.get().split(',')
                for index in range(len(network_choice)):
                    stream_net_selection.__iadd__(stream_geo_selection.select(network=network_choice[index]))

            stream_sta_selection = Stream()
            # Sta choice
            if len(self.controller.view.stations.get()) == 0:
                stream_sta_selection = stream_net_selection.copy()
            else:
                station_choice = self.controller.view.stations.get().split(',')
                for index in range(len(station_choice)):
                    stream_sta_selection.__iadd__(stream_net_selection.select(station=station_choice[index]))

            stream_loc_selection = Stream()
            # Loc choice
            if len(self.controller.view.locations.get()) == 0:
                stream_loc_selection = stream_sta_selection.copy()
            else:
                location_choice = self.controller.view.locations.get().split(',')
                for index in range(len(location_choice)):
                    stream_loc_selection.__iadd__(stream_sta_selection.select(location=location_choice[index]))

            stream_chn_selection = Stream()
            # Chn choice
            if len(self.controller.view.channels.get()) == 0:
                stream_chn_selection = stream_loc_selection.copy()
            else:
                channel_choice = self.controller.view.channels.get().split(',')
                for index in range(len(channel_choice)):
                    stream_chn_selection.__iadd__(stream_loc_selection.select(channel=channel_choice[index]))

            # finally put back in the main stream the selected traces
            stream = stream_chn_selection

            # Bandpass   
            if len(self.controller.view.freq_min.get()) == 0:
                freq_min = None
            else:
                freq_min = float(self.controller.view.freq_min.get())
            if len(self.controller.view.freq_max.get()) == 0:
                freq_max = None
            else:
                freq_max = float(self.controller.view.freq_max.get())
            if freq_min is not None and freq_max is not None:
                stream.filter('bandpass', freqmin=freq_min, freqmax=freq_max)
            elif freq_min is None and freq_max is not None: 
                stream.filter('lowpass', freq=freq_max)
            elif freq_min is not None and freq_max is None:
                stream.filter('highpass', freq=freq_min)
            
            times.append(self._get_time(data_type, stream, cat))
            streams.append(stream)

        return [times, streams]


    def get_elements_times_and_streams(self, depths, latitudes, longitudes):
        # Get times and streams
        times = []
        streams = []

        for element in self.elements_database.selected_database:
            element_object = self.elements_database.database[element]['element_object']
            channel_time = element_object.data_time

            traces = Stream()
            inv = Inventory(
                networks=[],
                source="Ad-hoc inventory for elements output")

            time = []

            for i, depth in enumerate(depths):
                # Create point in geographical coords to be fed to element_output.py
                latitude = float(latitudes[i])
                longitude = float(longitudes[i])
                radius = 6371000 - depth * 1e3
                # Get wave data 
                wave_data = element_object.stream(np.array([radius, latitude, longitude]))
                for trace in wave_data:
                    traces.append(trace)
                
                ################
                # FORM INVENTORY
                ################
                
                net_code = wave_data[0].id.split('.')[0]
                sta_code = wave_data[0].id.split('.')[1]

                # Get coordinates of the stations channels (RTZ, etc)
                channel_type = element_object.coordinate_frame

                # Create network if not already existent
                net_exists = False
                for network in inv:
                    if network.code == net_code:
                        net_exists = True
                        net = network
                if net_exists == False:
                    net=Network(
                    code=net_code,
                    stations=[])
                    # add new network to inventory
                    inv.networks.append(net)
                    
                # Create station (should be unique!)
                sta = Station(
                code=sta_code,
                latitude=latitude,
                longitude=longitude,
                elevation=-depth)
                net.stations.append(sta)
                
                # Create the channels
                for channel in channel_type:
                    cha = Channel(
                    code=channel,
                    location_code="",
                    latitude=latitude,
                    longitude=longitude,
                    elevation=-depth,
                    depth=depth,
                    azimuth=None,
                    dip=None,
                    sample_rate=None)
                    sta.channels.append(cha)

                # This is a bit bs, but I have to give each channel
                # its own time (hence the triple append) otherwise
                # the plotter will freak out (this is because the plotter
                # was originally made for the stations output where the time 
                # is given for each channel)
                for i in range(len(wave_data)):
                    time.append(channel_time)

            # Chn choice
            stream_chn_selection = Stream()
            if len(self.controller.view.elements_channel.get()) == 0:
                stream_chn_selection = traces.copy()
            else:
                channel_choice = self.controller.view.elements_channel.get().split(',')
                for index in range(len(channel_choice)):
                    stream_chn_selection.__iadd__(traces.select(channel=channel_choice[index]))
                
            streams.append(stream_chn_selection)
            times.append(time)
            
        return times, streams, inv

                
    def _get_time(self, data_type, stream, cat):
        # Get the times for the selected traces
        # Center time axis on event origin time
        # Axisem3D gives centred data
        # Instaseis always starts at event time (0)
        # The time axis of the real data starts at 0 even
        # if we downloaded data starting x seconds before the
        # event time, so we must shift the time
        if (data_type == 'real') or \
            (data_type == 'simulation'):
            evt_time = cat[0].origins[0].time
            time = []
            for trace in stream:
                start_time = trace.stats.starttime 
                time_shift = start_time - evt_time
                time.append(trace.times() + time_shift)
        elif data_type == 'instaseis': 
            time_shift = 0 
            time = []
            for trace in stream:
                time.append(trace.times() + time_shift)

        return time                    
        
    def get_selected_inv(self):
        # Geographical choice
        if len(self.controller.view.min_lat.get()) == 0:
            minlatitude = [-90]
        else:
            minlatitude = [float(elem) for elem in self.controller.view.min_lat.get().split(',')]
        if len(self.controller.view.max_lat.get()) == 0:
            maxlatitude = [90]
        else:
            maxlatitude = [float(elem) for elem in self.controller.view.max_lat.get().split(',')]
        if len(self.controller.view.min_lon.get()) == 0:
            minlongitude = [-180]
        else:
            minlongitude = [float(elem) for elem in self.controller.view.min_lon.get().split(',')]
        if len(self.controller.view.max_lon.get()) == 0:
            maxlongitude = [180]
        else:
            maxlongitude = [float(elem) for elem in self.controller.view.max_lon.get().split(',')]

        # Get the inventory of one of the selections(they should all have the same stations)
        element = self.wavefield_database.selected_database[0]
        inv = self.wavefield_database.database[element]['inv']
        inv_geo_selection = Inventory()
        for index in range(len(minlatitude)):
            inv_geo_selection.__iadd__(inv.select(minlatitude=minlatitude[index],
                                maxlatitude=maxlatitude[index],
                                minlongitude=minlongitude[index],
                                maxlongitude=maxlongitude[index]))
        inv_selection = Inventory()

        # Station choice
        if len(self.controller.view.stations.get()) == 0:
            inv_selection = inv_geo_selection.copy()
        else:
            station_choice = self.controller.view.stations.get().split(',')
            for sta in station_choice:
                inv_selection.__iadd__(inv_geo_selection.select(station=sta))
        
        return inv_selection