# Sicurezza informatica

## Build the docker image

```
git clone <this repo>
docker buildx build . -t sicinf:cpu
```

## Evaluate test data
### Run inference
```
docker run --rm -it \
    -v ./dataset:/dataset:z \
    -v ./out:/out \
    sicinf:cpu \
    python main.py NoFun --dataset /dataset/<dataset>.json --results /out/result.json --output /out/out.json
```

### Generate plots

```
docker run --rm -it \
    -v ./out:/out \
    sicinf:cpu \
    python ELAB.py /out/out.json /out/plots/
```
