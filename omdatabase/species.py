import json
import os


script_path = os.path.dirname(os.path.realpath(__file__))
NAME_ORDER = ['scientific name', 'authority',
              'genbank common name', 'common name']


def load_json(method):
    def wrapper(*args):
        json_file = args[0]
        if not os.path.exists(json_file):
            my_dict = method(*args)
            with open(json_file, 'w') as json_file_inf:
                json.dump(my_dict, json_file_inf)
            return my_dict
        else:
            with open(json_file) as json_inf:
                out_dict = json.load(json_inf)
                return out_dict
    return wrapper


class Species(object):

    def __init__(self, search_id):
        self.search_id = search_id
        self.tax_dir = os.path.join(script_path, 'taxdump')
        self.name2gi = dict()
        self.gi2div = dict()

    def _get_species_inf(self):
        name2gi_json = os.path.join(self.tax_dir, 'name2gi.json')
        name_inf_file = os.path.join(self.tax_dir, 'names.dmp')
        gi2div_json = os.path.join(self.tax_dir, 'gi2div.json')
        gi2div_file = os.path.join(self.tax_dir, 'nodes.dmp')

        @load_json
        def get_div_inf(gi2div_json, gi2div_file):
            my_dict = {}
            with open(gi2div_file) as gi2div_inf:
                for eachline in gi2div_inf:
                    eachline_inf = eachline.strip().split('|')
                    gi = eachline_inf[0].strip()
                    sp = eachline_inf[2].strip().lower()
                    div = eachline_inf[4].strip()
                    if sp == 'species':
                        my_dict[gi] = div
            return my_dict
        self.gi2div = get_div_inf(gi2div_json, gi2div_file)

        @load_json
        def get_name_inf(name2gi_json, name_inf_file):
            my_dict = {}
            with open(name_inf_file) as name_inf:
                for eachline in name_inf:
                    eachline_inf = eachline.strip().split('|')
                    gi = eachline_inf[0].strip()
                    name = eachline_inf[1].strip().lower()
                    name_class = eachline_inf[3].strip()
                    if gi in self.gi2div:
                        my_dict.setdefault(name, {})[name_class] = gi
                return my_dict

        self.name2gi = get_name_inf(name2gi_json, name_inf_file)

    def kingdom(self):
        if not self.name2gi or not self.gi2div:
            self._get_species_inf()
        if self.search_id in self.name2gi:
            for each_name in NAME_ORDER:
                if each_name in self.name2gi[self.search_id]:
                    gi = self.name2gi[self.search_id][each_name]
                    if self.gi2div[gi] == '4':
                        return 'plant'
                    else:
                        return 'animal'
        else:
            return 'unknown'
