from __future__ import print_function
import envoy
import os
from omdatabase.utils import config


def write_obj_to_file(obj, fn, append=False):
    fh = open(fn, 'a' if append is True else 'w')
    if type(obj) is str:
        fh.write('%s\n' % obj)
    elif type(obj) is list:
        for item in obj:
            fh.write('%s\n' % item)
    elif type(obj) is dict:
        for key, val in obj.iteritems():
            fh.write('%s\t%s\n' % (key, val))
    else:
        raise TypeError('invalid type for %s' % obj)
    fh.close()


class BuildIndex(object):
    '''A class to build index for different analysis
    '''
    def __init__(self, db, path,
                 analysis='rnaseq'):
        self.db = db
        self.path = path
        self.analysis = analysis

    def _get_script(self):
        for each_script in config.SCRIPT:
            each_script_path = os.path.join(
                config.config_path,
                'support_scripts',
                config.SCRIPT[each_script])
            self.__setattr__(each_script, each_script_path)

    @property
    def build(self):
        self._get_script()
        prepare_script = os.path.join(self.path.anno_dir,
                                      'prepare_db.sh')
        analysis_list = config.ANALYSIS[self.analysis]
        cmd_list = list()
        for each_analysis in analysis_list:
            analysis_stat_file = os.path.join(
                self.path.anno_dir, '{a}.finished'.format(
                    a=each_analysis))
            if os.path.exists(analysis_stat_file):
                print('{a} preparation finished!'.format(a=each_analysis))
                continue
            each_cmd = config.CMD[each_analysis].format(t=self)
            each_cmd_list = each_cmd.split('|')
            cmd_list.extend(each_cmd_list)
        write_obj_to_file(cmd_list,
                          prepare_script)
            # envoy.run(each_cmd)
            # print(each_cmd)
