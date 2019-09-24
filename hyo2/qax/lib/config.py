from collections import defaultdict
from pathlib import Path
from typing import Dict, List
import copy
import json
import os
import time


class QaxConfigSurveyProduct:
    """
    Represents a specific Survey Product. A survey product is a type of data.
    Examples include a Digital Terrain Model that could be in a number of
    formats.
    """

    @classmethod
    def from_dict(cls, data: Dict) -> 'QaxConfigSurveyProduct':
        description = data['description'] if 'description' in data else None
        extensions = data['extensions'] if 'extensions' in data else []
        survey_product = cls(
            name=data['name'],
            description=description,
            extensions=extensions
        )
        return survey_product

    @classmethod
    def merge(
            cls, survey_products: List['QaxConfigSurveyProduct']
            ) -> List['QaxConfigSurveyProduct']:
        """
        Merges a list of `QaxConfigSurveyProduct` based on common name
        attributes. Extension lists of each survey product are also merged.
        """
        sp_dict = {}
        for sp in survey_products:
            merged_sp = None
            if sp.name not in sp_dict:
                merged_sp = QaxConfigSurveyProduct(
                    sp.name, sp.description, copy.deepcopy(sp.extensions))
                sp_dict[merged_sp.name] = merged_sp
            else:
                merged_sp = sp_dict[sp.name]
                for ext in sp.extensions:
                    if ext not in merged_sp.extensions:
                        merged_sp.extensions.append(ext)
        return list(sp_dict.values())

    def __init__(
            self, name: str, description: str, extensions: List[str] = []):
        self.name = name
        self.description = description
        self.extensions = extensions

    def __eq__(self, other):
        if not (other is QaxConfigSurveyProduct):
            return false
        return self.name == other.name

    def __repr__(self):
        msg = super().__repr__()
        msg += "\n"
        msg += "name: {}".format(self.name)
        msg += "description: {}".format(self.description)
        return msg


class QaxConfigCheckTool:
    """
    Represents the configuration of a single check tool. Includes definition
    of what survey products the tool is capable of checking and default input
    parameters to these checks.
    """

    @classmethod
    def from_dict(cls, data: Dict) -> 'QaxConfigCheckTool':
        survey_products = []
        if 'surveyProducts' in data:
            for survey_product_dict in data['surveyProducts']:
                survey_product = QaxConfigSurveyProduct.from_dict(
                    survey_product_dict)
                survey_products.append(survey_product)

        description = data['description'] if 'description' in data else None
        check_tool = cls(
            name=data['name'],
            description=description,
            survey_products=survey_products
        )
        return check_tool

    def __init__(
            self, name: str, description: str,
            survey_products: List[QaxConfigSurveyProduct] = []):
        self.name = name
        self.description = description
        self.survey_products = survey_products

    def __repr__(self):
        msg = super().__repr__()
        msg += "\n"
        msg += "name: {}".format(self.name)
        msg += "description: {}".format(self.description)
        msg += "survey product count: {}".format(len(self.survey_products))
        return msg


class QaxConfigProfile:
    """
    Represents a single QAX Profile, a profile is a collection of QA check
    tools. Examples of profiles may include "AusSeabed" and "NOAA"
    """

    @classmethod
    def from_dict(cls, data: Dict) -> 'QaxConfigProfile':
        """
        Factory method to create a QAX Profile from a dict
        """
        name = data['name']

        check_tools = []
        for check_tool_dict in data['checkTools']:
            check_tool = QaxConfigCheckTool.from_dict(check_tool_dict)
            check_tools.append(check_tool)

        profile = cls(
            name=name,
            check_tools=check_tools
        )
        return profile

    def __init__(self, name: str, check_tools: List[QaxConfigCheckTool]):
        self.name = name
        self.check_tools = check_tools

    def get_unique_survey_products(self) -> List[QaxConfigSurveyProduct]:
        """
        Generate a list of `QaxConfigSurveyProduct` that includes only unique
        survey products across all check tools included in this profile.
        """
        all_prods = []
        for check_tool in self.check_tools:
            all_prods.extend(check_tool.survey_products)
        unique_prods = QaxConfigSurveyProduct.merge(all_prods)
        return unique_prods

    def __repr__(self):
        msg = super().__repr__()
        msg += "\n"
        msg += "name: {}".format(self.name)
        msg += "check tool count: {}".format(len(self.check_tools))
        return msg


class QaxConfig:
    """
    Handles loading of QAX Profiles from JSON based configurations stored in
    a config folder.
    """

    @classmethod
    def config_folder(cls) -> Path:
        app_path = Path().absolute()
        config_path = app_path.joinpath('config')
        if not config_path.exists():
            raise RuntimeError(
                "unable to locate config folder {}".format(config_path))
        return config_path

    def __init__(self, path: Path = None):
        if path is None:
            self.path = QaxConfig.config_folder()
        else:
            self.path = path

        self.profiles = []

    def __get_config_files(self) -> List[Path]:
        config_files = []
        for x in self.path.iterdir():
            if x.is_file() and x.suffix == '.json':
                config_files.append(x)
        return config_files

    def __profile_from_dict(self, config_data: Dict) -> QaxConfigProfile:
        return QaxConfigProfile.from_dict(config_data)

    def __load_config(self, config_file: Path):
        profile = None
        with config_file.open() as f:
            config_data = json.load(f)
            profile = self.__profile_from_dict(config_data)
        return profile

    def load(self):
        """
        Loads all JSON config files found in `self.path`. Files not having a
        .json extension will be skipped.
        """
        config_files = self.__get_config_files()
        for config_file in config_files:
            profile = self.__load_config(config_file)
            self.profiles.append(profile)
