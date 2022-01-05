from fontTools.designspaceLib import DesignSpaceDocument
from fontTools.designspaceLib.statNames import StatNames

from .fixtures import datadir


def test_instance_getStatNames(datadir):
    doc = DesignSpaceDocument.fromfile(datadir / "test_v5_sourceserif.designspace")

    assert doc.instances[0].getStatNames(doc) == StatNames(
        familyNames={"en": "Source Serif 4"},
        styleNames={"en": "Caption ExtraLight"},
        postScriptFontName="SourceSerif4-CaptionExtraLight",
        styleMapFamilyNames={"en": "Source Serif 4 Caption ExtraLight"},
        styleMapStyleName="regular",
    )


def test_detect_ribbi_aktiv(datadir):
    doc = DesignSpaceDocument.fromfile(datadir / "test_v5_aktiv.designspace")

    for instance in doc.instances:
        if instance.getFullDesignLocation(doc) == {
            "Weight": 115,
            "Width": 125,
            "Italic": 1,
        }:
            extended_semibold_italic = instance

    assert extended_semibold_italic.getStatNames(doc) == StatNames(
        familyNames={"en": "Aktiv Grotesk"},
        styleNames={"en": "Ex SemiBold Italic"},
        postScriptFontName="AktivGrotesk-ExSemiBoldItalic",
        styleMapFamilyNames={"en": "Aktiv Grotesk Ex SemiBold"},
        styleMapStyleName="italic",
    )

    for instance in doc.instances:
        if instance.getFullDesignLocation(doc) == {
            "Weight": 133,
            "Width": 75,
            "Italic": 1,
        }:
            condensed_bold_italic = instance

    assert condensed_bold_italic.getStatNames(doc) == StatNames(
        familyNames={"en": "Aktiv Grotesk"},
        styleNames={"en": "Cd Bold Italic"},
        postScriptFontName="AktivGrotesk-CdBoldItalic",
        styleMapFamilyNames={"en": "Aktiv Grotesk Cd"},
        styleMapStyleName="bold italic",
    )
