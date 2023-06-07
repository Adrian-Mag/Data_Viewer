# Libraries
import obspy 
# In house files
from AxiSEM3D_Data_Handler.element_output import element_output

class ElementsDatabase():
    
    def __init__(self):
        self.database = {}
        self.selected_database = []


    def add_to_database(self, elements_path: str, name: str, 
                        element_object: element_output, 
                        cat: obspy.Catalog):
        self.database[name] = {'element_object': element_object, 'cat': cat,
                               'elements_path': elements_path}


    def add_to_selected_database(self, name):
        self.selected_database.append(name)


    def remove_from_selected_database(self, name):
        self.selected_database.remove(name)


    def remove_from_database(self, name):
        if name in self.selected_database:
            self.remove_from_selected_database(name)
        self.database.pop(name)