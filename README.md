# Sicurezza informatica

## Build the docker image

```
git clone <this repo>
docker buildx build . -t ghcr.io/eletoo/24-llmbinary:latest
```

## Evaluate test data
### Run inference on a single dataset
Please replace `<dataset>.json` with the desired dataset file name in the `/dataset` directory.
```
mkdir /out
docker run --rm -it \
    -v ./dataset:/dataset:z \
    -v ./out:/out:z \
    ghcr.io/eletoo/24-llmbinary:latest \
    python main.py NoFun --dataset /dataset/<dataset>.json --results /out/result.json --output /out/out.json
```

### Generate plots for a given output
```
mkdir /out
docker run --rm -it \
    -v ./out:/out:z \
    ghcr.io/eletoo/24-llmbinary:latest \
    python ELAB.py /out/out.json /out/plots/
```

### Autorun inference and generate plots 
This script will run inference and plot generation for every dataset present in the /dataset directory.
It will output all the files with the naming convention `<dataset name>.(output|results)` and will place
the plots in a directory, named the same as the dataset, inside `/out/plots`.

```
mkdir /out
docker run --rm -it -v ./dataset:/dataset:z -v ./out:/out:z ghcr.io/eletoo/24-llmbinary:latest
```
