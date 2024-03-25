import click
from rdflib import Graph

@click.command()
@click.argument('owl_file', type=click.Path(exists=True))
@click.argument('output_dir', type=click.Path())
def run(owl_file, output_dir):
    g = Graph().parse(owl_file, format='xml')

    extension = str(owl_file).split('.')[-1]
    file_name = str(owl_file).replace('.' + extension, '')

    g.serialize(file_name + '.nt', format='nt')
    #g.serialize(file_name + '.rdf', format='xml')
    #g.serialize(file_name + '.n3', format='n3')
    #g.serialize(file_name + '.jsonld', format='json-ld')


if __name__ == '__main__':
    run()
