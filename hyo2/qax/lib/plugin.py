from pathlib import Path
from typing import Dict, List, NoReturn, Optional, Callable, Tuple
import importlib
import re

from hyo2.qax.lib.config import QaxConfig, QaxConfigCheckTool, QaxConfigProfile
from hyo2.qax.lib.check_options import CheckOption
from ausseabed.qajson.model import QajsonRoot, QajsonQa, QajsonDataLevel, \
    QajsonParam, QajsonCheck, QajsonInfo, QajsonGroup, QajsonFile
from ausseabed.qajson.parser import QajsonParser

""" Module defines the architecture and utility functions/classes for the
QAX check tool plugin system. A check tool must implement the QAX check tool
plugin inferface for it to be supported by QAX.

The module handles importing of the plugin module based on the definition
included in the QAX JSON Config file.
"""


class QaxFileType:
    """
    Represents a file type
    """

    @classmethod
    def from_dict(cls, data: Dict) -> 'QaxFileType':
        icon = data['icon'] if 'icon' in data else None
        file_type = cls(
            name=data['name'],
            extension=data['extension'],
            group=data['group'],
            icon=icon
        )
        return file_type

    def __init__(
            self,
            name: str,
            extension: str,
            group: str,
            icon: str = None):
        """ Constructor

        :param str name: name of the file type (not the filename)
        :param str extension: extension of the file type
        :param str group: the user interface groups files together based on
            this attribute.
        :param str icon: icon is a filename (without path) that exists in the
            applications `media` folder. eg; `tif.png`, `kng.png`. When
            provided the icon image will be shown next to files in list boxes
        """
        self.name = name
        self.extension = extension
        self.group = group
        self.icon = icon

    def formatted_name(self):
        return "{} (*.{})".format(self.name, self.extension)

    def supports_file(self, file_path: Path, file_group: str) -> bool:
        """ Returns True if the file_path file's extension matches
        `self.extension` and the file_group matches `self.extension`.
        """
        extension = file_path.suffix
        extension = extension.lstrip('.')
        return (
            ((extension == self.extension) or (self.extension == '*')) and
            file_group == self.group
        )

    def __repr__(self):
        msg = super().__repr__()
        msg += "\n"
        msg += "name: {}\n".format(self.name)
        msg += "extension: {}\n".format(self.extension)
        msg += "group: {}\n".format(self.group)
        return msg


class QaxFileGroup:
    """ Defines a collection of file types. This is constructed by util
    functions to support the user interface. The file lists presented to users
    are based on these groups
    """

    @classmethod
    def from_dict(cls, data: Dict) -> 'QaxFileGroup':
        file_type_dicts = data['fileTypes'] if 'fileTypes' in data else []
        file_types = [
            QaxFileType.from_dict(file_type_dict)
            for file_type_dict in file_type_dicts]

        survey_product = cls(
            name=data['name'],
            file_types=file_types
        )
        return survey_product

    @staticmethod
    def merge(file_groups: List['QaxFileGroup']) -> List['QaxFileGroup']:
        """ Merges a list of file groups so that it contains no duplicates
        """
        file_groups_dict = {}
        for fg in file_groups:
            for file_type in fg.file_types:
                if file_type.group in file_groups_dict:
                    # add to existing file group
                    fg = file_groups_dict[file_type.group]
                    fg.add(file_type)
                else:
                    fg = QaxFileGroup(file_type.group, [file_type])
                    file_groups_dict[fg.name] = fg
        return list(file_groups_dict.values())

    def __init__(self, name: str, file_types: List[QaxFileType]):
        self.name = name
        self.file_types = file_types

    def clean_name(self) -> str:
        """ Name with white space and special characters removed (or replaced)
        to support use in file names or config params.
        """
        name = self.name.replace(' ', '_')
        name = re.sub('[^a-zA-Z0-9_\\n\\.]', '', name)
        return name

    def matching_file_type(self, path: Path) -> QaxFileType:
        """ Finds a file type with an extension that matched that of the
        given path. None will be returned if no matching file type is found.
        """
        extension = path.suffix
        extension = extension.lstrip('.')
        match = next(
            (ft for ft in self.file_types if ft.extension == extension), None)
        return match

    def add(self, file_type: QaxFileType) -> NoReturn:
        """ Adds a new file type to this group. Duplicates will not be added.
        """
        match = next(
            (
                ft for ft in self.file_types
                if (
                    ft.name == file_type.name and
                    ft.extension == file_type.extension and
                    ft.group == file_type.group
                )
            ),
            None
        )
        if match is None:
            self.file_types.append(file_type)


class QaxCheckReference():
    """ Defines a reference to a check that is implemented elsewhere. Class
    includes details required to generate a QA JSON check definition. Does not
    include implementation of the check.
    """

    def __init__(
            self,
            id: str,
            name: str,
            data_level: str,
            description: str = None,
            supported_file_types: List[QaxFileType] = [],
            default_input_params: List[QajsonParam] = [],
            version: str = None
    ):
        """
        Constructor

        :param str id: UUID of the check. This will be included in the
            generated QA JSON file and therefore must match the id contained
            within the check tool implementation.
        :param str name: Name of the check
        :param str data_level: Data level of the check, must match that of the
            QA JSON schema (eg; raw_data, survey_products, chart_adequacy)
        :param str description: Optional description of the check
        :param List[QaxFileType] supported_file_types: list of file types
            supported by this check tool.
        :param List[QajsonParam] default_input_params: list of the
            input parameters and their default values.
        :param str version: version identifier of the check
        """
        self.id = id
        self.name = name
        self.data_level = data_level
        self.description = description
        self.supported_file_types = supported_file_types
        self.default_input_params = default_input_params
        self.version = version

    def supports_file(self, file_path: Path, file_group: str) -> bool:
        """ Returns True if the file_path file is supported by this check tool.
        """
        for supported_file_type in self.supported_file_types:
            if supported_file_type.supports_file(file_path, file_group):
                return True
        return False


class QaxCheckToolPlugin():
    """ Check tools must inherit this plugin class
    """

    def __init__(self):
        # name of the check tool
        self.name = 'unknown'
        self.description = None
        self.plugin_class = None  # full namespace string
        self.icon = None
        self.profile = None   # QaxConfigProfile, set when plugin loaded
        self.options = {}

    @property
    def spatial_outputs_qajson(self) -> bool:
        if CheckOption.spatial_output_qajson in self.options:
            return self.options[CheckOption.spatial_output_qajson]
        else:
            return False

    @property
    def spatial_outputs_export(self) -> bool:
        if CheckOption.spatial_output_export in self.options:
            return self.options[CheckOption.spatial_output_export]
        else:
            return False

    @property
    def spatial_outputs_export_location(self) -> str:
        if CheckOption.spatial_output_export_location in self.options:
            return self.options[CheckOption.spatial_output_export_location]
        else:
            return None

    def get_file_groups(self) -> List[QaxFileGroup]:
        """ Generate a list of file groups for this check tool plugin
        """
        file_groups_dict = {}
        for check in self.checks():
            for file_type in check.supported_file_types:
                if file_type.group in file_groups_dict:
                    # add to existing file group
                    fg = file_groups_dict[file_type.group]
                    fg.add(file_type)
                else:
                    fg = QaxFileGroup(file_type.group, [file_type])
                    file_groups_dict[fg.name] = fg
        return list(file_groups_dict.values())

    def _get_or_add_check(
            self,
            data_level: QajsonDataLevel,
            check_reference: QaxCheckReference) -> QajsonCheck:
        """ If a check exists it will be returned, otherwise a new check will
        be created, added, and then returned.
        """
        matching_check = data_level.get_check(check_reference.id)
        if matching_check is not None:
            return matching_check

        check_info = QajsonInfo(
            id=check_reference.id,
            name=check_reference.name,
            description=check_reference.description,
            version=check_reference.version,
            group=QajsonGroup("", "", ""),
        )

        new_check = QajsonCheck(info=check_info, inputs=None, outputs=None)
        data_level.checks.append(new_check)
        return new_check

    def _get_qajson_checks(self, qajson: QajsonRoot) -> List[QajsonCheck]:
        """ Gets a list of the qajson check objects that within this qajson
        root object. Utility function
        """
        #  list of all the data levels
        data_levels = [
            getattr(qajson.qa, a) for a in dir(qajson.qa)
            if isinstance(getattr(qajson.qa, a), QajsonDataLevel)
        ]

        all_checks = []
        # loop over the qajson tree finding all AajsonChecks that are
        # implemented by this plugin
        for data_level in data_levels:
            for check in data_level.checks:
                if self.implements_check(check.info.id):
                    all_checks.append(check)
        return all_checks

    def _checks_filtered_by_file(self, filename: str, checks: List[QajsonCheck]) -> List[QajsonCheck]:
      """ Filters the list of QajsonCheck objects so that it only includes checks
      that have been run on this file.
      """
      filtered_checks = []
      for check in checks:
          for file in check.inputs.files:
              if file.path == filename:
                  filtered_checks.append(check)
      return filtered_checks

    def _checks_filtered_by_name(self, check_name: str, checks: List[QajsonCheck]) -> List[QajsonCheck]:
        filtered_checks = [
            c for c in checks
            if c.info.name == check_name
        ]
        return filtered_checks

    def update_qa_json(self, qa_json: QajsonRoot) -> NoReturn:
        """ Includes this plugins checks into the `qa_json` object based on
        the checks this plugin provides
        """
        if qa_json.qa is None:
            # assume schema naming convention is
            #  `some_path/v0.1.2/qa.schema.json` or similar
            last_path = QajsonParser.schema_paths()[-1]
            version = last_path.parent.name[1:]
            # if no qa object, initialise the minimum spec
            qa_json.qa = QajsonQa(
                version=version,
                raw_data=None,
                survey_products=None,
            )
            qa_json.qa.get_or_add_data_level('raw_data')
            qa_json.qa.get_or_add_data_level('survey_products')

        check_refs = self.checks()
        for check_ref in check_refs:
            data_level = qa_json.qa.get_or_add_data_level(check_ref.data_level)
            self._get_or_add_check(data_level, check_ref)

    def update_qa_json_input_files(
            self, qa_json: QajsonRoot, files: List) -> NoReturn:
        """ Updates the input definitions included in the qa_json object
        to include the `files` list. Files are only added to a check if the
        check already exists in the `qa_json` object, and the check supports
        that file type (based on files extension and the supported file types
        included in the QaxCheckReference).
        """
        all_data_levels = [check_ref.data_level for check_ref in self.checks()]
        all_data_levels = list(set(all_data_levels))

        # build a list of checks in the qa_json for all the different data
        # levels
        all_checks = []
        for dl in all_data_levels:
            dl_sp = getattr(qa_json.qa, dl)
            if dl_sp is None:
                continue
            all_checks.extend(dl_sp.checks)

        for check in all_checks:
            inputs = check.get_or_add_inputs()
            check_ref = self.get_check_reference(check.info.id)
            if check_ref is None:
                # then this is a check within the qa json that is not
                # implemented by the plugin. This is ok, so skip and move
                # onto next check.
                continue
            supported_files = [
                QajsonFile(path=str(f), file_type=f_group, description=None)
                for (f, f_group) in files if check_ref.supports_file(f, f_group)]

            inputs.files.extend(supported_files)

    def update_qa_json_input_params(
            self,
            qa_json: QajsonRoot,
            check_id: str,
            params: List[QajsonParam]) -> NoReturn:
        """ Updates the input definitions included in the qa_json object
        to include the `params` list. Parameters are only added to a check if
        the check already exists in the `qa_json` object, and the check id
        matches that passed to this function.
        """
        all_data_levels = [check_ref.data_level for check_ref in self.checks()]
        all_data_levels = list(set(all_data_levels))  # remove duplicates

        # build a list of checks in the qa_json for all the different data
        # levels
        all_checks = []
        for dl in all_data_levels:
            dl_sp = getattr(qa_json.qa, dl)
            if dl_sp is None:
                continue
            all_checks.extend(dl_sp.checks)

        for check in all_checks:
            inputs = check.get_or_add_inputs()
            check_ref = self.get_check_reference(check.info.id)
            if check_ref is None:
                # then this is a check within the qa json that is not
                # implemented by the plugin. This is ok, so skip and move
                # onto next check.
                continue
            if check.info.id != check_id:
                # then the params aren't being assigned to this check, so
                # skip to next
                continue
            inputs.params.extend(params)

    def implements_check(self, check_id: str) -> bool:
        """ Does this plugin implement this check
        """
        return (self.get_check_reference(check_id) is not None)

    def get_check_reference(self, check_id: str) -> QaxCheckReference:
        """ gets a check reference with the given id, if not found return None
        """
        check = next((cr for cr in self.checks() if cr.id == check_id), None)
        return check

    def checks(self) -> List[QaxCheckReference]:
        """ returns a list of checks that are provided by this check tool.
        Each check includes a list of what file formats it supports and what
        data level it belongs too.

        * Must be implemented by plugin. *
        """
        raise NotImplementedError

    def run(
            self,
            qajson: QajsonRoot,
            progress_callback: Callable = None,
            qajson_update_callback: Callable = None,
            is_stopped: Callable = None
    ) -> NoReturn:
        """ Runs the checks implemented within the check tool plugin.

        * Must be implemented by plugin. *

        :param QajsonRoot qajson: QA JSON definition including the definition
            of what checks to run and what the inputs to those checks are (
            files and parameters).
        :progress_callback Callable: A reference to a function that will be
            passed a reference to a check tool plugin and a float (between 0.0
            and 1.0) representing the progress of the check tool execution.
            Optional.
        :qajson_update_callback: A check should pass any updated qajson into
            this callback to update the display of qajson
        :is_stopped: Each check & check tool should periodically call this function,
            if True is returned the check should finish operation
        """
        raise NotImplementedError

    def get_summary_details(self) -> List[Tuple[str, str]]:
        """ Gets a list of summary fields that can be extracted from this
        plugin. This is returned as a list of tuples, each tuple being two
        strings for the grouping of the field (section name) and the name
        of the field.

        Returns an empty list by default.
        """
        return []

    def get_summary_value(
            self,
            field_section: str,
            field_name: str,
            filename: str,
            qajson: QajsonRoot
        ) -> object:
        """ Gets the summary value from the qajson and returns it. This
        value may be a string or number type.
        """
        raise NotImplementedError("Plugins must implement get_summary_value function")

class QaxProfilePlugins():
    """ Manages a list of plugins that are specific to single profile
    """

    def __init__(self, plugins: List[QaxCheckToolPlugin]):
        self.plugins = plugins

    def update_qa_json(self, qa_json: QajsonRoot) -> NoReturn:
        """ Refer to docstring for QaxProfile. This function simply runs
        the equivalent QaxProfile function for each plugin.
        """
        for plugin in self.plugins:
            plugin.update_qa_json(qa_json)

    def update_qa_json_input_files(
            self, qa_json: QajsonRoot, files: List[Path]) -> NoReturn:
        """ Refer to docstring for QaxProfile. This function simply runs
        the equivalent QaxProfile function for each plugin.
        """
        for plugin in self.plugins:
            plugin.update_qa_json_input_files(qa_json, files)

    def update_qa_json_input_params(
            self,
            qa_json: QajsonRoot,
            check_id: str,
            params: List[QajsonParam]) -> NoReturn:
        """ Refer to docstring for QaxProfile. This function simply runs
        the equivalent QaxProfile function for each plugin.
        """
        for plugin in self.plugins:
            plugin.update_qa_json_input_params(qa_json, check_id, params)

    def get_plugin_for_check(
            self, check_id: str) -> Optional[QaxCheckToolPlugin]:
        """ Gets the plugin that this check belongs to or return None if not found
        """
        for plugin in self.plugins:
            check_ref = plugin.get_check_reference(check_id)
            if check_ref is not None:
                return plugin
        return None


class QaxPluginError(Exception):
    """ Custom Error for plugin issues
    """

    def __init__(self, message):
        super().__init__(message)


class QaxPluginLoadError(QaxPluginError):
    """ Custom Error for plugin issues
    """

    def __init__(self, message):
        super().__init__(message)


class QaxPlugins():
    """ Class manages plugins
    """
    _instance = None  # singleton instance

    @staticmethod
    def instance() -> 'QaxPlugins':
        if QaxPlugins._instance is None:
            raise QaxPluginError("Plugins have not been loaded")
        return QaxPlugins._instance

    def __init__(self):
        # list of `QaxCheckToolPlugin`
        self.plugins = []

    def _load_plugin(
            self,
            profile: QaxConfigProfile,
            check_tool: QaxConfigCheckTool
    ) -> QaxCheckToolPlugin:
        """ creates an instance of the plugin based on the `plugin_class`
        defined in the QA JSON config for the given `check_tool`
        """
        if check_tool.plugin_class is None:
            raise QaxPluginError(
                "No pluginClass defined for {}".format(check_tool.name))

        mod_class_bits = check_tool.plugin_class.rsplit('.', 1)
        if len(mod_class_bits) < 2:
            raise QaxPluginError(
                "pluginClass is expected to be a fully qualified class "
                "name (eg; `qax.hyo2.plugin.myplugin.MyPlugin`). "
                "{} was provided".format(check_tool.name))

        module_name, class_name = mod_class_bits
        try:
            plugin_module = importlib.import_module(module_name)
        except ModuleNotFoundError as ex:
            raise QaxPluginLoadError(
                "Could not load plugin module {}".format(module_name))

        if not hasattr(plugin_module, class_name):
            raise QaxPluginLoadError(
                "Could not load plugin class {} (of module {})"
                .format(class_name, module_name))

        plugin_class = getattr(plugin_module, class_name)
        plugin_instance = plugin_class()
        plugin_instance.plugin_class = check_tool.plugin_class
        plugin_instance.profile = profile
        if check_tool.icon is not None and len(check_tool.icon) > 0:
            plugin_instance.icon = check_tool.icon
        if check_tool.name is not None and len(check_tool.name) > 0:
            plugin_instance.name = check_tool.name
        if check_tool.description is not None and len(
                check_tool.description) > 0:
            plugin_instance.description = check_tool.description
        return plugin_instance

    def get_plugin(
            self,
            profile_name: str,
            check_tool_class: str
    ) -> Optional[QaxCheckToolPlugin]:
        """ Gets a plugin instance that has already been loaded based on the
        class name string (as included in QAX config) and the profile name.
        Will return None if no matching plugin found.
        """
        match = next(
            (
                p
                for p in self.plugins
                if (
                    p.plugin_class == check_tool_class and
                    p.profile.name == profile_name)
            ),
            None
        )
        return match

    def get_plugin_for_check(self, check_id: str) -> Optional[QaxCheckToolPlugin]:
        """ Gets the plugin that this check belongs to or return None if not found
        """
        for plugin in self.plugins:
            check_ref = plugin.get_check_reference(check_id)
            if check_ref is not None:
                return plugin
        return None

    def get_profile_plugins(
            self, profile: QaxConfigProfile) -> QaxProfilePlugins:
        """ Gets the plugins for this profile ONLY
        """
        plugins = []
        for check_tool in profile.check_tools:
            plugin = self.get_plugin(profile.name, check_tool.plugin_class)
            if plugin is None:
                continue
            plugins.append(plugin)
        return QaxProfilePlugins(plugins)

    def load(self, config: QaxConfig) -> NoReturn:
        """ Loads plugins defined in `config`
        """
        for profile in config.profiles:
            for check_tool in profile.check_tools:
                plugin = self._load_plugin(profile, check_tool)
                self.plugins.append(plugin)

        QaxPlugins._instance = self
