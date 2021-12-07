#################################
DesignSpaceDocument Specification
#################################

An object to read, write and edit interpolation systems for typefaces.
Define sources, axes, rules, variable fonts and instances.

-  `The Python API of the objects <#python-api>`_
-  `The document XML structure <#document-xml-structure>`_


**********
Python API
**********



.. _designspacedocument-object:

DesignSpaceDocument object
==========================

.. autoclass:: fontTools.designspaceLib::DesignSpaceDocument
   :members:
   :undoc-members:
   :member-order: bysource


AxisDescriptor object
=====================

.. autoclass:: fontTools.designspaceLib::AxisDescriptor
   :members:
   :undoc-members:
   :inherited-members: SimpleDescriptor
   :member-order: bysource


DiscreteAxisDescriptor object
=============================

.. autoclass:: fontTools.designspaceLib::DiscreteAxisDescriptor
   :members:
   :undoc-members:
   :inherited-members: SimpleDescriptor
   :member-order: bysource


AxisLabelDescriptor object
==========================

.. autoclass:: fontTools.designspaceLib::AxisLabelDescriptor
   :members:
   :undoc-members:
   :member-order: bysource


LocationLabelDescriptor object
==========================

.. autoclass:: fontTools.designspaceLib::LocationLabelDescriptor
   :members:
   :undoc-members:
   :member-order: bysource


SourceDescriptor object
=======================

.. autoclass:: fontTools.designspaceLib::SourceDescriptor
   :members:
   :undoc-members:
   :member-order: bysource


VariableFontDescriptor object
=============================

.. autoclass:: fontTools.designspaceLib::VariableFontDescriptor
   :members:
   :undoc-members:
   :member-order: bysource


RangeAxisSubsetDescriptor object
================================

.. autoclass:: fontTools.designspaceLib::RangeAxisSubsetDescriptor
   :members:
   :undoc-members:
   :member-order: bysource


ValueAxisSubsetDescriptor object
================================

.. autoclass:: fontTools.designspaceLib::ValueAxisSubsetDescriptor
   :members:
   :undoc-members:
   :member-order: bysource


InstanceDescriptor object
=========================

.. autoclass:: fontTools.designspaceLib::InstanceDescriptor
   :members:
   :undoc-members:
   :member-order: bysource


RuleDescriptor object
=====================

.. autoclass:: fontTools.designspaceLib::RuleDescriptor
   :members:
   :undoc-members:
   :member-order: bysource


Evaluating rules
----------------

.. autofunction:: fontTools.designspaceLib::evaluateRule
.. autofunction:: fontTools.designspaceLib::evaluateConditions
.. autofunction:: fontTools.designspaceLib::processRules


.. _subclassing-descriptors:

Subclassing descriptors
=======================

The DesignSpaceDocument can take subclassed Reader and Writer objects.
This allows you to work with your own descriptors. You could subclass
the descriptors. But as long as they have the basic attributes the
descriptor does not need to be a subclass.

.. code:: python

    class MyDocReader(BaseDocReader):
        axisDescriptorClass = MyAxisDescriptor
        discreteAxisDescriptorClass = MyDiscreteAxisDescriptor
        axisLabelDescriptorClass = MyAxisLabelDescriptor
        locationLabelDescriptorClass = MyLocationLabelDescriptor
        sourceDescriptorClass = MySourceDescriptor
        variableFontsDescriptorClass = MyVariableFontDescriptor
        valueAxisSubsetDescriptorClass = MyValueAxisSubsetDescriptor
        rangeAxisSubsetDescriptorClass = MyRangeAxisSubsetDescriptor
        instanceDescriptorClass = MyInstanceDescriptor
        ruleDescriptorClass = MyRuleDescriptor

    class MyDocWriter(BaseDocWriter):
        axisDescriptorClass = MyAxisDescriptor
        discreteAxisDescriptorClass = MyDiscreteAxisDescriptor
        axisLabelDescriptorClass = MyAxisLabelDescriptor
        locationLabelDescriptorClass = MyLocationLabelDescriptor
        sourceDescriptorClass = MySourceDescriptor
        variableFontsDescriptorClass = MyVariableFontDescriptor
        valueAxisSubsetDescriptorClass = MyValueAxisSubsetDescriptor
        rangeAxisSubsetDescriptorClass = MyRangeAxisSubsetDescriptor
        instanceDescriptorClass = MyInstanceDescriptor
        ruleDescriptorClass = MyRuleDescriptor

    myDoc = DesignSpaceDocument(MyDocReader, MyDocWriter)


**********************
Document xml structure
**********************


-  The ``axes`` element contains one or more ``axis`` elements.
-  The ``labels`` element contains one or more ``label`` elements.
-  The ``sources`` element contains one or more ``source`` elements.
-  The ``variable-fonts`` element contains one or more ``variable-font`` elements.
-  The ``instances`` element contains one or more ``instance`` elements.
-  The ``rules`` element contains one or more ``rule`` elements.
-  The ``lib`` element contains arbitrary data.

.. code:: xml

    <?xml version='1.0' encoding='utf-8'?>
    <designspace format="3">
        <axes>
            <!-- define axes here -->
            <axis ... />
        </axes>
        <labels>
            <!-- define STAT format 4 labels here -->
            <!-- New in version 5.0 -->
            <label ... />
        </labels>
        <sources>
            <!-- define masters here -->
            <source ... />
        </sources>
        <variable-fonts>
            <!-- define variable fonts here -->
            <!-- New in version 5.0 -->
            <variable-font ... />
        </variable-fonts>
        <instances>
            <!-- define instances here -->
            <instance ... />
        </instances>
        <rules>
            <!-- define rules here -->
            <rule ... />
        </rules>
        <lib>
            <dict>
                <!-- store custom data here -->
            </dict>
        </lib>
    </designspace>

.. 1-axis-element:

1. axis element
===============

-  Define a single axis
-  Child element of ``axes``
-  The axis can be either continuous (as in version 4.0) or discrete (new in version 5.0).
Discrete axes have a list of discrete values instead of a range.

.. attributes-2:

Attributes
----------

-  ``name``: required, string. Name of the axis that is used in the
   location elements.
-  ``tag``: required, string, 4 letters. Some axis tags are registered
   in the OpenType Specification.
-  ``default``: required, number. The default value for this axis, in user space coordinates.
-  ``hidden``: optional, 0 or 1. Records whether this axis needs to be
   hidden in interfaces.

-  ``minimum``: required, number. The minimum value for this axis, in user space coordinates.
-  ``maximum``: required, number. The maximum value for this axis, in user space coordinates.

.. code:: xml

    <axis name="weight" tag="wght" minimum="1" maximum="1000" default="400">

    <!--
      Discrete axes provide a list of discrete values.
      No interpolation is allowed between these.
    -->
    <axis name="Italic" tag="ital" default="0" values="0 1">

.. 11-labelname-element:

1.1 labelname element
=====================

-  Defines a human readable name for UI use.
-  Optional for non-registered axis names.
-  Can be localised with ``xml:lang``
-  Child element of ``axis``

.. attributes-3:

Attributes
----------

-  ``xml:lang``: required, string. `XML language
   definition <https://www.w3.org/International/questions/qa-when-xmllang.en>`__

Value
-----

-  The natural language name of this axis.

.. example-2:

Example
-------

.. code:: xml

    <labelname xml:lang="fa-IR">قطر</labelname>
    <labelname xml:lang="en">Wéíght</labelname>


.. 12-map-element:

1.2 map element
===============

-  Defines a single node in a series of input value (user space coordinate)
   to output value (designspace coordinate) pairs.
-  Together these values transform the designspace.
-  Child of ``axis`` element.

.. example-3:

Example
-------

.. code:: xml

    <map input="1.0" output="10.0" />
    <map input="400.0" output="66.0" />
    <map input="1000.0" output="990.0" />


.. 13-labels-element:

1.3 labels and label elements
=============================

-  Define STAT format 1, 2, 3 labels for the locations on this axis.
-  The axis can have several ``label`` elements,
TODO here

.. example-3:

Example
-------

.. code:: xml

    <map input="1.0" output="10.0" />
    <map input="400.0" output="66.0" />
    <map input="1000.0" output="990.0" />


Example of all axis elements together:
--------------------------------------

.. code:: xml

        <axes>
            <axis default="1" maximum="1000" minimum="0" name="weight" tag="wght">
                <labelname xml:lang="fa-IR">قطر</labelname>
                <labelname xml:lang="en">Wéíght</labelname>
            </axis>
            <axis default="100" maximum="200" minimum="50" name="width" tag="wdth">
                <map input="50.0" output="10.0" />
                <map input="100.0" output="66.0" />
                <map input="200.0" output="990.0" />
            </axis>
        </axes>

.. 2-location-element:

1. location element
===================

-  Defines a coordinate in the design space.
-  Dictionary of axisname: axisvalue
-  Used in ``source``, ``instance`` and ``glyph`` elements.

.. 21-dimension-element:

2.1 dimension element
=====================

-  Child element of ``location``

.. attributes-4:

Attributes
----------

-  ``name``: required, string. Name of the axis.
-  ``xvalue``: required, number. The value on this axis.
-  ``yvalue``: optional, number. Separate value for anisotropic
   interpolations.

.. example-4:

Example
-------

.. code:: xml

    <location>
        <dimension name="width" xvalue="0.000000" />
        <dimension name="weight" xvalue="0.000000" yvalue="0.003" />
    </location>

.. 3-source-element:

3. source element
=================

-  Defines a single font or layer that contributes to the designspace.
-  Child element of ``sources``
-  Location in designspace coordinates.

.. attributes-5:

Attributes
----------

-  ``familyname``: optional, string. The family name of the source font.
   While this could be extracted from the font data itself, it can be
   more efficient to add it here.
-  ``stylename``: optional, string. The style name of the source font.
-  ``name``: required, string. A unique name that can be used to
   identify this font if it needs to be referenced elsewhere.
-  ``filename``: required, string. A path to the source file, relative
   to the root path of this document. The path can be at the same level
   as the document or lower.
-  ``layer``: optional, string. The name of the layer in the source file.
   If no layer attribute is given assume the foreground layer should be used.

.. 31-lib-element:

3.1 lib element
===============

There are two meanings for the ``lib`` element:

1. Source lib
    -  Example: ``<lib copy="1" />``
    -  Child element of ``source``
    -  Defines if the instances can inherit the data in the lib of this
       source.
    -  MutatorMath only

2. Document and instance lib
    - Example:

      .. code:: xml

        <lib>
            <dict>
                <key>...</key>
                <string>The contents use the PLIST format.</string>
            </dict>
        </lib>

    - Child element of ``designspace`` and ``instance``
    - Contains arbitrary data about the whole document or about a specific
      instance.
    - Items in the dict need to use **reverse domain name notation** <https://en.wikipedia.org/wiki/Reverse_domain_name_notation>__

.. 32-info-element:

3.2 info element
================

-  ``<info copy="1" />``
-  Child element of ``source``
-  Defines if the instances can inherit the non-interpolating font info
   from this source.
-  MutatorMath

.. 33-features-element:

3.3 features element
====================

-  ``<features copy="1" />``
-  Defines if the instances can inherit opentype feature text from this
   source.
-  Child element of ``source``
-  MutatorMath only

.. 34-glyph-element:

3.4 glyph element
=================

-  Can appear in ``source`` as well as in ``instance`` elements.
-  In a ``source`` element this states if a glyph is to be excluded from
   the calculation.
-  MutatorMath only

.. attributes-6:

Attributes
----------

-  ``mute``: optional attribute, number 1 or 0. Indicate if this glyph
   should be ignored as a master.
-  ``<glyph mute="1" name="A"/>``
-  MutatorMath only

.. 35-kerning-element:

3.5 kerning element
===================

-  ``<kerning mute="1" />``
-  Can appear in ``source`` as well as in ``instance`` elements.

.. attributes-7:

Attributes
----------

-  ``mute``: required attribute, number 1 or 0. Indicate if the kerning
   data from this source is to be excluded from the calculation.
-  If the kerning element is not present, assume ``mute=0``, yes,
   include the kerning of this source in the calculation.
-  MutatorMath only

.. example-5:

Example
-------

.. code:: xml

    <source familyname="MasterFamilyName" filename="masters/masterTest1.ufo" name="master.ufo1" stylename="MasterStyleNameOne">
        <lib copy="1" />
        <features copy="1" />
        <info copy="1" />
        <glyph mute="1" name="A" />
        <glyph mute="1" name="Z" />
        <location>
            <dimension name="width" xvalue="0.000000" />
            <dimension name="weight" xvalue="0.000000" />
        </location>
    </source>

.. 4-instance-element:

4. instance element
===================

-  Defines a single font that can be calculated with the designspace.
-  Child element of ``instances``
-  For use in Varlib the instance element really only needs the names
   and the location. The ``glyphs`` element is not required.
-  MutatorMath uses the ``glyphs`` element to describe how certain
   glyphs need different masters, mainly to describe the effects of
   conditional rules in Superpolator.
-  Location in designspace coordinates.

.. attributes-8:

Attributes
----------

-  ``familyname``: required, string. The family name of the instance
   font. Corresponds with ``font.info.familyName``
-  ``stylename``: required, string. The style name of the instance font.
   Corresponds with ``font.info.styleName``
-  ``name``: required, string. A unique name that can be used to
   identify this font if it needs to be referenced elsewhere.
-  ``filename``: string. Required for MutatorMath. A path to the
   instance file, relative to the root path of this document. The path
   can be at the same level as the document or lower.
-  ``postscriptfontname``: string. Optional for MutatorMath. Corresponds
   with ``font.info.postscriptFontName``
-  ``stylemapfamilyname``: string. Optional for MutatorMath. Corresponds
   with ``styleMapFamilyName``
-  ``stylemapstylename``: string. Optional for MutatorMath. Corresponds
   with ``styleMapStyleName``

Example for varlib
------------------

.. code:: xml

    <instance familyname="InstanceFamilyName" filename="instances/instanceTest2.ufo" name="instance.ufo2" postscriptfontname="InstancePostscriptName" stylemapfamilyname="InstanceStyleMapFamilyName" stylemapstylename="InstanceStyleMapStyleName" stylename="InstanceStyleName">
    <location>
        <dimension name="width" xvalue="400" yvalue="300" />
        <dimension name="weight" xvalue="66" />
    </location>
    <kerning />
    <info />
    <lib>
        <dict>
            <key>com.coolDesignspaceApp.specimenText</key>
            <string>Hamburgerwhatever</string>
        </dict>
    </lib>
    </instance>

.. 41-glyphs-element:

4.1 glyphs element
==================

-  Container for ``glyph`` elements.
-  Optional
-  MutatorMath only.

.. 42-glyph-element:

4.2 glyph element
=================

-  Child element of ``glyphs``
-  May contain a ``location`` element.

.. attributes-9:

Attributes
----------

-  ``name``: string. The name of the glyph.
-  ``unicode``: string. Unicode values for this glyph, in hexadecimal.
   Multiple values should be separated with a space.
-  ``mute``: optional attribute, number 1 or 0. Indicate if this glyph
   should be supressed in the output.

.. 421-note-element:

4.2.1 note element
==================

-  String. The value corresponds to glyph.note in UFO.

.. 422-masters-element:

4.2.2 masters element
=====================

-  Container for ``master`` elements
-  These ``master`` elements define an alternative set of glyph masters
   for this glyph.

.. 4221-master-element:

4.2.2.1 master element
======================

-  Defines a single alternative master for this glyph.

4.3 Localised names for instances
=================================

Localised names for instances can be included with these simple elements
with an ``xml:lang`` attribute:
`XML language definition <https://www.w3.org/International/questions/qa-when-xmllang.en>`__

-  stylename
-  familyname
-  stylemapstylename
-  stylemapfamilyname

.. example-6:

Example
-------

.. code:: xml

    <stylename xml:lang="fr">Demigras</stylename>
    <stylename xml:lang="ja">半ば</stylename>
    <familyname xml:lang="fr">Montserrat</familyname>
    <familyname xml:lang="ja">モンセラート</familyname>
    <stylemapstylename xml:lang="de">Standard</stylemapstylename>
    <stylemapfamilyname xml:lang="de">Montserrat Halbfett</stylemapfamilyname>
    <stylemapfamilyname xml:lang="ja">モンセラート SemiBold</stylemapfamilyname>

.. attributes-10:

Attributes
----------

-  ``glyphname``: the name of the alternate master glyph.
-  ``source``: the identifier name of the source this master glyph needs
   to be loaded from

.. example-7:

Example
-------

.. code:: xml

    <instance familyname="InstanceFamilyName" filename="instances/instanceTest2.ufo" name="instance.ufo2" postscriptfontname="InstancePostscriptName" stylemapfamilyname="InstanceStyleMapFamilyName" stylemapstylename="InstanceStyleMapStyleName" stylename="InstanceStyleName">
    <location>
        <dimension name="width" xvalue="400" yvalue="300" />
        <dimension name="weight" xvalue="66" />
    </location>
    <glyphs>
        <glyph name="arrow2" />
        <glyph name="arrow" unicode="0x4d2 0x4d3">
        <location>
            <dimension name="width" xvalue="100" />
            <dimension name="weight" xvalue="120" />
        </location>
        <note>A note about this glyph</note>
        <masters>
            <master glyphname="BB" source="master.ufo1">
            <location>
                <dimension name="width" xvalue="20" />
                <dimension name="weight" xvalue="20" />
            </location>
            </master>
        </masters>
        </glyph>
    </glyphs>
    <kerning />
    <info />
    <lib>
        <dict>
            <key>com.coolDesignspaceApp.specimenText</key>
            <string>Hamburgerwhatever</string>
        </dict>
    </lib>
    </instance>

.. 50-rules-element:

5.0 rules element
=================

-  Container for ``rule`` elements
-  The rules are evaluated in this order.

Rules describe designspace areas in which one glyph should be replaced by another.
A rule has a name and a number of conditionsets. The rule also contains a list of
glyphname pairs: the glyphs that need to be substituted. For a rule to be triggered
**only one** of the conditionsets needs to be true, ``OR``. Within a conditionset
**all** conditions need to be true, ``AND``.

.. attributes-11:

Attributes
----------

-  ``processing``: flag, optional. Valid values are [``first``, ``last``]. This flag indicates whether the substitution rules should be applied before or after other glyph substitution features.
-  If no ``processing`` attribute is given, interpret as ``first``, and put the substitution rule in the ``rvrn`` feature.
-  If ``processing`` is ``last``, put it in ``rclt``.
-  If you want to use a different feature altogether, e.g. ``calt``, use the lib key ``com.github.fonttools.varLib.featureVarsFeatureTag``::

    <lib>
        <dict>
            <key>com.github.fonttools.varLib.featureVarsFeatureTag</key>
            <string>calt</string>
        </dict>
    </lib>


.. 51-rule-element:

5.1 rule element
================

-  Defines a named rule.
-  Each ``rule`` element contains one or more ``conditionset`` elements.
-  **Only one** ``conditionset`` needs to be true to trigger the rule.
-  **All** conditions in a ``conditionset`` must be true to make the ``conditionset`` true.
-  For backwards compatibility a ``rule`` can contain ``condition`` elements outside of a conditionset. These are then understood to be part of a single, implied, ``conditionset``. Note: these conditions should be written wrapped in a conditionset.
-  A rule element needs to contain one or more ``sub`` elements in order to be compiled to a variable font.
-  Rules without sub elements should be ignored when compiling a font.
-  For authoring tools it might be necessary to save designspace files without ``sub`` elements just because the work is incomplete.

.. attributes-11:

Attributes
----------

-  ``name``: optional, string. A unique name that can be used to
   identify this rule if it needs to be referenced elsewhere. The name
   is not important for compiling variable fonts.

5.1.1 conditionset element
==========================

-  Child element of ``rule``
-  Contains one or more ``condition`` elements.

.. 512-condition-element:

5.1.2 condition element
=======================

-  Child element of ``conditionset``
-  Between the ``minimum`` and ``maximum`` this condition is ``True``.
-  ``minimum`` and ``maximum`` are in designspace coordinates.
-  If ``minimum`` is not available, assume it is ``axis.minimum``, mapped to designspace coordinates.
-  If ``maximum`` is not available, assume it is ``axis.maximum``, mapped to designspace coordinates.
-  The condition must contain at least a minimum or maximum or both.

.. attributes-12:

Attributes
----------

-  ``name``: string, required. Must match one of the defined ``axis``
   name attributes.
-  ``minimum``: number, required*. The low value, in designspace coordinates.
-  ``maximum``: number, required*. The high value, in designspace coordinates.

.. 513-sub-element:

5.1.3 sub element
=================

-  Child element of ``rule``.
-  Defines which glyph to replace when the rule evaluates to **True**.
-  The ``sub`` element contains a pair of glyphnames. The ``name`` attribute is the glyph that should be visible when the rule evaluates to **False**. The ``with`` attribute is the glyph that should be visible when the rule evaluates to **True**.

Axis values in Conditions are in designspace coordinates.

.. attributes-13:

Attributes
----------

-  ``name``: string, required. The name of the glyph this rule looks
   for.
-  ``with``: string, required. The name of the glyph it is replaced
   with.

.. example-8:

Example
-------

Example with an implied ``conditionset``. Here the conditions are not
contained in a conditionset.

.. code:: xml

    <rules processing="last">
        <rule name="named.rule.1">
            <condition minimum="250" maximum="750" name="weight" />
            <condition minimum="50" maximum="100" name="width" />
            <sub name="dollar" with="dollar.alt"/>
        </rule>
    </rules>

Example with ``conditionsets``. All conditions in a conditionset must be true.

.. code:: xml

    <rules>
        <rule name="named.rule.2">
            <conditionset>
                <condition minimum="250" maximum="750" name="weight" />
                <condition minimum="50" maximum="100" name="width" />
            </conditionset>
            <conditionset>
                <condition ... />
                <condition ... />
            </conditionset>
            <sub name="dollar" with="dollar.alt"/>
        </rule>
    </rules>

.. 6-notes:

6 Notes
=======

Paths and filenames
-------------------

A designspace file needs to store many references to UFO files.

-  designspace files can be part of versioning systems and appear on
   different computers. This means it is not possible to store absolute
   paths.
-  So, all paths are relative to the designspace document path.
-  Using relative paths allows designspace files and UFO files to be
   **near** each other, and that they can be **found** without enforcing
   one particular structure.
-  The **filename** attribute in the ``SourceDescriptor`` and
   ``InstanceDescriptor`` classes stores the preferred relative path.
-  The **path** attribute in these objects stores the absolute path. It
   is calculated from the document path and the relative path in the
   filename attribute when the object is created.
-  Only the **filename** attribute is written to file.
-  Both **filename** and **path** must use forward slashes (``/``) as
   path separators, even on Windows.

Right before we save we need to identify and respond to the following
situations:

In each descriptor, we have to do the right thing for the filename
attribute. Before writing to file, the ``documentObject.updatePaths()``
method prepares the paths as follows:

**Case 1**

::

    descriptor.filename == None
    descriptor.path == None

**Action**

-  write as is, descriptors will not have a filename attr. Useless, but
   no reason to interfere.

**Case 2**

::

    descriptor.filename == "../something"
    descriptor.path == None

**Action**

-  write as is. The filename attr should not be touched.

**Case 3**

::

    descriptor.filename == None
    descriptor.path == "~/absolute/path/there"

**Action**

-  calculate the relative path for filename. We're not overwriting some
   other value for filename, it should be fine.

**Case 4**

::

    descriptor.filename == '../somewhere'
    descriptor.path == "~/absolute/path/there"

**Action**

-  There is a conflict between the given filename, and the path. The
   difference could have happened for any number of reasons. Assuming
   the values were not in conflict when the object was created, either
   could have changed. We can't guess.
-  Assume the path attribute is more up to date. Calculate a new value
   for filename based on the path and the document path.

Recommendation for editors
--------------------------

-  If you want to explicitly set the **filename** attribute, leave the
   path attribute empty.
-  If you want to explicitly set the **path** attribute, leave the
   filename attribute empty. It will be recalculated.
-  Use ``documentObject.updateFilenameFromPath()`` to explicitly set the
   **filename** attributes for all instance and source descriptors.

.. 7-common-lib-key-registry:

7 Common Lib Key Registry
=========================

public.skipExportGlyphs
-----------------------

This lib key works the same as the UFO lib key with the same name. The
difference is that applications using a Designspace as the corner stone of the
font compilation process should use the lib key in that Designspace instead of
any of the UFOs. If the lib key is empty or not present in the Designspace, all
glyphs should be exported, regardless of what the same lib key in any of the
UFOs says.

.. 8-implementation-and-differences:


8 Implementation and differences
================================

The designspace format has gone through considerable development.

 -  the format was originally written for MutatorMath.
 -  the format is now also used in fontTools.varlib.
 -  not all values are be required by all implementations.

8.1 Varlib vs. MutatorMath
--------------------------

There are some differences between the way MutatorMath and fontTools.varlib handle designspaces.

 -  Varlib does not support anisotropic interpolations.
 -  MutatorMath will extrapolate over the boundaries of
    the axes. Varlib can not (at the moment).
 -  Varlib requires much less data to define an instance than
    MutatorMath.
 -  The goals of Varlib and MutatorMath are different, so not all
    attributes are always needed.


8.3 Rules and generating static UFO instances
---------------------------------------------

When making instances as UFOs from a designspace with rules, it can
be useful to evaluate the rules so that the characterset of the ufo
reflects, as much as possible, the state of a variable font when seen
at the same location. This can be done by some swapping and renaming of
glyphs.

While useful for proofing or development work, it should be noted that
swapping and renaming leaves the UFOs with glyphnames that are no longer
descriptive. For instance, after a swap `dollar.bar` could contain a shape
without a bar. Also, when the swapped glyphs are part of other GSUB variations
it can become complex very quickly. So proceed with caution.

 -  Assuming `rulesProcessingLast = True`:
 -  We need to swap the glyphs so that the original shape is still available.
    For instance, if a rule swaps ``a`` for ``a.alt``, a glyph
    that references ``a`` in a component would then show the new ``a.alt``.
 -  But that can lead to unexpected results, the two glyphs may have different
    widths or height. So, glyphs that are not specifically referenced in a rule
    **should not change appearance**. That means that the implementation that swaps
    ``a`` and ``a.alt`` also swap all components that reference these
    glyphs in order to preserve their appearance.
 -  The swap function also needs to take care of swapping the names in
    kerning data and any GPOS code.

9 Version history
=================

9.1 Version 5.0
---------------

The format was extended to describe the entire design space of a reasonably
regular font family in one file, with global data about the family to reduce
repetition in sub-sections. "Reasonably regular" means that the sources and
instances across the previously multiple Designspace files are positioned on a
grid and derive their metadata (like style name) in a way that's compatible with
the STAT model, based on their axis positions. Axis mappings must be the same
across the entire space.

1. Each axis can have labels attached to stops within the axis range, analogous to the
   `OpenType STAT <https://docs.microsoft.com/en-us/typography/opentype/spec/stat>`_
   table. Free-standing labels for locations are also allowed. The data is intended
   to be compiled into a ``STAT`` table.
2. The axes can be discrete, to say that they do not interpolate, like a distinctly
   constructed upright and italic variant of a family.
3. The data can be used to derive style and PostScript names for instances.
4. A new ``variable-fonts`` element can subdivide the Designspace into multiple subsets that
   mix and match the globally available axes. It is possible for these sub-spaces to have
   a different default location from the global default location. It is required if the
   Designspace contains a discrete axis and you want to produce a variable font.

What is currently not supported is e.g.

1. A setup where different sources sit at the same logical location in the design space,
   think "MyFont Regular" and "MyFont SmallCaps Regular". (this situation could be
   encoded by adding a "SmallCaps" discrete axis, if that makes sense).
2. Anisotropic locations for axis labels.

9.2 Older versions
------------------

-  In some implementations that preceed Variable Fonts, the `copyInfo`
   flag in a source indicated the source was to be treated as the default.
   This is no longer compatible with the assumption that the default font
   is located on the default value of each axis.
-  Older implementations did not require axis records to be present in
   the designspace file. The axis extremes for instance were generated
   from the locations used in the sources. This is no longer possible.


.. 10-this-document

10 This document
================

-  Changes are to be expected.


