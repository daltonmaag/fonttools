"""Extra method for DesignSpaceDocument to convert itself from a version 5
document to a list of version 4 documents, one per variable font.
"""
# pyright: basic

# FIXME: we're building a stylespace as in statmake but it's not part of fontTools
# TODO: either move this converter out of fontTools so it can keep creating the stylespace
#       or make this converter use the fontTools APIs for stat/generate data for these
# FIXME: How to deal with Designspaces where e.g. the wght axis mapping differs slightly? See
#        e.g. Source Serif 4.

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union

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

LOGGER = logging.getLogger(__name__)


def convert5to4(
    self: DesignSpaceDocument,
) -> Dict[str, DesignSpaceDocument]:
    ribbi_mapping = self.getRibbiMapping()

    # Make one DesignspaceDoc v4 for each variable font
    variable_fonts = {}
    for vf in self.variableFonts:
        vf_doc = DesignSpaceDocument()

        # For each axis, 2 cases:
        #  - it has a range = it's an axis in the VF DS
        #  - it's a single location = write in the lib org.statmake.additionalLocations of VF DS
        axes_with_range: Dict[str, AxisDescriptor] = {}
        axes_with_single_location: Dict[str, float] = {}
        for axis_subset in vf.axisSubsets:
            axis = self.getAxis(axis_subset.name)
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
        for axis in self.axes:
            if (
                axis.name not in axes_with_range
                and axis.name not in axes_with_single_location
            ):
                axes_with_single_location[axis.name] = axis.default

        region_selection: RegionSelection = _region_selection_from(
            axes_with_range, axes_with_single_location
        )
        # Rules: subset them based on conditions
        vf_doc.rules = _subset_rules_based_on_conditions(self.rules, region_selection)
        vf_doc.rulesProcessingLast = self.rulesProcessingLast

        # Sources: keep only the ones that fall within the kept axis ranges
        for source in self.sources:
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
        for instance in self.instances:
            if not location_in_selection(instance.location, region_selection):
                continue

            stat_names = _make_STAT_names(self, instance, ribbi_mapping)
            vf_doc.addInstance(
                InstanceDescriptor(
                    filename=instance.filename,
                    path=instance.path,
                    font=instance.font,
                    name=instance.name,
                    location=_filter_location(axes_with_range, instance.location),
                    familyName=(
                        instance.familyName or stat_names.familyName or None
                    ),
                    styleName=instance.styleName or stat_names.styleName or None,
                    postScriptFontName=(
                        instance.postScriptFontName
                        or stat_names.postScriptFontName
                        or None
                    ),
                    styleMapFamilyName=(
                        instance.styleMapFamilyName
                        or stat_names.styleMapFamilyName
                        or None
                    ),
                    styleMapStyleName=(
                        instance.styleMapStyleName
                        or stat_names.styleMapStyleName
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
            **self.lib,
            **vf.lib,
        }

        variable_fonts[vf.filename] = vf_doc

    return variable_fonts


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
