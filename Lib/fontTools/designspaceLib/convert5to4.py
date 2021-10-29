# pyright: basic

# FIXME: we're building a stylespace as in statmake but it's not part of fontTools
# TODO: either move this converter out of fontTools so it can keep creating the stylespace
#       or make this converter use the fontTools APIs for stat/generate data for these
# TODO: The STAT table has a fallback name id for styles where everything is elided, but it
#       is a name id, which exists in a VF, but not in a Designspace. Make accessible somehow?
#       It should be set to "2" most of the time.
# FIXME: How to deal with Designspaces where e.g. the wght axis mapping differs slightly? See
#        e.g. Source Serif 4.

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

from attr import asdict
from fontTools.designspaceLib import (
    AxisDescriptor,
    AxisLabelDescriptor,
    RangeAxisSubsetDescriptor,
    DesignSpaceDocument,
    DesignSpaceDocumentError,
    InstanceDescriptor,
    LocationLabelDescriptor,
    RuleDescriptor,
    SourceDescriptor,
)
from fontTools.designspaceLib.types import (
    ConditionSet,
    Location,
    Range,
    RegionSelection,
    location_in_selection,
)
from statmake.classes import (
    DESIGNSPACE_STYLESPACE_INLINE_KEY,
    Axis,
    AxisValueFlag,
    FlagList,
    LocationFormat1,
    LocationFormat2,
    LocationFormat3,
    LocationFormat4,
    NameRecord,
    Stylespace,
)

LOGGER = logging.getLogger(__name__)


def convert5to4(
    doc: DesignSpaceDocument,
) -> Tuple[Dict[str, DesignSpaceDocument], Stylespace]:
    stylespace = Stylespace(
        axes=[
            Axis(
                name=NameRecord({"en": axis.name, **axis.labelNames}),
                tag=axis.tag,
                locations=[
                    _axis_label_to_stylespace_location(label)
                    for label in axis.axisLabels
                ],
                ordering=axis.axisOrdering,  # TODO: rename to axisOrdering
            )
            for axis in doc.axes
        ],
        locations=[
            LocationFormat4(
                name=NameRecord({"en": label.name, **label.labelNames}),
                axis_values=label.location,
                flags=_label_to_flag_list(label),
            )
            for label in doc.locationLabels
        ],
        elided_fallback_name_id=2,  # FIXME: should this be DSv5?
    )

    ribbi_mapping = get_ribbi_mapping(doc)

    # Make one DesignspaceDoc v4 for each variable font
    variable_fonts = {}
    for vf in doc.variableFonts:
        vf_doc = DesignSpaceDocument()

        # For each axis, 2 cases:
        #  - it has a range = it's an axis in the VF DS
        #  - it's a single location = write in the lib org.statmake.additionalLocations of VF DS
        axes_with_range: Dict[str, AxisDescriptor] = {}
        axes_with_single_location: Dict[str, float] = {}
        for axis_subset in vf.axisSubsets:
            axis = doc.getAxis(axis_subset.name)
            if isinstance(axis_subset, RangeAxisSubsetDescriptor):
                vf_axis = AxisDescriptor(
                    # Same info
                    tag=axis.tag,
                    name=axis.name,
                    labelNames=axis.labelNames,
                    hidden=axis.hidden,
                    # Subset range
                    minimum=max(axis_subset.userMinimum, axis.minimum),
                    default=axis_subset.userDefault or axis.default,
                    maximum=min(axis_subset.userMaximum, axis.maximum),
                    map=[
                        (user, design)
                        for user, design in axis.map
                        if axis_subset.userMinimum <= user <= axis_subset.userMaximum
                    ],
                    # Don't include any new-in-DS5 info
                    axisOrdering=None,
                    axisLabels=None,
                )
                axes_with_range[axis.name] = vf_axis
                vf_doc.addAxis(vf_axis)
            else:
                axes_with_single_location[axis.name] = axis_subset.userValue
        # Any axis not mentioned explicitly has a single location = default value
        for axis in doc.axes:
            if (
                axis.name not in axes_with_range
                and axis.name not in axes_with_single_location
            ):
                axes_with_single_location[axis.name] = axis.default

        region_selection: RegionSelection = _region_selection_from(
            axes_with_range, axes_with_single_location
        )
        # Rules: subset them based on conditions
        vf_doc.rules = _subset_rules_based_on_conditions(doc.rules, region_selection)
        vf_doc.rulesProcessingLast = doc.rulesProcessingLast

        # Sources: keep only the ones that fall within the kept axis ranges
        # FIXME: validate in advance that sources exist at the corners of the subset?
        #           argument to not bother = it will blow up anyway eventually
        #           should be done later though in order to provide a nice error message immediately after reading the designspace
        for source in doc.sources:
            if not location_in_selection(source.location, region_selection):
                continue

            vf_doc.addSource(
                SourceDescriptor(
                    filename=source.filename,
                    path=source.path,
                    font=source.font,
                    name=source.name,
                    location=_filter_location(axes_with_range, source.location),
                    layerName=source.layerName,
                    familyName=source.familyName,
                    styleName=source.styleName,
                    # copyLib=False,
                    # copyInfo=False,
                    # copyGroups=False,
                    # copyFeatures=False,
                    muteKerning=source.muteKerning,
                    muteInfo=source.muteInfo,
                    mutedGlyphNames=source.mutedGlyphNames,
                )
            )

        # Instances: same as Sources + compute missing names
        for instance in doc.instances:
            if not location_in_selection(instance.location, region_selection):
                continue

            vf_instance_names = _make_STAT_names(doc, instance, ribbi_mapping)
            vf_doc.addInstance(
                InstanceDescriptor(
                    filename=instance.filename,
                    path=instance.path,
                    font=instance.font,
                    name=instance.name,
                    location=_filter_location(axes_with_range, instance.location),
                    familyName=(
                        instance.familyName or vf_instance_names.familyName or None
                    ),
                    styleName=instance.styleName or vf_instance_names.styleName or None,
                    postScriptFontName=(
                        instance.postScriptFontName
                        or vf_instance_names.postScriptFontName
                        or None
                    ),
                    styleMapFamilyName=(
                        instance.styleMapFamilyName
                        or vf_instance_names.styleMapFamilyName
                        or None
                    ),
                    styleMapStyleName=(
                        instance.styleMapStyleName
                        or vf_instance_names.styleMapStyleName
                        or None
                    ),
                    # localisedFamilyName=instance.localisedFamilyName
                    # or vf_instance_names.localisedFamilyName,
                    # localisedStyleName=instance.localisedStyleName
                    # or vf_instance_names.localisedStyleName,
                    # localisedStyleMapFamilyName=instance.localisedStyleMapFamilyName
                    # or vf_instance_names.localisedStyleMapFamilyName,
                    # localisedStyleMapStyleName=instance.localisedStyleMapStyleName
                    # or vf_instance_names.localisedStyleMapStyleName,
                    # Deprecated
                    # glyphs=None,
                    # kerning=True,
                    # info=True,
                    lib=instance.lib,
                    # No DS5 data
                    # label=None,
                )
            )

        vf_doc.lib = {
            **doc.lib,
            **vf.lib,
            DESIGNSPACE_STYLESPACE_INLINE_KEY: asdict(stylespace),
            "org.statmake.additionalLocations": axes_with_single_location,
        }

        variable_fonts[vf.name] = vf_doc

    return (variable_fonts, stylespace)


def _label_to_flag_list(
    label: Union[AxisLabelDescriptor, LocationLabelDescriptor]
) -> FlagList:
    flag_list = []
    if label.olderSibling:
        flag_list.append(AxisValueFlag.OlderSiblingFontAttribute)
    if label.elidable:
        flag_list.append(AxisValueFlag.ElidableAxisValueName)
    return FlagList(flag_list)


def _axis_label_to_stylespace_location(
    label: AxisLabelDescriptor,
) -> Union[LocationFormat1, LocationFormat2, LocationFormat3]:
    label_format = label.getFormat()
    name = NameRecord({"en": label.name, **label.labelNames})
    flags = _label_to_flag_list(label)
    if label_format == 1:
        return LocationFormat1(name=name, value=label.userValue, flags=flags)
    if label_format == 2:
        return LocationFormat2(
            name=name,
            value=label.userValue,
            range=[label.userMinimum, label.userMaximum],
            flags=flags,
        )
    if label_format == 3:
        return LocationFormat3(
            name=name,
            value=label.userValue,
            linked_value=label.linkedUserValue,
            flags=flags,
        )
    raise Exception("unreachable")


def _region_selection_from(
    axes_with_range: Dict[str, AxisDescriptor],
    axes_with_single_location: Dict[str, float],
) -> RegionSelection:
    region: RegionSelection = {}
    for axis_name, axis in axes_with_range.items():
        minimum = axis.minimum
        if minimum is not None:
            minimum = axis.map_forward(minimum)
        else:
            minimum = -math.inf
        maximum = axis.maximum
        if maximum is not None:
            maximum = axis.map_forward(maximum)
        else:
            maximum = math.inf
        region[axis_name] = Range(minimum, maximum)
    for axis_name, axis_value in axes_with_single_location.items():
        region[axis_name] = axis_value
    return region


def _condition_set_from(condition_set: List[Dict[str, Any]]) -> ConditionSet:
    c: ConditionSet = {}
    for condition in condition_set:
        c[condition["name"]] = Range(
            condition.get("minimum") or -math.inf, condition.get("maximum") or math.inf
        )
    return c


def _subset_rules_based_on_conditions(
    rules: List[RuleDescriptor], region_selection: RegionSelection
) -> List[RuleDescriptor]:
    # What rules to keep:
    #  - Keep the rule if any conditionset is relevant.
    #  - A conditionset is relevant if all conditions are relevant or it is empty.
    #  - A condition is relevant if
    #    - axis is point (C-AP),
    #       - and point in condition's range (C-AP-in)
    #       - else (C-AP-out) whole conditionset can be discarded (condition false
    #         => conditionset false)
    #    - axis is range (C-AR),
    #       - (C-AR-all) and axis range fully contained in condition range: we can
    #         scrap the condition because it's always true
    #       - (C-AR-inter) and intersection(axis range, condition range) not empty:
    #         keep the condition with the smaller range (= intersection)
    #       - (C-AR-none) else, whole conditionset can be discarded

    new_rules: List[RuleDescriptor] = []
    for rule in rules:
        new_rule: RuleDescriptor = RuleDescriptor(
            name=rule.name, conditionSets=[], subs=rule.subs
        )
        for conditionset in rule.conditionSets:
            cs = _condition_set_from(conditionset)
            new_conditionset: List[Dict[str, Any]] = []
            discard_conditionset = False
            for selection_name, selection_value in region_selection.items():
                # TODO: Ensure that all(key in conditionset for key in region_selection.keys())?
                if selection_name not in cs:
                    # raise Exception("Selection has different axes than the rules")
                    continue
                if isinstance(selection_value, (float, int)):  # is point
                    # Case C-AP-in
                    if selection_value in cs[selection_name]:
                        pass  # always matches, conditionset can stay empty for this one.
                    # Case C-AP-out
                    else:
                        discard_conditionset = True
                else:  # is range
                    # Case C-AR-all
                    if selection_value in cs[selection_name]:
                        pass  # always matches, conditionset can stay empty for this one.
                    # Case C-AR-inter
                    elif cs[selection_name].intersection(selection_value) is not None:
                        intersection = cs[selection_name].intersection(selection_value)
                        new_conditionset.append(
                            {
                                "name": selection_name,
                                "minimum": intersection.start,
                                "maximum": intersection.end,
                            }
                        )
                    # Case C-AR-none
                    else:
                        discard_conditionset = True
            if not discard_conditionset:
                new_rule.conditionSets.append(new_conditionset)
        if new_rule.conditionSets:
            new_rules.append(new_rule)

    return new_rules


def _filter_location(
    axes_with_range: Dict[str, AxisDescriptor],
    location: Dict[str, float],
) -> Dict[str, float]:
    return {k: v for k, v in location.items() if k in axes_with_range}


@dataclass
class StatNames:
    familyName: str
    styleName: str
    postScriptFontName: str
    styleMapFamilyName: str | None
    styleMapStyleName: str | None


# TODO: Deal with anisotropic locations.
# TODO: Deal with localization.
# TODO: Decide how to deal with familyName, for which there would need to be a
#       new localized familyname element in sources, unless it's ok to query the
#       source UFO directly (but what about source TTFs?)
# TODO: Deal with STAT format 2 ranges.
def _make_STAT_names(
    doc: DesignSpaceDocument,
    instance: InstanceDescriptor,
    ribbi_mapping: dict[tuple[tuple[str, float], ...], RibbiStyle],
) -> StatNames:
    user_location = location_to_user_location(doc, instance.location)

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
            if instance.styleName is None:
                instance_id: str = instance.name or repr(instance.location)
                raise DesignSpaceDocumentError(
                    f"Cannot infer style name for instance '{instance_id}' because all "
                    "labels are elided. Please fill in the 'stylename' attribute yourself."
                )
            else:
                style_name = instance.styleName

    if family_name is None:
        post_script_font_name = None
    else:
        post_script_font_name = f"{family_name}-{style_name}".replace(" ", "")

    # TODO: look at how ufo2ft generates style_map_family_name
    style_map_family_name = None
    style_map_style_name = ribbi_mapping.get(tuple(instance.location.items()))

    return StatNames(
        familyName=family_name,
        styleName=style_name,
        postScriptFontName=post_script_font_name,
        styleMapFamilyName=style_map_family_name,
        styleMapStyleName=style_map_style_name,
    )


def location_to_user_location(doc: DesignSpaceDocument, location: Location) -> Location:
    axes_by_name: Dict[str, AxisDescriptor] = {a.name: a for a in doc.axes}
    return {k: axes_by_name[k].map_backward(v) for k, v in location.items()}


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


RibbiStyle = Union[
    Literal["regular"], Literal["bold"], Literal["italic"], Literal["bold italic"]
]


# TODO: Also grab labels when no linkedUserValue is set? I.e. from well-known axis positions?
def get_ribbi_mapping(
    doc: DesignSpaceDocument,
) -> dict[tuple[tuple[str, float], ...], RibbiStyle]:
    default_location: Location = doc.newDefaultLocation()
    if default_location is None:
        raise DesignSpaceDocumentError("Cannot determine default location.")
    mapping: dict[tuple[tuple[str, float], ...], RibbiStyle] = {}

    bold_value: tuple[str, float] | None = None
    italic_value: tuple[str, float] | None = None

    axes_by_tag = {a.tag: a for a in doc.axes}
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
