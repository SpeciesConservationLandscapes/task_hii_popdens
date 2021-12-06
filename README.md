HII POPULATION DENSITY DRIVER
---------------

## What does this task do?

This task calculates the (unitless) "influence" of population density on the terrestrial surface as one of the key
drivers for a combined [Human Influence Index](https://github.com/SpeciesConservationLandscapes/task_hii_weightedsum). "Influence" is a logarithmically scaled pressure score based on population density.

The source population density cells are derived from the WoldPop Population Data dataset developed by [WorldPop](https://www.worldpop.org/). This dataset models the distribution of the global human population annually beginning in 2000 at a spatial resolution of 100 m. As a class property of HIITask the original dataset values are converted from the number of people per 100m x 100m grid cell to actual population density of people/sq km.

The pressure score is calculated as
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
```

## Usage

*All parameters may be specified in the environment as well as the command line.*

```
/app # python task.py --help
usage: task.py [-h] [-d TASKDATE] [--overwrite]

optional arguments:
  -h, --help            show this help message and exit
  -d TASKDATE, --taskdate TASKDATE
  --overwrite           overwrite existing outputs instead of incrementing
```
