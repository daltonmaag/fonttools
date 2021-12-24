"""Extra methods for DesignSpaceDocument to generate its STAT table data."""

from __future__ import annotations

from typing import Dict, List, Union
import fontTools.otlLib.builder
from fontTools.ttLib import TTFont
from fontTools.designspaceLib import (
    AxisLabelDescriptor,
    DesignSpaceDocument,
    LocationLabelDescriptor,
)


def getStatAxes(self: DesignSpaceDocument) -> List[Dict]:
    """Return a list of axis dicts suitable for use as the ``axes``
    argument to :fun:`fontTools.otlLib.builder.buildStatTable()`.

    .. versionadded:: 5.0
    """
    return [
        dict(
            tag=axis.tag,
            name={"en": axis.name, **axis.labelNames},
            ordering=axis.axisOrdering,
            locations=[_axisLabelToStatLocation(label) for label in axis.axisLabels],
        )
        for axis in self.axes
    ]


def getStatLocations(self: DesignSpaceDocument) -> List[Dict]:
    """Return a list of location dicts suitable for use as the ``locations``
    argument to :fun:`fontTools.otlLib.builder.buildStatTable()`.

    .. versionadded:: 5.0
    """
    axesByName = {axis.name: axis for axis in self.axes}
    return [
        dict(
            name={"en": label.name, **label.labelNames},
            # Location in the designspace is keyed by axis name
            # Location in buildStatTable by axis tag
            location={
                axesByName[name].tag: value
                for name, value in label.getFullUserLocation(self).items()
            },
            flags=_labelToFlags(label),
        )
        for label in self.locationLabels
    ]


def _labelToFlags(label: Union[AxisLabelDescriptor, LocationLabelDescriptor]) -> int:
    flags = 0
    if label.olderSibling:
        flags |= 1
    if label.elidable:
        flags |= 2
    return flags


def _axisLabelToStatLocation(
    label: AxisLabelDescriptor,
) -> Dict:
    label_format = label.getFormat()
    name = {"en": label.name, **label.labelNames}
    flags = _labelToFlags(label)
    if label_format == 1:
        return dict(name=name, value=label.userValue, flags=flags)
    if label_format == 3:
        return dict(
            name=name,
            value=label.userValue,
            linkedValue=label.linkedUserValue,
            flags=flags,
        )
    if label_format == 2:
        return dict(
            name=name,
            nominalValue=label.userValue,
            rangeMinValue=label.userMinimum,
            rangeMaxValue=label.userMaximum,
            flags=flags,
        )
    raise Exception("unreachable")
