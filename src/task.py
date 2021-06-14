import argparse
import ee
from datetime import datetime, timezone
from task_base import HIITask


class HIIPopulationDensity(HIITask):
    scale = 300
    gpw_cadence = 5
    inputs = {
        "gpw": {
            "ee_type": HIITask.IMAGECOLLECTION,
            "ee_path": "CIESIN/GPWv411/GPW_Population_Density",
            "maxage": 5,  # years
        },
        "watermask": {
            "ee_type": HIITask.IMAGE,
            "ee_path": "projects/HII/v1/source/phys/watermask_jrc70_cciocean",
            "static": True,
        },
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gpw = ee.ImageCollection(self.inputs["gpw"]["ee_path"])
        self.watermask = ee.Image(self.inputs["watermask"]["ee_path"])
        self.ee_taskdate = ee.Date(self.taskdate.strftime(self.DATE_FORMAT))

    def gpw_earliest(self):
        return self.gpw.sort("system:time_start").first()

    def gpw_latest(self):
        return self.gpw.sort("system:time_start", False).first()

    def gpw_interpolated(self):
        gpw_prev = self.gpw.filterDate(
            self.ee_taskdate.advance(-self.gpw_cadence, "year"), self.ee_taskdate
        ).first()
        gpw_next = self.gpw.filterDate(
            self.ee_taskdate, self.ee_taskdate.advance(self.gpw_cadence, "year")
        ).first()

        gpw_delta_days = gpw_next.date().difference(gpw_prev.date(), "day")
        taskdate_delta_days = self.ee_taskdate.difference(gpw_prev.date(), "day")

        gpw_diff = gpw_next.subtract(gpw_prev)

        gpw_daily_change = gpw_diff.divide(gpw_delta_days)
        gpw_change = gpw_daily_change.multiply(taskdate_delta_days)

        return gpw_prev.add(gpw_change)

    def calc(self):
        gpw_taskdate = None

        ee_taskdate_millis = self.ee_taskdate.millis()
        gpw_first_date = ee.Date(
            self.gpw.sort("system:time_start").first().get("system:time_start")
        ).millis()
        gpw_last_date = ee.Date(
            self.gpw.sort("system:time_start", False).first().get("system:time_start")
        ).millis()
        start_test = ee_taskdate_millis.lte(gpw_first_date)
        end_test = ee_taskdate_millis.gte(gpw_last_date)
        interpolate_test = start_test.eq(0).And(end_test.eq(0))

        if interpolate_test.getInfo():
            gpw_taskdate = self.gpw_interpolated()
        elif end_test.getInfo():
            gpw_taskdate = self.gpw_latest()
        elif start_test.getInfo():
            gpw_taskdate = self.gpw_earliest()
        else:
            raise Exception("no valid GPW image")

        hii_popdens_driver = (
            gpw_taskdate.resample("bilinear")
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
