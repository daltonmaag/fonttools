"""Extra method for DesignSpaceDocument to convert itself from a version 5
document to a list of version 4 documents, one per variable font.
"""
# pyright: basic

# FIXME: How to deal with Designspaces where e.g. the wght axis mapping differs slightly? See
#        e.g. Source Serif 4.

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional, Union

from fontTools.designspaceLib import (
    AxisDescriptor,
    DesignSpaceDocument,
    InstanceDescriptor,
    RangeAxisSubsetDescriptor,
    RuleDescriptor,
    SimpleLocationDict,
    SourceDescriptor,
)
from fontTools.designspaceLib.statNames import RibbiStyle

LOGGER = logging.getLogger(__name__)


def convert5to4(
    self: DesignSpaceDocument,
    ribbi_mapping: dict[tuple[tuple[str, float], ...], RibbiStyle] = None,
) -> Dict[str, DesignSpaceDocument]:
    if ribbi_mapping is None:
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

            stat_names = instance.getStatNames(self, ribbi_mapping)
            vf_doc.addInstance(
                InstanceDescriptor(
                    filename=instance.filename,
                    path=instance.path,
                    font=instance.font,
                    name=instance.name,
                    location=_filter_location(axes_with_range, instance.location),
                    familyName=(instance.familyName or stat_names.familyName or None),
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
class Range:
    __slots__ = "start", "end"

    start: float
    """Inclusive start of the range."""
    end: float
    """Inclusive end of the range."""

    def __contains__(self, value: Union[float, Range, Stops]) -> bool:
        if isinstance(value, Range):
            start, end = sorted((value.start, value.end))
            return self.start <= start <= self.end and self.start <= end <= self.end
        if isinstance(value, Stops):
            return all(self.start <= stop <= self.end for stop in value.stops)
        return self.start <= value <= self.end

    def intersection(self, other: Range) -> Optional[Range]:
        self_start, self_end = sorted((self.start, self.end))
        other_start, other_end = sorted((other.start, other.end))
        if self_end < other_start or self_start > other_end:
            return None
        else:
            return Range(max(self_start, other_start), min(self_end, other_end))


@dataclass
class Stops:
    __slots__ = "stops"

    stops: set[float]

    def __contains__(self, value: Union[float, Range, Stops]) -> bool:
        if isinstance(value, Range):
            return value.start == value.end and value.start in self.stops
        if isinstance(value, Stops):
            return all(stop in self.stops for stop in value.stops)
        return value in self.stops


Region = Mapping[str, Union[Range, Stops]]


# A region selection is either a range or a single value, as a Designspace v5
# axis-subset element only allows a single discrete value or a range for a
# variable-font element.
RegionSelection = Mapping[str, Union[Range, float]]

# A conditionset is a set of named ranges.
ConditionSet = Mapping[str, Range]

# A rule is a list of conditionsets where any has to be relevant for the whole rule to be relevant.
Rule = List[ConditionSet]
Rules = Dict[str, Rule]


def in_region(
    value: Union[SimpleLocationDict, RegionSelection, Region], region: Region
) -> bool:
    return value.keys() == region.keys() and all(
        value in region[name] for name, value in value.items()
    )


def location_in_selection(
    location: SimpleLocationDict, selection: RegionSelection
) -> bool:
    if location.keys() != selection.keys():
        return False
    for name, value in location.items():
        selection_value = selection[name]
        if isinstance(selection_value, (float, int)):
            if value != selection_value:
                return False
        else:
            if value not in selection_value:
                return False
    return True
