import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
import numpy as np
from obspy.taup import TauPyModel
from obspy.taup.utils import parse_phase_list
from obspy.taup.seismic_phase import SeismicPhase
from matplotlib.pyplot import get_cmap
import obspy 
import tkinter as tk
from mayavi import mlab
import os
os.environ['PROJ_LIB'] = '/home/users/scro4564/anaconda3/envs/visualization/share/proj'
from mpl_toolkits.basemap import Basemap

def _find_distance_in_degree(lat0: float, lon0: float, lat1: float, lon1:float) -> float:
    """Finds the distance in degrees between two geographical points

    Args:
        lat0 (float): point one latitude    
        lon0 (float): point one longitude
        lat1 (float): point two latitude
        lon1 (float): point two longitude

    Returns:
        float: distance in degerees
    """    
    return np.rad2deg(np.arccos(np.cos(np.deg2rad(lat0)) * np.cos(np.deg2rad(lat1)) * np.cos(np.deg2rad(lon0 - lon1)) \
                      + np.sin(np.deg2rad(lat0)) * np.sin(np.deg2rad(lat1))))


def dummy_Plot(time: np.ndarray, data:np.ndarray) -> plt.figure:
    """Creates a dummy plot used for initiating frames

    Args:
        time (np.ndarray): time
        data (np.ndarray): data

    Returns:
        plt.figure: figure
    """    
    fig, axs = plt.subplots(2)
    axs[0].plot(time[0], data[0])
    axs[1].plot(time[1], data[1])

    return fig


def Plot(times: np.array, streams: obspy.Stream, inv_selection: obspy.Inventory, 
         cat: obspy.Catalog, model: obspy.taup.tau.TauPyModel, phase_list: list, PLOT_DIFFERENCE: bool = False, xlims=None) -> plt.figure:
    """Builds figure for plotting wave data time series

    Args:
        times (np.array): time array
        streams (obspy.Stream): stream containing traces of data that will be plotted
        inv (obspy.Inventory): inventory of stations/channels that will be plotted
        cat (obspy.Catalog): catalogue of events
        model (obspy.taup.tau.TauPyModel): earth reference model from taup
        phase_list (list): list of strings of phases eg PcP,PP,...
        PLOT_DIFFERENCE (bool): set to true if you want to plot the difference between two datasets
                                instead of plotting them on top of eachother
        xlims (list, optional): list with min and max time limits for plotting. Defaults to None.

    Returns:
        plt.figure: figure
    """

    ########################################
    # ORDER STATIONS BY DISTANCE FROM ORIGIN
    ########################################

    # Initialize lists that contain the IDs of the stations and the distances
    # between each station and the event
    ids = []
    distances = []
    
    # IMPLEMENT SOMETHING THAT CHECKS IF THE SELECTED DATA HAVE THE SAME SOURCE
    # CAT. IF THEY DON'T THEN THEY SHOULD NOT BE PLOTTED TOGETHER!!!!
    
    # get event location
    try:
        evt_lat = cat[0].origins[0].latitude
        evt_lon = cat[0].origins[0].longitude
        evt_depth = cat[0].origins[0].depth
    except:
        evt_lat = cat.origins[0].latitude
        evt_lon = cat.origins[0].longitude
        evt_depth = cat.origins[0].depth
    
    # Go trace by trace and find the ID and source-receiver distance
    for trace in streams[0]:
        id = str(trace.stats.network) + '.' + str(trace.stats.station) \
                + '.' + str(trace.stats.location) + '.' + str(trace.stats.channel)
        # select the part of the inventory that will be plotted here
        inv_selected = inv_selection.select(network=trace.stats.network, 
                                            station=trace.stats.station, 
                                            channel=str('*' + trace.stats.channel[-1]))
        # find distance between current station and event
        distance_in_degree = _find_distance_in_degree(inv_selected[0][0].latitude, 
                                                        inv_selected[0][0].longitude, 
                                                        evt_lat, evt_lon)
        ids.append(id)
        distances.append(distance_in_degree)
    
    # sort distances and ids in ascending order concomitently
    zipped_lists = zip(distances, ids)
    sorted_pairs = sorted(zipped_lists)
    tuples = zip(*sorted_pairs)
    distances, ids = [ list(tuple) for tuple in  tuples]

    #################################
    # CUSTOMIZE TAUP PICKS APPEARENCE
    #################################

    # Create a colormap for the Taup picks
    cmap = get_cmap('Paired', lut=12)
    COLORS = ['#%02x%02x%02x' % tuple(int(col * 255) for col in cmap(i)[:3])
            for i in range(12)]
    COLORS = COLORS[1:][::2][:-1] + COLORS[::2][:-1]

    # Format the strings in the phase list to be of type "" instead of ''
    # otherwise the taup implementation in obspy will freak out
    phase_list = ["{0}".format(elem) for elem in phase_list]
    model = TauPyModel(model)
    
    # Colors for waveforms 
    plot_colors = ['black', 'red', 'navy', 'limegreen', 'yellow', 'orange', 'magenta']

    ##################
    # FIND MASTER TIME
    ##################

    t_max = max([max(t) for time in times for t in time])    # find earliest time data point
    t_min = min([min(t) for time in times for t in time])        # find latest time data point
    delta_t_min = min([t[1] - t[0] for time in times for t in time])    # find smallest delta t
    master_time = np.arange(t_min, t_max, delta_t_min)
    
    ######
    # PLOT
    ######

    fig_seismographs, ax = plt.subplots(len(streams[0]), sharex=True, figsize=(8,4), dpi=200)
    # go over data sets
    if PLOT_DIFFERENCE is True:
        stream1 = streams[0]
        stream2 = streams[1]
        plot_index = -1
        # if stream has more than one trace we use multiple axes
        if len(stream1) > 1:
            for trace_index, id in enumerate(ids):
                trace1 = stream1.select(id=id)[0]
                trace2 = stream2.select(id=id)[0]
                plot_index += 1
                
                # get distance in degree from source
                distance_in_degree = distances[trace_index]
                
                # Interpolate traces onto the master time
                interp_trace1 = np.interp(master_time, times[0][trace_index], trace1.data)
                interp_trace2 = np.interp(master_time, times[1][trace_index], trace2.data)
                id = str(trace1.stats.network) + '.' + str(trace1.stats.station) + \
                    '.' + str(trace1.stats.location) + '.' + str(trace1.stats.channel)
                
                # plot difference squares
                ax[plot_index].plot(master_time, (interp_trace1 - interp_trace2)**2, lw=0.2, 
                                    color=plot_colors[0], label=id)
                # add text of label
                ax[plot_index].text(.95, .2, 
                                    id + '|' + str(round(distance_in_degree)), 
                                    transform = ax[plot_index].transAxes, 
                                    ha='right', va='top', fontsize=5, color=plot_colors[0])
                ax[plot_index].tick_params(axis='both', which='major', labelsize=5)
                ax[plot_index].tick_params(axis='both', which='minor', labelsize=5)

                # if there are travel times of phases to be plotted
                all_travel_times = {}
                if len(phase_list) != 0:
                        
                        phase_list = sorted(parse_phase_list(phase_list))
                        for i, phase in enumerate(phase_list):
                            c = COLORS[i % len(COLORS)]
                            arrivals = model.get_travel_times(source_depth_in_km=evt_depth * 1e-3,
                                                            distance_in_degree=distance_in_degree,
                                                            phase_list=[phase])
                            if arrivals:
                                arrival_time = [arrivals[k].time for k in range(len(arrivals[:]))]
                                ax[plot_index].scatter(arrival_time, np.zeros(len(arrival_time)), marker='|', 
                                                                c=c, label=phase)
                                all_travel_times[phase] = arrival_time
        else:
            # there is just one trace for each stream
            trace1 = streams[0]
            trace2 = streams[1]
                
            # find distance between current station and event
            distance_in_degree = distances[0]
                
            # Interpolate traces onto the master time
            interp_trace1 = np.interp(master_time, times[0][0], trace1.data)
            interp_trace2 = np.interp(master_time, times[1][0], trace2.data)
            id = str(trace1.stats.network) + '.' + str(trace1.stats.station) + \
                '.' + str(trace1.stats.location) + '.' + str(trace1.stats.channel)
            
            # Plot trace
            ax.plot(master_time, (interp_trace1 - interp_trace2)**2, lw=0.2, color=plot_colors[0], label=id)
            
            # Add label text
            ax.text(.95, .2, 
                    id + '|' + str(round(distance_in_degree)), 
                    transform = ax.transAxes, 
                    ha='right', va='top', fontsize=5, color=plot_colors[0])
            ax.tick_params(axis='both', which='major', labelsize=5)
            ax.tick_params(axis='both', which='minor', labelsize=5)

            # if there are travel times of phases to be plotted
            all_travel_times = {}
            if len(phase_list) != 0:

                    phase_list = sorted(parse_phase_list(phase_list))
                    for i, phase in enumerate(phase_list):
                        c = COLORS[i % len(COLORS)]
                        arrivals = model.get_travel_times(source_depth_in_km=evt_depth * 1e-3,
                                                        distance_in_degree=distance_in_degree,
                                                        phase_list=[phase])
                        if arrivals:
                            arrival_time = [arrivals[k].time for k in range(len(arrivals[:]))]
                            ax.scatter(arrival_time, np.zeros(len(arrival_time)), marker='|', 
                                                            c=c, label=phase)
                            all_travel_times[phase] = arrival_time
    else: 
        for index, stream in enumerate(streams): 
            
            plot_index = -1
            # if stream has more than one trace we use multiple axes
            if len(stream) > 1:
                for trace_index, id in enumerate(ids):
                    trace = stream.select(id=id)[0]
                    plot_index += 1
                    
                    # get distance in degree from source
                    distance_in_degree = distances[trace_index]
                    
                    # Interpolate traces onto the master time
                    interp_trace = np.interp(master_time, times[index][trace_index], trace.data)
                    id = str(trace.stats.network) + '.' + str(trace.stats.station) + \
                        '.' + str(trace.stats.location) + '.' + str(trace.stats.channel)
                    
                    # plot trace
                    ax[plot_index].plot(master_time, interp_trace, lw=0.2, 
                                        color=plot_colors[index], label=id)
                    # add text of label
                    ax[plot_index].text(.95, .2 + index*0.2, 
                                        id + '|' + str(round(distance_in_degree)), 
                                        transform = ax[plot_index].transAxes, 
                                        ha='right', va='top', fontsize=5, color=plot_colors[index])
                    ax[plot_index].tick_params(axis='both', which='major', labelsize=5)
                    ax[plot_index].tick_params(axis='both', which='minor', labelsize=5)

                    # if there are travel times of phases to be plotted
                    all_travel_times = {}
                    if len(phase_list) != 0:
                            
                            phase_list = sorted(parse_phase_list(phase_list))
                            for i, phase in enumerate(phase_list):
                                c = COLORS[i % len(COLORS)]
                                arrivals = model.get_travel_times(source_depth_in_km=evt_depth * 1e-3,
                                                                distance_in_degree=distance_in_degree,
                                                                phase_list=[phase])
                                if arrivals:
                                    arrival_time = [arrivals[k].time for k in range(len(arrivals[:]))]
                                    ax[plot_index].scatter(arrival_time, np.zeros(len(arrival_time)), marker='|', 
                                                                    c=c, label=phase)
                                    all_travel_times[phase] = arrival_time
            else:
                # there is just one trace for each stream
                trace = stream[0]
                    
                # find distance between current station and event
                distance_in_degree = distances[0]
                    
                # Interpolate traces onto the master time
                interp_trace = np.interp(master_time, times[index][0], trace.data)
                id = str(trace.stats.network) + '.' + str(trace.stats.station) + \
                    '.' + str(trace.stats.location) + '.' + str(trace.stats.channel)
                
                # Plot trace
                ax.plot(master_time, interp_trace, lw=0.2, color=plot_colors[index], label=id)
                
                # Add label text
                ax.text(.95, .2 + index*0.2, 
                        id + '|' + str(round(distance_in_degree)), 
                        transform = ax.transAxes, 
                        ha='right', va='top', fontsize=5, color=plot_colors[index])
                ax.tick_params(axis='both', which='major', labelsize=5)
                ax.tick_params(axis='both', which='minor', labelsize=5)

                # if there are travel times of phases to be plotted
                all_travel_times = {}
                if len(phase_list) != 0:

                        phase_list = sorted(parse_phase_list(phase_list))
                        for i, phase in enumerate(phase_list):
                            c = COLORS[i % len(COLORS)]
                            arrivals = model.get_travel_times(source_depth_in_km=evt_depth * 1e-3,
                                                            distance_in_degree=distance_in_degree,
                                                            phase_list=[phase])
                            if arrivals:
                                arrival_time = [arrivals[k].time for k in range(len(arrivals[:]))]
                                ax.scatter(arrival_time, np.zeros(len(arrival_time)), marker='|', 
                                                                c=c, label=phase)
                                all_travel_times[phase] = arrival_time

    fig_seismographs.text(0.5, 0.04, 'Time from event [s]', ha='center')
    fig_seismographs.text(0.04, 0.5, 'Amplitude [m]', va='center', rotation='vertical')

    # Time axis limits (x lims)
    if xlims is None:
        if len(streams[0]) > 1 :
            ax[0].set_xlim(master_time[0], master_time[-1])
        else:
            ax.set_xlim(master_time[0], master_time[-1])
    elif type(xlims) is str:
        try:
            min_arrival_time = min(all_travel_times[xlims])
            max_arrival_time = max(all_travel_times[xlims])
        except:
            tk.messagebox.showerror("Error", "The phase chosen has no arrival at the last station chose to plot!")
        if len(streams[0]) > 1 :
            ax[0].set_xlim(min_arrival_time - 100, max_arrival_time + 100)
        else:
            ax.set_xlim(min_arrival_time - 100, max_arrival_time + 100)
    else:
        if len(streams[0]) > 1 :
            ax[0].set_xlim(xlims[0], xlims[-1])
        else:
            ax.set_xlim(xlims[0], xlims[-1])

    plt.show()


def Plot_3D_Earth(phase_list: list, earth_model: str, inv_selection: obspy.Inventory,
                  cat: obspy.Catalog, file: str, PLOT_RAYS: bool = False):
    """Plots a 3D interactive Earth model that shows Earth's surface
    , CMB topography, the source and stations locations, as well as the 
    paths of the chosen phases.

    Args:
        phase_list (list): list of the phases to be plotted
        earth_model (str): Taup model used for computing phase rays
        inv_selection (obspy.Inventory): selected inventory
        cat (obspy.Catalog): catalogue
        file (str): path to CMB txt file

    Returns:
        Nothing: Just plots
    """    
    # Define the lat lon grid (must match data file)
    lat = np.arange(-90, 90.01, 1)*np.pi/180
    lon = np.arange(-180, 180.01, 1)*np.pi/180
    LON, LAT = np.meshgrid(lon, lat)
    nlat = len(lat)
    nlon = len(lon)
    nrow = nlat * nlon

    # Get radial data for CMB
    if len(file) != 0:
        data = np.loadtxt(file)
        data = data[:,2]
        
        # Put data in matrix form and put average of the data at the poles
        CMB = np.zeros((nlat, nlon))
        # north pole
        CMB[0, :] = data[0:nlon].sum() / nlon
        # south pole
        CMB[-1, :] = data[nrow - nlon:nrow].sum() / nlon
        for i in range(1, nlat):
            CMB[i, :] = data[i * nlon:i * nlon + nlon]
    else:
         CMB = np.ones((nlat, nlon))
    
    # Construct CMB and Surface matrices
    R_cmb = 3480
    R = CMB + R_cmb
    R_surface = 6371 * np.ones(np.shape(CMB))

    # Transform to cartesian coords
    X = R * np.cos(LAT) * np.cos(LON)
    Y = R * np.cos(LAT) * np.sin(LON)
    Z = R * np.sin(LAT)

    X_surface = R_surface * np.cos(LAT) * np.cos(LON)
    Y_surface = R_surface * np.cos(LAT) * np.sin(LON)
    Z_surface = R_surface * np.sin(LAT)

    # plot
    # create colormap
    N = len(CMB.flatten()) # Number of points
    scalars = np.arange(N).reshape(CMB.shape[0], CMB.shape[1]) # Key point: set an integer for each point

    CMB_neg = CMB.copy()
    CMB_neg[CMB_neg>0] = 0 # for blue
    CMB_pos = CMB.copy()
    CMB_neg[CMB_pos<0] = 0 # for red
    # Define color table (including alpha), which must be uint8 and [0,255]
    colors = np.ones((N, 4))
    colors[:,0] = (1 - CMB_pos.flatten() / np.abs(CMB).max()) * 255 # red
    colors[:,1] = (1 - np.abs(CMB).flatten() / np.abs(CMB).max()) * 255 # green
    colors[:,2] = (1 + CMB_neg.flatten() / np.abs(CMB).max()) * 255 # blue
    colors = colors.astype(np.uint8)
    colors[:,-1] = 255 # No transparency
    
    mlab.figure(bgcolor=(0,0,0))
    # Plot CMB
    CMB_surface = mlab.mesh(X, Y, Z, scalars=scalars, mode='sphere', opacity=0.6)
    # Set look-up table and redraw
    CMB_surface.module_manager.scalar_lut_manager.lut.table = colors
    # Plot surface
    Surface = mlab.mesh(X_surface, Y_surface, Z_surface, color=(1,1,1), opacity=0.2)   

    # Create basemap instance
    m = Basemap(projection='cyl', llcrnrlat=-90, urcrnrlat=90,
                llcrnrlon=-180, urcrnrlon=180, resolution='c')

    if PLOT_RAYS is True:
        # Get location of earthquake 
        evt_depth = cat[0].origins[0].depth
        evt_lat = np.deg2rad(cat[0].origins[0].latitude)
        evt_lon = np.deg2rad(cat[0].origins[0].longitude)
        evt_lat_deg = cat[0].origins[0].latitude
        evt_lon_deg = cat[0].origins[0].longitude
        evt_rad = (6371000 - evt_depth)/1000
        X_evt = evt_rad * np.cos(evt_lat) * np.cos(evt_lon)
        Y_evt = evt_rad * np.cos(evt_lat) * np.sin(evt_lon)
        Z_evt = evt_rad * np.sin(evt_lat)
        # Plot source
        mlab.points3d(X_evt, Y_evt, Z_evt, scale_factor=100, color=(1,0,0), opacity=1)
        # Plot stations
        earth_model = TauPyModel(model=earth_model)
        phase_list = ["{0}".format(elem) for elem in phase_list]
        for net in inv_selection:
            for sta in net:
                sta_lat = np.deg2rad(sta.latitude)
                sta_lon = np.deg2rad(sta.longitude)
                sta_lat_deg = sta.latitude
                sta_lon_deg = sta.longitude
                sta_rad = 6371
                X_sta = sta_rad * np.cos(sta_lat) * np.cos(sta_lon)
                Y_sta = sta_rad * np.cos(sta_lat) * np.sin(sta_lon)
                Z_sta = sta_rad * np.sin(sta_lat)
                mlab.points3d(X_sta, Y_sta, Z_sta, scale_factor=200, color=(0,1,0))
                for phase in phase_list:
                    rays = earth_model.get_ray_paths_geo(evt_depth/1000, 
                                                        evt_lat_deg, 
                                                        evt_lon_deg, 
                                                        sta_lat_deg, 
                                                        sta_lon_deg, 
                                                        phase_list=[phase], 
                                                        resample=False, 
                                                        ray_param_tol=1e-06)
                    if len(rays) > 0:
                        for ray in rays:
                            depth = []
                            lat = []
                            lon = []
                            for point in ray.path:
                                depth.append(point[3])
                                lat.append(point[4])
                                lon.append(point[5])
                            r = 6371 - np.array(depth)
                            lat = np.array(lat)
                            lon = np.array(lon)
                        
                            X_ray = r * np.cos(np.deg2rad(lat)) * np.cos(np.deg2rad(lon))
                            Y_ray = r * np.cos(np.deg2rad(lat)) * np.sin(np.deg2rad(lon))
                            Z_ray = r * np.sin(np.deg2rad(lat))
                            
                        mlab.plot3d(X_ray, Y_ray, Z_ray, color=(0.1568,0.70588,1), tube_radius=10)

    mlab.show()    