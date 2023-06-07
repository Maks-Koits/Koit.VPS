import argparse
import os
import os.path as osp
import subprocess

parser = argparse.ArgumentParser()

parser.add_argument(
    "--audio_dir", help="Path to the folder containing the input files.", type=str, required=True
)

parser.add_argument(
    "--out_dir", help="Path to the target folder for the transcripts.", type=str, required=True
)

parser.add_argument(
    "--whisper_model", type=str, choices=("small", "medium", "large"), default="medium"
)

parser.add_argument(
    "--print_only", type=str, default="false",
    help="Only prints the files to be processed instead "
         "of actually processing them", choices=("true", "false")
)

args = parser.parse_args()
args_d = {"true": True, "false": False}
args.print_only = args_d[args.print_only]

files_to_process = []
for file in os.listdir(args.audio_dir):
    #    if file.endswith(('.mp3', '.mp4')):
    files_to_process.append(file)

print(f"Processing {len(files_to_process)} files:")
print("\n".join(files_to_process))
# input(“Press Enter to continue / CTRL-C to cancel.")
print(20 * '-')

if not osp.exists(args.out_dir):
    os.makedirs(args.out_dir)

for file in files_to_process:
    print('Processing:', file)

    cmd = (f"whisper {osp.join(args.audio_dir, file)} --model {args.whisper_model}  "
           f"--language ru --output_dir {args.out_dir} --verbose True "
           "--task transcribe --output_format txt")

    if args.print_only:
        print(cmd)
    else:
        subprocess.run(cmd.split(), check=True)

    print('Finished processing', file)
    print(20 * '-')
