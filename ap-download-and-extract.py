import requests
import os
import subprocess

active_papers = {
    "scripts": "https://zenodo.org/record/162171/files/bayesian_inference_fbm.ap?download=1",
    "traj1": "https://zenodo.org/record/61742/files/POPC_martini_nvt_cm_300ps.ap?download=1",
    "traj2": "https://zenodo.org/record/61743/files/POPC_martini_nvt_cm_600ns.ap?download=1",
}

for active_paper, url in active_papers.items():
    filename = os.path.split(url)[1].split("?")[0]
    if os.path.exists(filename):
        print("Already exists:", filename)
        continue
    print("Download", filename)
    r = requests.get(url)
    with open(filename , 'wb') as f:
        f.write(r.content)

subprocess.run("""
for d in TEMP data code-ORIGINAL documentation-ORIGINAL; do
    rm -rf $d
    mkdir $d
done
mkdir -p ap-extract-logs
cd TEMP
for f in bayesian_inference_fbm POPC_martini_nvt_cm_300ps POPC_martini_nvt_cm_600ns; do
    aptool -p ../$f.ap ls > ../ap-extract-logs/$f.log 2>&1
    aptool -p ../$f.ap checkout >> ../ap-extract-logs/$f.log 2>&1
done
rm -rf data
f=bayesian_inference_fbm
python3 ../aptool-dump.py ../$f.ap . >> ../ap-extract-logs/$f.log 2>&1

f=POPC_martini_nvt_cm_300ps
python3 ../aptool-dump.py ../$f.ap . >> ../ap-extract-logs/$f.log 2>&1
rm -rf data/short_time_trajectory.npy
mv data/POPC_martini_nvt data/short_time_trajectory

f=POPC_martini_nvt_cm_600ns
python3 ../aptool-dump.py ../$f.ap . >> ../ap-extract-logs/$f.log 2>&1
rm -rf data/long_time_trajectory.npy
mv data/POPC_martini_nvt data/long_time_trajectory

mv -f data/* ../data
mv -f code/* ../code-ORIGINAL
mv -f documentation/* ../documentation-ORIGINAL
rmdir code data documentation
cd ..
rmdir TEMP
""", shell=True, check=False,executable="bash")
