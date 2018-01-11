from ftplib import FTP
from rnaseq.utils import config
from rnaseq.utils import database
import os
import species
# from . import species
import re
import sys
import subprocess


HOST_DICT = {
    'animal': 'ftp.ensembl.org',
    'plant': 'ftp.ensemblgenomes.org'}


def save_mkdir(path):
    if not os.path.isdir(path):
        os.makedirs(path)


def save_link(path, dest):
    path = os.path.abspath(path)
    dest_path = os.path.dirname(dest)
    if not os.path.isdir(dest_path):
        sys.exit('destination directory [{d}] not exists.'.format(d=dest_path))
    if os.path.isfile(path):
        try:
            os.symlink(path, dest)
        except OSError:
            print 'destination file exists.'
    else:
        sys.exit('file [{d}] not exists.'.format(d=path))


class PrepareDatabase(object):

    def __init__(self, species, version='current', force=False):
        self.species = species
        self.version = version
        self.force = force
        self.download_fa = True
        self.release = ''
        self.g_version = ''
        self.ftp_genome_dir = ''

    def _prepare(self):
        _species = ' '.join(self.species.split('_'))
        my_sp_inf = species.Species(_species)
        self.kingdom = my_sp_inf.kingdom
        self.host = HOST_DICT[self.kingdom]
        # get database version
        ftp = FTP(self.host)
        ftp.login()
        self.ftp_genome_dir = '/pub/{v}_fasta/{s}/dna'.format(
            s=self.species, v=self.version)
        if self.version == 'current':
            ftp.cwd('/pub/current_fasta/')
            self.release = ftp.pwd().split('/')[-2]
        else:
            self.release = self.version
        self.database_detail = database.sepcies_annotation_path(
            'ensembl', self.species, self.release)
        self.database_detail.get_anno_inf()
        ftp.quit()

    def _get_genome_version(self):
        ftp = FTP(self.host)
        ftp.login()
        ftp.cwd(self.ftp_genome_dir)
        fa_list = ftp.nlst()
        for each_fa in fa_list:
            if 'dna.toplevel.fa.gz' in each_fa:
                genome_fa = each_fa
        g_pattern = re.compile('{s}.(\S+).dna.toplevel.fa.gz'.format(
            s=self.species.capitalize()
        ))
        g_version = g_pattern.match(genome_fa).groups()[0]
        ftp.quit()
        return genome_fa, g_version

    def _download_ensembl(self, f_path, f_name, f_out):
        ftp = FTP(self.host)
        ftp.login()
        ftp.cwd(f_path)
        with open(f_out, 'w') as f_out_inf:
            ftp.retrbinary('RETR %s' % f_name, f_out_inf.write)
        ftp.quit()

    def _decompression(self, f_path):
        cmd = 'gunzip -c {f}.gz > {f}'.format(f=f_path)
        cmd_log = subprocess.Popen(cmd, shell=True)
        os.waitpid(cmd_log.pid, 0)
        return cmd_log.stderr

    def download(self):
        self._prepare()
        genome_fa, self.g_version = self._get_genome_version()
        if not os.path.exists(self.database_detail.genome_fa):
            genome_fa, self.g_version = self._get_genome_version()
            self.genome_dir = os.path.join(
                config.database['genome'], 'ensembl', self.kingdom,
                self.species, 'genome', self.g_version)
            genome_path = os.path.join(
                self.genome_dir, genome_fa.rstrip('.gz'))
            if not os.path.exists(genome_path):
                save_mkdir(self.genome_dir)
                self._download_ensembl(
                    self.ftp_genome_dir, genome_fa,
                    '{g}.gz'.format(g=genome_path))
                self._decompression(genome_path)
                save_link(genome_path, self.database_detail.genome_fa)
        if not os.path.exists(self.database_detail.gtf):
            self.database_dir = os.path.dirname(self.database_detail.gtf)
            save_mkdir(self.database_dir)
            ftp_gtf_dir = '/pub/{v}_gtf/{s}/'.format(
                s=self.species, v=self.version)
            gtf_file = '{s}.{g}.{d}.gtf.gz'.format(
                s=self.species.capitalize(), g=self.g_version,
                d=self.release.split('-')[-1])
            download_gtf = os.path.join(self.database_dir, gtf_file)
            self._download_ensembl(ftp_gtf_dir, gtf_file, download_gtf)
            self._decompression(download_gtf.rstrip('.gz'))
            save_link(download_gtf.rstrip('.gz'), self.database_detail.gtf)
