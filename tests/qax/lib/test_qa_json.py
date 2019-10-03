from pathlib import Path
import os
import unittest

from hyo2.qax.lib.qa_json import QAJson, QaJsonRoot, QaJsonQa, QaJsonQa, \
    QaJsonDataLevel, QaJsonCheck, QaJsonOutputs, QaJsonInputs, QaJsonInfo, \
    QaJsonParam, QaJsonExecution, QaJsonGroup, QaJsonFile


class TestQaJson(unittest.TestCase):

    qa_json_file_01_dict = {
        "path": "/not/a/real/path/test.txt",
        "description": "test file 1"
    }
    qa_json_file_02_dict = {
        "path": "/not/a/real/path/test2.txt"
    }

    qa_json_param_01_dict = {
        "name": "threshold",
        "value": 123
    }
    qa_json_param_02_dict = {
        "name": "myVal",
        "value": "foo bar"
    }

    qa_json_outputs = {
        "percentage": 55,
        "execution": {
            "start": "2019-07-08T14:56:49.006647",
            "end": "2019-07-08T14:56:49.006677",
            "status": "completed"
        },
        "files": [{"path": "t3.txt"}, {"path": "t4.txt"}]
    }

    qa_json_info = {
        "id": "7761e08b-1380-46fa-a7eb-f1f41db38541",
        "name": "Filename checked",
        "description": "desc",
        "version": "1",
        "group": {
            "id": "123",
            "name": "123"
        }
    }

    qa_json_inputs = {
        "files": [qa_json_file_01_dict, qa_json_file_02_dict],
        "params": []
    }

    def test_qa_json_file(self):
        f1 = QaJsonFile.from_dict(TestQaJson.qa_json_file_01_dict)
        self.assertDictEqual(TestQaJson.qa_json_file_01_dict, f1.to_dict())

        f2 = QaJsonFile.from_dict(TestQaJson.qa_json_file_02_dict)
        self.assertDictEqual(TestQaJson.qa_json_file_02_dict, f2.to_dict())

    def test_qa_json_param(self):
        p1 = QaJsonParam.from_dict(TestQaJson.qa_json_param_01_dict)
        self.assertDictEqual(TestQaJson.qa_json_param_01_dict, p1.to_dict())

        p2 = QaJsonParam.from_dict(TestQaJson.qa_json_param_02_dict)
        self.assertDictEqual(TestQaJson.qa_json_param_02_dict, p2.to_dict())

    def test_qa_json_param(self):
        f1 = QaJsonFile.from_dict(TestQaJson.qa_json_file_01_dict)
        self.assertDictEqual(TestQaJson.qa_json_file_01_dict, f1.to_dict())

        f2 = QaJsonFile.from_dict(TestQaJson.qa_json_file_02_dict)
        self.assertDictEqual(TestQaJson.qa_json_file_02_dict, f2.to_dict())

    def test_qa_json_inputs(self):
        i1 = QaJsonInputs.from_dict(TestQaJson.qa_json_inputs)
        self.assertDictEqual(TestQaJson.qa_json_inputs, i1.to_dict())

    def test_qa_json_outputs(self):
        o1 = QaJsonOutputs.from_dict(TestQaJson.qa_json_outputs)
        self.assertDictEqual(TestQaJson.qa_json_outputs, o1.to_dict())

    def test_qa_json_info(self):
        i1 = QaJsonInfo.from_dict(TestQaJson.qa_json_info)
        self.assertDictEqual(TestQaJson.qa_json_info, i1.to_dict())

    def test_qa_json_load(self):
        here = os.path.abspath(os.path.dirname(__file__))
        test_file = os.path.join(here, "qa_json_test.json")

        qajson = QAJson(test_file)

        self.assertIsInstance(qajson.root, QaJsonRoot)
        self.assertIsInstance(qajson.root.qa, QaJsonQa)

        self.assertEqual(qajson.root.qa.version, '0.1.4')

        self.assertIsInstance(qajson.root.qa.raw_data, QaJsonDataLevel)
        self.assertIsInstance(qajson.root.qa.survey_products, QaJsonDataLevel)
        self.assertIsInstance(qajson.root.qa.chart_adequacy, QaJsonDataLevel)
