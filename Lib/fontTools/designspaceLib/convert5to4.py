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

LOGGER = logging.getLogger(__name__)


def convert5to4(
    self: DesignSpaceDocument,
) -> Dict[str, DesignSpaceDocument]:
    # Make one DesignspaceDoc v4 for each variable font
    variableFonts = {}
    for vf in self.variableFonts:
        vfDoc = DesignSpaceDocument()
        vfDoc.formatVersion = "4.1"

        # For each axis, 2 cases:
        #  - it has a range = it's an axis in the VF DS
        #  - it's a single location = write in the lib org.statmake.additionalLocations of VF DS
        axesWithRange: Dict[str, AxisDescriptor] = {}
        axesWithSingleLocation: Dict[str, float] = {}
        for axesSubset in vf.axisSubsets:
            axis = self.getAxis(axesSubset.name)
            if isinstance(axesSubset, RangeAxisSubsetDescriptor):
                vfAxis = AxisDescriptor(
                    # Same info
                    tag=axis.tag,
                    name=axis.name,
                    labelNames=axis.labelNames,
                    hidden=axis.hidden,
                    # Subset range
                    minimum=max(axesSubset.userMinimum, axis.minimum),
                    default=axesSubset.userDefault or axis.default,
                    maximum=min(axesSubset.userMaximum, axis.maximum),
                    map=[
                        (user, design)
                        for user, design in axis.map
                        if axesSubset.userMinimum <= user <= axesSubset.userMaximum
                    ],
                    # Don't include any new-in-DS5 info
                    axisOrdering=None,
                    axisLabels=None,
                )
                axesWithRange[axis.name] = vfAxis
                vfDoc.addAxis(vfAxis)
            else:
                axesWithSingleLocation[axis.name] = axesSubset.userValue
        # Any axis not mentioned explicitly has a single location = default value
        for axis in self.axes:
            if (
                axis.name not in axesWithRange
                and axis.name not in axesWithSingleLocation
            ):
                axesWithSingleLocation[axis.name] = axis.default

        regionSelection: RegionSelection = _regionSelectionFrom(
            axesWithRange, axesWithSingleLocation
        )
        # Rules: subset them based on conditions
        vfDoc.rules = _subsetRulesBasedOnConditions(self.rules, regionSelection)
        vfDoc.rulesProcessingLast = self.rulesProcessingLast

        # Sources: keep only the ones that fall within the kept axis ranges
        for source in self.sources:
            if not _locationInSelection(source.location, regionSelection):
                continue

            vfDoc.addSource(
                SourceDescriptor(
                    filename=source.filename,
                    path=source.path,
                    font=source.font,
                    name=source.name,
                    location=_filter_location(axesWithRange, source.location),
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
            if not _locationInSelection(instance.location, regionSelection):
                continue

            statNames = instance.getStatNames(self)
            vfDoc.addInstance(
                InstanceDescriptor(
                    filename=instance.filename,
                    path=instance.path,
                    font=instance.font,
                    name=instance.name,
                    location=_filter_location(axesWithRange, instance.location),
                    familyName=instance.familyName or statNames.familyNames.get("en"),
                    styleName=instance.styleName or statNames.styleNames.get("en"),
                    postScriptFontName=instance.postScriptFontName
                    or statNames.postScriptFontName,
                    styleMapFamilyName=instance.styleMapFamilyName
                    or statNames.styleMapFamilyNames.get("en"),
                    styleMapStyleName=instance.styleMapStyleName
                    or statNames.styleMapStyleName,
                    localisedFamilyName=instance.localisedFamilyName
                    or statNames.familyNames,
                    localisedStyleName=instance.localisedStyleName
                    or statNames.styleNames,
                    localisedStyleMapFamilyName=instance.localisedStyleMapFamilyName
                    or statNames.styleMapFamilyNames,
                    localisedStyleMapStyleName=instance.localisedStyleMapStyleName
                    or {},
                    # Deprecated
                    # glyphs=None,
                    # kerning=True,
                    # info=True,
                    lib=instance.lib,
                    # No DS5 data
                    # label=None,
                )
            )

        vfDoc.lib = {
            **self.lib,
            **vf.lib,
        }

        variableFonts[vf.filename] = vfDoc

    return variableFonts


def _regionSelectionFrom(
    axesWithRange: Dict[str, AxisDescriptor],
    axesWithSingleLocation: Dict[str, float],
) -> RegionSelection:
    region: RegionSelection = {}
    for axis_name, axis in axesWithRange.items():
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
    for axis_name, axis_value in axesWithSingleLocation.items():
        region[axis_name] = axis_value
    return region


def _conditionSetFrom(conditionSet: List[Dict[str, Any]]) -> ConditionSet:
    c: ConditionSet = {}
    for condition in conditionSet:
        c[condition["name"]] = Range(
            condition.get("minimum") or -math.inf, condition.get("maximum") or math.inf
        )
    return c


def _subsetRulesBasedOnConditions(
    rules: List[RuleDescriptor], regionSelection: RegionSelection
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

    newRules: List[RuleDescriptor] = []
    for rule in rules:
        newRule: RuleDescriptor = RuleDescriptor(
            name=rule.name, conditionSets=[], subs=rule.subs
        )
        for conditionset in rule.conditionSets:
            cs = _conditionSetFrom(conditionset)
            newConditionset: List[Dict[str, Any]] = []
            discardConditionset = False
            for selectionName, selectionValue in regionSelection.items():
                # TODO: Ensure that all(key in conditionset for key in regionSelection.keys())?
                if selectionName not in cs:
                    # raise Exception("Selection has different axes than the rules")
                    continue
                if isinstance(selectionValue, (float, int)):  # is point
                    # Case C-AP-in
                    if selectionValue in cs[selectionName]:
                        pass  # always matches, conditionset can stay empty for this one.
                    # Case C-AP-out
                    else:
                        discardConditionset = True
                else:  # is range
                    # Case C-AR-all
                    if selectionValue in cs[selectionName]:
                        pass  # always matches, conditionset can stay empty for this one.
                    # Case C-AR-inter
                    elif cs[selectionName].intersection(selectionValue) is not None:
                        intersection = cs[selectionName].intersection(selectionValue)
                        newConditionset.append(
                            {
                                "name": selectionName,
                                "minimum": intersection.start,
                                "maximum": intersection.end,
                            }
                        )
                    # Case C-AR-none
                    else:
                        discardConditionset = True
            if not discardConditionset:
                newRule.conditionSets.append(newConditionset)
        if newRule.conditionSets:
            newRules.append(newRule)

    return newRules


def _filter_location(
    axesWithRange: Dict[str, AxisDescriptor],
    location: Dict[str, float],
) -> Dict[str, float]:
    return {k: v for k, v in location.items() if k in axesWithRange}


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
        selfStart, selfEnd = sorted((self.start, self.end))
        otherStart, otherEnd = sorted((other.start, other.end))
        if selfEnd < otherStart or selfStart > otherEnd:
            return None
        else:
            return Range(max(selfStart, otherStart), min(selfEnd, otherEnd))


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


def _locationInSelection(
    location: SimpleLocationDict, selection: RegionSelection
) -> bool:
    if location.keys() != selection.keys():
        return False
    for name, value in location.items():
        selectionValue = selection[name]
        if isinstance(selectionValue, (float, int)):
            if value != selectionValue:
                return False
        else:
            if value not in selectionValue:
                return False
    return True
