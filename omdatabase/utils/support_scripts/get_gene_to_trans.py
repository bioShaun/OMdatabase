'''
get gene-transcript map from gtf file or gff3 file

'''

import os
from HTSeq import GFF_Reader
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--gff', help='assembled GTF file or gff', required=True)
parser.add_argument('--out_dir', help='Output directory.', required=True)
parser.add_argument('--name', help='Output file prefix.', required=True)
args = parser.parse_args()

gene_trans_map_file = os.path.join(
    args.out_dir, '{n}.gene_trans_map.txt'.format(n=args.name))
gene_trans_map_file_info = open(gene_trans_map_file, 'w')
tr_dict = {}

if args.gff.endswith('gff') or args.gff.endswith('gff3'):
    for eachline in GFF_Reader(args.gff):
        if eachline.type == "transcript":
            transcript_id = eachline.attr['ID']
            gene_id = eachline.attr['Parent']
            gene_trans_map_file_info.write('%s\t%s\n' % (gene_id,
                                                         transcript_id))
    gene_trans_map_file_info.close()
elif args.gff.endswith('gtf'):
    for eachline in GFF_Reader(args.gff):
        if 'transcript_id' not in eachline.attr:
            continue
        transcript_id = eachline.attr['transcript_id']
        gene_id = eachline.attr['gene_id']
        if 'ref_gene_id' in eachline.attr:
            gene_id = eachline.attr['ref_gene_id']
        if transcript_id not in tr_dict:
            tr_dict[transcript_id] = gene_id
            gene_trans_map_file_info.write('%s\t%s\n' % (gene_id,
                                                         transcript_id))
    gene_trans_map_file_info.close()
