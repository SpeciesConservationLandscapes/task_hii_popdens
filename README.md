HII POPULATION DENSITY DRIVER
---------------

## What does this task do?

This task calculates the (unitless) "influence" of population density on the terrestrial surface as one of the key
drivers for a combined [Human Influence Index](https://github.com/SpeciesConservationLandscapes/task_hii_weightedsum). "Influence" is a logarithmically scaled pressure score based on population density.

The source population density cells are from the Gridded Population of the World (GPW) dataset developed by the Centre for International Earth Science Information Network (CIESIN). This dataset models the distribution of the global human population on a 5 year cadence beginning in 2000 at a spatial resolution of 30 arc-seconds (~1km).

For any given task date between two available GPW input images, the estimated population density is linearly interpolated to the specific task date. If the task date either precedes or is succeeds the available GPW images, the first or last available GPW image are used respectively.

These values are bilinearly interpolated to an ~300m x 300m grid. The pressure score is calculated as
```
pressure score = 3.333 * log(population density + 1)
```

Population density values above 1000 are given a maximum pressure score of 10. This directly follows the logic by [Venter et al. 2016](https://www.nature.com/articles/sdata201667).

Values are multiplied by 100 and converted to an integer for efficient exporting and storage in the Earth Engine HII Population Density Driver image collection ('projects/HII/v1/driver/population_density').

## Variables and Defaults

### Environment variables
```
SERVICE_ACCOUNT_KEY=<GOOGLE SERVICE ACCOUNT KEY>
```

### Class constants

```
scale=300
gpw_cadence=5
```

## Usage

```
/app # python hii_popdens.py --help
usage: task.py [-h] [-d TASKDATE]

optional arguments:
  -h, --help            show this help message and exit
  -d TASKDATE, --taskdate TASKDATE
```
