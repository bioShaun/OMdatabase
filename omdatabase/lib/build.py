from __future__ import print_function
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
                 analysis='rnaseq',
                 launch='local',
                 cpu=8):
        self.db = db
        self.path = path
        self.analysis = analysis
        self.launch = launch
        self.script = None
        self.cpu = cpu

    def _get_script(self):
        for each_script in config.SCRIPT:
            each_script_path = os.path.join(
                config.config_path,
                'support_scripts',
                config.SCRIPT[each_script])
            self.__setattr__(each_script, each_script_path)

    def _launch_job(self):
        if self.launch == 'local':
            launch_cmd = 'nohuprun.sh {t.script}'.format(t=self)
        elif self.launch == 'slurm':
            launch_cmd = 'omsrunone.sh {t.script} {t.cpu}'.format(t=self)
        os.system(launch_cmd)

    @property
    def build(self):
        self._get_script()
        self.script = os.path.join(self.path.anno_dir,
                                   'prepare_db.sh')
        analysis_list = config.ANALYSIS[self.analysis]
        cmd_list = ['#!/bin/bash']
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
        write_obj_to_file(cmd_list, self.script)
        self._launch_job()
