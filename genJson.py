import os
import subprocess
from natsort import natsorted, ns

config = 'config.yaml'
indir = 'audio'
outdir = 'descriptors'

audiofiles = os.listdir(indir)
audiofiles = [f for f in audiofiles if f.endswith('.mp3')]
audiofiles = natsorted(audiofiles, key=lambda y: y.lower())

if not os.path.exists(outdir):
	os.makedirs(outdir)

for idx,f in enumerate(audiofiles):
	f = f.split('.')
	filename = f[0]
	extension = f[1]
	if extension == 'mp3':
		infile = '{}.mp3'.format(filename)
		inpath = os.path.join(indir, infile)
		outfile = '{}.json'.format(filename)
		outpath = os.path.join(outdir, outfile)
		if os.path.isfile(outpath):
			print 'Skipping {}'.format(outpath)
		else:
			print 'Generating {}... {}/{}'.format(outpath, idx, len(audiofiles))
			with open(os.devnull, 'w') as devnull:
				p = subprocess.call(["streaming_extractor_music.exe", inpath, outpath, config], stdout=devnull)
