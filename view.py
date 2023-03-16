from tkinter import ttk
import tkinter as tk
import matplotlib
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
)
import matplotlib # noqa
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa
import numpy as np
import plotter

class View(tk.Tk):
    """ Docs
    """
    PAD = 10

    def __init__(self, controller):

        super().__init__()

        self.controller = controller

        self.title('Post processing')
        self.grid_rowconfigure(0,weight=1)
        self.grid_rowconfigure(1,weight=1)
        self.grid_rowconfigure(2,weight=1)
        self.grid_columnconfigure(0,weight=1)
        self.geometry('{}x{}'.format(1080, 1920))
        
        self._make_databases_frame()
        self._make_add_databases_frame()
        self._make_review_databases_frame()
        self._make_graph_control_frame()

        #self._make_crosscorrelation_control_frame()

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
        
        # Create entry for path to mseed file
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
        self.data_type_options = tk.OptionMenu(self.add_databases_frame, self.data_type, "real", "simulation", "instaseis").grid(row=3, column=1)
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
        
        self.delete_wavefield = tk.Button(self.database_buttons_frame,
                                                text="Delete wavefield",
                             command=self.controller.on_press_delete_wavefield) # noqa
        self.delete_wavefield.grid(row=0,column=1)

        
        
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
        self.plot_traveltimes_button = tk.Button(self.graph_control_frame,
                                                text="Plot Earth",
                             command=self.controller.on_press_plot_earth_button) # noqa
        self.plot_traveltimes_button.grid(row=3,column=10)

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