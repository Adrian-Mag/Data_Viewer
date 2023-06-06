import obspy 


class WavefieldDatabase:
    """A class for the database. This class is instanciated 
    when the first database entry is loaded into the program.
    The database is at its core a dictionary. The key of each 
    dictionary is the name of the directory containing the wave
    data. 
    
    The second attribute of this class is "selected_database" 
    which is a list containing the names (keys) of the currently
    selected database entries.
    """    
    def __init__(self):
        self.database = {}
        self.selected_database = []

    def add_to_database(self, name: str, stream: obspy.Stream,  
                        cat: obspy.Catalog, inv: obspy.Inventory, 
                        data_type: str):        
        self.database[name] = {'stream': stream, 'cat': cat, 
                               'inv': inv, 'type': data_type}
        
    def add_to_selected_database(self, name):
        self.selected_database.append(name)
        
    def remove_from_selected_database(self, name):
        self.selected_database.remove(name)
        
    def remove_from_database(self, name):
        if name in self.selected_database:
            self.remove_from_selected_database(name)
        self.database.pop(name)
