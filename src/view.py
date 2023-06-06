# Libraries
import tkinter as tk
import matplotlib
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
)
import matplotlib # noqa
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa
import numpy as np

# In house files
import plotter

class View(tk.Tk):
    """ Docs
    """
    PAD = 10 # Window padding


    def __init__(self, controller):

        super().__init__()

        # Link view to controller
        self.controller = controller

        # Configure main window
        self.title('Post processing')
        self.grid_rowconfigure(0,weight=1)
        self.grid_rowconfigure(1,weight=1)
        self.grid_rowconfigure(2,weight=1)
        self.grid_columnconfigure(0,weight=1)
        self.geometry('{}x{}'.format(1080, 1920))
        
        # Create the frames for the station window
        self._make_databases_frame()
        self._make_add_databases_frame()
        self._make_review_databases_frame()
        self._make_graph_control_frame()
        self._make_other_buttons_frame()


    def main(self):
        self.mainloop()


################
# DATABASE FRAME
################
    def _make_databases_frame(self):
        self.databases_frame = tk.Frame(self, bg='#002147')
        self.databases_frame.grid(sticky="nsew", row=0, padx=10, pady=10)
        self.databases_frame.rowconfigure(0, weight=1)
        self.databases_frame.columnconfigure(0, weight=1)
        self.databases_frame.columnconfigure(1, weight=2)


    def _make_add_databases_frame(self):
        self.add_databases_frame = tk.Frame(self.databases_frame)
        self.add_databases_frame.grid(sticky="nsew", row=0, column=0, padx=10, pady=10)
        self.add_databases_frame.rowconfigure(0, weight=1)
        self.add_databases_frame.rowconfigure(1, weight=1)
        self.add_databases_frame.rowconfigure(2, weight=1)
        self.add_databases_frame.rowconfigure(3, weight=1)
        self.add_databases_frame.columnconfigure(0, weight=1)
        self.add_databases_frame.columnconfigure(1, weight=1)
        self.add_databases_frame.columnconfigure(2, weight=1)
        
        # Create entry for path to mseed file, catalogue, inventory, and data
        # type
        self.wavefield_path = tk.StringVar()
        self.cat_path = tk.StringVar()
        self.inv_path = tk.StringVar()
        self.data_type = tk.StringVar()
        
        # Entry for path to wavefield
        self.wavefield_path_entry = tk.Entry(
            self.add_databases_frame,
            justify='left',
            width=50,
            textvariable=self.wavefield_path,
        )
        self.wavefield_path_entry.grid(row=0,column=1)
        tk.Label(self.add_databases_frame, text='Path to wavefield mseed file').grid(row=0,column=0)
        # Entry for path to catalogue
        self.cat_path_entry = tk.Entry(
            self.add_databases_frame,
            justify='left',
            width=50,
            textvariable=self.cat_path,
        )
        self.cat_path_entry.grid(row=1,column=1)
        tk.Label(self.add_databases_frame, text='Path to catalogue file').grid(row=1,column=0)
        # Entry for path to inventory
        self.inv_path_entry = tk.Entry(
            self.add_databases_frame,
            justify='left',
            width=50,
            textvariable=self.inv_path,
        )
        self.inv_path_entry.grid(row=2,column=1)
        tk.Label(self.add_databases_frame, text='Path to inventory file').grid(row=2,column=0)
        # Drop down menu for data type        
        self.data_type.set('simulation')
        self.data_type_options = tk.OptionMenu(self.add_databases_frame, self.data_type, 
                                               "real", "simulation", "instaseis").grid(row=3, column=1)
        tk.Label(self.add_databases_frame, text='Data type').grid(row=3,column=0)
        # Create button to load mseed file
        self.load_wavefield = tk.Button(self.add_databases_frame,
                                                text="Load wavefield",
                             command=self.controller.on_press_load_wavefield) # noqa
        self.load_wavefield.grid(row=0,column=2)
        # auto load button (searches for cat and inv by itself)
        self.auto_load_wavefield = tk.Button(self.add_databases_frame,
                                                text="Auto load wavefield",
                             command=self.controller.on_press_auto_load_wavefield) # noqa
        self.auto_load_wavefield.grid(row=1,column=2)


    def _make_review_databases_frame(self):
        self.review_databases_frame = tk.Frame(self.databases_frame)
        self.review_databases_frame.grid(sticky="nsew", row=0, column=1, padx=10, pady=10)
        self.review_databases_frame.rowconfigure(0, weight=1)
        self.review_databases_frame.rowconfigure(1, weight=1)
        self.review_databases_frame.columnconfigure(0, weight=1)
        self.review_databases_frame.columnconfigure(1, weight=1)
        
        # Database listbox
        tk.Label(self.review_databases_frame, text='Database').grid(row=0,column=0)
        self.listbox = tk.Listbox(self.review_databases_frame)
        self.listbox.grid(sticky='nsew', row=1,column=0)
        self.listbox_index = 0
        
        # buttons for listbox
        self.database_buttons_frame = tk.Frame(self.review_databases_frame)
        self.database_buttons_frame.grid(sticky="nsew", row=2, column=0, padx=0, pady=0)
        self.database_buttons_frame.rowconfigure(0, weight=1)
        self.database_buttons_frame.columnconfigure(0, weight=1)
        self.database_buttons_frame.columnconfigure(1, weight=1)
        self.select_wavefield = tk.Button(self.database_buttons_frame,
                                                text="Select wavefield",
                             command=self.controller.on_press_select_wavefield) # noqa
        self.select_wavefield.grid(row=0,column=0)
        
        # Button for removing wavefield
        self.remove_wavefield = tk.Button(self.database_buttons_frame,
                                                text="Remove wavefield",
                             command=self.controller.on_press_remove_wavefield) # noqa
        self.remove_wavefield.grid(row=0,column=1)
        
        # A text saying this is selection area
        tk.Label(self.review_databases_frame, text='Selection').grid(row=0,column=1)

        # Selection listbox
        self.deselect_wavefield = tk.Button(self.review_databases_frame,
                                                text="Deselect wavefield",
                             command=self.controller.on_press_deselect_wavefield) # noqa
        self.deselect_wavefield.grid(row=2,column=1)

        self.selection_listbox = tk.Listbox(self.review_databases_frame)
        self.selection_listbox.grid(sticky='nsew', row=1,column=1)
        self.selection_listbox_index = 0

    
#####################
# CONTROL PLOTS FRAME
#####################
    def _make_graph_control_frame(self):
        self.graph_control_frame = tk.Frame(self, bg='#002147')
        self.graph_control_frame.grid(sticky="nsew", row=1, column=0, padx=20, pady=20)
        self.graph_control_frame.rowconfigure(0, weight=1)
        self.graph_control_frame.rowconfigure(1, weight=1)
        self.graph_control_frame.rowconfigure(2, weight=1)
        self.graph_control_frame.rowconfigure(3, weight=1)
        self.graph_control_frame.rowconfigure(4, weight=1)
        self.graph_control_frame.rowconfigure(5, weight=1)
        self.graph_control_frame.columnconfigure(0, weight=1)
        self.graph_control_frame.columnconfigure(1, weight=1)
        self.graph_control_frame.columnconfigure(2, weight=1)
        self.graph_control_frame.columnconfigure(3, weight=1)
        self.graph_control_frame.columnconfigure(4, weight=1)
        self.graph_control_frame.columnconfigure(5, weight=1)
        self.graph_control_frame.columnconfigure(6, weight=1)
        self.graph_control_frame.columnconfigure(7, weight=1)
        self.graph_control_frame.columnconfigure(8, weight=1)
        self.graph_control_frame.columnconfigure(9, weight=1)
        self.graph_control_frame.columnconfigure(10, weight=1)
        self.graph_control_frame.columnconfigure(11, weight=10)

        # Plot button
        self.plot_button = tk.Button(self.graph_control_frame,
                                                text="Plot",
                             command=self.controller.on_press_plot_button) # noqa
        self.plot_button.grid(row=0,column=10)
        # Station plot button
        self.plot_stations_button = tk.Button(self.graph_control_frame,
                                                text="Plot stations",
                             command=self.controller.on_press_plot_stations_button) # noqa
        self.plot_stations_button.grid(row=1,column=10)
        # Traveltime plot button
        self.plot_traveltimes_button = tk.Button(self.graph_control_frame,
                                                text="Plot travel times",
                             command=self.controller.on_press_plot_traveltimes_button) # noqa
        self.plot_traveltimes_button.grid(row=2,column=10)
        # 3D Earth plot button
        self.plot_Earth_button = tk.Button(self.graph_control_frame,
                                                text="Plot Earth",
                             command=self.controller.on_press_plot_earth_button) # noqa
        self.plot_Earth_button.grid(row=3,column=10)

        # Min freq
        self.freq_min = tk.StringVar()
        self.freq_min_entry = tk.Entry(
            self.graph_control_frame,
            justify='left',
            width=10,
            textvariable=self.freq_min,
        )
        self.freq_min_entry.grid(row=0, column=1)
        tk.Label(self.graph_control_frame, text='Min freq').grid(row=0,column=0)
        # Max freq
        self.freq_max = tk.StringVar()
        self.freq_max_entry = tk.Entry(
            self.graph_control_frame,
            justify='left',
            width=10,
            textvariable=self.freq_max,
        )
        self.freq_max_entry.grid(row=1, column=1)
        tk.Label(self.graph_control_frame, text='Max freq').grid(row=1,column=0)
        # Min lat
        self.min_lat = tk.StringVar()
        self.min_lat_entry = tk.Entry(
            self.graph_control_frame,
            justify='left',
            width=10,
            textvariable=self.min_lat,
        )
        self.min_lat_entry.grid(row=0, column=3)
        tk.Label(self.graph_control_frame, text='Min lat').grid(row=0,column=2)
        # Max lat
        self.max_lat = tk.StringVar()
        self.max_lat_entry = tk.Entry(
            self.graph_control_frame,
            justify='left',
            width=10,
            textvariable=self.max_lat,
        )
        self.max_lat_entry.grid(row=1, column=3)
        tk.Label(self.graph_control_frame, text='Max lat').grid(row=1,column=2)
        # Min lon
        self.min_lon = tk.StringVar()
        self.min_lon_entry = tk.Entry(
            self.graph_control_frame,
            justify='left',
            width=10,
            textvariable=self.min_lon,
        )
        self.min_lon_entry.grid(row=2, column=3)
        tk.Label(self.graph_control_frame, text='Min lon').grid(row=2,column=2)
        # Max lon
        self.max_lon = tk.StringVar()
        self.max_lon_entry = tk.Entry(
            self.graph_control_frame,
            justify='left',
            width=10,
            textvariable=self.max_lon,
        )
        self.max_lon_entry.grid(row=3, column=3)
        tk.Label(self.graph_control_frame, text='Max lon').grid(row=3,column=2)
        # Networks
        self.networks = tk.StringVar()
        self.networks_entry = tk.Entry(
            self.graph_control_frame,
            justify='left',
            width=10,
            textvariable=self.networks,
        )
        self.networks_entry.grid(row=0, column=5)
        tk.Label(self.graph_control_frame, text='Networks').grid(row=0,column=4)
        # Stations
        self.stations = tk.StringVar()
        self.stations_entry = tk.Entry(
            self.graph_control_frame,
            justify='left',
            width=10,
            textvariable=self.stations,
        )
        self.stations_entry.grid(row=1, column=5)
        tk.Label(self.graph_control_frame, text='Stations').grid(row=1,column=4)
        # Channels
        self.channels = tk.StringVar()
        self.channels_entry = tk.Entry(
            self.graph_control_frame,
            justify='left',
            width=10,
            textvariable=self.channels,
        )
        self.channels_entry.grid(row=2, column=5)
        tk.Label(self.graph_control_frame, text='Channels').grid(row=2,column=4)
        # Locations
        self.locations = tk.StringVar()
        self.locations_entry = tk.Entry(
            self.graph_control_frame,
            justify='left',
            width=10,
            textvariable=self.locations,
        )
        self.locations_entry.grid(row=3, column=5)
        tk.Label(self.graph_control_frame, text='Locations').grid(row=3,column=4)
        # X lim
        self.xlim = tk.StringVar()
        self.xlim_entry = tk.Entry(
            self.graph_control_frame,
            justify='left',
            width=10,
            textvariable=self.xlim,
        )
        self.xlim_entry.grid(row=0, column=7)
        tk.Label(self.graph_control_frame, text='xlim').grid(row=0,column=6)
        # Model drop down
        self.model = tk.StringVar()
        self.model.set('prem')
        self.model_options = tk.OptionMenu(self.graph_control_frame, self.model, "prem", "iasp91", "ak135").grid(row=0, column=9)
        tk.Label(self.graph_control_frame, text='Taup Model').grid(row=0,column=8)
        # Phase list
        self.phase_list = tk.StringVar()
        self.phase_list_entry = tk.Entry(
            self.graph_control_frame,
            justify='left',
            width=10,
            textvariable=self.phase_list,
        )
        self.phase_list_entry.grid(row=1, column=9)
        tk.Label(self.graph_control_frame, text='Phase list').grid(row=1,column=8)
        # Event depth
        self.event_depth = tk.StringVar()
        self.event_depth_entry = tk.Entry(
            self.graph_control_frame,
            justify='left',
            width=10,
            textvariable=self.event_depth,
        )
        self.event_depth_entry.grid(row=2, column=9)
        tk.Label(self.graph_control_frame, text='Event depth').grid(row=2,column=8)
        # CMB txt file
        self.CMB_txt_file = tk.StringVar()
        self.CMB_txt_file_entry = tk.Entry(
            self.graph_control_frame,
            justify='left',
            width=10,
            textvariable=self.CMB_txt_file,
        )
        self.CMB_txt_file_entry.grid(row=3, column=9)
        tk.Label(self.graph_control_frame, text='CMB txt file').grid(row=3,column=8)
        # Checkbox for difference plot
        self.difference_checkbox_state = tk.IntVar()
        self.difference_checkbox = tk.Checkbutton(self.graph_control_frame, text='Plot difference squared',
                            variable=self.difference_checkbox_state, onvalue=1, offvalue=0)
        self.difference_checkbox.grid(row=0, column=11)

#####################
# OTHER BUTTONS FRAME
#####################

    def _make_other_buttons_frame(self):
        self.other_buttons_frame = tk.Frame(self, bg='#002147')
        self.other_buttons_frame.grid(sticky="nsew", row=2, column=0, padx=20, pady=20)
            
        # Element outputs
        self.elements_output_button = tk.Button(self.other_buttons_frame,
                                                text="Elements output",
                             command=self.controller.on_press_elements_output_button) # noqa
        self.elements_output_button.grid(row=0,column=0)
        
#######################        
# ELEMENTS OUPUT WINDOW
#######################
    def _create_elements_output_window(self):
        
        self.elements_output_window = tk.Toplevel(self)

        self.elements_output_window.title("Elements output")
        self.elements_output_window.grid_rowconfigure(0,weight=1)
        self.elements_output_window.grid_rowconfigure(1,weight=1)
        self.elements_output_window.grid_columnconfigure(0,weight=1)
        self.elements_output_window.geometry('{}x{}'.format(1080, 1920))
        
        self._make_elements_database_frame()
        self._make_elements_add_database_frame()
        self._make_elements_review_database_frame()
        self._make_elements_control_frame()
        

#########################
# ELEMENTS DATABASE FRAME
#########################
    def _make_elements_database_frame(self):
        self.elements_database_frame = tk.Frame(self.elements_output_window, bg='#002147')
        self.elements_database_frame.grid(sticky="nsew", row=0, column=0, padx=10, pady=10)
        self.elements_database_frame.rowconfigure(0, weight=1)
        self.elements_database_frame.columnconfigure(0, weight=1)
        self.elements_database_frame.columnconfigure(1, weight=2)

    def _make_elements_add_database_frame(self):
        self.elements_add_database_frame = tk.Frame(self.elements_database_frame)
        self.elements_add_database_frame.grid(sticky="nsew", row=0, column=0, padx=10, pady=10)
        self.elements_add_database_frame.rowconfigure(0, weight=1)
        self.elements_add_database_frame.rowconfigure(1, weight=1)
        self.elements_add_database_frame.columnconfigure(0, weight=1)
        self.elements_add_database_frame.columnconfigure(1, weight=1)
        
        # Create entry for path to elements output
        self.elements_path = tk.StringVar()
        self.elements_path_entry = tk.Entry(
            self.elements_add_database_frame,
            justify='left',
            width = 50,
            textvariable=self.elements_path
        )
        self.elements_path_entry.grid(row=0, column=1)
        tk.Label(self.elements_add_database_frame, text='Path to elements output dir').grid(row=0, column=0)

        # Create button for adding element output to elements database
        self.load_elements_output = tk.Button(self.elements_add_database_frame,
                                                text="Load elements data",
                             command=self.controller.on_press_load_elements_output) # noqa
        self.load_elements_output.grid(row=1,column=1)
        
    def _make_elements_review_database_frame(self):
        self.elements_review_database_frame = tk.Frame(self.elements_database_frame)
        self.elements_review_database_frame.grid(sticky="nsew", row=0, column=1, padx=10, pady=10)
        self.elements_review_database_frame.rowconfigure(0, weight=1)
        self.elements_review_database_frame.rowconfigure(1, weight=1)
        self.elements_review_database_frame.rowconfigure(2, weight=1)
        self.elements_review_database_frame.rowconfigure(3, weight=1)
        self.elements_review_database_frame.columnconfigure(0, weight=1)
        self.elements_review_database_frame.columnconfigure(1, weight=1)
        
        # Database listbox
        tk.Label(self.elements_review_database_frame, text='Database').grid(row=0,column=0)
        self.elements_listbox = tk.Listbox(self.elements_review_database_frame)
        self.elements_listbox.grid(sticky='nsew', row=1, column=0)
        self.elements_listbox_index = 0
        
        self.elements_review_database_buttons_subframe = tk.Frame(self.elements_review_database_frame)
        self.elements_review_database_buttons_subframe.grid(sticky="nsew", row=2, column=0, padx=10, pady=10)
        self.elements_review_database_buttons_subframe.rowconfigure(0, weight=1)
        self.elements_review_database_buttons_subframe.columnconfigure(0, weight=1)
        self.elements_review_database_buttons_subframe.columnconfigure(1, weight=1)
        
        # Buttons for Database listbox
        self.select_elements_wavefield = tk.Button(self.elements_review_database_buttons_subframe,
                                                   text='Select wavefield',
                                                   command=self.controller.on_press_select_elements_wavefield)
        self.select_elements_wavefield.grid(row=2, column=0)
        self.remove_elements_wavefield = tk.Button(self.elements_review_database_buttons_subframe,
                                                   text='Remove wavefield',
                                                   command=self.controller.on_press_remove_elements_wavefield)
        self.remove_elements_wavefield.grid(row=2, column=1)
        
        # Selected Database listbox
        tk.Label(self.elements_review_database_frame, text='Selected Database').grid(row=0,column=1)
        self.selected_elements_listbox = tk.Listbox(self.elements_review_database_frame)
        self.selected_elements_listbox.grid(sticky='nsew', row=1, column=1)
        self.selected_elements_listbox_index = 0
        
        # Button for Selected Database listbox
        self.deselect_elements_wavefield = tk.Button(self.elements_review_database_frame,
                                                   text='Deselect wavefield',
                                                   command=self.controller.on_press_deselect_elements_wavefield)
        self.deselect_elements_wavefield.grid(row=2, column=1)

        
########################
# ELEMENTS CONTROL FRAME
########################

    def _make_elements_control_frame(self):
        self.elements_control_frame = tk.Frame(self.elements_output_window, bg='#002147')
        self.elements_control_frame.grid(sticky="nsew", row=1, column=0, padx=10, pady=10)
        self.elements_control_frame.rowconfigure(0, weight=1)
        self.elements_control_frame.rowconfigure(1, weight=1)
        self.elements_control_frame.rowconfigure(2, weight=1)
        self.elements_control_frame.rowconfigure(3, weight=1)
        self.elements_control_frame.columnconfigure(0, weight=1)
        self.elements_control_frame.columnconfigure(1, weight=1)
        self.elements_control_frame.columnconfigure(2, weight=1)
        self.elements_control_frame.columnconfigure(3, weight=1)
        self.elements_control_frame.columnconfigure(4, weight=1)
        self.elements_control_frame.columnconfigure(5, weight=1)
        self.elements_control_frame.columnconfigure(6, weight=1)
        
        # Buttons 
        # Plot
        self.plot_elements_button = tk.Button(self.elements_control_frame,
                                                   text='Plot',
                                                   command=self.controller.on_press_plot_elements_button)
        self.plot_elements_button.grid(row=0, column=6)
        # Traveltime plot button
        self.plot_elements_traveltimes_button = tk.Button(self.elements_control_frame,
                                                text="Plot travel times 2",
                             command=self.controller.on_press_plot_elements_traveltimes_button) # noqa
        self.plot_elements_traveltimes_button.grid(row=2,column=6)
        # 3D Earth plot button
        self.plot_elements_Earth_button = tk.Button(self.elements_control_frame,
                                                text="Plot Earth",
                             command=self.controller.on_press_plot_elements_earth_button) # noqa
        self.plot_elements_Earth_button.grid(row=3,column=6)
        
        # Min freq
        self.elements_freq_min = tk.StringVar()
        self.elements_freq_min_entry = tk.Entry(
            self.elements_control_frame,
            justify='left',
            width=10,
            textvariable=self.elements_freq_min,
        )
        self.elements_freq_min_entry.grid(row=0, column=1)
        tk.Label(self.elements_control_frame, text='Min freq').grid(row=0,column=0)
        # Max freq
        self.elements_freq_max = tk.StringVar()
        self.elements_freq_max_entry = tk.Entry(
            self.elements_control_frame,
            justify='left',
            width=10,
            textvariable=self.elements_freq_max,
        )
        self.elements_freq_max_entry.grid(row=1, column=1)
        tk.Label(self.elements_control_frame, text='Max freq').grid(row=1,column=0)
        # Depth
        self.station_depth = tk.StringVar()
        self.station_depth_entry = tk.Entry(
            self.elements_control_frame,
            justify='left',
            width=10,
            textvariable=self.station_depth,
        )
        self.station_depth_entry.grid(row=0, column=3)
        tk.Label(self.elements_control_frame, text='Depth [km]').grid(row=0,column=2)
        # Latitude
        self.station_latitude = tk.StringVar()
        self.station_latitude_entry = tk.Entry(
            self.elements_control_frame,
            justify='left',
            width=10,
            textvariable=self.station_latitude,
        )
        self.station_latitude_entry.grid(row=1, column=3)
        tk.Label(self.elements_control_frame, text='Latitude [deg]').grid(row=1,column=2)
        # Longitude
        self.station_longitude = tk.StringVar()
        self.station_longitude_entry = tk.Entry(
            self.elements_control_frame,
            justify='left',
            width=10,
            textvariable=self.station_longitude,
        )
        self.station_longitude_entry.grid(row=2, column=3)
        tk.Label(self.elements_control_frame, text='Longitude [deg]').grid(row=2,column=2)
        # Channel
        self.elements_channel = tk.StringVar()
        self.elements_channel_entry = tk.Entry(
            self.elements_control_frame,
            justify='left',
            width=10,
            textvariable=self.elements_channel,
        )
        self.elements_channel_entry.grid(row=3, column=3)
        tk.Label(self.elements_control_frame, text='Channel').grid(row=3,column=2)
        # Model drop down
        self.elements_model = tk.StringVar()
        self.elements_model.set('prem')
        self.elements_model_options = tk.OptionMenu(self.elements_control_frame, self.elements_model, "prem", "iasp91", "ak135").grid(row=0, column=5)
        tk.Label(self.elements_control_frame, text='Taup Model').grid(row=0,column=4)
        # Phase list
        self.elements_phase_list = tk.StringVar()
        self.elements_phase_list_entry = tk.Entry(
            self.elements_control_frame,
            justify='left',
            width=10,
            textvariable=self.elements_phase_list,
        )
        self.elements_phase_list_entry.grid(row=1, column=5)
        tk.Label(self.elements_control_frame, text='Phase list').grid(row=1,column=4)
        # Event depth
        self.elements_event_depth = tk.StringVar()
        self.elements_event_depth_entry = tk.Entry(
            self.elements_control_frame,
            justify='left',
            width=10,
            textvariable=self.elements_event_depth,
        )
        self.elements_event_depth_entry.grid(row=2, column=5)
        tk.Label(self.elements_control_frame, text='Event depth').grid(row=2,column=4)
        # CMB txt file
        self.elements_CMB_txt_file = tk.StringVar()
        self.elements_CMB_txt_file_entry = tk.Entry(
            self.elements_control_frame,
            justify='left',
            width=10,
            textvariable=self.elements_CMB_txt_file,
        )
        self.elements_CMB_txt_file_entry.grid(row=3, column=5)
        tk.Label(self.elements_control_frame, text='CMB txt file').grid(row=3,column=4)