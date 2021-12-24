from fontTools.designspaceLib import DesignSpaceDocument
from fontTools.designspaceLib.statNames import StatNames

from .fixtures import datadir


def test_instance_getStatNames(datadir):
    doc = DesignSpaceDocument.fromfile(datadir / "test_v5_sourceserif.designspace")

    # TODO (Jany)

    assert doc.instances[0].getStatNames(doc) == StatNames(
        familyName="",
        styleName="",
        postScriptFontName="",
        styleMapFamilyName="",
        styleMapStyleName="",
    )


def test_detect_ribbi_aktiv(datadir):
    doc = DesignSpaceDocument.fromfile(datadir / "test_v5_aktiv.designspace")

    assert doc.getRibbiMapping() == {
        (("Weight", 84), ("Width", 100), ("Italic", 0)): "regular",
        (("Weight", 133), ("Width", 100), ("Italic", 0)): "bold",
        (("Weight", 84), ("Width", 100), ("Italic", 1)): "italic",
        (("Weight", 133), ("Width", 100), ("Italic", 1)): "bold italic",
    }
