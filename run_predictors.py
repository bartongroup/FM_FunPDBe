# -*- coding: utf-8 -*-

"""
# NOD cli downloaded from: http://www.compbio.dundee.ac.uk/www-nod/downloads.jsp
# Running instructions: http://www.compbio.dundee.ac.uk/www-nod/cli_help.jsp
# java -jar clinod-1.3.jar -in=test2.fasta -out=test2.nod -f=COMPLETE


# 14-3-3-Pred downloaded from: https://github.com/bartongroup/FM_14-3-3/www1433/app
# python2.7 prediction.py -i ./test.fasta -o ./


# Jpred downloaded from: http://www.compbio.dundee.ac.uk/jpred/api.shtml#download
# perl jpredapi submit mode=single format=fasta email=funpdbe@dundee.ac.uk file=test.fasta name=test

"""

import os
import sys
import time
import click
import logging
import requests
import textwrap
import click_log
from Bio import SeqIO
from subprocess import Popen

nod_jar = os.path.join('lib', 'NOD', 'clinod-1.3.jar')
pred1433_python = os.path.join('lib', '1433pred', 'prediction.py')
jpred_perl = os.path.join('lib', 'Jpred', 'jpredapi')


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
               '-out={}'.format(output_nod),
               '-f=COMPLETE']
        Popen(cmd)


@main.command('1433pred')
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

        cmd = ['python', pred1433_python,
               '-i', input_seq, '-o', output_1433pred]
        # Popen(cmd)
        os.system(' '.join(cmd))


@main.command('jpred')
@click.option('-l', '--log', default=sys.stderr,
              help="Path to the logfile.",
              type=click.File('wb'))
@click.argument('input',
                type=click.File('r'), required=True)
# @click.argument('output',
#                 type=click.File('w'), required=False)
@click_log.simple_verbosity_option(default="INFO")
def jpred(input, log):
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
        output_jpred = os.path.join(os.path.dirname(__file__),
                                    'data', 'output', 'Jpred')

        output_jpred_jnet = os.path.join(os.path.dirname(__file__),
                                         'data', 'output', 'Jpred',
                                         '{}.jnet'.format(pid))

        output_jpred_tar = os.path.join(os.path.dirname(__file__),
                                        'data', 'output', 'Jpred',
                                        '{}.tar.gz'.format(pid))

        if not os.path.exists(input_seq):
            output = open(input_seq, 'w')
            seq = '\n'.join(textwrap.wrap(str(seq), width=60))
            output.write(">{}\n{}\n".format(pid, seq))
            output.close()

        cmd = ['perl', jpred_perl, 'submit', 'mode=single', 'format=fasta',
               'email=funpdbe@dundee.ac.uk',
               'file={}'.format(input_seq), 'name={}'.format(pid),
               '>', os.path.join(output_jpred, '{}.log'.format(pid))]
        # Popen(cmd)
        os.system(' '.join(cmd))

        # parse Jpred job id
        jobid = ""
        with open(os.path.join(output_jpred, '{}.log'.format(pid)), 'r') as lines:
            for line in lines:
                if line.startswith("Created JPred job with jobid: "):
                    jobid = line.strip().split()[-1]

        finished = False
        while not finished:

            # check job status
            cmd = ['perl', jpred_perl, 'status', 'jobid={}'.format(jobid), 'getResults=no',
                   'checkEvery=once', 'silent', 'email=funpdbe@dundee.ac.uk',
                   '>', os.path.join(output_jpred, '{}.status.log'.format(pid))]
            # Popen(cmd)
            os.system(' '.join(cmd))

            # parse job status
            jobstatus = ""

            with open(os.path.join(output_jpred, '{}.status.log'.format(pid)), 'r') as lines:
                for line in lines:
                    if "Results available at the following URL:" in line:
                        jobstatus = "Job finished"
                    elif "ERROR" in line:
                        jobstatus = "Job failed"

            if jobstatus == "Job finished":
                finished = True

                # get results: jnet
                jpred_url = "http://www.compbio.dundee.ac.uk/jpred4/results"
                jpred_url_full = "{}/{}/{}.jnet".format(jpred_url, jobid, jobid)
                with open(output_jpred_jnet, "wb") as outfile:
                    r = requests.get(url=jpred_url_full)
                    outfile.write(r.content)

                # get results: tar.gz
                jpred_url = "http://www.compbio.dundee.ac.uk/jpred4/results"
                jpred_url_full = "{}/{}/{}.tar.gz".format(jpred_url, jobid, jobid)
                with open(output_jpred_tar, "wb") as outfile:
                    r = requests.get(url=jpred_url_full)
                    outfile.write(r.content)

            elif jobstatus == "Job failed":
                finished = True
                print("Jpred job {} has errored. See {} for more details"
                      "".format(jobid, os.path.join(output_jpred, '{}.status.log'.format(pid))))

            # sleep 30 seconds
            time.sleep(30)


if __name__ == "__main__":
    main()
