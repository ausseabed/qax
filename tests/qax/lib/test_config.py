import unittest

from hyo2.qax.lib.config import QaxConfig
from hyo2.qax.lib.config import QaxConfigFileType
from hyo2.qax.lib.config import QaxConfigProfile
from hyo2.qax.lib.config import QaxConfigSurveyProduct


class TestQaxConfig(unittest.TestCase):

    profile_dict = {
        'name': "test profile",
        'description': "profile for unit testing",
        'checkTools': [
            {
                'name': 'raw check 1',
                'surveyProducts': [
                    {
                        'name': 'raw type 1',
                        'fileTypes': [
                            {
                                'name': 'Konsgberg file',
                                'extension': 'all'
                            },
                            {
                                'name': 'Konsgberg file',
                                'extension': 'wcd'
                            }
                        ]
                    }
                ]
            },
            {
                'name': 'raw check 2',
                'surveyProducts': [
                    {
                        'name': 'raw type 1',
                        'fileTypes': [
                            {
                                'name': 'Konsgberg file',
                                'extension': 'all'
                            },
                            {
                                'name': 'Konsgberg file',
                                'extension': 'wcd'
                            }
                        ]
                    }
                ]
            },
            {
                'name': 'dtm check',
                'surveyProducts': [
                    {
                        'name': 'grid type 1',
                        "fileTypes": [
                            {
                                'name': 'BAG file',
                                'extension': 'bag'
                            },
                            {
                                'name': 'CSAR file',
                                'extension': 'csar'
                            }
                        ]
                    }
                ]
            },
        ]
    }

    def test_survey_product_from_dict(self):
        survey_product_dict = {
            'name': 'test name',
            'description': 'test description',
            'fileTypes': [
                {'name': 'ft name 1', 'extension': 'ft1'},
                {'name': 'ft name 2', 'extension': 'ft2'}
            ]
        }
        survey_product = QaxConfigSurveyProduct.from_dict(survey_product_dict)

        self.assertEqual(survey_product_dict['name'], survey_product.name)
        self.assertEqual(
            survey_product_dict['description'], survey_product.description)
        self.assertEqual(
            len(survey_product_dict['fileTypes']),
            len(survey_product.file_types))

    def test_survey_product_merge(self):
        sp1 = QaxConfigSurveyProduct(
            name="Raw Products",
            description="",
            file_types=[
                QaxConfigFileType('all file', 'all'),
                QaxConfigFileType('raw file', 'raw'),
            ]
        )
        sp2 = QaxConfigSurveyProduct(
            name="Raw Products",
            description="",
            file_types=[
                QaxConfigFileType('raw file', 'raw'),
            ]
        )
        sp3 = QaxConfigSurveyProduct(
            name="Survey DTMs",
            description="",
            file_types=[
                QaxConfigFileType('tif file', 'tif'),
            ]
        )

        merged_prods = QaxConfigSurveyProduct.merge([sp1, sp2, sp3])
        self.assertEqual(2, len(merged_prods))

        self.assertTrue(any(p.name == "Raw Products" for p in merged_prods))
        self.assertTrue(any(p.name == "Survey DTMs" for p in merged_prods))

        raw_prod = next(
            (p for p in merged_prods if p.name == "Raw Products"), None)
        self.assertEqual(2, len(raw_prod.file_types))
        raw_prod_all_ft = next(
            (ft for ft in raw_prod.file_types if ft.name == "all file"), None)
        self.assertTrue(raw_prod_all_ft is not None)
        raw_prod_raw_ft = next(
            (ft for ft in raw_prod.file_types if ft.name == "raw file"), None)
        self.assertTrue(raw_prod_raw_ft is not None)
        raw_prod_tif_ft = next(
            (ft for ft in raw_prod.file_types if ft.name == "tif file"), None)
        self.assertTrue(raw_prod_tif_ft is None)

        dtm_prod = next(
            (p for p in merged_prods if p.name == "Survey DTMs"), None)
        self.assertEqual(1, len(dtm_prod.file_types))
        dtm_prod_tif_ft = next(
            (ft for ft in dtm_prod.file_types if ft.name == "tif file"), None)
        self.assertTrue(dtm_prod_tif_ft is not None)

    def test_profile_survey_product_merge(self):
        profile = QaxConfigProfile.from_dict(TestQaxConfig.profile_dict)
        unique_products = profile.get_unique_survey_products()

        self.assertEqual(2, len(unique_products))
        self.assertTrue(any(p.name == "raw type 1" for p in unique_products))
        self.assertTrue(any(p.name == "grid type 1" for p in unique_products))
