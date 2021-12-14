import shutil
from pathlib import Path

import pytest
from fontTools.designspaceLib import DesignSpaceDocument

from .fixtures import datadir


@pytest.mark.parametrize(
    "test_ds,expected_vfs",
    [
        (
            "test_v5_aktiv.designspace",
            {
                "AktivGroteskVF_Italics_Wght.ttf",
                "AktivGroteskVF_Italics_WghtWdth.ttf",
                "AktivGroteskVF_Wght.ttf",
                "AktivGroteskVF_WghtWdth.ttf",
                "AktivGroteskVF_WghtWdthItal.ttf",
            },
        ),
        (
            "test_v5_sourceserif.designspace",
            {
                "SourceSerif4Variable-Italic.otf",
                "SourceSerif4Variable-Roman.otf",
            },
        ),
    ],
)
def test_convert5to4(datadir, tmpdir, test_ds, expected_vfs):
    data_in = datadir / test_ds
    temp_in = tmpdir / test_ds
    shutil.copy(data_in, temp_in)
    doc = DesignSpaceDocument.fromfile(temp_in)

    variable_fonts = doc.convert5to4()

    assert variable_fonts.keys() == expected_vfs
    for vf_name, vf in variable_fonts.items():
        data_out = (datadir / "convert5to4_out" / vf_name).with_suffix(".designspace")
        temp_out = (Path(tmpdir) / "out" / vf_name).with_suffix(".designspace")
        temp_out.parent.mkdir(exist_ok=True)
        vf.write(temp_out)

        assert data_out.read_text(encoding="utf-8") == temp_out.read_text(
            encoding="utf-8"
        )
