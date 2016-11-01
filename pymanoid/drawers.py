#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 Stephane Caron <stephane.caron@normalesup.org>
#
# This file is part of pymanoid <https://github.com/stephane-caron/pymanoid>.
#
# pymanoid is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# pymanoid is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# pymanoid. If not, see <http://www.gnu.org/licenses/>.

import time

from numpy import hstack, zeros

from draw import draw_force, draw_line, draw_polygon
from misc import norm
from sim import Process


class COMForceDrawer(Process):

    KO_COLOR = [.8, .4, .4]
    OK_COLOR = [1., 1., 1.]

    def __init__(self, com, contact_set, force_scale=0.0025):
        self.contact_set = contact_set
        self.force_scale = force_scale
        self.handles = []
        self.last_bkgnd_switch = None

    def on_tick(self, sim):
        """Find supporting contact forces at each COM acceleration update."""
        com = self.com
        comdd = com.pdd  # needs to be stored by the user
        gravity = sim.gravity
        wrench = hstack([com.mass * (comdd - gravity), zeros(3)])
        support = self.contact_set.find_supporting_forces(
            wrench, com.p, com.mass, 10.)
        if not support:
            self.handles = []
            sim.viewer.SetBkgndColor(self.KO_COLOR)
            self.last_bkgnd_switch = time.time()
        else:
            self.handles = [
                draw_force(c, fc, self.force_scale) for (c, fc) in support]
        if self.last_bkgnd_switch is not None \
                and time.time() - self.last_bkgnd_switch > 0.2:
            # let's keep epilepsy at bay
            sim.viewer.SetBkgndColor(self.OK_COLOR)
            self.last_bkgnd_switch = None


class SEPDrawer(Process):

    """Draw the static-equilibrium polygon of a contact set."""

    def __init__(self, contact_set, z=0.):
        contact_dict = contact_set.contact_dict
        self.contact_dict = contact_dict
        self.contact_poses = {}
        self.contact_set = contact_set
        self.handle = None
        self.z = z
        self.update_contact_poses()
        self.update_polygon()

    def on_tick(self, sim):
        for (k, c) in self.contact_dict.iteritems():
            if norm(c.pose - self.contact_poses[k]) > 1e-10:
                self.update_contact_poses()
                self.update_polygon()
                break

    def update_contact_poses(self):
        for (k, c) in self.contact_dict.iteritems():
            self.contact_poses[k] = c.pose

    def update_polygon(self):
        self.handle = None
        try:
            vertices = self.contact_set.compute_static_equilibrium_polygon()
            self.handle = draw_polygon(
                [(x[0], x[1], self.z) for x in vertices],
                normal=[0, 0, 1], color=(0.5, 0., 0.5, 0.5))
        except:
            pass


class StaticForceDrawer(Process):

    KO_COLOR = [.8, .4, .4]
    OK_COLOR = [1., 1., 1.]

    def __init__(self, com, contact_set, force_scale=0.0025):
        self.com = com
        self.contact_set = contact_set
        self.force_scale = force_scale
        self.handles = []
        self.last_bkgnd_switch = None

    def on_tick(self, sim):
        """Find supporting contact forces at each COM acceleration update."""
        support = self.contact_set.find_static_supporting_forces(
            self.com.p, self.com.mass)
        if not support:
            self.handles = []
            sim.viewer.SetBkgndColor(self.KO_COLOR)
            self.last_bkgnd_switch = time.time()
        else:
            self.handles = [
                draw_force(c, fc, self.force_scale) for (c, fc) in support]
        if self.last_bkgnd_switch is not None \
                and time.time() - self.last_bkgnd_switch > 0.2:
            # let's keep epilepsy at bay
            sim.viewer.SetBkgndColor(self.OK_COLOR)
            self.last_bkgnd_switch = None


class TrajectoryDrawer(Process):

    def __init__(self, body, combined='b-', color=None, linewidth=3,
                 linestyle=None):
        color = color if color is not None else combined[0]
        linestyle = linestyle if linestyle is not None else combined[1]
        assert linestyle in ['-', '.']
        self.body = body
        self.color = color
        self.handles = []
        self.last_pos = body.p
        self.linestyle = linestyle
        self.linewidth = linewidth

    def on_tick(self, sim):
        if self.linestyle == '-':
            self.handles.append(draw_line(
                self.last_pos, self.body.p, color=self.color,
                linewidth=self.linewidth))
        self.last_pos = self.body.p

    def dash_graph_handles(self):
        for i in xrange(len(self.handles)):
            if i % 2 == 0:
                self.handles[i] = None