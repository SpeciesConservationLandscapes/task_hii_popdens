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
        self.gpw_taskdate = None

    def gpw_earliest(self):
        self.gpw_taskdate = self.gpw.sort("system:time_start").first()

    def gpw_latest(self):
        self.gpw_taskdate = self.gpw.sort("system:time_start", False).first()

    def gpw_interpolated(self):
        gpw_prev = self.gpw.filterDate(
            ee_taskdate.advance(-self.gpw_cadence, "year"), ee_taskdate
        ).first()
        gpw_next = self.gpw.filterDate(
            ee_taskdate, ee_taskdate.advance(self.gpw_cadence, "year")
        ).first()

        gpw_delta_days = gpw_next.date().difference(gpw_prev.date(), "day")
        taskdate_delta_days = ee_taskdate.difference(gpw_prev.date(), "day")

        gpw_diff = gpw_next.subtract(gpw_prev)

        gpw_daily_change = gpw_diff.divide(gpw_delta_days)
        gpw_change = gpw_daily_change.multiply(taskdate_delta_days)

        self.gpw_taskdate = gpw_prev.add(gpw_change)

    def calc(self):
        ee_taskdate = ee.Date(self.taskdate.strftime(self.DATE_FORMAT))
        ee_taskdate_millis = ee_taskdate.millis()
        gpw_first_date = ee.Date(
            self.gpw.sort("system:time_start").first().get("system:time_start")
        ).millis()
        gpw_last_date = ee.Date(
            self.gpw.sort("system:time_start", False).first().get("system:time_start")
        ).millis()
        start_test = ee_taskdate_millis.lt(gpw_first_date)
        end_test = ee_taskdate_millis.gt(gpw_last_date)
        interpolate_test = start_test.eq(0).And(end_test.eq(0))

        if interpolate_test.getInfo():
            self.gpw_interpolated()
        elif end_test.getInfo():
            self.gpw_latest()
        elif start_test.getInfo():
            self.gpw_earliest()
        else:
            print("no valid GPW image")
        # TODO: can probably remove the reproject, as the scale is set in export.
        gpw_taskdate_300m = self.gpw_taskdate.resample("bilinear").reproject(
            crs=self.crs, scale=self.scale
        )
        # TODO: this does not quite match the Venter formula.
        hii_popdens_driver = (
            gpw_taskdate_300m.add(ee.Image(1))
            .log()
            .multiply(ee.Image(3.333))
            .unmask(0)
            .updateMask(self.watermask)
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
    parser.add_argument("-d", "--taskdate", default=datetime.now(timezone.utc).date())
    options = parser.parse_args()
    popdens_task = HIIPopulationDensity(**vars(options))
    popdens_task.run()
