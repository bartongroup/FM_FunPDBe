#!/bin/csh

perl jpredapi submit mode=single format=fasta email=name@domain.com file=InputFile1.txt name=TestJob1 silent
perl jpredapi submit mode=single format=fasta email=name@domain.com file=InputFile2.txt name=TestJob2 silent
perl jpredapi submit mode=single format=fasta email=name@domain.com file=InputFile3.txt name=TestJob3 silent
perl jpredapi submit mode=single format=fasta email=name@domain.com file=InputFile4.txt name=TestJob4 silent
perl jpredapi submit mode=single format=fasta email=name@domain.com file=InputFile5.txt name=TestJob5 silent
