.. _stim-desc:

Stimulation
===========


Experimental protocols in Stytra are defined as sequences of timed stimuli presented to the animal through a projector or external actuators. A sequence of stimuli, defined as a Python list of :class:`~stytra.stimulation.stimuli.generic_stimuli.Stimulus` objects, is defined in a :class:`~stytra.stimulation.Protocol` object. This structure enables  straightforward design of new experimental protocols, requiring very little knowledge of the general structure of the library and only basic Python syntax. A dedicated class coordinates the timed execution of the protocol relying on a ``QTimer`` from the PyQt5 library, ensuring a temporal resolution in the order of 15-20 ms (around the response time of a normal monitor, see inset). Drawing very complex stimuli consisting of many polygons or requiring online computation of large arrays can decrease the stimulus display performance.

.. figure:: ../../figures/framerates.svg
    :align: right
    :figwidth: 200px

    Interval duration when flickering a white stimulus on every update of the display loop. The screen was recorded at 2 kHz.

The stimulus display framerate can be monitored online from the user interface when the protocol is running (see the lower left corner of the window in :ref:`interface <gui-desc>`.  Milli- or microsecond precision, which might be required for optogenetic experiments, for example, is currently not supported. Each :class:`~stytra.stimulation.stimuli.generic_stimuli.Stimulus` has methods which are called at starting time or at every subsequent time step while it is set. In this way one can generate dynamically changing stimuli, or trigger external devices. New :class:`~stytra.stimulation.stimuli.generic_stimuli.Stimulus` types can be easily added to the library just by subclassing :class:`~stytra.stimulation.stimuli.generic_stimuli.Stimulus` and re-defining the :meth:`~stytra.stimulation.stimuli.generic_stimuli.Stimulus.start` and :meth:`~stytra.stimulation.stimuli.generic_stimuli.Stimulus.update` methods.



A large number of stimuli is included in the package. In particular, a library of visual stimuli has been implemented as :class:`~stytra.stimulation.stimuli.visual.VisualStimulus` objects using the `QPainter <https://doc.qt.io/qt-5/qpainter.html>`_ object, a part of the Qt GUI library, enabling efficient drawing with OpenGL. Relying on a set of high-level drawing primitives makes the code very readable and maintainable. Stytra already includes common stimuli used in  visual neuroscience, such as moving bars, dots, whole-field translation or rotations of patterns on a screen, and additional features such as movie playback and the presentation of images from a file (which can be generated by packages such as Imagen :cite:`imagen`). The classes describing visual stimuli can be combined, and new stimuli where these patterns are moved or masked can be quickly defined by combining the appropriate :class:`~stytra.stimulation.stimuli.generic_stimuli.Stimulus` types. Finally, new stimuli can be easily created by redefining the :meth:`~stytra.stimulation.stimuli.visual.VisualStimulus.paint` method in a new :class:`~stytra.stimulation.stimuli.visual.VisualStimulus` object. Multiple stimuli can be presented simultaneously using :class:`~stytra.stimulation.stimuli.visual.StimulusCombiner`. Presenting different stimuli depending on animal behavior or external signals can be achieved using the :class:`~stytra.stimulation.stimuli.conditional.ConditionalWrapper` container, or with similarly designed custom objects. Visual stimuli are usually displayed on a secondary screen, therefore Stytra provides a convenient interface for positioning and calibrating the stimulation window (visible in :ref:`interface <gui-desc>` on the right-hand side). Although in our experiments we are using a single stimulation monitor, displaying stimuli on multiple screens can be achieved with virtual desktop technology or screen-splitting hardware boards. Importantly, all stimulus parameters are specified in physical units and are therefore independent of the display hardware. Finally, the timed execution of code inside :class:`~stytra.stimulation.stimuli.generic_stimuli.Stimulus` objects can be used to control hardware via I/O boards or serial communication with micro-controllers such as `Arduino <https://www.arduino.cc/>`_ or `MicroPython PyBoard <https://micropython.org/>`_. For example, in this way one may deliver odors or temperature stimuli or optogenetic stimulation.  Examples for a few different kinds of stimuli are provided below.
For a description of how to synchronize the stimulus with an external data-acquisition device such a s a microscope, see the :ref:`triggering <trig-desc>` section of the developer documentation.



Stimuli examples
----------------

Full-field luminance
....................

.. raw:: html

        <video loop src="../_static/stim_movie_full_field.mp4"
        width="200px" autoplay controls></video>

.. literalinclude:: ../../../stytra/tests/record_stimuli.py
   :language: python
   :lines: 45-50

Gratings
........

.. raw:: html

        <video loop src="../_static/stim_movie_grating.mp4"
        width="200px" autoplay controls></video>

.. literalinclude:: ../../../stytra/tests/record_stimuli.py
   :language: python
   :lines: 70-74

OKR inducing rotating windmill stimulus
.......................................

.. raw:: html

        <video loop src="../_static/stim_movie_okr.mp4"
        width="200px" autoplay controls></video>

.. literalinclude:: ../../../stytra/tests/record_stimuli.py
   :language: python
   :lines: 60-64

Seamlessly-tiled image
......................

.. raw:: html

        <video loop src="../_static/stim_movie_seamless_image.mp4"
        width="200px" autoplay controls></video>

.. literalinclude:: ../../../stytra/tests/record_stimuli.py
   :language: python
   :lines: 80-87


Radial sine (freely-swimming fish centering stimulus)
.....................................................

.. raw:: html

        <video loop src="../_static/stim_movie_radial_sine.mp4"
        width="200px" autoplay controls></video>

.. literalinclude:: ../../../stytra/tests/record_stimuli.py
   :language: python
   :lines: 34-36

Set voltage of an NI board
..........................
This example set a voltage on an external NI board.
Note that this code would require an installed NI board and the nidaqmx library installed.


.. code-block:: python

   def get_stim_sequence():
       return([SetVoltageStimulus(duration=10, dev="Dev1", chan="ao0", voltage=0),
               SetVoltageStimulus(duration=1, dev="Dev1", chan="ao0", voltage=3.5)])