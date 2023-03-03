""" Utility functions and classes to support the use of QAJSON within the QAX
user interface
"""
from collections import OrderedDict
from pathlib import Path
from typing import List, TypeVar, Optional, Tuple

import pandas as pd
import xlsxwriter

from ausseabed.qajson.model import QajsonRoot, QajsonInfo
from hyo2.qax.lib.plugin import QaxProfilePlugins, QaxCheckToolPlugin

# summary type, type for the summary field value
ST = TypeVar('ST')


class QajsonSummaryField():

    def __init__(self, name: str, value: ST = None) -> None:
        self.name = name
        self.value = value


class QajsonSummarySection():

    def __init__(self, name: str) -> None:
        self.name = name
        self.fields: List[QajsonSummaryField] = []

    def add_field(self, field_name: str) -> QajsonSummaryField:
        new_field = QajsonSummaryField(field_name)
        self.fields.append(new_field)
        return new_field
    
    def get_or_add_field(self, field_name: str) -> QajsonSummaryField:
        field = next(
            (f for f in self.fields if f.name == field_name),
            None
        )
        if field is None:
            return self.add_field(field_name)
        else:
            return field


class QajsonFileSummary():

    def __init__(self, filename) -> None:
        self.filename = filename
        self.sections: List[QajsonSummarySection] = []

    @property
    def summary_heading_label(self) -> str:
        """ Generates a nice name based on the filename for inclusion
        into the summary file.
        Basic logic is as follows.
        1. Identify which character is used to separate tokens in the
           filename, based on how many times that character appears in
           the filename.
        2. Split the filename by that separator character
        3. Rejoin the first three tokens with the separator

        If there is no separator, then just use the filename without the
        extension.
        """
        potential_separators = ['-', '_', ' ']
        name_only = Path(self.filename).stem
        separator = None
        separator_count = 0
        for sep in potential_separators:
            c = name_only.count(sep)
            if c > separator_count:
                separator = sep
                separator_count = c

        if separator_count == 0:
            return name_only

        name_tokens = name_only.split(separator)
        name_tokens = name_tokens[:3]

        name = separator.join(name_tokens)

        return name

    def add_section(self, section_name: str) -> QajsonSummarySection:
        new_section = QajsonSummarySection(section_name)
        self.sections.append(new_section)
        return new_section
    
    def get_or_add_section(self, section_name: str) -> QajsonSummarySection:

        section = next(
            (s for s in self.sections if s.name == section_name),
            None
        )
        if section is None:
            return self.add_section(section_name)
        else:
            return section

    def clone(self) -> "QajsonFileSummary":
        clone_fs = QajsonFileSummary(self.filename)
        for s in self.sections:
            clone_s = clone_fs.get_or_add_section(s.name)
            for f in s.fields:
                clone_s.get_or_add_field(f.name)
        return clone_fs

    def row_labels(self) -> List[Tuple[str, bool]]:
        """ Generates the list of row labels that should appear in the output
        table.
        """
        rows = []
        # the top left corner is blank

        for section in self.sections:
            if section.name == 'header':
                # then there's no label for the header
                pass
            else:
                rows.append((section.name, True))
            # now include a label for each one of the fields
            for field in section.fields:
                rows.append((field.name, False))

        return rows

    def row_values(self) -> List[str]:
        """ Generates the list of row values that should appear in the output
        table.
        """
        values = []
        for section in self.sections:
            if section.name == 'header':
                pass
            else:
                # the blank line where the section label runs across
                values.append("")
            # now include a label for each one of the fields
            for field in section.fields:
                values.append(field.value)

        return values


class QajsonTableSummaryCheck():

    def __init__(self, check_info: QajsonInfo) -> None:
        self.check_info = check_info
        self.file_summaries = OrderedDict()


class QajsonTableSummary():

    def __init__(self, qajson: QajsonRoot, plugins: QaxProfilePlugins) -> None:
        self.check_summaries = None
        self.qajson = qajson
        self.plugins = plugins

        # TODO - this list should be included in the ausseabed.qajson
        # pacakge somewhere
        self.all_data_levels = ['raw_data', 'chart_adequacy', 'survey_products']

    def get_header_fields(self) -> List[str]:
        """ Get a list of field that are included in the header section for all
        files.
        """
        # headers to be included irrespective of the plugins group selected
        constant_headers = [
            "File Name",
            "Latest Update",
            "Summary",
        ]
        return constant_headers

    def initialise_check_list(self) -> None:
        """ Builds the initial list of all checks that were included
        in the QAJSON
        """
        # build a dictionary of all the checks based on the check ID
        # this will ensure we only have a list of unique checks
        all_checks = OrderedDict()
        
        for dl_name in self.all_data_levels:
            dl = self.qajson.qa.get_data_level(dl_name)
            if dl is None:
                continue
            for check in dl.checks:
                ci = check.info
                all_checks[ci.id] = QajsonTableSummaryCheck(ci)

        self.check_summaries = all_checks


    def initialise_file_list(self) -> None:
        """ Builds a list of all files under each QajsonTableSummaryCheck
        """
        self.all_files = []

        for dl_name in self.all_data_levels:
            dl = self.qajson.qa.get_or_add_data_level(dl_name)
            for check in dl.checks:
                input_files = check.inputs.files
                # most checks at this stage of processing will only have
                # one input file ni the qajson. Regardless of if they
                # have more, just use the first one.
                if len(input_files) == 0:
                    continue
                input_file = input_files[0]
                input_file_name = input_file.path
                if input_file_name not in self.all_files:
                    self.all_files.append(input_file_name)
                self.check_summaries[check.info.id].file_summaries[input_file_name] = check

    def build_template(self) -> None:
        self.template_file_summary = QajsonFileSummary(None)

        # add in the header fields
        for field_name in self.get_header_fields():
            section = self.template_file_summary.get_or_add_section("header")
            section.get_or_add_field(field_name)

        # now loop through the check results that we have in the qajson
        # to find the other fields that should be included
        for _, check in self.check_summaries.items():
            qajson_check_info = check.check_info
            plugin = self.plugins.get_plugin_for_check(qajson_check_info.id)
            if plugin is not None:
                sd_list = plugin.get_summary_details()
                for section_name, field_name in sd_list:
                    section = self.template_file_summary.get_or_add_section(
                        section_name)
                    section.get_or_add_field(field_name)

    def __get_plugin(self, field_name: str, section_name: str) -> Optional[QaxCheckToolPlugin]:
        """ Gets a plugin that provides this field value
        """
        for _, check in self.check_summaries.items():
            qajson_check_info = check.check_info
            plugin = self.plugins.get_plugin_for_check(qajson_check_info.id)
            if plugin is not None:
                sd_list = plugin.get_summary_details()
                for p_section_name, p_field_name in sd_list:
                    if p_section_name == section_name and p_field_name == field_name:
                        return plugin
        return None

    def _get_field_value(self, field_name: str, section_name: str, filename: str) -> object:
        plugin = self.__get_plugin(field_name, section_name)
        if plugin is None:
            return "no plugin"
        value = plugin.get_summary_value(section_name, field_name, filename, self.qajson)
        return value


    def build(self) -> None:
        self.file_summaries: List[QajsonFileSummary] = []
        for filename in self.all_files:
            new_summary = self.template_file_summary.clone()
            new_summary.filename = filename
            self.file_summaries.append(new_summary)
            for section in new_summary.sections:
                for field in section.fields:
                    value = self._get_field_value(field.name, section.name, filename)
                    field.value = value





    @property
    def rows(self) -> int:
        """ Gets the number of rows that will be output base on the extracted
        summary information
        """
        if len(self.file_summaries) < 1:
            raise RuntimeError("Can't get row count until summary data is extracted")
        file_summary = self.file_summaries[0]

    @property
    def columns(self) -> int:
        """ Number of columns in this table
        """
        # number of files plus 1 column to include the labels
        return len(self.file_summaries) + 1




class QajsonExporter():

    def __init__(self) -> None:
        # name of the exporter
        self.name = None
        # description for the exporter
        self.description = None
        # extension of the filename the exporter generates
        self.extension = None

    def export(qajson: QajsonRoot, file: Path) -> None:
        """ Exports the `qajson` object to the `file`
        """
        raise NotImplemented("Export function must be overwritten")


class QajsonExcelExporter(QajsonExporter):

    def __init__(self) -> None:
        super().__init__()
        self.name = "Microsoft Excel"
        self.description = "Save QAJSON to Microsoft Excel workbook"
        self.extension = "xlsx"

    def _get_safe_shortname(self, file_summary: QajsonFileSummary, existing_data: List) -> str:
        """ Ensures there are no duplicate short names included in the orderedDict
        that is converted to pandas and then xls. Duplicate names must be avoided
        as the dictionary will simply replace existing entries.
        """
        short_name = file_summary.summary_heading_label
        count = 0
        for fs in existing_data:
            if fs.summary_heading_label == short_name:
                count += 1

        if count == 0:
            return short_name
        else:
            return f"{short_name} ({count})"


    def _generate_summary_dataframe(
            self,
            tableSummary: QajsonTableSummary
        ) -> pd.DataFrame:
        """ Generate pandas data frame including summary data for all the
        checks and files in this tableSummary
        """
        processed_summaries = []

        data = OrderedDict()
        row_label = [rl[0] for rl in tableSummary.template_file_summary.row_labels()]
        data[''] = row_label
        for file_summary in tableSummary.file_summaries:
            short_filename = self._get_safe_shortname(
                file_summary, processed_summaries)
            data[short_filename] = file_summary.row_values()
            processed_summaries.append(file_summary)

        df = pd.DataFrame(data)
        return df

    def _write_formatted_file(self, dataFrame: pd.DataFrame, tableSummary: QajsonTableSummary, output_file: Path) -> None:
        writer = pd.ExcelWriter(
            output_file,
            engine='xlsxwriter'
        )
        dataFrame.to_excel(writer, sheet_name='Sheet1', index=False)
        workbook  = writer.book
        worksheet: xlsxwriter.workbook.Worksheet = writer.sheets['Sheet1']

        sectionStyle = workbook.add_format({'bg_color': 'B4C6E7'})
        for rowIndex, value in enumerate(tableSummary.template_file_summary.row_labels()):
            _, isSectionHeading = value
            if isSectionHeading:
                # +1 to row index because excel is 1 based indexing
                worksheet.set_row(rowIndex + 1, None, sectionStyle)

        writer.close()

    def export(
            self,
            qajson: QajsonRoot,
            file: Path,
            plugins: QaxProfilePlugins
        ) -> None:
        """ Writes QAJSON to an XLSX file
        """

        tableSummary = QajsonTableSummary(qajson, plugins)
        tableSummary.initialise_check_list()
        tableSummary.initialise_file_list()
        tableSummary.build_template()
        tableSummary.build()

        df = self._generate_summary_dataframe(tableSummary)
        self._write_formatted_file(df, tableSummary, output_file=file)



