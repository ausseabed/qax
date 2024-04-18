from pathlib import Path

from hyo2.qax.lib.plugin import QaxPlugins, QaxCheckToolPlugin, QaxFileGroup

"""
Offers plugin related capability as a service that can be injected into
other classes
"""
class PluginService:

    def __init__(self, plugins: list[QaxCheckToolPlugin]) -> None:
        self.plugins = plugins

    def get_all_file_groups(self) -> list[QaxFileGroup]:
        all:list[QaxFileGroup] = []
        for plugin in self.plugins:
            for file_group in plugin.get_file_groups():
                all.append(file_group)
        return all

    def get_all_file_group_names(self) -> list[str]:
        all = self.get_all_file_groups()
        all_names = [fg.name for fg in all]
        all_names.append("Unknown")
        # remove duplicates, and sort
        all_names = sorted(list(set(all_names)))
        return all_names

    def identify_file_group(self, filename: str) -> str:
        """
        Identifies the file group this file belongs to based on
        its name (extension). If no matching filegroup is found
        then 'Unknown' is returned
        """
        for plugin in self.plugins:
            for file_group in plugin.get_file_groups():
                ft = file_group.matching_file_type(Path(filename))
                if ft is not None:
                    return file_group.name
        
        return 'Unknown'

    def get_file_details(self, filename: str) -> str:
        for plugin in self.plugins:
            for file_group in plugin.get_file_groups():
                for check_ref in plugin.checks():
                    if check_ref.supports_file(Path(filename), file_group.name):
                        return plugin.get_file_details(filename)

        return ""
