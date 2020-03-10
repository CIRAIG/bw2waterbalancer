# bw2waterbalancer

``bw2waterbalancer`` is a Python library used to create balanced water samples to override unbalanced sample.

Unbalanced samples arise when water exchanges are independently sampled. ``bw2waterbalancer`` rescales certain exchanges 
to ensure that the ratio of water inputs to water outputs is conserved. It is based on the 
[Brightway2 LCA framework](https://brightwaylca.org/), and is meant to be used with 
[presamples](https://presamples.readthedocs.io/en/latest/).
 
The rescaling is done according to three different strategy, depending on the nature of the exchanges:
    * default: rescale sampled inputs so that mass ratio of sampled input to sampled output is same as 
    in static activity  
    * inverse: rescale sampled outputs so that mass ratio of sampled input to sampled output is same
     as in static activity  
    * set_static: replace sampled exchanges with value in static activity  
 
It was developped with ecoinvent in mind, though the modifications required to make it useful for other databases would be minimal.  


[![pipeline status](https://gitlab.com/pascal.lesage/bw2waterbalancer/badges/master/pipeline.svg)](https://gitlab.com/pascal.lesage/bw2waterbalancer/commits/master)
[![coverage report](https://gitlab.com/pascal.lesage/bw2waterbalancer/badges/master/coverage.svg)](https://gitlab.com/pascal.lesage/bw2waterbalancer/commits/master)

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install bw2waterbalancer:

```bash
pip install bw2waterbalancer
```

or use conda: 
```bash
conda install --channel pascallesage bw2waterbalancer
```

## Usage

```python
from bw2waterbalancer import DatabaseWaterBalancer
from brightway2 import projects

projects.set_current("my project")

dwb = DatabaseWaterBalancer(
    ecoinvent_version="3.6", # used to identify activities with water production exchanges
    database_name="ei36_cutoff", #name the LCI db in the brightway2 project
)
```
Validating data
Getting information on technosphere water exchanges
0% [##############################] 100% | ETA: 00:00:00
Total time elapsed: 00:00:00
Getting information on biosphere water exchanges
0% [##############################] 100% | ETA: 00:00:00
Total time elapsed: 00:01:09

```python
# Generate samples, and format as matrix_data for use in presamples
dwb.add_samples_for_all_acts(iterations=1000)
```
0% [##############################] 100% | ETA: 00:00:00
Total time elapsed: 00:18:11

```python
# Create presamples package
dwb.create_presamples(
    name='some name', 
    dirpath=some/path, 
    id_='some id',
    seed='sequential', #or None, or int
    )
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## Acknowledgment
Special thanks to Quantis US for having funded the early iterations of this work. 

## License
[MIT](https://choosealicense.com/licenses/mit/)
