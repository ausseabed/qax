from pathlib import Path
import os
import unittest

from ausseabed.qajson.parser import QajsonParser
from ausseabed.qajson.model import QajsonRoot, QajsonQa, QajsonQa, \
    QajsonDataLevel, QajsonCheck, QajsonOutputs, QajsonInputs, QajsonInfo, \
    QajsonParam, QajsonExecution, QajsonGroup, QajsonFile
from hyo2.qax.lib.project import QaCheckSummary


class TestQaCheckSummary(unittest.TestCase):

    qa_json = QajsonRoot.from_dict({
        "qa": {
            "version": "0.1.4",
            "raw_data": {
                "checks": [
                    {
                        "info": {
                            "id": "1",
                            "name": "check 01",
                            "version": "1",
                            "group": {"id": "", "name": ""}
                        },
                        "inputs": {
                            "files": [
                                {"path": "file1.txt"}
                            ]
                        },
                        "outputs": {
                            "percentage": 0,
                            "execution": {
                                "start": "2019-07-08T14:56:49.006647",
                                "end": "2019-07-08T14:56:49.006677",
                                "status": "completed"
                            },
                            "files": [],
                            "qa_pass": "yes"
                        }
                    },
                    {
                        "info": {
                            "id": "1",
                            "name": "check 01",
                            "version": "1",
                            "group": {"id": "", "name": ""}
                        },
                        "inputs": {
                            "files": [
                                {"path": "file3.txt"}
                            ]
                        },
                        "outputs": {
                            "percentage": 0,
                            "execution": {
                                "start": "2019-07-08T14:56:49.006647",
                                "end": "2019-07-08T14:56:49.006677",
                                "status": "completed"
                            },
                            "files": [],
                            "qa_pass": "yes"
                        }
                    },
                    {
                        "info": {
                            "id": "1",
                            "name": "check 01",
                            "version": "1",
                            "group": {"id": "", "name": ""}
                        },
                        "inputs": {
                            "files": [
                                {"path": "file4.txt"}
                            ]
                        },
                        "outputs": {
                            "percentage": 0,
                            "execution": {
                                "start": "2019-07-08T14:56:49.006647",
                                "end": "2019-07-08T14:56:49.006677",
                                "status": "completed"
                            },
                            "files": [],
                            "qa_pass": "no"
                        }
                    },
                    {
                        "info": {
                            "id": "2",
                            "name": "check 02",
                            "version": "1",
                            "group": {"id": "", "name": ""}
                        },
                        "inputs": {
                            "files": [
                                {"path": "file2.txt"}
                            ]
                        },
                        "outputs": {
                            "percentage": 0,
                            "execution": {
                                "start": "2019-07-08T14:56:49.006647",
                                "end": "2019-07-08T14:56:49.006677",
                                "status": "failed"
                            },
                            "files": []
                        }
                    },
                ]
            },
            "survey_products": []
        }
    })

    def test_get_summary(self):
        summaries = QaCheckSummary.get_summary(TestQaCheckSummary.qa_json)

        summary_01 = next((s for s in summaries if s.id == "1"), None)
        self.assertEqual(summary_01.total_executions, 3)
        self.assertEqual(summary_01.failed_executions, 0)
        self.assertEqual(summary_01.failed_check_state, 1)

        summary_02 = next((s for s in summaries if s.id == "2"), None)
        self.assertEqual(summary_02.total_executions, 1)
        self.assertEqual(summary_02.failed_executions, 1)
        self.assertEqual(summary_02.failed_check_state, 0)
