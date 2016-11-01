#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2016 Stephane Caron <stephane.caron@normalesup.org>
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

from numpy import array, zeros

from generic import Task


class DOFTask(Task):

    """Track a reference DOF value"""

    task_type = 'dof'

    def __init__(self, robot, dof_id, dof_ref, **kwargs):
        """
        Create task.

        INPUT:

        - ``robot`` -- a Robot object
        """
        J = zeros((1, robot.nb_dofs))
        J[0, dof_id] = 1.

        def pos_residual():
            return array([dof_ref - robot.q[dof_id]])

        def jacobian():
            return J

        self.dof_id = dof_id
        super(DOFTask, self).__init__(
            jacobian, pos_residual=pos_residual, **kwargs)

    @property
    def name(self):
        return 'dof-%d' % self.dof_id