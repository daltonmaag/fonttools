from pathlib import Path

import pytest
from fontTools.designspaceLib import (
    AxisDescriptor as Axis,
    DesignSpaceDocument,
    DiscreteAxisDescriptor as DiscreteAxis,
    AxisLabelDescriptor as AxisLabel,
    LocationLabelDescriptor as LocationLabel,
    VariableFontDescriptor as VariableFont,
    RangeAxisSubsetDescriptor,
    ValueAxisSubsetDescriptor,
)


@pytest.fixture
def datadir():
    return Path(__file__).parent / "data"


def test_read_v5_document_simple(datadir):
    doc = DesignSpaceDocument.fromfile(datadir / "test_v5.designspace")

    assert doc.locationLabels == [
        LocationLabel(name="asdf", location={"weight": 10, "width": 20, "Italic": 0}),
        LocationLabel(name="dfdf", location={"weight": 100, "width": 200, "Italic": 1}),
    ]

    expected_axes = [
        Axis(
            tag="wght",
            name="weight",
            minimum=0,
            maximum=1000,
            default=0,
            labelNames={"en": "Wéíght", "fa-IR": "قطر"},
            map=[(200, 0), (300, 100), (400, 368), (600, 600), (700, 824), (900, 1000)],
            axisOrdering=None,
            axisLabels=[
                AxisLabel(
                    name="Extra Light",
                    userMinimum=200,
                    userValue=200,
                    userMaximum=250,
                    labelNames={"de": "Extraleicht", "fr": "Extra léger"},
                ),
                AxisLabel(
                    name="Light", userMinimum=250, userValue=300, userMaximum=350
                ),
                AxisLabel(
                    name="Regular",
                    userMinimum=350,
                    userValue=400,
                    userMaximum=450,
                    elidable=True,
                ),
                AxisLabel(
                    name="Semi Bold", userMinimum=450, userValue=600, userMaximum=650
                ),
                AxisLabel(name="Bold", userMinimum=650, userValue=700, userMaximum=850),
                AxisLabel(
                    name="Black", userMinimum=850, userValue=900, userMaximum=900
                ),
            ],
        ),
        Axis(
            tag="wdth",
            name="width",
            minimum=0,
            maximum=1000,
            default=15,
            hidden=True,
            labelNames={"fr": "Chasse"},
            map=[(0, 10), (15, 20), (401, 66), (1000, 990)],
            axisOrdering=None,
            axisLabels=[
                AxisLabel(name="Condensed", userValue=0),
                AxisLabel(
                    name="Normal", elidable=True, olderSibling=True, userValue=15
                ),
                AxisLabel(name="Wide", userValue=401),
                AxisLabel(name="Extra Wide", userValue=1000),
            ],
        ),
        DiscreteAxis(
            tag="ital",
            name="Italic",
            values=[0, 1],
            default=0,
            axisOrdering=None,
            axisLabels=[
                AxisLabel(name="Roman", userValue=0, elidable=True, linkedUserValue=1),
                AxisLabel(name="Italic", userValue=1),
            ],
        ),
    ]

    assert [v.asdict() for v in doc.axes] == [v.asdict() for v in expected_axes]

    expected_variable_fonts = [
        VariableFont(
            filename="Test_WghtWdth.ttf",
            axisSubsets=[
                RangeAxisSubsetDescriptor(name="Weight"),
                RangeAxisSubsetDescriptor(name="Width"),
            ],
            lib={"com.vtt.source": "sources/vtt/Test_WghtWdth.vtt"},
        ),
        VariableFont(
            filename="Test_Wght.ttf",
            axisSubsets=[RangeAxisSubsetDescriptor(name="Weight")],
            lib={"com.vtt.source": "sources/vtt/Test_Wght.vtt"},
        ),
        VariableFont(
            filename="TestCd_Wght.ttf",
            axisSubsets=[
                RangeAxisSubsetDescriptor(name="Weight"),
                ValueAxisSubsetDescriptor(name="Width", userValue=0),
            ],
        ),
        VariableFont(
            filename="TestWd_Wght.ttf",
            axisSubsets=[
                RangeAxisSubsetDescriptor(name="Weight"),
                ValueAxisSubsetDescriptor(name="Width", userValue=1000),
            ],
        ),
        VariableFont(
            filename="TestItalic_Wght.ttf",
            axisSubsets=[
                RangeAxisSubsetDescriptor(name="Weight"),
                ValueAxisSubsetDescriptor(name="Italic", userValue=1),
            ],
        ),
        VariableFont(
            filename="TestRB_Wght.ttf",
            axisSubsets=[
                RangeAxisSubsetDescriptor(
                    name="Weight", userMinimum=400, userDefault=400, userMaximum=700
                ),
                ValueAxisSubsetDescriptor(name="Italic", userValue=0),
            ],
        ),
    ]
    assert [v.asdict() for v in doc.variableFonts] == [
        v.asdict() for v in expected_variable_fonts
    ]


def test_read_v5_document_decovar(datadir):
    doc = DesignSpaceDocument.fromfile(datadir / "test_v5_decovar.designspace")

    assert not doc.variableFonts

    expected_axes = [
        Axis(default=0, maximum=1000, minimum=0, name="Inline", tag="BLDA"),
        Axis(default=0, maximum=1000, minimum=0, name="Shearded", tag="TRMD"),
        Axis(default=0, maximum=1000, minimum=0, name="Rounded Slab", tag="TRMC"),
        Axis(default=0, maximum=1000, minimum=0, name="Stripes", tag="SKLD"),
        Axis(default=0, maximum=1000, minimum=0, name="Worm Terminal", tag="TRML"),
        Axis(default=0, maximum=1000, minimum=0, name="Inline Skeleton", tag="SKLA"),
        Axis(
            default=0, maximum=1000, minimum=0, name="Open Inline Terminal", tag="TRMF"
        ),
        Axis(default=0, maximum=1000, minimum=0, name="Inline Terminal", tag="TRMK"),
        Axis(default=0, maximum=1000, minimum=0, name="Worm", tag="BLDB"),
        Axis(default=0, maximum=1000, minimum=0, name="Weight", tag="WMX2"),
        Axis(default=0, maximum=1000, minimum=0, name="Flared", tag="TRMB"),
        Axis(default=0, maximum=1000, minimum=0, name="Rounded", tag="TRMA"),
        Axis(default=0, maximum=1000, minimum=0, name="Worm Skeleton", tag="SKLB"),
        Axis(default=0, maximum=1000, minimum=0, name="Slab", tag="TRMG"),
        Axis(default=0, maximum=1000, minimum=0, name="Bifurcated", tag="TRME"),
    ]
    assert [v.asdict() for v in doc.axes] == [v.asdict() for v in expected_axes]

    assert doc.locationLabels == [
        LocationLabel(name="Default", elidable=True, location={}),
        LocationLabel(
            name="Open", location={"Inline": 1000}, labelNames={"de": "Offen"}
        ),
        LocationLabel(name="Worm", location={"Worm": 1000}),
        LocationLabel(name="Checkered", location={"Inline Skeleton": 1000}),
        LocationLabel(name="Checkered Reverse", location={"Inline Terminal": 1000}),
        LocationLabel(name="Striped", location={"Stripes": 500}),
        LocationLabel(name="Rounded", location={"Rounded": 1000}),
        LocationLabel(name="Flared", location={"Flared": 1000}),
        LocationLabel(
            name="Flared Open", location={"Inline Skeleton": 1000, "Flared": 1000}
        ),
        LocationLabel(name="Rounded Slab", location={"Rounded Slab": 1000}),
        LocationLabel(name="Sheared", location={"Shearded": 1000}),
        LocationLabel(name="Bifurcated", location={"Bifurcated": 1000}),
        LocationLabel(
            name="Inline",
            location={"Inline Skeleton": 500, "Open Inline Terminal": 500},
        ),
        LocationLabel(name="Slab", location={"Slab": 1000}),
        LocationLabel(name="Contrast", location={"Weight": 1000}),
        LocationLabel(
            name="Fancy",
            location={"Inline Skeleton": 1000, "Flared": 1000, "Weight": 1000},
        ),
        LocationLabel(
            name="Mayhem",
            location={
                "Inline Skeleton": 1000,
                "Worm Skeleton": 1000,
                "Rounded": 500,
                "Flared": 500,
                "Rounded Slab": 750,
                "Bifurcated": 500,
                "Open Inline Terminal": 250,
                "Slab": 750,
                "Inline Terminal": 250,
                "Worm Terminal": 250,
                "Weight": 750,
                "Worm": 1000,
            },
        ),
    ]

    assert [i.location for i in doc.instances] == [
        "Default",
        "Open",
        "Worm",
        "Checkered",
        "Checkered Reverse",
        "Striped",
        "Rounded",
        "Flared",
        "Flared Open",
        "Rounded Slab",
        "Sheared",
        "Bifurcated",
        "Inline",
        "Slab",
        "Contrast",
        "Fancy",
        "Mayhem",
    ]


def test_read_v5_document_discrete(datadir):
    doc = DesignSpaceDocument.fromfile(datadir / "test_v5_discrete.designspace")

    assert not doc.locationLabels
    assert not doc.variableFonts

    expected_axes = [
        DiscreteAxis(
            default=400,
            values=[400, 700, 900],
            name="Weight",
            tag="wght",
            axisLabels=[
                AxisLabel(
                    name="Regular", userValue=400, elidable=True, linkedUserValue=700
                ),
                AxisLabel(name="Bold", userValue=700),
                AxisLabel(name="Black", userValue=900),
            ],
        ),
        DiscreteAxis(
            default=100,
            values=[75, 100],
            name="Width",
            tag="wdth",
            axisLabels=[
                AxisLabel(name="Narrow", userValue=75),
                AxisLabel(name="Normal", userValue=100, elidable=True),
            ],
        ),
        DiscreteAxis(
            default=0,
            values=[0, 1],
            name="Italic",
            tag="ital",
            axisLabels=[
                AxisLabel(name="Roman", userValue=0, elidable=True, linkedUserValue=1),
                AxisLabel(name="Italic", userValue=1),
            ],
        ),
    ]
    assert [v.asdict() for v in doc.axes] == [v.asdict() for v in expected_axes]


def test_read_v5_document_aktiv(datadir):
    doc = DesignSpaceDocument.fromfile(datadir / "test_v5_aktiv.designspace")

    assert not doc.locationLabels

    expected_axes = [
        Axis(
            tag="wght",
            name="Weight",
            minimum=100,
            default=400,
            maximum=900,
            map=[
                (100, 22),
                (200, 38),
                (300, 57),
                (400, 84),
                (500, 98),
                (600, 115),
                (700, 133),
                (800, 158),
                (900, 185),
            ],
            axisOrdering=1,
            axisLabels=[
                AxisLabel(name="Hair", userValue=100),
                AxisLabel(userValue=200, name="Thin"),
                AxisLabel(userValue=300, name="Light"),
                AxisLabel(
                    userValue=400, name="Regular", elidable=True, linkedUserValue=700
                ),
                AxisLabel(userValue=500, name="Medium"),
                AxisLabel(userValue=600, name="SemiBold"),
                AxisLabel(userValue=700, name="Bold"),
                AxisLabel(userValue=800, name="XBold"),
                AxisLabel(userValue=900, name="Black"),
            ],
        ),
        Axis(
            tag="wdth",
            name="Width",
            minimum=75,
            default=100,
            maximum=125,
            axisOrdering=0,
            axisLabels=[
                AxisLabel(name="Cd", userValue=75),
                AxisLabel(name="Normal", elidable=True, userValue=100),
                AxisLabel(name="Ex", userValue=125),
            ],
        ),
        Axis(
            tag="ital",
            name="Italic",
            minimum=0,
            default=0,
            maximum=1,
            axisOrdering=2,
            axisLabels=[
                AxisLabel(
                    name="Upright", userValue=0, elidable=True, linkedUserValue=1
                ),
                AxisLabel(name="Italic", userValue=1),
            ],
        ),
    ]

    assert [v.asdict() for v in doc.axes] == [v.asdict() for v in expected_axes]

    expected_variable_fonts = [
        VariableFont(
            filename="AktivGroteskVF_WghtWdthItal.ttf",
            axisSubsets=[
                RangeAxisSubsetDescriptor(name="Weight"),
                RangeAxisSubsetDescriptor(name="Width"),
                RangeAxisSubsetDescriptor(name="Italic"),
            ],
        ),
        VariableFont(
            filename="AktivGroteskVF_WghtWdth.ttf",
            axisSubsets=[
                RangeAxisSubsetDescriptor(name="Weight"),
                RangeAxisSubsetDescriptor(name="Width"),
            ],
        ),
        VariableFont(
            filename="AktivGroteskVF_Wght.ttf",
            axisSubsets=[
                RangeAxisSubsetDescriptor(name="Weight"),
            ],
        ),
        VariableFont(
            filename="AktivGroteskVF_Italics_WghtWdth.ttf",
            axisSubsets=[
                RangeAxisSubsetDescriptor(name="Weight"),
                RangeAxisSubsetDescriptor(name="Width"),
                ValueAxisSubsetDescriptor(name="Italic", userValue=1),
            ],
        ),
        VariableFont(
            filename="AktivGroteskVF_Italics_Wght.ttf",
            axisSubsets=[
                RangeAxisSubsetDescriptor(name="Weight"),
                ValueAxisSubsetDescriptor(name="Italic", userValue=1),
            ],
        ),
    ]
    assert [v.asdict() for v in doc.variableFonts] == [
        v.asdict() for v in expected_variable_fonts
    ]


def test_convert_v5_document_aktiv_to_v4(datadir):
    doc = DesignSpaceDocument.fromfile(datadir / "test_v5_aktiv.designspace")

    import fontTools.designspaceLib.convert5to4

    variable_fonts, stylespace = fontTools.designspaceLib.convert5to4.convert5to4(doc)
    for vf_name, vf in variable_fonts.items():
        vf.lib["org.statmake.stylespace"] = stylespace.to_dict()
        vf.write(datadir / "out" / (vf_name + ".designspace"))


def test_convert_v5_document_sourceserif_to_v4(datadir):
    doc = DesignSpaceDocument.fromfile(datadir / "test_v5_sourceserif.designspace")

    import fontTools.designspaceLib.convert5to4

    variable_fonts, stylespace = fontTools.designspaceLib.convert5to4.convert5to4(doc)
    for vf_name, vf in variable_fonts.items():
        vf.lib["org.statmake.stylespace"] = stylespace.to_dict()
        vf.write(datadir / "out" / (vf_name + ".designspace"))


def test_detect_ribbi_aktiv(datadir):
    doc = DesignSpaceDocument.fromfile(datadir / "test_v5_aktiv.designspace")

    from fontTools.designspaceLib.convert5to4 import get_ribbi_mapping

    assert get_ribbi_mapping(doc) == {
        (("Weight", 84), ("Width", 100), ("Italic", 0)): "regular",
        (("Weight", 133), ("Width", 100), ("Italic", 0)): "bold",
        (("Weight", 84), ("Width", 100), ("Italic", 1)): "italic",
        (("Weight", 133), ("Width", 100), ("Italic", 1)): "bold italic",
    }
