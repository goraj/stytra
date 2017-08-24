from stytra.stimulation.stimuli import Pause, Flash, \
    ShockStimulus, MovingGratingStimulus,\
    FullFieldPainterStimulus, ClosedLoop1D_variable_motion
from stytra.stimulation import Protocol
import pandas as pd
import numpy as np
from stytra.stimulation.backgrounds import gratings

import zmq

from copy import deepcopy

# Spontaneus activity
class SpontActivityProtocol(Protocol):
    def __init__(self, *args,  duration_sec=60, **kwargs):
        """
        :param duration:
        :param prepare_pause:
        :param zmq_trigger:
        """

        stimuli = []
        stimuli.append(Pause(duration=duration_sec))  # change here for duration (in s)

        self.stimuli = stimuli
        self.current_stimulus = stimuli[0]
        super().__init__(*args, stimuli=stimuli, name='spontaneous', **kwargs)


class FlashProtocol(Protocol):
    def __init__(self, repetitions=10, period_sec=30, duration_sec=1, pre_stim_pause=20):
        """
        :param repetitions:
        :param prepare_pause:
        :param zmq_trigger:
        """
        super().__init__()

        stimuli = []

        # stimuli.append(Pause(duration=period_sec-duration_sec))  # pre-flash interval
        for i in range(repetitions):
            stimuli.append(Pause(duration=pre_stim_pause))
            stimuli.append(Flash(duration=1, color=(255, 255, 255)))  # flash duration
            stimuli.append(Pause(duration=period_sec-duration_sec-pre_stim_pause))  # post flash interval

        self.stimuli = stimuli
        self.current_stimulus = stimuli[0]
        self.name = 'flash'


class ShockProtocol(Protocol):
    def __init__(self, repetitions=10, period_sec=30, pre_stim_pause=20.95,
                 prepare_pause=2, pyb=None, zmq_trigger=None):
        """

        :param repetitions:
        :param prepare_pause:
        :param pyb:
        :param zmq_trigger:
        """
        super().__init__()
        if not zmq_trigger:
            print('missing trigger')

        stimuli = []
        stimuli.append(Pause(duration=1))
        stimuli.append(PrepareAquisition(zmq_trigger=zmq_trigger))
        stimuli.append(Pause(duration=prepare_pause))
        stimuli.append(StartAquisition(zmq_trigger=zmq_trigger))  # start aquisition
          # pre-shock interval
        for i in range(repetitions):  # change here for number of trials
            stimuli.append(Pause(duration=pre_stim_pause))
            stimuli.append(ShockStimulus(pyboard=pyb, burst_freq=1, pulse_amp=3.5,
                                         pulse_n=1, pulse_dur_ms=5))
            stimuli.append(Pause(duration=period_sec-pre_stim_pause))  # post flash interval

        self.stimuli = stimuli
        self.current_stimulus = stimuli[0]
        self.name = 'shock'


class FlashShockProtocol(Protocol):
    def __init__(self, repetitions=10, period_sec=30, duration_sec=1, pre_stim_pause=20, shock_duration=0.05,
                 prepare_pause=2, pyb=None, zmq_trigger=None):
        """

        :param repetitions:
        :param prepare_pause:
        :param pyb:
        :param zmq_trigger:
        """
        super().__init__()
        if not zmq_trigger:
            print('missing trigger')

        stimuli = []
        stimuli.append(Pause(duration=1))
        stimuli.append(PrepareAquisition(zmq_trigger=zmq_trigger))
        stimuli.append(Pause(duration=prepare_pause))
        stimuli.append(StartAquisition(zmq_trigger=zmq_trigger))  # start aquisition

        for i in range(repetitions):  # change here for number of pairing trials
            stimuli.append(Pause(duration=pre_stim_pause))
            stimuli.append(Flash(duration=duration_sec-shock_duration, color=(255, 255, 255)))  # flash duration
            stimuli.append(ShockStimulus(pyboard=pyb, burst_freq=1, pulse_amp=3.5,
                                         pulse_n=1, pulse_dur_ms=5))
            stimuli.append(Flash(duration=shock_duration, color=(255, 255, 255)))  # flash duration
            stimuli.append(Pause(duration=period_sec - duration_sec - pre_stim_pause ))

        self.stimuli = stimuli
        self.current_stimulus = stimuli[0]
        self.name = 'flashshock'


def make_value_blocks(duration_value_tuples):
    """ For all the stimuli that accept a motion parameter,
        we usually want one thing to stay the same in a block

    :param duration_value_tuples:
    :return:
    """
    t = []
    vals = []

    for dur, val in duration_value_tuples:
        if len(t) == 0:
            last_t = 0
        else:
            last_t = t[-1]

        t.extend([last_t, last_t+dur])
        vals.extend([val, val])
    return t, vals


class ReafferenceProtocol(Protocol):
    def __init__(self, n_backwards=7, pause_duration=7, backwards_duration=0.5,
                 forward_duration=2, backward_vel=20, forward_vel=10,
                 n_forward=14,
                 gain_probability=0.5, gain=1, grating_args=None):
        gains = []
        vels = []
        ts = []
        for i in range(n_backwards):
            if len(ts) == 0:
                last_t = 0
            else:
                last_t = ts[-1]
            ts.extend([last_t, last_t+pause_duration,
                       last_t + pause_duration, last_t+backwards_duration])
            vels.extend([0,0,backward_vel, backward_vel])
        gains.extend([0]*len(vels))
        for i in range(n_forward):
            gain_exists = (np.random.random_sample() < gain_probability)*1
            ts.extend([last_t, last_t+pause_duration,
                       last_t + pause_duration, last_t+forward_duration])
            vels.extend([0, 0, forward_vel, forward_vel])
            gains.extend([0, 0, gain_exists*gain])
        super().__init__([ClosedLoop1D_variable_motion(motion=pd.DataFrame(
            dict(t=ts, vel=vels, gain=gains,
                 background=gratings(**grating_args))))])
        self.name = 'Reafference'


class MultistimulusExp06Protocol(Protocol):
    def __init__(self, repetitions=20,
                        flash_durations=(0.05, 0.1, 0.2, 0.5, 1, 3),
                        velocities=(3, 10, 30, -10),
                        pre_stim_pause=4,
                        one_stimulus_duration=7,
                        grating_motion_duration=4,
                        grating_args=None,
                        shock_args=None,
                        shock_on=False,
                        lr_vel=10,
                        spontaneous_duration_pre=120,
                        spontaneous_duration_post=120,
                 calibrator=None,
                *args, **kwargs):

        if grating_args is None:
            grating_args = dict()
        if shock_args is None:
            shock_args = dict()

        stimuli = []
        stimuli.append(Pause(duration=spontaneous_duration_pre))
        for i in range(repetitions):  # change here for number of pairing trials
            stimuli.append(Pause(duration=pre_stim_pause))
            for flash_duration in flash_durations:
                stimuli.append(FullFieldPainterStimulus(duration=flash_duration, color=(255, 0, 0)))  # flash duration
                stimuli.append(Pause(duration=one_stimulus_duration-flash_duration))

            t = [0, one_stimulus_duration]
            y = [0., 0.]
            x = [0., 0.]

            for vel in velocities:
                t.append(t[-1] + grating_motion_duration)
                y.append(y[-1] + vel*grating_motion_duration)
                t.append(t[-1] + one_stimulus_duration)
                y.append(y[-1])
                x.extend([0., 0.])

            last_time = t[-1]
            motion = pd.DataFrame(dict(t=t,
                                 x=x,
                                 y=y))
            stimuli.append(MovingGratingStimulus(motion=motion,
                                               duration=last_time, **grating_args, calibrator=calibrator))


            if lr_vel>0:
                t = [0, one_stimulus_duration]
                y = [0., 0.]
                x = [0., 0.]
                for xvel in [-lr_vel, lr_vel]:
                    t.append(t[-1] + grating_motion_duration)
                    x.append(x[-1] + xvel * grating_motion_duration)
                    t.append(t[-1] + one_stimulus_duration)
                    x.append(x[-1])
                    y.extend([0., 0.])
                last_time = t[-1]
                motion = pd.DataFrame(dict(t=t,
                                           x=x,
                                           y=y))
                grating_args_v = deepcopy(grating_args)
                grating_args_v['grating_orientation'] = 'vertical'
                grating_args_v['grating_period'] *= 2 # because of the stretch of the image
                stimuli.append(MovingGratingStimulus(motion=motion,
                                              **grating_args_v,
                                              duration=last_time, calibrator=calibrator))

            if shock_on:
                stimuli.append(Pause(duration=pre_stim_pause))
                stimuli.append(ShockStimulus(**shock_args))
                stimuli.append(Pause(duration=one_stimulus_duration))

        stimuli.append(Pause(duration=spontaneous_duration_post))

        super().__init__(*args, stimuli=stimuli, **kwargs)
        self.name = 'exp006multistim'