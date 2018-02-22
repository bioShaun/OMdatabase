import click
import pandas as pd


def get_unique(obj):
    str_obj = list()
    for each in obj:
        if not pd.isna(each):
            each = str(each)
            if each not in str_obj:
                str_obj.append(each)
    uniq_out = '|'.join(str_obj) if str_obj else '--'
    return uniq_out


@click.command()
@click.option(
    '-b',
    '--biomart_download',
    help='downloaded description file.',
    type=click.Path(dir_okay=False),
    required=True,
)
@click.option(
    '-n',
    '--name_map',
    help='interpro name map file.',
    type=click.Path(dir_okay=False),
    required=True,
)
@click.option(
    '-o',
    '--output',
    help='output file.',
    type=click.Path(dir_okay=False),
    required=True,
)
def main(biomart_download, name_map, output):
    download_df = pd.read_csv(biomart_download)
    des_df = pd.read_table(name_map, header=None)
    des_df.columns = ['interpro', 'description']
    merged_df = pd.merge(download_df, des_df,
                         left_on='interpro', right_on='interpro',
                         how='left')
    grouped_dl = merged_df.groupby('ensembl_gene_id')
    grouped_df = grouped_dl.aggregate(get_unique)
    grouped_df.to_csv(output, sep='\t')


if __name__ == '__main__':
    main()
