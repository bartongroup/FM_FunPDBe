# -*- coding: utf-8 -*-

"""
# NOD cli donwloaded from: http://www.compbio.dundee.ac.uk/www-nod/downloads.jsp
# Running instructions: http://www.compbio.dundee.ac.uk/www-nod/cli_help.jsp

# java -jar clinod-1.3.jar -in=test2.fasta -out=test2.nod -f=COMPLETE


# 14-3-3-Pred downloaded from: https://github.com/bartongroup/FM_14-3-3/www1433/app

# python2.7 prediction.py -i ./test.fasta -o ./

"""

import os
import sys
import click
import logging
import textwrap
import click_log
from Bio import SeqIO
from subprocess import Popen

nod_jar = os.path.join('lib', 'NOD', 'clinod-1.3.jar')
# nod_jar = '/homes/fmmarquesmadeira/clinod-1.3.jar'
pred1433_python = os.path.join('lib', '1433pred', 'prediction.py')


# main application
@click_log.simple_verbosity_option(default="INFO")
@click.group(chain=True,
             context_settings={'help_option_names': ['-h', '--help']})
def main():
    """Main interface to the available pySTAMP sub-commands and options."""


@main.command('nod')
@click.option('-l', '--log', default=sys.stderr,
              help="Path to the logfile.",
              type=click.File('wb'))
@click.argument('input',
                type=click.File('r'), required=True)
# @click.argument('output',
#                 type=click.File('w'), required=False)
@click_log.simple_verbosity_option(default="INFO")
def nod(input, log):
    logging.basicConfig(stream=log,
                        format='%(asctime)s - %(levelname)s - %(message)s ')

    # process input
    seqs = SeqIO.parse(input, "fasta")
    for i, record in enumerate(seqs):
        seq = record.seq
        pid = record.id
        print(i + 1, pid)

        # write a sequence per file
        input_seq = os.path.join(os.path.dirname(__file__),
                                 'data', 'input', '{}.fasta'.format(pid))
        output_nod = os.path.join(os.path.dirname(__file__),
                                  'data', 'output', 'NOD', '{}.nod'.format(pid))

        if not os.path.exists(input_seq):
            output = open(input_seq, 'w')
            seq = '\n'.join(textwrap.wrap(str(seq), width=60))
            output.write(">{}\n{}\n".format(pid, seq))
            output.close()

        cmd = ['java', '-jar', nod_jar,
               '-in={}'.format(input_seq),
               "-out={}".format(output_nod),
               '-f=COMPLETE']
        Popen(cmd)


@main.command('pred1433')
@click.option('-l', '--log', default=sys.stderr,
              help="Path to the logfile.",
              type=click.File('wb'))
@click.argument('input',
                type=click.File('r'), required=True)
# @click.argument('output',
#                 type=click.File('w'), required=False)
@click_log.simple_verbosity_option(default="INFO")
def pred1433(input, log):
    logging.basicConfig(stream=log,
                        format='%(asctime)s - %(levelname)s - %(message)s ')

    # process input
    seqs = SeqIO.parse(input, "fasta")
    for i, record in enumerate(seqs):
        seq = record.seq
        pid = record.id
        print(i + 1, pid)

        # write a sequence per file
        input_seq = os.path.join(os.path.dirname(__file__),
                                 'data', 'input', '{}.fasta'.format(pid))
        output_1433pred = os.path.join(os.path.dirname(__file__),
                                       'data', 'output', '1433pred')

        if not os.path.exists(input_seq):
            output = open(input_seq, 'w')
            seq = '\n'.join(textwrap.wrap(str(seq), width=60))
            output.write(">{}\n{}\n".format(pid, seq))
            output.close()

        cmd = ['python2.7', pred1433_python,
               "-i", input_seq, "-o", output_1433pred]
        # Popen(cmd)
        os.system(' '.join(cmd))


if __name__ == "__main__":
    main()
