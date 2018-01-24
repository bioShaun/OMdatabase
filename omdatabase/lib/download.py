import os
import sys
from ftplib import FTP
import subprocess
from omdatabase.utils import config
import envoy


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


def download_ftp(host, f_path, f_out):
    ftp = FTP(host)
    ftp.login()
    with open(f_out, 'wb') as f_out_inf:
        ftp.retrbinary('RETR %s' % f_path, f_out_inf.write)
    ftp.quit()


def decompression(gz_file, out_file):
    cmd = 'gunzip -c {gz} > {ungz}'.format(gz=gz_file,
                                           ungz=out_file)
    r = subprocess.Popen(cmd, shell=True)
    r.communicate()
    return r.stderr


class DownloadDB(object):

    def __init__(self, db, path):
        self.db = db
        self.path = path
        self.download_genome = True
        self.download_gtf = True
        self.download_go = True
        self.download_kegg = True

    def _check_db(self):
        if os.path.isfile(self.path.genome_fa):
            self.download_genome = False
        else:
            save_mkdir(self.path.genome_dir)
        if os.path.isfile(self.path.genome_gtf):
            self.download_gtf = False
        else:
            save_mkdir(self.path.anno_dir)
        if os.path.isfile(self.path.go):
            self.download_go = False
        if os.path.isfile(self.path.kegg_blast):
            self.download_kegg = False

    def _download_gtf(self):
        if self.download_gtf:
            gtf_download = os.path.join(self.path.anno_dir,
                                        os.path.basename(self.db.gtf_url))
            download_ftp(self.db.host,
                         self.db.gtf_url,
                         gtf_download)
            decompression(gtf_download, self.path.genome_gtf)
        else:
            print 'gtf file exists!'

    def _download_genome(self):
        if self.download_genome:
            genome_download = os.path.join(
                self.path.genome_dir,
                os.path.basename(self.db.genome_url))
            ungz_genome = genome_download.rstrip('.gz')
            if os.path.isfile(ungz_genome):
                save_link(ungz_genome, self.path.genome_fa)
            else:
                download_ftp(self.db.host,
                             self.db.genome_url,
                             genome_download)
                decompression(genome_download, ungz_genome)
                save_link(ungz_genome, self.path.genome_fa)
        else:
            print 'genome fasta file exists!'

    def _get_script(self):
        for each_script in config.SCRIPT:
            each_script_path = os.path.join(
                config.config_path,
                'support_scripts',
                config.SCRIPT[each_script])
            self.__setattr__(each_script, each_script_path)

    def _download_go(self):
        self._get_script()
        if self.download_go:
            download_cmd = config.CMD['download_go'].format(t=self)
            r = envoy.run(download_cmd)
            return r.std_err
        else:
            print 'go file exists!'

    def _download_kegg(self):
        self._get_script()
        if self.download_kegg:
            download_cmd = config.CMD['download_kegg'].format(t=self)
            print download_cmd
            r = envoy.run(download_cmd)
            return r.std_err
        else:
            print 'kegg file exists!'

    @property
    def download(self):
        self._check_db()
        self._download_gtf()
        self._download_genome()
        self._download_go()
        self._download_kegg()
