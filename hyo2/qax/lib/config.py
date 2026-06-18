from pathlib import Path
from typing import Any
import json

"""
Module defines classes for QAX JSON config file. Hierarchy is as follows;

QaxConfig
    QaxConfigProfile
        QaxConfigCheckTool
    QaxConfigSpecification
        QaxConfigCheck
            QaxConfigParameter
"""


class QaxConfigCheckTool:
    """
    Represents the configuration of a single check tool.
    """

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "QaxConfigCheckTool":
        name = data.get("name", "")
        plugin_class = data.get("pluginClass", None)
        description = data.get("description", "")
        icon = data.get("icon", None)

        return cls(
            name=name,
            description=description,
            plugin_class=plugin_class,
            icon=icon,
        )

    def __init__(
        self,
        name: str,
        description: str,
        plugin_class: str | None = None,
        icon: str | None = None,
    ):
        self.name = name
        self.description = description
        self.plugin_class = plugin_class
        self.icon = icon

    def __repr__(self):
        msg = super().__repr__()
        msg += "\n"
        msg += "name: {}".format(self.name)
        msg += "description: {}".format(self.description)
        msg += "plugin class: {}".format(self.plugin_class)
        return msg


class QaxConfigParameter:
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "QaxConfigParameter":
        """
        Function to support parsing config file
        """
        parameterName = data["name"]
        parameterValue = data["value"]

        p = cls(parameterName=parameterName, parameterValue=parameterValue)
        return p

    def __init__(
        self,
        parameterName: str,
        parameterValue: Any = None,
    ) -> None:
        """
        A QAX config parameter is first matched to a check parameter value by
        either the checkId (a UUID str) or checkName.

        Parameters:
        parameterName (str): Name of parameter (as defined in check implementation)
        parameterValue (Any): The value that will be used as the default for this
            parameter when this specification is selected.
        """
        self.name = parameterName
        self.value = parameterValue


class QaxConfigCheck:
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "QaxConfigCheck":
        """
        Function to support parsing config file
        """

        checkId = data.get("checkId", None)
        checkName = data.get("checkName", None)

        parameters = [
            QaxConfigParameter.from_dict(pd) for pd in data.get("parameters", [])
        ]
        c = cls(checkId=checkId, checkName=checkName, parameters=parameters)
        return c

    def __init__(
        self,
        checkId: str | None = None,
        checkName: str | None = None,
        parameters: list[QaxConfigParameter] = [],
    ) -> None:
        self.checkId = checkId
        self.checkName = checkName
        self.parameters = parameters

        if self.checkId is None and self.checkName is None:
            raise RuntimeError("checkId and checkName cannot both be None")


class QaxConfigSpecification:
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "QaxConfigSpecification":
        """
        Function to support parsing config file
        """
        name = data.get("name", "")
        description = data.get("description", "")
        checks = [QaxConfigCheck.from_dict(pd) for pd in data.get("checks", [])]

        p = cls(name=name, description=description, checks=checks)
        return p

    def __init__(
        self,
        name: str,
        description: str = "",
        checks: list[QaxConfigCheck] = [],
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
        self.checks = checks

    def get_config_check(self, check_id: str) -> QaxConfigCheck | None:
        for c in self.checks:
            if c.checkId == check_id:
                return c
        return None


class QaxConfigProfile:
    """
    Represents a single QAX Profile, a profile is a collection of QA check
    tools. Examples of profiles may include "AusSeabed" and "NOAA"
    """

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "QaxConfigProfile":
        """
        Factory method to create a QAX Profile from a dict
        """
        name = data["name"]
        description = data.get("description", "")

        check_tools = [
            QaxConfigCheckTool.from_dict(check_tool_dict)
            for check_tool_dict in data.get("checkTools", [])
        ]

        specifications = [
            QaxConfigSpecification.from_dict(pd)
            for pd in data.get("specifications", [])
        ]

        profile = cls(
            name=name,
            description=description,
            check_tools=check_tools,
            specifications=specifications,
        )
        return profile

    def __init__(
        self,
        name: str,
        description: str,
        check_tools: list[QaxConfigCheckTool],
        specifications: list[QaxConfigSpecification],
    ):
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
        config_path = app_path.joinpath("config")
        if not config_path.exists():
            raise RuntimeError("unable to locate config folder {}".format(config_path))
        return config_path

    @staticmethod
    def instance() -> "QaxConfig":
        if QaxConfig._instance is None:
            raise RuntimeError("Configuration has not been loaded")
        return QaxConfig._instance

    def __init__(self, path: Path | None = None):
        self.path = path or QaxConfig.config_folder()
        self.profiles: list[QaxConfigProfile] = []

    def __get_config_files(self) -> list[Path]:
        return [
            dir_entry
            for dir_entry in self.path.iterdir()
            if dir_entry.is_file() and dir_entry.suffix == ".json"
        ]

    def __profile_from_dict(self, config_data: dict[str, Any]) -> QaxConfigProfile:
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
        self.profiles = sorted(
            [self.__load_config(cfg) for cfg in self.__get_config_files()],
            key=lambda x: x.name,
            reverse=False,
        )

        QaxConfig._instance = self
