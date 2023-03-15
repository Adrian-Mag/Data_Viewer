import os, glob

class Wavefield_database:

    def __init__(self):
        self.database = {}
        self.selected_database = []

    def add_to_database(self, name, stream, cat, inv, data_type):        
        self.database[name] = {'stream': stream, 'cat': cat, 'inv': inv, 'type': data_type}
        
    def add_to_selected_database(self, name):
        self.selected_database.append(name)
        
    def remove_from_selected_database(self, name):
        self.selected_database.remove(name)
        
    def delete_from_database(self, name):
        if name in self.selected_database:
            self.remove_from_selected_database(name)
        self.database.pop(name)
