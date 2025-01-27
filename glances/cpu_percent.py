# -*- coding: utf-8 -*-
#
# This file is part of Glances.
#
# Copyright (C) 2021 Nicolargo <nicolas@nicolargo.com>
#
# Glances is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Glances is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""CPU percent stats shared between CPU and Quicklook plugins."""

from glances.timer import Timer

import psutil


class CpuPercent(object):

    """Get and store the CPU percent."""

    def __init__(self, cached_time=1):
        self.cpu_info = {}
        self.cpu_percent = 0
        self.percpu_percent = []

        # cached_time is the minimum time interval between stats updates
        # since last update is passed (will retrieve old cached info instead)
        self.cached_time = 1
        self.timer_cpu_info = Timer(0)
        self.timer_cpu = Timer(0)
        self.timer_percpu = Timer(0)

    def get_key(self):
        """Return the key of the per CPU list."""
        return 'cpu_number'

    def get(self, percpu=False):
        """Update and/or return the CPU using the psutil library.
        If percpu, return the percpu stats"""
        if percpu:
            return self.__get_percpu()
        else:
            return self.__get_cpu()

    def get_info(self):
        """Get additional informations about the CPU"""
        # Never update more than 1 time per cached_time
        if self.timer_cpu_info.finished():
            # Get the CPU name from the /proc/cpuinfo file
            # @TODO: Multisystem...
            try:
                self.cpu_info['cpu_name'] = open('/proc/cpuinfo', 'r').readlines()[4].split(':')[1][1:-2]
            except:
                self.cpu_info['cpu_name'] = 'CPU'
            # Get the CPU freq current/max
            self.cpu_info['cpu_hz_current'] = psutil.cpu_freq().current
            self.cpu_info['cpu_hz'] = psutil.cpu_freq().max
            # Reset timer for cache
            self.timer_cpu_info = Timer(self.cached_time)
        return self.cpu_info

    def __get_cpu(self):
        """Update and/or return the CPU using the psutil library."""
        # Never update more than 1 time per cached_time
        if self.timer_cpu.finished():
            self.cpu_percent = psutil.cpu_percent(interval=0.0)
            # Reset timer for cache
            self.timer_cpu = Timer(self.cached_time)
        return self.cpu_percent

    def __get_percpu(self):
        """Update and/or return the per CPU list using the psutil library."""
        # Never update more than 1 time per cached_time
        if self.timer_percpu.finished():
            self.percpu_percent = []
            for cpu_number, cputimes in enumerate(psutil.cpu_times_percent(interval=0.0, percpu=True)):
                cpu = {'key': self.get_key(),
                       'cpu_number': cpu_number,
                       'total': round(100 - cputimes.idle, 1),
                       'user': cputimes.user,
                       'system': cputimes.system,
                       'idle': cputimes.idle}
                # The following stats are for API purposes only
                if hasattr(cputimes, 'nice'):
                    cpu['nice'] = cputimes.nice
                if hasattr(cputimes, 'iowait'):
                    cpu['iowait'] = cputimes.iowait
                if hasattr(cputimes, 'irq'):
                    cpu['irq'] = cputimes.irq
                if hasattr(cputimes, 'softirq'):
                    cpu['softirq'] = cputimes.softirq
                if hasattr(cputimes, 'steal'):
                    cpu['steal'] = cputimes.steal
                if hasattr(cputimes, 'guest'):
                    cpu['guest'] = cputimes.guest
                if hasattr(cputimes, 'guest_nice'):
                    cpu['guest_nice'] = cputimes.guest_nice
                # Append new CPU to the list
                self.percpu_percent.append(cpu)
                # Reset timer for cache
                self.timer_percpu = Timer(self.cached_time)
        return self.percpu_percent


# CpuPercent instance shared between plugins
cpu_percent = CpuPercent()
