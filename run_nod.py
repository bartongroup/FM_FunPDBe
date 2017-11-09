# -*- coding: utf-8 -*-

"""
# NOD cli downlaoded from: http://www.compbio.dundee.ac.uk/www-nod/downloads.jsp
# Running instructions: http://www.compbio.dundee.ac.uk/www-nod/cli_help.jsp

# java -jar clinod-1.3.jar -in=test2.fasta -out=test2.nod -f=COMPLETE

"""

import os
import sys
import click
import logging
import click_log
from Bio import SeqIO
from subprocess import Popen

nod_jar = "/homes/fmmarquesmadeira/clinod-1.3.jar"


@click.command(context_settings={'help_option_names': ['-h', '--help']})
@click.option('-l', '--log', default=sys.stderr,
              help="Path to the logfile.",
              type=click.File('wb'))
@click.argument('input',
                type=click.File('r'), required=True)
# @click.argument('output',
#                 type=click.File('w'), required=False)
@click_log.simple_verbosity_option(default="INFO")
def main(input, log):

    logging.basicConfig(stream=log,
                        format='%(asctime)s - %(levelname)s - %(message)s ')

    # process input
    seqs = SeqIO.parse(input, "fasta")
    for i, record in enumerate(seqs):
        seq = record.seq
        pid = record.id
        print(i, pid)

        # write a sequence per file
        input_seq = os.path.join(os.path.dirname(__file__),
                                 'data', 'input', '{}.fasta'.format(pid))
        output_nod = os.path.join(os.path.dirname(__file__),
                                  'data', 'output', 'NOD', '{}.nod'.format(pid))

        if not os.path.exists(input_seq):
            output = open(input_seq, 'w')
            output.write(">{}\n{}\n".format(pid, seq))
            output.close()

        cmd = ['java', '-jar', nod_jar,
               '-in={}'.format(input_seq),
               "-out={}".format(output_nod),
               '-f=COMPLETE']
        Popen(cmd)


if __name__ == "__main__":
    main()

