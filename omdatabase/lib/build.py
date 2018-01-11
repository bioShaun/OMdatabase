import species
from omdatabase.utils import config
import os
import envoy


class BuildIndex(object):
    '''A class to build index for different analysis
    '''
    def __init__(self,
                 species,
                 database='ensembl',
                 version='current',
                 genome='',
                 gtf='',
                 analysis='rnaseq'):
        self.species = species
        self.database = database
        self.version = version
        self.genome = genome
        self.gtf = gtf
        self.path = None
        self.analysis = analysis

    def _get_path(self):
        query_id = ' '.join(self.species.split('_'))
        sp_obj = species.Species(query_id)
        kingdom = sp_obj.kingdom
        self.path = os.path.join(config.BASE_DIR,
                                 self.database,
                                 kingdom, self.species,
                                 'annotation', self.version)
        self.genome = os.path.join(self.path,
                                   '{t.species}.genome.fa'.format(t=self))
        self.gtf = os.path.join(self.path,
                                '{t.species}.genome.gtf'.format(t=self))

    def build(self):
        self._get_path()
        analysis_list = config.ANALYSIS[self.analysis]
        for each_analysis in analysis_list:
            each_cmd = config.CMD['bowtie'].format(t=self)
            envoy.run(each_cmd)
            # print each_cmd

