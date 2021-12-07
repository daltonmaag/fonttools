**********************
Document XML structure
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
            <axis... />
        </axes>
        <labels>
            <!-- define STAT format 4 labels here -->
            <!-- New in version 5.0 -->
            <label... />
        </labels>
        <sources>
            <!-- define masters here -->
            <source... />
        </sources>
        <variable-fonts>
            <!-- define variable fonts here -->
            <!-- New in version 5.0 -->
            <variable-font... />
        </variable-fonts>
        <instances>
            <!-- define instances here -->
            <instance... />
        </instances>
        <rules>
            <!-- define rules here -->
            <rule... />
        </rules>
        <lib>
            <dict>
                <!-- store custom data here -->
            </dict>
        </lib>
    </designspace>


axis element
============

-  Define a single axis
-  Child element of ``axes``
-  The axis can be either continuous (as in version 4.0) or discrete (new in version 5.0).
   Discrete axes have a list of values instead of a range minimum and maximum.


Attributes
----------

-  ``name``: required, string. Name of the axis that is used in the
   location elements.
-  ``tag``: required, string, 4 letters. Some axis tags are registered
   in the OpenType Specification.
-  ``default``: required, number. The default value for this axis, in user space coordinates.
-  ``hidden``: optional, 0 or 1. Records whether this axis needs to be
   hidden in interfaces.

For a continuous axis:
   -  ``minimum``: required, number. The minimum value for this axis, in user space coordinates.
   -  ``maximum``: required, number. The maximum value for this axis, in user space coordinates.

For a discrete axis:
   -  ``values``: required, space-separated numbers. The exhaustive list of possible values along this axis.


Example
-------

.. code:: xml

    <axis name="weight" tag="wght" minimum="1" maximum="1000" default="400">

    <!--
      Discrete axes provide a list of discrete values.
      No interpolation is allowed between these.
    -->
    <axis name="Italic" tag="ital" default="0" values="0 1">


labelname element
=================

-  Defines a human readable name for UI use.
-  Optional for non-registered axis names.
-  Can be localised with ``xml:lang``
-  Child element of ``axis``


Attributes
----------

-  ``xml:lang``: required, string. `XML language
   definition <https://www.w3.org/International/questions/qa-when-xmllang.en>`__

Value
-----

-  The natural language name of this axis.


Example
-------

.. code:: xml

    <labelname xml:lang="fa-IR">قطر</labelname>
    <labelname xml:lang="en">Wéíght</labelname>


map element
===========

-  Defines a single node in a series of input value (user space coordinate)
   to output value (designspace coordinate) pairs.
-  Together these values transform the designspace.
-  Child of ``axis`` element.


Example
-------

.. code:: xml

    <map input="1.0" output="10.0" />
    <map input="400.0" output="66.0" />
    <map input="1000.0" output="990.0" />


labels and label elements
=========================

-  Define STAT format 1, 2, 3 labels for the locations on this axis.
-  The axis can have several ``label`` elements,
TODO here


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


location element
================

-  Defines a coordinate in the design space.
-  Dictionary of axisname: axisvalue
-  Used in ``source``, ``instance`` and ``glyph`` elements.


dimension element
=================

-  Child element of ``location``


Attributes
----------

-  ``name``: required, string. Name of the axis.
-  ``xvalue``: required, number. The value on this axis.
-  ``yvalue``: optional, number. Separate value for anisotropic
   interpolations.


Example
-------

.. code:: xml

    <location>
        <dimension name="width" xvalue="0.000000" />
        <dimension name="weight" xvalue="0.000000" yvalue="0.003" />
    </location>


source element
==============

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


lib element
===========

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


info element
============

-  ``<info copy="1" />``
-  Child element of ``source``
-  Defines if the instances can inherit the non-interpolating font info
   from this source.
-  MutatorMath


features element
================

-  ``<features copy="1" />``
-  Defines if the instances can inherit opentype feature text from this
   source.
-  Child element of ``source``
-  MutatorMath only


glyph element
=============

-  Can appear in ``source`` as well as in ``instance`` elements.
-  In a ``source`` element this states if a glyph is to be excluded from
   the calculation.
-  MutatorMath only


Attributes
----------

-  ``mute``: optional attribute, number 1 or 0. Indicate if this glyph
   should be ignored as a master.
-  ``<glyph mute="1" name="A"/>``
-  MutatorMath only


kerning element
===============

-  ``<kerning mute="1" />``
-  Can appear in ``source`` as well as in ``instance`` elements.


Attributes
----------

-  ``mute``: required attribute, number 1 or 0. Indicate if the kerning
   data from this source is to be excluded from the calculation.
-  If the kerning element is not present, assume ``mute=0``, yes,
   include the kerning of this source in the calculation.
-  MutatorMath only


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


instance element
================

-  Defines a single font that can be calculated with the designspace.
-  Child element of ``instances``
-  For use in Varlib the instance element really only needs the names
   and the location. The ``glyphs`` element is not required.
-  MutatorMath uses the ``glyphs`` element to describe how certain
   glyphs need different masters, mainly to describe the effects of
   conditional rules in Superpolator.
-  Location in designspace coordinates.


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


glyphs element
==============

-  Container for ``glyph`` elements.
-  Optional
-  MutatorMath only.


glyph element
=============

-  Child element of ``glyphs``
-  May contain a ``location`` element.


Attributes
----------

-  ``name``: string. The name of the glyph.
-  ``unicode``: string. Unicode values for this glyph, in hexadecimal.
   Multiple values should be separated with a space.
-  ``mute``: optional attribute, number 1 or 0. Indicate if this glyph
   should be supressed in the output.


note element
============

-  String. The value corresponds to glyph.note in UFO.


masters element
===============

-  Container for ``master`` elements
-  These ``master`` elements define an alternative set of glyph masters
   for this glyph.


master element
==============

-  Defines a single alternative master for this glyph.

Localised names for instances
=============================

Localised names for instances can be included with these simple elements
with an ``xml:lang`` attribute:
`XML language definition <https://www.w3.org/International/questions/qa-when-xmllang.en>`__

-  stylename
-  familyname
-  stylemapstylename
-  stylemapfamilyname


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


Attributes
----------

-  ``glyphname``: the name of the alternate master glyph.
-  ``source``: the identifier name of the source this master glyph needs
   to be loaded from


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


rules element
=============

-  Container for ``rule`` elements
-  The rules are evaluated in this order.

Rules describe designspace areas in which one glyph should be replaced by another.
A rule has a name and a number of conditionsets. The rule also contains a list of
glyphname pairs: the glyphs that need to be substituted. For a rule to be triggered
**only one** of the conditionsets needs to be true, ``OR``. Within a conditionset
**all** conditions need to be true, ``AND``.


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



rule element
============

-  Defines a named rule.
-  Each ``rule`` element contains one or more ``conditionset`` elements.
-  **Only one** ``conditionset`` needs to be true to trigger the rule.
-  **All** conditions in a ``conditionset`` must be true to make the ``conditionset`` true.
-  For backwards compatibility a ``rule`` can contain ``condition`` elements outside of a conditionset. These are then understood to be part of a single, implied, ``conditionset``. Note: these conditions should be written wrapped in a conditionset.
-  A rule element needs to contain one or more ``sub`` elements in order to be compiled to a variable font.
-  Rules without sub elements should be ignored when compiling a font.
-  For authoring tools it might be necessary to save designspace files without ``sub`` elements just because the work is incomplete.


Attributes
----------

-  ``name``: optional, string. A unique name that can be used to
   identify this rule if it needs to be referenced elsewhere. The name
   is not important for compiling variable fonts.

conditionset element
=================

-  Child element of ``rule``
-  Contains one or more ``condition`` elements.


condition element
=================

-  Child element of ``conditionset``
-  Between the ``minimum`` and ``maximum`` this condition is ``True``.
-  ``minimum`` and ``maximum`` are in designspace coordinates.
-  If ``minimum`` is not available, assume it is ``axis.minimum``, mapped to designspace coordinates.
-  If ``maximum`` is not available, assume it is ``axis.maximum``, mapped to designspace coordinates.
-  The condition must contain at least a minimum or maximum or both.


Attributes
----------

-  ``name``: string, required. Must match one of the defined ``axis``
   name attributes.
-  ``minimum``: number, required*. The low value, in designspace coordinates.
-  ``maximum``: number, required*. The high value, in designspace coordinates.


sub element
===========

-  Child element of ``rule``.
-  Defines which glyph to replace when the rule evaluates to **True**.
-  The ``sub`` element contains a pair of glyphnames. The ``name`` attribute is the glyph that should be visible when the rule evaluates to **False**. The ``with`` attribute is the glyph that should be visible when the rule evaluates to **True**.

Axis values in Conditions are in designspace coordinates.


Attributes
----------

-  ``name``: string, required. The name of the glyph this rule looks
   for.
-  ``with``: string, required. The name of the glyph it is replaced
   with.


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

