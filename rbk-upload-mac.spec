# -*- mode: python -*-

block_cipher = None


a = Analysis(['rbk_upload/upload.py'],
             pathex=[''],
             binaries=None,
             datas=[('conf/config.json', 'conf')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='RBK Upload',
          strip=False,
          upx=False,
          debug=env.get("DEBUG", False),
          console=env.get("DEBUG", False),
          icon='rbk_upload/images/rbk_icon.icns')

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               name='RBK Upload')

app = BUNDLE(coll,
         name='RBK Upload.app',
         icon='rbk_upload/images/rbk_icon.icns',
         bundle_identifier='org.qt-project.Qt.QtWebEngineCore',
         info_plist={
            'CFBundleDisplayName': 'RBK File Upload Utility',
            'CFBundleShortVersionString':'0.1.0',
            'NSPrincipalClass':'NSApplication',
            'NSHighResolutionCapable': 'True'
         })