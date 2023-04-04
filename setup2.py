from plistlib import Plist
from setuptools import setup
plist = Plist.fromFile('Info.plist')
plist.update(dict(
    LSPrefersPPC=True,
))
setup(
    app=['moin_moin.py'],
options=dict(py2app=dict(
    plist=plist,
)),
)