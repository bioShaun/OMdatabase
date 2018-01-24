import yaml
import os


def load_yaml(yaml_file):
    if os.path.isfile(yaml_file):
        with open(yaml_file) as yaml_inf:
            yaml_obj = yaml.load(yaml_inf)
    else:
        yaml_obj = dict()
    return yaml_obj


config_path = os.path.dirname(os.path.realpath(__file__))

# read config
module_path = os.path.join(config_path, 'config_defaults.yaml')
with open(module_path) as f:
    configs = yaml.load(f)
    for c, v in configs.items():
        globals()[c] = v

# read sp -> kegg config
kegg_config_path = os.path.join(config_path, 'organism.yaml')
with open(kegg_config_path) as kegg_inf:
    kegg_map = yaml.load(kegg_inf)

# read saved database information
database_cfg_path = os.path.join(config_path, 'database.yaml')
db_saved = load_yaml(database_cfg_path)

# read saved kingdom information
kingdom_cfg_path = os.path.join(config_path, 'kingdom.yaml')
kingdom_saved = load_yaml(kingdom_cfg_path)


def update_db(db_obj):
    db_release = '{t.database}-{t.release}'.format(t=db_obj)
    if (db_obj.species in db_saved and db_release in db_saved[db_obj.species]):
        pass
    else:
        db_saved.setdefault(db_obj.species, {})[db_release] = [
            db_obj.genome_version, db_obj.genome_url, db_obj.gtf_url
        ]
        with open(database_cfg_path, 'w') as db_inf:
            yaml.dump(db_saved, db_inf)


def update_sp(sp, kingdom):
    if sp not in kingdom_saved:
        kingdom_saved[sp] = kingdom
        with open(kingdom_cfg_path, 'w') as kd_inf:
            yaml.dump(kingdom_saved, kd_inf)
