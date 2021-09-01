import argparse
import ee
from task_base import HIITask


class HIIPopulationDensity(HIITask):
    inputs = {
        "watermask": {
            "ee_type": HIITask.IMAGE,
            "ee_path": "projects/HII/v1/source/phys/watermask_jrc70_cciocean",
            "static": True,
        },
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.watermask = ee.Image(self.inputs["watermask"]["ee_path"])

    def calc(self):
        hii_popdens_driver = (
            self.population_density.resample("bilinear")
            .add(ee.Image(1))
            .log10()
            .multiply(ee.Image(3.333))
            .unmask(0)
            .clamp(0, 10)
            .updateMask(self.watermask)
            .multiply(100)
            .int()
            .rename("hii_popdens_driver")
        )

        self.export_image_ee(
            hii_popdens_driver,
            f"driver/population_density",
        )

    def check_inputs(self):
        super().check_inputs()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--taskdate")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="overwrite existing outputs instead of incrementing",
    )
    options = parser.parse_args()
    popdens_task = HIIPopulationDensity(**vars(options))
    popdens_task.run()
