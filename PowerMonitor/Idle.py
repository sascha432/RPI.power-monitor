#
# Author: sascha_lammers@gmx.de
#

from . import BaseApp
import sys
import subprocess
import shlex
import re

class Idle(BaseApp.BaseApp):

    def __init__(self):
        global AppConfig
        AppConfig = self._app_config
        self._state = None
        self._cmd = None

    @property
    def has_idle_support(self):
        return self._gui and AppConfig.idle_check_cmd.strip()!=''

    @property
    def monitor_on():
        if self._cmd==None:
            return None
        return self._state

    @property
    def monitor_off():
        if self._cmd==None:
            return None
        return not self._state

    def reload(self):
        self._cmd = shlex.split(AppConfig.idle_check_cmd.format(DISPLAY=shlex.quote(AppConfig.gui.display)))

    def start(self):
        self.debug(__name__, 'start')
        flag = self.has_idle_support
        if flag and 'win' in sys.platform:
            flag = False
            self.error(__name__, 'idle_check_cmd not supported on windows')
        if not flag:
            self._state = None
            self._cmd = None
            return
        self.reload()
        self.thread_daemonize(__name__, self.check_idle_thread)

    def _get_state(self):
        if self._cmd==None:
            return None
        state = None
        msg = ''
        try:
            p = subprocess.run(self._cmd, timeout=30, capture_output=True)
            out = p.stdout.decode()
            if re.search(AppConfig.idle_check_monitor_on, out, re.I|re.M):
                state = True
            elif re.search(AppConfig.idle_check_monitor_off, out, re.I|re.M):
                state = False
            else:
                self.error(__name__, 'could not find monitor on/off pattern: returncode=%u cmd=%s' % (shlex.join(self._cmd), p.returncode))
        except Exception as e:
            self.error(__name__, 'failed to execute command: returncode=%d cmd=%s error=%s' % (p.returncode, shlex.join(self._cmd), e))

        # self.debug(__name__, 'monitor enabled: %s', state)
        return state

    def check_idle_thread(self):
        self.thread_register(__name__)

        # wait for the animation to start
        while not self.terminate.is_set() and not self._animation.active:
            self.terminate.wait(1)

        self._state = self._animation.running

        while not self.terminate.is_set():
            sleep = AppConfig.idle_check_interval
            if not self._animation.active:
                sleep = 5
            elif self.ani:
                state = self._get_state()
                if state==None:
                    sleep = max(120, sleep) # wait at least 2 minutes after an error
                elif state!=self._state:
                    self._state = state
                    self.debug(__name__, 'set interval for monitor enabled: %s', state)
                    self.set_screen_update_rate(state)
            self.terminate.wait(sleep)

        self.thread_unregister(__name__)
