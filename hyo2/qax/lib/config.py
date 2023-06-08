from collections import defaultdict
from pathlib import Path
from typing import Dict, List
import copy
import json
import os
import re
import time

"""
Module defines classes for QAX JSON config file. Hierarchy is as follows;

QaxConfig
  QaxConfigProfile
    QaxConfigCheckTool
  QaxConfigSpecification
    QaxConfigParameter
"""


class QaxConfigCheckTool:
    """
    Represents the configuration of a single check tool.
    """

    @classmethod
    def from_dict(cls, data: Dict) -> 'QaxConfigCheckTool':
        name = data['name'] if ('name' in data) else None
        plugin_class = data['pluginClass'] if ('pluginClass' in data) else None
        checked = data['checked'] if ('checked' in data) else False
        enabled = data['enabled'] if ('enabled' in data) else True
        description = data['description'] if 'description' in data else None
        icon = data['icon'] if 'icon' in data else None

        check_tool = cls(
            name=name,
            description=description,
            plugin_class=plugin_class,
            enabled=enabled,
            checked=checked,
            icon=icon
        )
        return check_tool

    def __init__(
            self, name: str, description: str,
            plugin_class: str = None,
            enabled: bool = True, checked: bool = False,
            icon: str = None):
        self.name = name
        self.description = description
        self.plugin_class = plugin_class
        # `enabled` indicates if the selection of this check tool can be
        # altered by QAX users
        self.enabled = enabled
        # `checked` sets the default as to whether the check should be executed
        # the checks are run.
        self.checked = checked
        self.icon = icon

    def __repr__(self):
        msg = super().__repr__()
        msg += "\n"
        msg += "name: {}".format(self.name)
        msg += "description: {}".format(self.description)
        msg += "plugin class: {}".format(self.plugin_class)
        msg += "enabled: {}".format(self.enabled)
        msg += "checked: {}".format(self.checked)
        return msg


class QaxConfigParameter:

    @classmethod
    def from_dict(cls, data: Dict) -> 'QaxConfigParameter':
        """
        Function to support parsing config file
        """
        parameterName = data['name']
        parameterValue = data['value']

        checkId = None
        if 'checkId' in data:
            checkId = data['checkId']

        checkName = None
        if 'checkName' in data:
            checkId = data['checkName']

        p = cls(
            checkId=checkId,
            checkName=checkName,
            parameterName=parameterName,
            parameterValue=parameterValue
        )
        return p

    def __init__(
            self,
            checkId: str = None,
            checkName: str = None,
            parameterName: str = None,
            parameterValue: object = None
        ) -> None:
        """
        A QAX config parameter is first matched to a check parameter value by
        either the checkId (a UUID str) or checkName.

        Parameters:
        checkId (str): UUID string that matches on of the check UUIDs (as defined
            in check implementation)
        parameterName (str): Name of parameter (as defined in check implementation)
        parameterValue (object): The value that will be used as the default for this
            parameter when this specification is selected.
        """
        self.checkId = checkId
        self.checkName = checkName
        self.name = parameterName
        self.value = parameterValue

        if self.checkId is None and self.checkName is None:
            raise RuntimeError("checkId and checkName cannot both be None")


class QaxConfigSpecification:

    @classmethod
    def from_dict(cls, data: Dict) -> 'QaxConfigSpecification':
        """
        Function to support parsing config file
        """
        name = None
        if 'name' in data:
            name = data['name']

        description = None
        if 'description' in data:
            description = data['description']

        parameters = []
        if 'parameters' in data:
            parameters_dict = data['parameters']
            parameters = [QaxConfigParameter.from_dict(pd) for pd in parameters_dict]

        p = cls(
            name=name,
            description=description,
            parameters=parameters
        )
        return p

    def __init__(
            self,
            name: str,
            description: str = None,
            parameters: List[QaxConfigParameter] = []
        ) -> None:
        """
        Parameters:
        name (str): the name of this specification (shown in list of specifications)
        description (str): the description of this specification (shown after a
            specification has been selected)
        parameters (List[QaxConfigParameter]): list of default parameter values for
            this specification
        """
        self.name = name
        self.description = description
        self.parameters = parameters


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

        description = None
        if 'description' in data:
            description = data['description']

        check_tools = []
        for check_tool_dict in data['checkTools']:
            check_tool = QaxConfigCheckTool.from_dict(check_tool_dict)
            check_tools.append(check_tool)

        specifications = []
        if 'specifications' in data:
            specifications_dict = data['specifications']
            specifications = [QaxConfigSpecification.from_dict(pd) for pd in specifications_dict]

        profile = cls(
            name=name,
            description=description,
            check_tools=check_tools,
            specifications=specifications
        )
        return profile

    def __init__(
            self,
            name: str,
            description: str,
            check_tools: List[QaxConfigCheckTool],
            specifications: List[QaxConfigSpecification]):
        self.name = name
        self.check_tools = check_tools
        self.description = description
        self.specifications = specifications

    def __repr__(self):
        msg = super().__repr__()
        msg += "\n"
        msg += "name: {}".format(self.name)
        msg += "check tool count: {}".format(len(self.check_tools))
        msg += "specification count: {}".format(len(self.specifications))
        return msg


class QaxConfig:
    """
    Handles loading of QAX Profiles from JSON based configurations stored in
    a config folder.
    """
    _instance = None  # singleton instance

    @classmethod
    def config_folder(cls) -> Path:
        app_path = Path().absolute()
        config_path = app_path.joinpath('config')
        if not config_path.exists():
            raise RuntimeError(
                "unable to locate config folder {}".format(config_path))
        return config_path

    @staticmethod
    def instance() -> 'QaxConfig':
        if QaxConfig._instance is None:
            raise RuntimeError("Configuration has not been loaded")
        return QaxConfig._instance

    def __init__(self, path: Path = None):
        if path is None:
            self.path = QaxConfig.config_folder()
        else:
            self.path = path

        self.profiles: List[QaxConfigProfile] = []

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

        self.profiles.sort(key=lambda x: x.name, reverse=False)

        QaxConfig._instance = self
