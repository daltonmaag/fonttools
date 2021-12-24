"""Extra methods for:
- DesignSpaceDocument, to assing a RIBBI style (styleMapStyleName) to weight
  and italic locations with style linking;
- InstanceDescriptor, to generate its names according to the
  naming scheme in the document's STAT table.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple, Union
import logging

from fontTools.designspaceLib import (
    AxisDescriptor,
    AxisLabelDescriptor,
    DesignSpaceDocument,
    DesignSpaceDocumentError,
    DiscreteAxisDescriptor,
    SimpleLocationDict,
    SourceDescriptor,
)

LOGGER = logging.getLogger(__name__)

# TODO(Python 3.8): use Literal
# RibbiStyleName = Union[Literal["regular"], Literal["bold"], Literal["italic"], Literal["bold italic"]]
RibbiStyle = str
BOLD_ITALIC_TO_RIBBI_STYLE = {
    (False, False): "regular",
    (False, True): "italic",
    (True, False): "bold",
    (True, True): "bold italic",
}


@dataclass
class StatNames:
    familyNames: Dict[str, str]
    styleNames: Dict[str, str]
    postScriptFontName: Optional[str]
    styleMapFamilyNames: Dict[str, str]
    styleMapStyleName: Optional[RibbiStyle]


UserLocationTuple = Tuple[Tuple[str, float], ...]


def getStatNames(
    doc: DesignSpaceDocument, userLocation: SimpleLocationDict
) -> StatNames:
    """Compute the family, style, PostScript names of the given ``userLocation``
    using the document's STAT information.

    .. versionadded:: 5.0
    """
    familyNames: Dict[str, str] = {}
    defaultSource: Optional[SourceDescriptor] = doc.findDefault()
    if defaultSource is None:
        LOGGER.warning("Cannot determine default source to look up family name.")
    elif defaultSource.familyName is None:
        LOGGER.warning(
            "Cannot look up family name, assign the 'familyname' attribute to the default source."
        )
    else:
        familyNames = {
            "en": defaultSource.familyName,
            **defaultSource.localisedFamilyName,
        }

    styleNames: Dict[str, str] = {}
    # If a free-standing label matches the location, use it for name generation.
    label = doc.labelForUserLocation(userLocation)
    if label is not None:
        styleNames = {"en": label.name, **label.labelNames}
    # Otherwise, scour the axis labels for matches.
    else:
        # Gather all languages in which at least one translation is provided
        # Then build names for all these languages, but fallback to English
        # whenever a translation is missing.
        labels = _getAxisLabelsForUserLocation(doc.axes, userLocation)
        languages = set(language for label in labels for language in label.labelNames)
        languages.add("en")
        for language in languages:
            styleName = " ".join(
                label.labelNames.get(language, label.defaultName)
                for label in labels
                if not label.elidable
            )
            if not styleName and doc.elidedFallbackName is not None:
                styleName = doc.elidedFallbackName
            styleNames[language] = styleName

    postScriptFontName = None
    if "en" in familyNames and "en" in styleNames:
        postScriptFontName = f"{familyNames['en']}-{styleNames['en']}".replace(" ", "")

    styleMapStyleName, regularUserLocation = _getRibbiStyle(doc, userLocation)

    styleNamesForStyleMap = styleNames
    if regularUserLocation != userLocation:
        regularStatNames = getStatNames(doc, regularUserLocation)
        styleNamesForStyleMap = regularStatNames.styleNames

    styleMapFamilyNames = {}
    for language, familyName in familyNames.items():
        styleName = styleNamesForStyleMap.get(language, styleNames["en"])
        styleMapFamilyNames[language] = (familyName + " " + styleName).strip()

    return StatNames(
        familyNames=familyNames,
        styleNames=styleNames,
        postScriptFontName=postScriptFontName,
        styleMapFamilyNames=styleMapFamilyNames,
        styleMapStyleName=styleMapStyleName,
    )


def _getSortedAxisLabels(
    axes: list[AxisDescriptor],
) -> Dict[str, list[AxisLabelDescriptor]]:
    """Returns axis labels sorted by their ordering, with unordered ones appended as
    they are listed."""

    # First, get the axis labels with explicit ordering...
    sortedAxes = sorted(
        (axis for axis in axes if axis.axisOrdering is not None),
        key=lambda a: a.axisOrdering,
    )
    sortedLabels: Dict[str, list[AxisLabelDescriptor]] = {
        axis.name: axis.axisLabels for axis in sortedAxes
    }

    # ... then append the others in the order they appear.
    # NOTE: This relies on Python 3.7+ dict's preserved insertion order.
    for axis in axes:
        if axis.axisOrdering is None:
            sortedLabels[axis.name] = axis.axisLabels

    return sortedLabels


def _getAxisLabelsForUserLocation(
    axes: list[Union[AxisDescriptor, DiscreteAxisDescriptor]],
    userLocation: SimpleLocationDict,
) -> list[AxisLabelDescriptor]:
    labels: list[AxisLabelDescriptor] = []

    allAxisLabels = _getSortedAxisLabels(axes)
    if allAxisLabels.keys() != userLocation.keys():
        raise DesignSpaceDocumentError(
            f"Mismatch between user location '{userLocation.keys()}' and available "
            f"labels for '{allAxisLabels.keys()}'."
        )

    for axisName, axisLabels in allAxisLabels.items():
        userValue = userLocation[axisName]
        label: Optional[AxisLabelDescriptor] = next(
            (
                l
                for l in axisLabels
                if l.userValue == userValue
                or (
                    l.userMinimum is not None
                    and l.userMaximum is not None
                    and l.userMinimum <= userValue <= l.userMaximum
                )
            ),
            None,
        )
        if label is None:
            raise DesignSpaceDocumentError(
                f"Document needs a label for axis '{axisName}', user value '{userValue}'."
            )
        labels.append(label)

    return labels


def _getRibbiStyle(
    self: DesignSpaceDocument, userLocation: SimpleLocationDict
) -> Tuple[RibbiStyle, SimpleLocationDict]:
    """Compute the RIBBI style name of the given user location.

    .. versionadded:: 5.0
    """
    regularUserLocation = {}
    axes_by_tag = {axis.tag: axis for axis in self.axes}

    bold: bool = False
    italic: bool = False

    axis = axes_by_tag.get("wght")
    if axis is not None:
        for regular_label in axis.axisLabels:
            if regular_label.linkedUserValue == userLocation[axis.name]:
                regularUserLocation[axis.name] = regular_label.userValue
                bold = True
                break

    axis = axes_by_tag.get("ital") or axes_by_tag.get("slnt")
    if axis is not None:
        for urpright_label in axis.axisLabels:
            if urpright_label.linkedUserValue == userLocation[axis.name]:
                regularUserLocation[axis.name] = urpright_label.userValue
                italic = True
                break

    return BOLD_ITALIC_TO_RIBBI_STYLE[bold, italic], {
        **userLocation,
        **regularUserLocation,
    }
