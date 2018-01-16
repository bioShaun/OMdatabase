import envoy
from omdatabase.utils import config


class BuildIndex(object):
    '''A class to build index for different analysis
    '''
    def __init__(self, db, path,
                 analysis='rnaseq'):
        self.db = db
        self.path = path
        self.analysis = analysis

    @property
    def build(self):
        analysis_list = config.ANALYSIS[self.analysis]
        for each_analysis in analysis_list:
            each_cmd = config.CMD[each_analysis].format(t=self)
            envoy.run(each_cmd)
            # print each_cmd
