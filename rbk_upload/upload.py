import os
import sys
import logging
from deriva_common import urlquote, read_config
from deriva_io.deriva_upload import DerivaUpload
from deriva_io.deriva_upload_cli import DerivaUploadCLI
from deriva_qt.upload_gui.upload_app import DerivaUploadGUI

DESC = "RBK Data Upload Utility"
INFO = "For more information see: https://github.com/informatics-isi-edu/rbk-upload"


class RBKUpload(DerivaUpload):

    def __init__(self, config_file=None, credential_file=None, server=None):
        DerivaUpload.__init__(self, config_file, credential_file, server)

    @classmethod
    def getVersion(cls):
        return "0.2.0"

    @classmethod
    def getConfigPath(cls):
        return "~/.deriva/rbk/rbk-upload"

    @classmethod
    def getServers(cls):
        return [
            {
                "host": "www.rebuildingakidney.org",
                "desc": "RBK Production",
                "catalog_id": 2,
                "default": True
            },
            {
                "host": "staging.rebuildingakidney.org",
                "desc": "RBK Staging",
                "catalog_id": 2
            },
            {
                "host": "dev.rebuildingakidney.org",
                "desc": "RBK Development",
                "catalog_id": 2
            }
          ]


def gui_main():
    gui = DerivaUploadGUI(RBKUpload, DESC, INFO)
    gui.main()


def cli_main():
    cli = DerivaUploadCLI(RBKUpload, DESC, INFO)
    cli.main()

if __name__ == '__main__':
    sys.exit(gui_main())
