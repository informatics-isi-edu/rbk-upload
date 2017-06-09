import os
import sys
import logging
from deriva_common import urlquote
from deriva_io.deriva_upload import DerivaUpload
from deriva_io.deriva_upload_cli import DerivaUploadCLI
from deriva_qt.upload_gui.upload_app import DerivaUploadGUI

DESC = "RBK Data Upload Utility"
INFO = "For more information see: https://github.com/informatics-isi-edu/rbk-upload"


class RBKUpload(DerivaUpload):

    config_dir = "~/.deriva/rbk/rbk-upload"
    metadata = dict()
    column_map = dict()

    def __init__(self, config, credentials):
        DerivaUpload.__init__(self, config, credentials)
        self.column_map.update(config.get("column_map", {}))

    @staticmethod
    def getInstance(config=None, credentials=None):
        return RBKUpload(config, credentials)

    def getDeployedConfigFilePath(self):
        return os.path.join(os.path.expanduser(
            os.path.normpath(self.config_dir)), DerivaUpload.DefaultConfigFileName)

    def getDeployedTransferStateFilePath(self):
        return os.path.join(os.path.expanduser(
            os.path.normpath(self.config_dir)), DerivaUpload.DefaultTransferStateFileName)

    def cleanup(self):
        DerivaUpload.cleanup(self)

    def _getExtensionMetadata(self, ext):
        ext_map = self.config.get("file_ext_mappings", [])
        entry = ext_map.get(ext)
        if entry:
            self.metadata.update(entry)

    def _getFileMetadata(self, file_path, asset_mapping, match_groupdict):
        """
        Helper function that queries the catalog to get required metadata for a given file/asset
        """
        file_name = self.getFileDisplayName(file_path)
        logging.info("Computing metadata for file: [%s]." % file_name)

        self.metadata.clear()
        self.metadata.update(match_groupdict)
        for k, v in self.metadata.items():
            self.metadata[k] = urlquote(v)

        self.metadata["basename"] = self.getFileDisplayName(file_path)
        self.metadata["file_size"] = self.getFileSize(file_path)

        logging.info("Computing checksums for file: [%s]. Please wait..." % file_name)
        hashes = self.getFileHashes(file_path, asset_mapping.get('checksum_types', ['sha256']))
        for alg, checksum in hashes.items():
            alg = alg.lower()
            self.metadata[alg] = urlquote(checksum[0])
            self.metadata[alg + "_base64"] = checksum[1]

        for uri in asset_mapping.get("metadata_query_templates", []).values():
            try:
                path = uri % self.metadata
            except KeyError:
                continue
            result = self.catalog.get(path).json()
            if result:
                self.metadata.update(result[0])

        self._getExtensionMetadata(self.metadata.get("file_ext"))

        for k, v in asset_mapping.get("column_value_templates", {}).items():
            try:
                self.metadata[k] = v % self.metadata
            except KeyError:
                continue

    def _getFileRecord(self, asset_mapping):
        """
        Helper function that queries the catalog to get a file record, creating it if not found.
        :return: the file record
        """
        self.metadata['base_record_type'] = self.getCatalogTable(asset_mapping)
        rqt = asset_mapping['record_query_templates']
        path = rqt.get("get_record") % self.metadata
        result = self.catalog.get(path).json()
        if result:
            self.metadata.update(result[0])
        else:
            row = self.processTemplates(self.metadata, self.column_map)
            result = self._catalogRecordCreate(self.getCatalogTable(asset_mapping), row)
            if result:
                self.metadata.update(result[0])

        return self.processTemplates(self.metadata, self.column_map, allowNone=True)

    def uploadFile(self, file_path, asset_mapping, match_groupdict, callback=None):
        """
        Primary API subclass function.
        :param file_path:
        :param asset_mapping:
        :param match_groupdict:
        :param callback:
        :return:
        """
        logging.info("Processing file: [%s]" % file_path)

        # 1. Populate metadata by querying the catalog
        self._getFileMetadata(file_path, asset_mapping, match_groupdict)

        # 2. Check for an existing record and create a new one if needed
        current_row = self._getFileRecord(asset_mapping)

        # 3. Perform the Hatrac upload
        self.metadata["URI"] = asset_mapping["hatrac_templates"]["hatrac_uri"] % self.metadata
        self.metadata["hatrac_filename"] = asset_mapping["hatrac_templates"]["hatrac_filename"] % self.metadata
        self.metadata["content-disposition"] = asset_mapping["hatrac_templates"]["content-disposition"] % self.metadata
        self._hatracUpload(self.metadata["URI"],
                           file_path,
                           md5=self.metadata.get("md5_base64"),
                           sha256=self.metadata.get("sha256_base64"),
                           content_type=self.guessContentType(file_path),
                           content_disposition=self.metadata.get("content-disposition"),
                           chunked=True,
                           create_parents=True,
                           allow_versioning=True,
                           callback=callback)

        # 4. Update the catalog
        updated_row = self.processTemplates(self.metadata, self.column_map)
        file_name = self.getFileDisplayName(file_path)
        if updated_row != current_row:
            logging.info("Updating catalog for file [%s]" % file_name)
            self._catalogRecordUpdate(self.getCatalogTable(asset_mapping), current_row, updated_row)
        else:
            logging.info("Update not required. Catalog already up-to-date for file: [%s]" % file_name)


def gui_main():
    gui = DerivaUploadGUI(RBKUpload, DESC, INFO)
    gui.main()


def cli_main():
    cli = DerivaUploadCLI(RBKUpload, DESC, INFO)
    cli.main()

if __name__ == '__main__':
    sys.exit(gui_main())
