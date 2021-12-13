"""Extra methods for:
- DesignSpaceDocument, to assing a RIBBI style (styleMapStyleName) to weight
  and italic locations with style linking;
- InstanceDescriptor, to generate its names according to the
  naming scheme in the document's STAT table.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import logging

from fontTools.designspaceLib import AxisDescriptor, AxisLabelDescriptor, DesignSpaceDocument, DesignSpaceDocumentError, InstanceDescriptor, SourceDescriptor

LOGGER = logging.getLogger(__name__)

@dataclass
class StatNames:
    familyName: str
    styleName: str
    postScriptFontName: str
    styleMapFamilyName: Optional[str]
    styleMapStyleName: Optional[str]


# TODO: Deal with anisotropic locations.
# TODO: Deal with localization.
# TODO: Decide how to deal with familyName, for which there would need to be a
#       new localized familyname element in sources, unless it's ok to query the
#       source UFO directly (but what about source TTFs?)
# TODO: Deal with STAT format 2 ranges.
def getStatNames(
    self: InstanceDescriptor,
    doc: DesignSpaceDocument,
    ribbi_mapping: dict[tuple[tuple[str, float], ...], RibbiStyle] = None
) -> StatNames:
    user_location = self.getFullUserLocation()

    family_name: Optional[str] = None
    default_source: Optional[SourceDescriptor] = doc.findDefault()
    if default_source is None:
        LOGGER.warning("Cannot determine default source to look up family name.")
    elif default_source.familyName is None:
        LOGGER.warning(
            "Cannot look up family name, assign the 'familyname' attribute to the default source."
        )
    else:
        family_name = default_source.familyName

    # If a free-standing label matches the location, use it for name generation.
    label = doc.labelForUserLocation(user_location)
    if label is not None:
        style_name = label.defaultName
    # Otherwise, scour the axis labels for matches.
    else:
        labels = get_axis_labels_for_user_location(doc.axes, user_location)
        style_name = " ".join(
            label.defaultName for label in labels if not label.elidable
        )
        if not style_name:
            if self.styleName is None:
                instance_id: str = self.name or repr(self.location)
                raise DesignSpaceDocumentError(
                    f"Cannot infer style name for instance '{instance_id}' because all "
                    "labels are elided. Please fill in the 'stylename' attribute yourself."
                )
            else:
                style_name = self.styleName

    if family_name is None:
        post_script_font_name = None
    else:
        post_script_font_name = f"{family_name}-{style_name}".replace(" ", "")

    # TODO: look at how ufo2ft generates style_map_family_name
    style_map_family_name = None
    style_map_style_name = ribbi_mapping.get(tuple(self.location.items()))

    return StatNames(
        familyName=family_name,
        styleName=style_name,
        postScriptFontName=post_script_font_name,
        styleMapFamilyName=style_map_family_name,
        styleMapStyleName=style_map_style_name,
    )


def get_sorted_axis_labels(
    axes: list[AxisDescriptor],
) -> dict[str, list[AxisLabelDescriptor]]:
    """Returns axis labels sorted by their ordering, with unordered ones appended as
    they are listed."""

    # First, get the axis labels with explicit ordering...
    sorted_axes = sorted(
        (axis for axis in axes if axis.axisOrdering is not None),
        key=lambda a: a.axisOrdering,
    )
    sorted_labels: dict[str, list[AxisLabelDescriptor]] = {
        axis.name: axis.axisLabels for axis in sorted_axes
    }

    # ... then append the others in the order they appear.
    # NOTE: This relies on Python 3.7+ dict's preserved insertion order.
    for axis in axes:
        if axis.axisOrdering is None:
            sorted_labels[axis.name] = axis.axisLabels

    return sorted_labels


def get_axis_labels_for_user_location(
    axes: list[AxisDescriptor], user_location: Location
) -> list[AxisLabelDescriptor]:
    labels: list[AxisLabelDescriptor] = []

    all_axis_labels = get_sorted_axis_labels(axes)
    if all_axis_labels.keys() != user_location.keys():
        raise DesignSpaceDocumentError(
            f"Mismatch between user location '{user_location.keys()}' and available "
            f"labels for '{all_axis_labels.keys()}'."
        )

    for axis_name, axis_labels in all_axis_labels.items():
        user_value = user_location[axis_name]
        label: Optional[AxisLabelDescriptor] = next(
            (l for l in axis_labels if l.userValue == user_value), None
        )
        if label is None:
            raise DesignSpaceDocumentError(
                f"Document needs a label for axis '{axis_name}', user value '{user_value}'."
            )
        labels.append(label)

    return labels



# TODO(Python 3.8): use Literal
# RibbiStyle = Union[Literal["regular"], Literal["bold"], Literal["italic"], Literal["bold italic"]]
RibbiStyle = str


# TODO: Also grab labels when no linkedUserValue is set? I.e. from well-known axis positions?
def getRibbiMapping(
    self: DesignSpaceDocument,
) -> dict[tuple[tuple[str, float], ...], RibbiStyle]:
    """Compute the RIBBI style name of each design space location for which a linkedUserValue is provided.

    .. versionadded:: 5.0
    """
    default_location = self.newDefaultLocation()
    if default_location is None:
        raise DesignSpaceDocumentError("Cannot determine default location.")
    mapping: dict[tuple[tuple[str, float], ...], RibbiStyle] = {}

    bold_value: tuple[str, float] | None = None
    italic_value: tuple[str, float] | None = None

    axes_by_tag = {a.tag: a for a in self.axes}
    axis = axes_by_tag.get("wght")
    if axis is not None:
        rg_label = next(
            (label for label in axis.axisLabels if label.userValue == 400), None
        )
        if rg_label is not None:
            rg_value = axis.map_forward(400)
            rg_location = {**default_location, axis.name: rg_value}
            mapping[tuple(rg_location.items())] = "regular"
            if rg_label.linkedUserValue is not None:
                bd_value = axis.map_forward(rg_label.linkedUserValue)
                bd_location = {**default_location, axis.name: bd_value}
                mapping[tuple(bd_location.items())] = "bold"
                bold_value = (axis.name, bd_value)

    axis = axes_by_tag.get("ital") or axes_by_tag.get("slnt")
    if axis is not None:
        rg_label = next(
            (label for label in axis.axisLabels if label.userValue == 0), None
        )
        if rg_label is not None and rg_label.linkedUserValue is not None:
            it_value = axis.map_forward(rg_label.linkedUserValue)
            it_location = {**default_location, axis.name: it_value}
            mapping[tuple(it_location.items())] = "italic"
            italic_value = (axis.name, it_value)

    if bold_value is not None and italic_value is not None:
        bd_name, bd_value = bold_value
        it_name, it_value = italic_value
        bd_it_location = {**default_location, bd_name: bd_value, it_name: it_value}
        mapping[tuple(bd_it_location.items())] = "bold italic"

    return mapping
