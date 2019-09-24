import unittest

from hyo2.qax.lib.config import QaxConfig
from hyo2.qax.lib.config import QaxConfigProfile
from hyo2.qax.lib.config import QaxConfigSurveyProduct


class TestQaxConfig(unittest.TestCase):

    profile_dict = {
        'name': "test profile",
        'description': "profile for unit testing",
        'checkTools': [
            {
                'name': 'raw check',
                'surveyProducts': [
                    {
                        'name': 'raw type 1',
                        'extensions': ['abc', 'def']
                    }
                ]
            },
            {
                'name': 'raw check',
                'surveyProducts': [
                    {
                        'name': 'raw type 1',
                        'extensions': ['abc', 'ijk']
                    }
                ]
            },
            {
                'name': 'dtm check',
                'surveyProducts': [
                    {
                        'name': 'grid type 1',
                        'extensions': ['xyz']
                    }
                ]
            },
        ]
    }

    def test_survey_product_from_dict(self):
        survey_product_dict = {
            'name': 'test name',
            'description': 'test description',
            'extensions': ['test_ext_01', 'test_ext_02']
        }
        survey_product = QaxConfigSurveyProduct.from_dict(survey_product_dict)

        self.assertEqual(survey_product_dict['name'], survey_product.name)
        self.assertEqual(
            survey_product_dict['description'], survey_product.description)
        self.assertEqual(
            len(survey_product_dict['extensions']),
            len(survey_product.extensions))

    def test_survey_product_merge(self):
        sp1 = QaxConfigSurveyProduct(
            name="Raw Products", description="", extensions=["all", "raw"]
        )
        sp2 = QaxConfigSurveyProduct(
            name="Raw Products", description="", extensions=["raw"]
        )
        sp3 = QaxConfigSurveyProduct(
            name="Survey DTMs", description="", extensions=["tif"]
        )

        merged_prods = QaxConfigSurveyProduct.merge([sp1, sp2, sp3])
        self.assertEqual(2, len(merged_prods))

        self.assertTrue(any(p.name == "Raw Products" for p in merged_prods))
        self.assertTrue(any(p.name == "Survey DTMs" for p in merged_prods))

        raw_prod = next(
            (p for p in merged_prods if p.name == "Raw Products"), None)
        self.assertEqual(2, len(raw_prod.extensions))
        self.assertTrue('all' in raw_prod.extensions)
        self.assertTrue('raw' in raw_prod.extensions)
        self.assertFalse('tif' in raw_prod.extensions)

        dtm_prod = next(
            (p for p in merged_prods if p.name == "Survey DTMs"), None)
        self.assertEqual(1, len(dtm_prod.extensions))
        self.assertTrue('tif' in dtm_prod.extensions)

    def test_profile_survey_product_merge(self):
        profile = QaxConfigProfile.from_dict(TestQaxConfig.profile_dict)
        unique_products = profile.get_unique_survey_products()

        self.assertEqual(2, len(unique_products))
        self.assertTrue(any(p.name == "raw type 1" for p in unique_products))
        self.assertTrue(any(p.name == "grid type 1" for p in unique_products))
