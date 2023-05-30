import tkinter as tk
from view import View
from model import Model
import plotter
from obspy.taup import plot_travel_times

class Controller():
    """
    Main controller
    """

    def __init__(self):
        self.view = View(self)
        self.model = Model(self)


    def main(self):
        self.view.main()

 
    def on_press_load_wavefield(self):
        """Functionality of load button
        """        
        # Check for possible errors
        if len(self.view.wavefield_path.get()) == 0:
            tk.messagebox.showerror("Error", "The wavefield path entry is empty!")
        elif len(self.view.cat_path.get()) == 0:
            tk.messagebox.showerror("Error", "The catalogue path entry is empty!")
        elif len(self.view.inv_path.get()) == 0:
            tk.messagebox.showerror("Error", "The inventory path entry is empty!")
        elif len(self.view.data_type.get()) == 0:
            tk.messagebox.showerror("Error", "The data type entry is empty!")
        else:
            # If the wavefield database is empty, create a database entry
            if self.model.wavefield_database is None:
                self.model.create_database()
                self.model.load_wavefield(self.view.wavefield_path.get(),
                                        self.view.cat_path.get(),
                                        self.view.inv_path.get(),
                                        self.view.data_type.get())
                stream_name = self.view.wavefield_path.get().split('/')[-1]
                self.view.listbox_index += 1
                self.view.listbox.insert(self.view.listbox_index, stream_name)
                self.view.wavefield_path_entry.delete(0, 'end')
                self.view.cat_path_entry.delete(0, 'end')
                self.view.inv_path_entry.delete(0, 'end')
            else:
                stream_name = self.view.wavefield_path.get().split('/')[-1]
                ENTRY_EXISTS = False
                for i, listbox_entry in enumerate(self.view.listbox.get(0, tk.END)):
                    if listbox_entry == stream_name:
                        ENTRY_EXISTS = True
                if ENTRY_EXISTS is True:
                    tk.messagebox.showerror("Error", "The database entry already exists!")
                else:
                    self.model.load_wavefield(self.view.wavefield_path.get(),
                                            self.view.cat_path.get(),
                                            self.view.inv_path.get(),
                                            self.view.data_type.get())
                    self.view.listbox_index += 1
                    self.view.listbox.insert(self.view.listbox_index, stream_name)
                    self.view.wavefield_path_entry.delete(0, 'end')
                    self.view.cat_path_entry.delete(0, 'end')
                    self.view.inv_path_entry.delete(0, 'end')


    def on_press_auto_load_wavefield(self):
        if len(self.view.wavefield_path.get()) == 0:
            tk.messagebox.showerror("Error", "The wavefield path entry is empty!")
        elif len(self.view.data_type.get()) == 0:
            tk.messagebox.showerror("Error", "The data type entry is empty!")
        else:
            if self.model.wavefield_database is None:
                self.model.create_database()
                self.model.auto_load_wavefield(self.view.wavefield_path.get(),
                                            self.view.data_type.get())
                stream_name = self.view.wavefield_path.get().split('/')[-1]
                self.view.listbox_index += 1
                self.view.listbox.insert(self.view.listbox_index, stream_name)
                self.view.wavefield_path_entry.delete(0, 'end')
                self.view.cat_path_entry.delete(0, 'end')
                self.view.inv_path_entry.delete(0, 'end')
            else:
                stream_name = self.view.wavefield_path.get().split('/')[-1]
                ENTRY_EXISTS = False
                for _, listbox_entry in enumerate(self.view.listbox.get(0, tk.END)):
                    if listbox_entry == stream_name:
                        ENTRY_EXISTS = True
                if ENTRY_EXISTS is True:
                    tk.messagebox.showerror("Error", "The database entry already exists!")
                else:
                    self.model.auto_load_wavefield(self.view.wavefield_path.get(),
                                                self.view.data_type.get())
                    self.view.listbox_index += 1
                    self.view.listbox.insert(self.view.listbox_index, stream_name)
                    self.view.wavefield_path_entry.delete(0, 'end')
                    self.view.cat_path_entry.delete(0, 'end')
                    self.view.inv_path_entry.delete(0, 'end')


    def on_press_select_wavefield(self):
        for i in self.view.listbox.curselection():
            SELECTION_EXISTS = False
            for _, listbox_entry in enumerate(self.view.selection_listbox.get(0, tk.END)):
                if listbox_entry == self.view.listbox.get(i):
                    SELECTION_EXISTS = True
            if SELECTION_EXISTS is True:
                tk.messagebox.showerror("Error", "The database entry is already selected!")
            else:
                self.view.selection_listbox_index += 1
                self.view.selection_listbox.insert(self.view.selection_listbox_index, 
                                                   self.view.listbox.get(i))
                self.model.add_selection(self.view.listbox.get(i))
                

    def on_press_deselect_wavefield(self):
        if len(self.view.selection_listbox.curselection()) == 0:
            tk.messagebox.showerror("Error", "Select a database to be deselected!")
        else:
            for i in self.view.selection_listbox.curselection():
                self.model.remove_selection(self.view.selection_listbox.get(i))
                self.view.selection_listbox.delete(i)


    def on_press_delete_wavefield(self):
        if len(self.view.listbox.curselection()) == 0:
            tk.messagebox.showerror("Error", "Select a database to be deleted!")
        else:
            for i in self.view.listbox.curselection():
                self.model.wavefield_database.delete_from_database(self.view.listbox.get(i))
                
                for j, selection_listbox_entry in enumerate(self.view.selection_listbox.get(0, tk.END)):
                    if selection_listbox_entry == self.view.listbox.get(i):
                        self.view.selection_listbox.delete(j)
                        
                self.view.listbox.delete(i)


    def on_press_plot_button(self):
        # Check if there is any database selected for plotting 
        try:
            self.model.wavefield_database.selected_database
        except:
            tk.messagebox.showerror("Error", "The selected database is empty!")
            
        if len(self.model.wavefield_database.database) == 0:
                tk.messagebox.showerror("Error", "The selected database is empty!")
                
        else:
            
            # get the data 
            times, streams = self.model.get_times_and_streams()
            
            if len(self.view.xlim.get()) == 0:
                xlims = None            
            else:
                if self.view.xlim.get() in self.view.phase_list.get().split(','):
                    xlims = self.view.xlim.get()
                else:
                    try:
                        float(self.view.xlim.get().split(',')[0])
                    except:
                        tk.messagebox.showerror("Error", 'Please insert a numerical interval' +  \
                                                'in the format int,int or a phase from the phase list!!')
                    xlims = [float(elem) for elem in self.view.xlim.get().split(',')]
            
            if len(self.view.model.get()) == 0:
                model = None
            else:
                model = self.view.model.get()
            if len(self.view.phase_list.get()) == 0:
                phase_list = []
            else:
                phase_list = self.view.phase_list.get().split(',')
            
            inv_selection = self.model.get_selected_inv()
            cat = self.model.wavefield_database.database[self.view.selection_listbox.get(0)]['cat']
            
            plotter.Plot(times, streams, inv_selection, cat, model, phase_list, 
                                    self.view.difference_checkbox_state.get(), xlims)

    def on_press_plot_elements_button(self):
        # Check if there is any database selected for plotting 
        try:
            self.model.elements_database.selected_database
        except:
            tk.messagebox.showerror("Error", "The selected database is empty!")
            
        if len(self.model.elements_database.database) == 0:
                tk.messagebox.showerror("Error", "The selected database is empty!")
        else:
            
            ERROR_FOUND = False
            
            if len(self.view.station_depth.get()) == 0:
                tk.messagebox.showerror("Error", "Please enter at least one depth, or a list of depths separated by commas")
                ERROR_FOUND = True
            elif len(self.view.station_latitude.get()) == 0:
                tk.messagebox.showerror("Error", "Please enter at least one latitude, or a list of latitudes separated by commas")
                ERROR_FOUND = True
            elif len(self.view.station_longitude.get()) == 0:
                tk.messagebox.showerror("Error", "Please enter at least one longitude, or a list of longitudes separated by commas")
                ERROR_FOUND = True
            if ERROR_FOUND is False:
                
                depths = [float(depth) for depth in self.view.station_depth.get().split(',')]
                latitudes = [float(latitude) for latitude in self.view.station_latitude.get().split(',')]
                longitudes = [float(longitude) for longitude in self.view.station_longitude.get().split(',')]
                
                # get the data
                times, streams, inv = self.model.get_elements_times_and_streams(depths, latitudes, longitudes)
                
                if len(self.view.elements_model.get()) == 0:
                    model = None
                else:
                    model = self.view.elements_model.get()
                if len(self.view.elements_phase_list.get()) == 0:
                    phase_list = []
                else:
                    phase_list = self.view.phase_list.get().split(',')
                
                # I'm assuming all events are the same !!!!!!!!!!!!!!!!!!!!
                cat = self.model.elements_database.database[self.view.selected_elements_listbox.get(0)]['cat']
                
                plotter.Plot(times, streams, inv, cat, model, phase_list, 
                             plot_diff=False, xlims=None)
            
    def on_press_plot_stations_button(self):
        
        try:
            self.model.wavefield_database.selected_database
        except:
            tk.messagebox.showerror("Error", "The selected database is empty!")
            
        if len(self.model.wavefield_database.database) == 0:
                tk.messagebox.showerror("Error", "The selected database is empty!")
        
        inv_selection = self.model.get_selected_inv()
        inv_selection.plot(size=50, marker='*', show=True)


    def on_press_plot_traveltimes_button(self):
        if len(self.view.phase_list.get()) != 0:
            phase_list = self.view.phase_list.get().split(',')
        else:
            tk.messagebox.showerror("Error", "Please enter phases")
        try:
            evt_depth = float(self.view.event_depth.get())
            earth_model = self.view.model.get()
            plot_travel_times(source_depth=evt_depth, phase_list=phase_list, model=earth_model)
        except:
            tk.messagebox.showerror("Error", "Please enter the depth")
        
        
    def on_press_plot_earth_button(self):
        try:
            self.model.wavefield_database.selected_database
        except:
            tk.messagebox.showerror("Error", "The selected database is empty!")
            
        if len(self.model.wavefield_database.database) == 0:
                tk.messagebox.showerror("Error", "The selected database is empty!")
                
        if len(self.view.phase_list.get()) != 0:
            phase_list = self.view.phase_list.get().split(',')
        else:
            tk.messagebox.showerror("Error", "Please enter phases")
        
        try:
            file = self.view.CMB_txt_file.get()
        except:
            tk.messagebox.showerror("Error", "Please enter the path to a CMB topography txt file")

        cat = self.model.wavefield_database.database[self.view.selection_listbox.get(0)]['cat']
        inv_selection = self.model.get_selected_inv()
        earth_model = self.view.model.get()
        
        plotter.Plot_3D_Earth(phase_list, earth_model, inv_selection, cat, file)


    def on_press_elements_output_button(self):
        self.view._create_elements_output_window()
        
    def on_press_load_elements_output(self):
        if len(self.view.elements_path.get()) == 0:
            tk.messagebox.showerror("Error", 'The path to the elements dir is empty!')
        else:
            # Check if the elements_database is empty
            if self.model.elements_database is None:
                # If empty, create elements database and add the first entry
                self.model.create_elements_database()
                self.model.load_elements(self.view.elements_path.get())
                elements_name = self.view.elements_path.get().split('/')[-1]
                self.view.elements_listbox_index += 1
                self.view.elements_listbox.insert(self.view.elements_listbox_index, elements_name)
                self.view.elements_path_entry.delete(0, 'end')
            else:
                elements_name = self.view.elements_path.get().split('/')[-1]
                ENTRY_EXISTS = False
                for _, listbox_entry in enumerate(self.view.elements_listbox.get(0, tk.END)):
                    if listbox_entry == elements_name:
                        ENTRY_EXISTS = True
                if ENTRY_EXISTS is True:
                    tk.meesagebox.showerror("Error", "The database entry already exists!")
                else:
                    self.model.load_elements(self.view.elements_path.get())
                    self.view.elements_listbox_index += 1
                    self.view.elements_listbox.insert(self.view.elements_listbox_index, elements_name)
                    self.view.elements_path_entry.delete(0, 'end')
                    

    def on_press_select_elements_wavefield(self):
        for i in self.view.elements_listbox.curselection():
            SELECTION_EXISTS = False
            for _, listbox_entry in enumerate(self.view.selected_elements_listbox.get(0, tk.END)):
                if listbox_entry == self.view.elements_listbox.get(i):
                    SELECTION_EXISTS = True
            if SELECTION_EXISTS is True:
                tk.messagebox.showerror("Error", "The database entry is already selected!")
            else:
                self.view.selected_elements_listbox_index += 1
                self.view.selected_elements_listbox.insert(self.view.selected_elements_listbox_index, 
                                                           self.view.elements_listbox.get(i))
                self.model.add_elements_selection(self.view.elements_listbox.get(i))


    def on_press_deselect_elements_wavefield(self):
        if len(self.view.selected_elements_listbox.curselection()) == 0:
            tk.messagebox.showerror("Error", "Select a database to be deselected!")
        else:
            for i in self.view.selected_elements_listbox.curselection():
                self.model.remove_elements_selection(self.view.selected_elements_listbox.get(i))
                self.view.selected_elements_listbox.delete(i)
    
    
    def on_press_delete_elements_wavefield(self):
        if len(self.view.elements_listbox.curselection()) == 0:
            tk.messagebox.showerror("Error", "Select a database to be deleted!")
        else:
            for i in self.view.elements_listbox.curselection():
                self.model.elements_database.delete_from_database(self.view.elements_listbox.get(i))
                
                for j, selected_listbox_entry in enumerate(self.view.selected_elements_listbox.get(0, tk.END)):
                    if selected_listbox_entry == self.view.elements_listbox.get(i):
                        self.view.selected_elements_listbox.delete(j)
                
                self.view.elements_listbox.delete(i)
                
                
if __name__ == '__main__':
    calculator = Controller()
    calculator.main()