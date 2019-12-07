import ee
from task_base import EETask


class HIIPopulationDensity(EETask):
    ee_rootdir = "projects/HII/v1/sumatra_poc"
    ee_driverdir = 'driver/popdens'
    # if input lives in ee, it should have an "ee_path" pointing to an ImageCollection/FeatureCollection
    inputs = {
        "gpw": {
            "ee_type": EETask.IMAGECOLLECTION,
            "ee_path": "CIESIN/GPWv411/GPW_Population_Density",
            "maxage": 5  # years
        },
        "ocean": {
            "ee_type": EETask.IMAGE,
            "ee_path": "users/aduncan/cci/ESACCI-LC-L4-WB-Ocean-Map-150m-P13Y-2000-v40",
        },
        "jrc": {
            "ee_type": EETask.IMAGE,
            "ee_path": 'JRC/GSW1_0/GlobalSurfaceWater',
        },
        "caspian": {
            "ee_type": EETask.FEATURECOLLECTION,
            "ee_path": 'users/aduncan/caspian',
        },            }
    gpw_cadence = 5

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_aoi_from_ee("{}/sumatra_poc_aoi".format(self.ee_rootdir))

    def calc(self):
        gpw = ee.ImageCollection(self.inputs['gpw']['ee_path'])

        ee_taskdate = ee.Date(self.taskdate.strftime(self.DATE_FORMAT))
        gpw_prior = gpw.filterDate(ee_taskdate.advance(-self.gpw_cadence, 'year'), ee_taskdate).first()
        gpw_later = gpw.filterDate(ee_taskdate, ee_taskdate.advance(self.gpw_cadence, 'year')).first()
        gpw_diff = gpw_later.subtract(gpw_prior)
        numerator = ee_taskdate.difference(gpw_prior.date(), 'day')
        gpw_diff_fraction = gpw_diff.multiply(numerator.divide(self.gpw_cadence * 365))
        gpw_taskdate = gpw_prior.add(gpw_diff_fraction)
        gpw_taskdate_300m = gpw_taskdate.resample().reproject(crs=self.crs, scale=self.scale)


        caspian = ee.FeatureCollection(self.inputs['caspian']['ee_path'])

        jrc = ee.Image(self.inputs['jrc']['ee_path'])\
                        .select('occurrence')\
                        .lte(75)\
                        .unmask(1)\
                        .multiply(ee.Image(0).clip(caspian).unmask(1))

        ocean = ee.Image(self.inputs['ocean']['ee_path'])


        gpw_venter = gpw_taskdate_300m.add(ee.Image(1))\
            .log()\
            .multiply(ee.Image(3.333))\
            .updateMask(jrc)\
            .updateMask(ocean)
        # TODO: mask water with centralized HII-defined water images

        self.export_image_ee(gpw_venter, '{}/{}'.format(self.ee_driverdir, 'hii_popdens_driver'))

    def check_inputs(self):
        super().check_inputs()
        # add any task-specific checks here, and set self.status = self.FAILED if any fail


if __name__ == "__main__":
    popdens_task = HIIPopulationDensity()
    popdens_task.run()
