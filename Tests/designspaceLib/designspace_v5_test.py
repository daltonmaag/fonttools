from pathlib import Path

import pytest
from fontTools.designspaceLib import (
    AxisDescriptor,
    DesignSpaceDocument,
    DiscreteAxisDescriptor,
    AxisLabelDescriptor,
    InstanceDescriptor,
    LocationLabelDescriptor,
    VariableFontDescriptor,
    RangeAxisSubsetDescriptor,
    ValueAxisSubsetDescriptor,
)


@pytest.fixture
def datadir():
    return Path(__file__).parent / "data"


def test_read_v5_document_simple(datadir):
    doc = DesignSpaceDocument.fromfile(datadir / "test_v5.designspace")

    assert doc.axes == [
        AxisDescriptor(
            tag="wght",
            name="weight",
            minimum=0,
            maximum=1000,
            default=0,
            labelNames={"en": "Wéíght", "fa-IR": "قطر"},
            map=[(200, 0), (300, 100), (400, 368), (600, 600), (700, 824), (900, 1000)],
            axisOrdering=None,
            axisLabels=[
                AxisLabelDescriptor(
                    name="Extra Light",
                    userMinimum=200,
                    userValue=200,
                    userMaximum=250,
                    labelNames={"de": "Extraleicht", "fr": "Extra léger"},
                ),
                AxisLabelDescriptor(
                    name="Light", userMinimum=250, userValue=300, userMaximum=350
                ),
                AxisLabelDescriptor(
                    name="Regular",
                    userMinimum=350,
                    userValue=400,
                    userMaximum=450,
                    elidable=True,
                ),
                AxisLabelDescriptor(
                    name="Semi Bold", userMinimum=450, userValue=600, userMaximum=650
                ),
                AxisLabelDescriptor(
                    name="Bold", userMinimum=650, userValue=700, userMaximum=850
                ),
                AxisLabelDescriptor(
                    name="Black", userMinimum=850, userValue=900, userMaximum=900
                ),
            ],
        ),
        AxisDescriptor(
            tag="wdth",
            name="width",
            minimum=50,
            maximum=150,
            default=100,
            hidden=True,
            labelNames={"fr": "Chasse"},
            map=[(50, 10), (100, 20), (125, 66), (150, 990)],
            axisOrdering=None,
            axisLabels=[
                AxisLabelDescriptor(name="Condensed", userValue=50),
                AxisLabelDescriptor(
                    name="Normal", elidable=True, olderSibling=True, userValue=100
                ),
                AxisLabelDescriptor(name="Wide", userValue=125),
                AxisLabelDescriptor(name="Extra Wide", userValue=150),
            ],
        ),
        DiscreteAxisDescriptor(
            tag="ital",
            name="Italic",
            values=[0, 1],
            default=0,
            axisOrdering=None,
            axisLabels=[
                AxisLabelDescriptor(
                    name="Roman", userValue=0, elidable=True, linkedUserValue=1
                ),
                AxisLabelDescriptor(name="Italic", userValue=1),
            ],
        ),
    ]

    assert doc.locationLabels == [
        LocationLabelDescriptor(
            name="asdf", userLocation={"weight": 10, "width": 50, "Italic": 0}
        ),
        LocationLabelDescriptor(
            name="dfdf", userLocation={"weight": 100, "width": 100, "Italic": 1}
        ),
    ]

    assert doc.variableFonts == [
        VariableFontDescriptor(
            filename="Test_WghtWdth.ttf",
            axisSubsets=[
                RangeAxisSubsetDescriptor(name="Weight"),
                RangeAxisSubsetDescriptor(name="Width"),
            ],
            lib={"com.vtt.source": "sources/vtt/Test_WghtWdth.vtt"},
        ),
        VariableFontDescriptor(
            filename="Test_Wght.ttf",
            axisSubsets=[RangeAxisSubsetDescriptor(name="Weight")],
            lib={"com.vtt.source": "sources/vtt/Test_Wght.vtt"},
        ),
        VariableFontDescriptor(
            filename="TestCd_Wght.ttf",
            axisSubsets=[
                RangeAxisSubsetDescriptor(name="Weight"),
                ValueAxisSubsetDescriptor(name="Width", userValue=0),
            ],
        ),
        VariableFontDescriptor(
            filename="TestWd_Wght.ttf",
            axisSubsets=[
                RangeAxisSubsetDescriptor(name="Weight"),
                ValueAxisSubsetDescriptor(name="Width", userValue=1000),
            ],
        ),
        VariableFontDescriptor(
            filename="TestItalic_Wght.ttf",
            axisSubsets=[
                RangeAxisSubsetDescriptor(name="Weight"),
                ValueAxisSubsetDescriptor(name="Italic", userValue=1),
            ],
        ),
        VariableFontDescriptor(
            filename="TestRB_Wght.ttf",
            axisSubsets=[
                RangeAxisSubsetDescriptor(
                    name="Weight", userMinimum=400, userDefault=400, userMaximum=700
                ),
                ValueAxisSubsetDescriptor(name="Italic", userValue=0),
            ],
        ),
    ]

    assert doc.instances == [
        InstanceDescriptor(
            filename="instances/instanceTest1.ufo",
            path="C:/UsersLocal/jany.belluz/Documents/code/fonttools/Tests/designspaceLib/data/instances/instanceTest1.ufo",
            name="instance.ufo1",
            designLocation={"weight": 500.0, "width": 20.0},
            familyName="InstanceFamilyName",
            styleName="InstanceStyleName",
            postScriptFontName="InstancePostscriptName",
            styleMapFamilyName="InstanceStyleMapFamilyName",
            styleMapStyleName="InstanceStyleMapStyleName",
            glyphs={"arrow": {"mute": True, "unicodes": [291, 292, 293]}},
            lib={
                "com.coolDesignspaceApp.binaryData": b"<binary gunk>",
                "com.coolDesignspaceApp.specimenText": "Hamburgerwhatever",
            },
        ),
        InstanceDescriptor(
            filename="instances/instanceTest2.ufo",
            path="C:/UsersLocal/jany.belluz/Documents/code/fonttools/Tests/designspaceLib/data/instances/instanceTest2.ufo",
            name="instance.ufo2",
            designLocation={"weight": 500.0, "width": (400.0, 300.0)},
            familyName="InstanceFamilyName",
            styleName="InstanceStyleName",
            postScriptFontName="InstancePostscriptName",
            styleMapFamilyName="InstanceStyleMapFamilyName",
            styleMapStyleName="InstanceStyleMapStyleName",
            glyphs={
                "arrow": {
                    "unicodes": [101, 201, 301],
                    "note": "A note about this glyph",
                    "instanceLocation": {"weight": 120.0, "width": 100.0},
                    "masters": [
                        {
                            "font": "master.ufo1",
                            "location": {"weight": 20.0, "width": 20.0},
                            "glyphName": "BB",
                        },
                        {
                            "font": "master.ufo2",
                            "location": {"weight": 900.0, "width": 900.0},
                            "glyphName": "CC",
                        },
                    ],
                },
                "arrow2": {},
            },
        ),
        InstanceDescriptor(
            locationLabel="asdf",
        ),
        InstanceDescriptor(
            designLocation={"weight": 600.0, "width": (401.0, 420.0)},
        ),
        InstanceDescriptor(
            designLocation={"weight": 10.0, "Italic": 0.0},
            userLocation={"width": 100.0},
        ),
        InstanceDescriptor(
            userLocation={"weight": 300.0, "width": 130.0, "Italic": 1.0},
        ),
    ]


def test_read_v5_document_decovar(datadir):
    doc = DesignSpaceDocument.fromfile(datadir / "test_v5_decovar.designspace")

    assert not doc.variableFonts

    assert doc.axes == [
        AxisDescriptor(default=0, maximum=1000, minimum=0, name="Inline", tag="BLDA"),
        AxisDescriptor(default=0, maximum=1000, minimum=0, name="Shearded", tag="TRMD"),
        AxisDescriptor(
            default=0, maximum=1000, minimum=0, name="Rounded Slab", tag="TRMC"
        ),
        AxisDescriptor(default=0, maximum=1000, minimum=0, name="Stripes", tag="SKLD"),
        AxisDescriptor(
            default=0, maximum=1000, minimum=0, name="Worm Terminal", tag="TRML"
        ),
        AxisDescriptor(
            default=0, maximum=1000, minimum=0, name="Inline Skeleton", tag="SKLA"
        ),
        AxisDescriptor(
            default=0, maximum=1000, minimum=0, name="Open Inline Terminal", tag="TRMF"
        ),
        AxisDescriptor(
            default=0, maximum=1000, minimum=0, name="Inline Terminal", tag="TRMK"
        ),
        AxisDescriptor(default=0, maximum=1000, minimum=0, name="Worm", tag="BLDB"),
        AxisDescriptor(default=0, maximum=1000, minimum=0, name="Weight", tag="WMX2"),
        AxisDescriptor(default=0, maximum=1000, minimum=0, name="Flared", tag="TRMB"),
        AxisDescriptor(default=0, maximum=1000, minimum=0, name="Rounded", tag="TRMA"),
        AxisDescriptor(
            default=0, maximum=1000, minimum=0, name="Worm Skeleton", tag="SKLB"
        ),
        AxisDescriptor(default=0, maximum=1000, minimum=0, name="Slab", tag="TRMG"),
        AxisDescriptor(
            default=0, maximum=1000, minimum=0, name="Bifurcated", tag="TRME"
        ),
    ]

    assert doc.locationLabels == [
        LocationLabelDescriptor(name="Default", elidable=True, userLocation={}),
        LocationLabelDescriptor(
            name="Open", userLocation={"Inline": 1000}, labelNames={"de": "Offen"}
        ),
        LocationLabelDescriptor(name="Worm", userLocation={"Worm": 1000}),
        LocationLabelDescriptor(
            name="Checkered", userLocation={"Inline Skeleton": 1000}
        ),
        LocationLabelDescriptor(
            name="Checkered Reverse", userLocation={"Inline Terminal": 1000}
        ),
        LocationLabelDescriptor(name="Striped", userLocation={"Stripes": 500}),
        LocationLabelDescriptor(name="Rounded", userLocation={"Rounded": 1000}),
        LocationLabelDescriptor(name="Flared", userLocation={"Flared": 1000}),
        LocationLabelDescriptor(
            name="Flared Open", userLocation={"Inline Skeleton": 1000, "Flared": 1000}
        ),
        LocationLabelDescriptor(
            name="Rounded Slab", userLocation={"Rounded Slab": 1000}
        ),
        LocationLabelDescriptor(name="Sheared", userLocation={"Shearded": 1000}),
        LocationLabelDescriptor(name="Bifurcated", userLocation={"Bifurcated": 1000}),
        LocationLabelDescriptor(
            name="Inline",
            userLocation={"Inline Skeleton": 500, "Open Inline Terminal": 500},
        ),
        LocationLabelDescriptor(name="Slab", userLocation={"Slab": 1000}),
        LocationLabelDescriptor(name="Contrast", userLocation={"Weight": 1000}),
        LocationLabelDescriptor(
            name="Fancy",
            userLocation={"Inline Skeleton": 1000, "Flared": 1000, "Weight": 1000},
        ),
        LocationLabelDescriptor(
            name="Mayhem",
            userLocation={
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

    assert [i.locationLabel for i in doc.instances] == [
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

    assert doc.axes == [
        DiscreteAxisDescriptor(
            default=400,
            values=[400, 700, 900],
            name="Weight",
            tag="wght",
            axisLabels=[
                AxisLabelDescriptor(
                    name="Regular", userValue=400, elidable=True, linkedUserValue=700
                ),
                AxisLabelDescriptor(name="Bold", userValue=700),
                AxisLabelDescriptor(name="Black", userValue=900),
            ],
        ),
        DiscreteAxisDescriptor(
            default=100,
            values=[75, 100],
            name="Width",
            tag="wdth",
            axisLabels=[
                AxisLabelDescriptor(name="Narrow", userValue=75),
                AxisLabelDescriptor(name="Normal", userValue=100, elidable=True),
            ],
        ),
        DiscreteAxisDescriptor(
            default=0,
            values=[0, 1],
            name="Italic",
            tag="ital",
            axisLabels=[
                AxisLabelDescriptor(
                    name="Roman", userValue=0, elidable=True, linkedUserValue=1
                ),
                AxisLabelDescriptor(name="Italic", userValue=1),
            ],
        ),
    ]


def test_read_v5_document_aktiv(datadir):
    doc = DesignSpaceDocument.fromfile(datadir / "test_v5_aktiv.designspace")

    assert not doc.locationLabels

    assert doc.axes == [
        AxisDescriptor(
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
                AxisLabelDescriptor(name="Hair", userValue=100),
                AxisLabelDescriptor(userValue=200, name="Thin"),
                AxisLabelDescriptor(userValue=300, name="Light"),
                AxisLabelDescriptor(
                    userValue=400, name="Regular", elidable=True, linkedUserValue=700
                ),
                AxisLabelDescriptor(userValue=500, name="Medium"),
                AxisLabelDescriptor(userValue=600, name="SemiBold"),
                AxisLabelDescriptor(userValue=700, name="Bold"),
                AxisLabelDescriptor(userValue=800, name="XBold"),
                AxisLabelDescriptor(userValue=900, name="Black"),
            ],
        ),
        AxisDescriptor(
            tag="wdth",
            name="Width",
            minimum=75,
            default=100,
            maximum=125,
            axisOrdering=0,
            axisLabels=[
                AxisLabelDescriptor(name="Cd", userValue=75),
                AxisLabelDescriptor(name="Normal", elidable=True, userValue=100),
                AxisLabelDescriptor(name="Ex", userValue=125),
            ],
        ),
        AxisDescriptor(
            tag="ital",
            name="Italic",
            minimum=0,
            default=0,
            maximum=1,
            axisOrdering=2,
            axisLabels=[
                AxisLabelDescriptor(
                    name="Upright", userValue=0, elidable=True, linkedUserValue=1
                ),
                AxisLabelDescriptor(name="Italic", userValue=1),
            ],
        ),
    ]

    assert doc.variableFonts == [
        VariableFontDescriptor(
            filename="AktivGroteskVF_WghtWdthItal.ttf",
            axisSubsets=[
                RangeAxisSubsetDescriptor(name="Weight"),
                RangeAxisSubsetDescriptor(name="Width"),
                RangeAxisSubsetDescriptor(name="Italic"),
            ],
        ),
        VariableFontDescriptor(
            filename="AktivGroteskVF_WghtWdth.ttf",
            axisSubsets=[
                RangeAxisSubsetDescriptor(name="Weight"),
                RangeAxisSubsetDescriptor(name="Width"),
            ],
        ),
        VariableFontDescriptor(
            filename="AktivGroteskVF_Wght.ttf",
            axisSubsets=[
                RangeAxisSubsetDescriptor(name="Weight"),
            ],
        ),
        VariableFontDescriptor(
            filename="AktivGroteskVF_Italics_WghtWdth.ttf",
            axisSubsets=[
                RangeAxisSubsetDescriptor(name="Weight"),
                RangeAxisSubsetDescriptor(name="Width"),
                ValueAxisSubsetDescriptor(name="Italic", userValue=1),
            ],
        ),
        VariableFontDescriptor(
            filename="AktivGroteskVF_Italics_Wght.ttf",
            axisSubsets=[
                RangeAxisSubsetDescriptor(name="Weight"),
                ValueAxisSubsetDescriptor(name="Italic", userValue=1),
            ],
        ),
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


@pytest.fixture
def map_doc():
    """Generate a document with a few axes to test the mapping functions"""
    doc = DesignSpaceDocument()
    doc.addAxis(
        AxisDescriptor(
            tag="wght",
            name="Weight",
            minimum=100,
            maximum=900,
            default=100,
            map=[(100, 10), (900, 90)],
        )
    )
    doc.addAxis(
        AxisDescriptor(
            tag="wdth",
            name="Width",
            minimum=75,
            maximum=200,
            default=100,
            map=[(75, 7500), (100, 10000), (200, 20000)],
        )
    )
    doc.addAxis(
        AxisDescriptor(tag="CUST", name="Custom", minimum=1, maximum=2, default=1.5)
    )
    doc.addLocationLabel(
        LocationLabelDescriptor(
            name="Wonky", userLocation={"Weight": 800, "Custom": 1.2}
        )
    )
    return doc


def test_doc_location_map_forward(map_doc: DesignSpaceDocument):
    assert map_doc.map_forward({"Weight": 400, "Width": 150, "Custom": 2}) == {
        "Weight": 40,
        "Width": 15000,
        "Custom": 2,
    }, "The mappings should be used to compute the design locations"
    assert map_doc.map_forward({"Weight": 400}) == {
        "Weight": 40,
        "Width": 10000,
        "Custom": 1.5,
    }, "Missing user locations should be assumed equal to the axis's default"


def test_doc_location_map_backward(map_doc: DesignSpaceDocument):
    assert map_doc.map_backward({"Weight": 40, "Width": 15000, "Custom": 2}) == {
        "Weight": 400,
        "Width": 150,
        "Custom": 2,
    }, "The mappings should be used to compute the user locations"
    assert map_doc.map_backward({"Weight": 40}) == {
        "Weight": 400,
        "Width": 100,
        "Custom": 1.5,
    }, "Missing design locations should be assumed equal to the axis's default"
    assert map_doc.map_backward(
        {"Weight": (40, 50), "Width": (15000, 100000), "Custom": (2, 1.5)}
    ) == {
        "Weight": 400,
        "Width": 150,
        "Custom": 2,
    }, "Only the xvalue of anisotropic locations is used"


def test_instance_location_from_label(map_doc):
    inst = InstanceDescriptor(locationLabel="Wonky")
    assert inst.getFullUserLocation(map_doc) == {
        "Weight": 800,
        "Width": 100,
        "Custom": 1.2,
    }, "an instance with a locationLabel uses the user location from that label, empty values on the label use axis defaults"
    assert inst.getFullDesignLocation(map_doc) == {
        "Weight": 80,
        "Width": 10000,
        "Custom": 1.2,
    }, "an instance with a locationLabel computes the design location from that label, empty values on the label use axis defaults"

    inst = InstanceDescriptor(locationLabel="Wonky", userLocation={"Width": 200})
    assert inst.getFullUserLocation(map_doc) == {
        "Weight": 800,
        "Width": 100,
        "Custom": 1.2,
    }, "an instance with a locationLabel uses the user location from that label, other location values are ignored"
    assert inst.getFullDesignLocation(map_doc) == {
        "Weight": 80,
        "Width": 10000,
        "Custom": 1.2,
    }, "an instance with a locationLabel computes the design location from that label, other location values are ignored"


def test_instance_location_no_data(map_doc):
    inst = InstanceDescriptor()
    assert inst.getFullUserLocation(map_doc) == {
        "Weight": 100,
        "Width": 100,
        "Custom": 1.5,
    }, "an instance without any location data has the default user location"
    assert inst.getFullDesignLocation(map_doc) == {
        "Weight": 10,
        "Width": 10000,
        "Custom": 1.5,
    }, "an instance without any location data has the default design location"


def test_instance_location_design_first(map_doc):
    inst = InstanceDescriptor(
        designLocation={"Weight": (60, 61), "Width": 11000, "Custom": 1.2},
        userLocation={"Weight": 700, "Width": 180, "Custom": 1.4},
    )
    assert inst.getFullUserLocation(map_doc) == {
        "Weight": 600,
        "Width": 110,
        "Custom": 1.2,
    }, "when both design and user location data are provided, design wins"
    assert inst.getFullDesignLocation(map_doc) == {
        "Weight": (60, 61),
        "Width": 11000,
        "Custom": 1.2,
    }, "when both design and user location data are provided, design wins (incl. anisotropy)"


def test_instance_location_mix(map_doc):
    inst = InstanceDescriptor(
        designLocation={"Weight": (60, 61)},
        userLocation={"Width": 180},
    )
    assert inst.getFullUserLocation(map_doc) == {
        "Weight": 600,
        "Width": 180,
        "Custom": 1.5,
    }, "instance location is a mix of design and user locations"
    assert inst.getFullDesignLocation(map_doc) == {
        "Weight": (60, 61),
        "Width": 18000,
        "Custom": 1.5,
    }, "instance location is a mix of design and user location"
