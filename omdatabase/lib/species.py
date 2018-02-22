import json
import os
import ujson
from omdatabase.utils import config


script_path = os.path.dirname(os.path.realpath(__file__))
NAME_ORDER = ['scientific name', 'authority',
              'genbank common name', 'common name']


def load_json(method):
    def wrapper(*args):
        json_file = args[0]
        data_file = args[1]
        if not os.path.exists(json_file):
            my_dict = dict()
            with open(data_file) as data_inf:
                for eachline in data_inf:
                    my_dict.update(method(json_file, data_file, eachline))
            with open(json_file, 'w') as json_file_inf:
                json.dump(my_dict, json_file_inf)
            return my_dict
        else:
            with open(json_file) as json_inf:
                out_dict = json.load(json_inf)
                return out_dict
    return wrapper


class Species(object):
    '''Get animal kingdom by latin name
    TODO: accelerate, too slow
    '''
    def __init__(self, search_id):
        self.search_id = search_id
        self.tax_dir = os.path.join(script_path, 'taxdump')
        self.name2gi = dict()
        self.gi2div = dict()
        self.fungi_dict = dict()
        self.name2kingdom = dict()

    def _get_species_inf(self):
        name2gi_json = os.path.join(self.tax_dir, 'name2gi.json')
        name_inf_file = os.path.join(self.tax_dir, 'names.dmp')
        gi2div_json = os.path.join(self.tax_dir, 'gi2div.json')
        gi2div_file = os.path.join(self.tax_dir, 'nodes.dmp')
        fungi_json = os.path.join(self.tax_dir, 'species_metadata_EnsemblFungi.json')

        with open(fungi_json) as fg_inf:
            self.fungi_dict = json.load(fg_inf)

        @load_json
        def get_div_inf(*args):
            my_dict = dict()
            eachline = args[-1]
            eachline_inf = eachline.strip().split('|')
            gi = eachline_inf[0].strip()
            sp = eachline_inf[2].strip().lower()
            div = eachline_inf[4].strip()
            if sp == 'species':
                my_dict[gi] = div
            return my_dict
        self.gi2div = get_div_inf(gi2div_json, gi2div_file)

        @load_json
        def get_name_inf(*args):
            my_dict = dict()
            eachline = args[-1]
            eachline_inf = eachline.strip().split('|')
            gi = eachline_inf[0].strip()
            name = eachline_inf[1].strip().lower()
            name_class = eachline_inf[3].strip()
            if gi in self.gi2div:
                my_dict.setdefault(name, {})[name_class] = gi
            return my_dict

        self.name2gi = get_name_inf(name2gi_json, name_inf_file)

    def _sp_to_kingdom(self):
        # name2kingdom_file = os.path.join(self.tax_dir, 'name2kingdom.json')
        # name2kingdom_file = os.path.join(self.tax_dir, 'name2kingdom.pickle')
        name2kingdom_file = os.path.join(self.tax_dir, 'name2kingdom.ujson')
        if not os.path.exists(name2kingdom_file):
            self._get_species_inf()
            for each_name in self.name2gi:
                outname = '_'.join(each_name.split())
                for each_cat in self.name2gi[each_name]:
                    gi = self.name2gi[each_name][each_cat]
                    if self.gi2div[gi] == '4':
                        if outname in self.fungi_dict[0]['compara'][0]['genomes']:
                            kingdom = 'fungi'
                        else:
                            kingdom = 'plant'
                    else:
                        kingdom = 'animal'
                    self.name2kingdom[outname] = kingdom
            with open(name2kingdom_file, 'wb') as kingdom_inf:
                ujson.dump(self.name2kingdom, kingdom_inf)
        else:
            with open(name2kingdom_file) as kingdom_inf:
                self.name2kingdom = ujson.load(kingdom_inf)

    @property
    def kingdom(self):
        if self.search_id in config.kingdom_saved:
            return config.kingdom_saved[self.search_id]
        self._sp_to_kingdom()
        if self.search_id in self.name2kingdom:
            kingdom = self.name2kingdom[self.search_id]
        else:
            kingdom = 'unknown'
        config.update_sp(self.search_id, kingdom)
        return kingdom
