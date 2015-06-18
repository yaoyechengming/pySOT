#!/usr/bin/env python
"""
.. module:: test_problems
  :synopsis: Test problems for multi-modal and
             box-constrained global optimization
.. moduleauthor:: David Eriksson <dme65@cornell.edu>
                 David Bindel <bindel@cornell.edu>

:Module: test_problems
:Author: David Eriksson <dme65@cornell.edu>
    David Bindel <bindel@cornell.edu>
"""

import random
from time import time
import numpy as np


def validate(obj):
    """
    Routine for checking that an implementation of an objective function
    follows the standard. This method checks everything, but can't make
    sure that the objective function and constraint methods return values
    of the correct type since this would involve actually evaluating the
    objective function which isn't feasible when the evaluations are
    expensive. If some test fails, an exception is raised through assert.

    :param obj: Objective function
    """
    assert hasattr(obj, "dim"), \
        "Problem dimension required"
    assert hasattr(obj, "xlow"), \
        "Numpy array of lower bounds required"
    assert isinstance(obj.xlow, np.ndarray), \
        "Numpy array of lower bounds required"
    assert hasattr(obj, "xup"), \
        "Numpy array of upper bounds required"
    assert isinstance(obj.xup, np.ndarray), \
        "Numpy array of upper bounds required"
    assert hasattr(obj, "integer"), \
        "Integer variables must be specified"
    if len(obj.integer) > 0:
        assert isinstance(obj.integer, np.ndarray), \
            "Integer variables must be specified"
    else:
        assert isinstance(obj.integer, np.ndarray) or \
            isinstance(obj.integer, list), \
            "Integer variables must be specified"
    assert hasattr(obj, "continuous"), \
        "Continuous variables must be specified"
    if len(obj.continuous) > 0:
        assert isinstance(obj.continuous, np.ndarray), \
            "Continuous variables must be specified"
    else:
        assert isinstance(obj.continuous, np.ndarray) or \
            isinstance(obj.continuous, list), \
            "Continuous variables must be specified"
    assert hasattr(obj, "constraints"), \
        "Existence of constraints must be specified"
    assert isinstance(obj.constraints, bool), \
        "Constraint existence must be bool"
    assert hasattr(obj, "objfunction"), \
        "Method 'objfunction' is not implemented"
    if obj.constraints:
        assert hasattr(obj, "eval_ineq_constraints"), \
            "Method 'eval_ineq_constraints' is not implemented"

    # Check for logical errors
    assert isinstance(obj.dim, int) and obj.dim > 0, \
        "Problem dimension must be a positive integer."
    assert (len(obj.xlow) == obj.dim and
            len(obj.xup) == obj.dim), \
        "Incorrect size for xlow and xup"
    assert all(obj.xlow[i] < obj.xup[i] for i in range(obj.dim)), \
        "Lower bounds must be below upper bounds."
    if len(obj.integer) > 0:
        assert np.amax(obj.integer) < obj.dim and np.amin(obj.integer) >= 0, \
            "Integer variable index can't exceed " \
            "number of dimensions or be negative"
    if len(obj.continuous) > 0:
        assert np.amax(obj.continuous) < obj.dim and np.amin(obj.continuous) >= 0, \
            "Continuous variable index can't exceed " \
            "number of dimensions or be negative"
    assert len(np.intersect1d(obj.continuous, obj.integer)) == 0, \
        "A variable can't be both an integer and continuous"
    assert len(obj.continuous)+len(obj.integer) == obj.dim, \
        "All variables must be either integer or continuous"

# ========================= 3-dimensional =======================


class Hartman3:
    """
    Hartman 3 function

    Details: http://www.sfu.ca/~ssurjano/hart3.html

    Global optimum: :math:`f(0.114614,0.555649,0.852547)=-3.86278`

    :ivar dim: Number of dimensions
    :ivar xlow: Lower bound constraints
    :ivar xup: Upper bound constraints
    :ivar info: Problem information:
    :ivar min: Global optimum
    :ivar integer: Integer variables
    :ivar continuous: Continuous variables:
    :ivar constraints: Whether there are non-bound constraints
    """
    def __init__(self, dim=3):
        self.xlow = np.zeros(3)
        self.xup = np.ones(3)
        self.dim = 3
        self.info = "3-dimensional Hartman function \nGlobal optimum: " +\
                    "f(0.114614,0.555649,0.852547) = -3.86278"
        self.min = -3.86278
        self.integer = []
        self.continuous = np.arange(0, 3)
        self.constraints = False
        validate(self)

    def objfunction(self, x):
        """
        Evaluate the Hartman 3 function  at x

        :param x: Data point
        :return: Value at x
        """
        if len(x) != self.dim:
            raise ValueError('Dimension mismatch')
        alpha = np.array([1, 1.2, 3, 3.2])
        A = np.matrix([[3.0, 10.0, 30.0], [0.1, 10.0, 35.0],
                       [3.0, 10.0, 30.0], [0.1, 10.0, 35.0]])
        P = np.matrix([[0.3689, 0.1170, 0.2673],
                       [0.4699, 0.4387, 0.747],
                       [0.1091, 0.8732, 0.5547],
                       [0.0381, 0.5743, 0.8828]])
        outer = 0
        for ii in range(4):
            inner = 0
            for jj in range(3):
                xj = x[jj]
                Aij = A[ii, jj]
                Pij = P[ii, jj]
                inner += Aij * ((xj-Pij) ** 2)
            outer += alpha[ii] * np.exp(-inner)
        return -outer

# ========================= n-dimensional =======================


class Rastrigin:
    """
    Rastrigin function

    .. math::
        f(x_1,\\ldots,x_n)=10n-\\sum_{i=1}^n (x_i^2 - 10 \\cos(2 \\pi x_i))

    subject to

    .. math::
        -5.12 \\leq x_i \\leq 5.12

    Global optimum: :math:`f(0,0,...,0)=0`

    :ivar dim: Number of dimensions
    :ivar xlow: Lower bound constraints
    :ivar xup: Upper bound constraints
    :ivar info: Problem information:
    :ivar min: Global optimum
    :ivar integer: Integer variables
    :ivar continuous: Continuous variables:
    :ivar constraints: Whether there are non-bound constraints
    """
    def __init__(self, dim=10):
        self.xlow = -5.12 * np.ones(dim)
        self.xup = 5.12 * np.ones(dim)
        self.dim = dim
        self.info = str(dim)+"-dimensional Rastrigin function \n" +\
                             "Global optimum: f(0,0,...,0) = 0"
        self.min = 0
        self.integer = []
        self.continuous = np.arange(0, dim)
        self.constraints = False
        validate(self)

    def objfunction(self, x):
        """
        Evaluate the Rastrigin function  at x

        :param x: Data point
        :return: Value at x
        """
        if len(x) != self.dim:
            raise ValueError('Dimension mismatch')
        return 10 * self.dim + sum(x**2 - 10 * np.cos(2 * np.pi * x))


class Ackley:
    """
    Ackley function

    .. math::
        f(x_1,\\ldots,x_n) = -20\\exp\\left( -0.2 \\sqrt{\\frac{1}{n} \
        \\sum_{j=1}^n x_j^2} \\right) -\\exp \\left( \\frac{1}{n} \
        \\sum{j=1}^n \\cos(2 \\pi x_j) \\right) + 20 - e

    subject to

    .. math::
        -15 \\leq x_i \\leq 20

    Global optimum: :math:`f(0,0,...,0)=0`

    :ivar dim: Number of dimensions
    :ivar xlow: Lower bound constraints
    :ivar xup: Upper bound constraints
    :ivar info: Problem information:
    :ivar min: Global optimum
    :ivar integer: Integer variables
    :ivar continuous: Continuous variables:
    :ivar constraints: Whether there are non-bound constraints
    """
    def __init__(self, dim=10):
        self.xlow = -15 * np.ones(dim)
        self.xup = 20 * np.ones(dim)
        self.dim = dim
        self.info = str(dim)+"-dimensional Ackley function \n" +\
                             "Global optimum: f(0,0,...,0) = 0"
        self.min = 0
        self.integer = []
        self.continuous = np.arange(0, dim)
        self.constraints = False
        validate(self)

    def objfunction(self, x):
        """
        Evaluate the Ackley function  at x

        :param x: Data point
        :return: Value at x
        """
        if len(x) != self.dim:
            raise ValueError('Dimension mismatch')
        n = float(len(x))
        return -20.0 * np.exp(-0.2*np.sqrt(sum(x**2)/n)) - \
            np.exp(sum(np.cos(2.0*np.pi*x))/n) + 20 + np.exp(1)


class Griewank:
    """
    Griewank function

    .. math::
        f(x_1,\\ldots,x_n) = 1 + \\frac{1}{4000} \\sum_{j=1}^n x_j^2 - \
        \\prod_{j=1}^n \\cos \\left( \\frac{x_i}{\\sqrt{i}} \\right)

    subject to

    .. math::
        -512 \\leq x_i \\leq 512

    Global optimum: :math:`f(0,0,...,0)=0`

    :ivar dim: Number of dimensions
    :ivar xlow: Lower bound constraints
    :ivar xup: Upper bound constraints
    :ivar info: Problem information:
    :ivar min: Global optimum
    :ivar integer: Integer variables
    :ivar continuous: Continuous variables:
    :ivar constraints: Whether there are non-bound constraints
    """
    def __init__(self, dim=10):
        self.xlow = -512 * np.ones(dim)
        self.xup = 512 * np.ones(dim)
        self.dim = dim
        self.info = str(dim)+"-dimensional Griewank function \n" +\
                             "Global optimum: f(0,0,...,0) = 0"
        self.min = 0
        self.integer = []
        self.continuous = np.arange(0, dim)
        self.constraints = False
        validate(self)

    def objfunction(self, x):
        """
        Evaluate the Griewank function  at x

        :param x: Data point
        :return: Value at x
        """
        if len(x) != self.dim:
            raise ValueError('Dimension mismatch')
        total = 1
        for i, y in enumerate(x):
            total *= np.cos(y / np.sqrt(i+1))
        return 1.0 / 4000.0 * sum([y**2 for y in x]) - total + 1


class Rosenbrock:
    """
    Rosenbrock function

    .. math::
        f(x_1,\\ldots,x_n) = \\sum_{j=1}^{n-1} \
        \\left( 100(x_j^2-x_{j+1})^2 + (1-x_j)^2 \\right)

    subject to

    .. math::
        -2.048 \\leq x_i \\leq 2.048

    Global optimum: :math:`f(1,1,...,1)=0`

    :ivar dim: Number of dimensions
    :ivar xlow: Lower bound constraints
    :ivar xup: Upper bound constraints
    :ivar info: Problem information:
    :ivar min: Global optimum
    :ivar integer: Integer variables
    :ivar continuous: Continuous variables:
    :ivar constraints: Whether there are non-bound constraints
    """
    def __init__(self, dim=10):
        self.xlow = -2.048 * np.ones(dim)
        self.xup = 2.048 * np.ones(dim)
        self.dim = dim
        self.info = str(dim)+"-dimensional Rosenbrock function \n" +\
                             "Global optimum: f(1,1,...,1) = 0"
        self.min = 0
        self.integer = []
        self.continuous = np.arange(0, dim)
        self.constraints = False
        validate(self)

    def objfunction(self, x):
        """
        Evaluate the Rosenbrock function  at x

        :param x: Data point
        :return: Value at x
        """
        if len(x) != self.dim:
            raise ValueError('Dimension mismatch')
        total = 0
        for i in range(len(x) - 1):
            total += 100 * (x[i]**2 - x[i+1])**2 + (x[i] - 1)**2
        return total


class Schwefel:
    """
    Schwefel function

    .. math::
        f(x_1,\\ldots,x_n) = \\sum_{j=1}^{n} \
        \\left( -x_j \\sin(\\sqrt{|x_j|}) \\right) + 418.982997 n

    subject to

    .. math::
        -512 \\leq x_i \\leq 512

    Global optimum: :math:`f(420.968746,420.968746,...,420.968746)=0`

    :ivar dim: Number of dimensions
    :ivar xlow: Lower bound constraints
    :ivar xup: Upper bound constraints
    :ivar info: Problem information:
    :ivar min: Global optimum
    :ivar integer: Integer variables
    :ivar continuous: Continuous variables:
    :ivar constraints: Whether there are non-bound constraints
    """
    def __init__(self, dim=10):
        self.xlow = -512 * np.ones(dim)
        self.xup = 512 * np.ones(dim)
        self.dim = dim
        self.info = str(dim)+"-dimensional Schwefel function \n" +\
                             "Global optimum: f(420.968746,...,420.968746) = 0"
        self.min = 0
        self.integer = []
        self.continuous = np.arange(0, dim)
        self.constraints = False
        validate(self)

    def objfunction(self, x):
        """
        Evaluate the Schwefel function  at x

        :param x: Data point
        :return: Value at x
        """
        if len(x) != self.dim:
            raise ValueError('Dimension mismatch')
        return 418.9829 * self.dim - \
            sum([y * np.sin(np.sqrt(abs(y))) for y in x])


class Sphere:
    """
    Sphere function

    .. math::
        f(x_1,\\ldots,x_n) = \\sum_{j=1}^n x_j^2

    subject to

    .. math::
        -5.12 \\leq x_i \\leq 5.12

    Global optimum: :math:`f(0,0,...,0)=0`

    :ivar dim: Number of dimensions
    :ivar xlow: Lower bound constraints
    :ivar xup: Upper bound constraints
    :ivar info: Problem information:
    :ivar min: Global optimum
    :ivar integer: Integer variables
    :ivar continuous: Continuous variables:
    :ivar constraints: Whether there are non-bound constraints
    """
    def __init__(self, dim=10):
        self.xlow = -5.12 * np.ones(dim)
        self.xup = 5.12 * np.ones(dim)
        self.dim = dim
        self.info = str(dim)+"-dimensional Sphere function \n" +\
                             "Global optimum: f(0,0,...,0) = 0"
        self.min = 0
        self.integer = []
        self.continuous = np.arange(0, dim)
        self.constraints = False
        validate(self)

    def objfunction(self, x):
        """
        Evaluate the Sphere function  at x

        :param x: Data point
        :return: Value at x
        """
        if len(x) != self.dim:
            raise ValueError('Dimension mismatch')
        return sum(x**2)


class Exponential:
    """
    Exponential function

    .. math::
        f(x_1,\\ldots,x_n) = \\sum_{j=1}^n e^{jx_j} - \\sum_{j=1} e^{-5.12 j}

    subject to

    .. math::
        -5.12 \\leq x_i \\leq 5.12

    Global optimum: :math:`f(0,0,...,0)=0`

    :ivar dim: Number of dimensions
    :ivar xlow: Lower bound constraints
    :ivar xup: Upper bound constraints
    :ivar info: Problem information:
    :ivar min: Global optimum
    :ivar integer: Integer variables
    :ivar continuous: Continuous variables:
    :ivar constraints: Whether there are non-bound constraints
    """
    def __init__(self, dim=10):
        self.xlow = -5.12 * np.ones(dim)
        self.xup = 5.12 * np.ones(dim)
        self.dim = dim
        self.info = str(dim)+"-dimensional Exponential function \n" +\
                             "Global optimum: f(-5.12,-5.12,...,-5.12) = 0"
        self.min = 0
        self.integer = []
        self.continuous = np.arange(0, dim)
        self.constraints = False
        validate(self)

    def objfunction(self, x):
        """
        Evaluate the Exponential function  at x

        :param x: Data point
        :return: Value at x
        """
        if len(x) != self.dim:
            raise ValueError('Dimension mismatch')
        total = 0
        for i in range(len(x)):
            total += np.exp((i+1)*x[i-1]) - np.exp(-5.12*(i+1))
        return total


class StyblinskiTang:
    """
    StyblinskiTang function

    .. math::
        f(x_1,\\ldots,x_n) = \\frac{1}{2} \\sum_{j=1}^n  \
        \\left(x_j^4 -16x_j^2 +5x_j \\right)

    subject to

    .. math::
        -5 \\leq x_i \\leq 5

    Global optimum: :math:`f(-2.903534,-2.903534,...,-2.903534)=\
    -39.16599 \\cdot n`

    :ivar dim: Number of dimensions
    :ivar xlow: Lower bound constraints
    :ivar xup: Upper bound constraints
    :ivar info: Problem information:
    :ivar min: Global optimum
    :ivar integer: Integer variables
    :ivar continuous: Continuous variables:
    :ivar constraints: Whether there are non-bound constraints
    """
    def __init__(self, dim=10):
        self.xlow = -5 * np.ones(dim)
        self.xup = 5 * np.ones(dim)
        self.dim = dim
        self.info = str(dim)+"-dimensional Styblinski-Tang function \n" +\
                             "Global optimum: f(-2.903534,...,-2.903534) = " + \
                             str(-39.16599*dim)
        self.min = -39.16599*dim
        self.integer = []
        self.continuous = np.arange(0, dim)
        self.constraints = False
        validate(self)

    def objfunction(self, x):
        """
        Evaluate the StyblinskiTang function  at x

        :param x: Data point
        :return: Value at x
        """
        if len(x) != self.dim:
            raise ValueError('Dimension mismatch')
        return 0.5*sum(x**4 - 16*x**2 + 5*x)


class Quartic:
    """
    Quartic function

    .. math::
        f(x_1,\\ldots,x_n) = \\sum_{j=1}^n j x_j^4 + random[0,1)

    subject to

    .. math::
        -1.28 \\leq x_i \\leq 1.28

    Global optimum: :math:`f(0,0,...,0)=0+noise`

    :ivar dim: Number of dimensions
    :ivar xlow: Lower bound constraints
    :ivar xup: Upper bound constraints
    :ivar info: Problem information:
    :ivar min: Global optimum
    :ivar integer: Integer variables
    :ivar continuous: Continuous variables:
    :ivar constraints: Whether there are non-bound constraints
    """
    def __init__(self, dim=10):
        self.xlow = -1.28 * np.ones(dim)
        self.xup = 1.28 * np.ones(dim)
        self.dim = dim
        self.info = str(dim)+"-dimensional Quartic function \n" +\
                             "Global optimum: f(0,0,...,0) = 0+noise"
        self.min = 0
        self.integer = []
        self.continuous = np.arange(0, dim)
        self.prng = random.Random()
        self.prng.seed(time())
        self.constraints = False
        validate(self)

    def objfunction(self, x):
        """
        Evaluate the Quartic function  at x

        :param x: Data point
        :return: Value at x
        """
        if len(x) != self.dim:
            raise ValueError('Dimension mismatch')
        total = 0.0
        for i in xrange(len(x)):
            total += (i+1.0) * x[i]**4.0
        return total + self.prng.uniform(0, 1)


class Whitley:
    """
    Quartic function

    .. math::
        f(x_1,\\ldots,x_n) = \\sum_{i=1}^n \\sum_{j=1}^n \
        \\left( \\frac{(100(x_i^2-x_j)^2+(1-x_j)^2)^2}{4000} \
        - \\cos(100(x_i^2-x_j)^2 + (1-x_j)^2 ) + 1 \\right)

    subject to

    .. math::
        -10.24 \\leq x_i \\leq 10.24

    Global optimum: :math:`f(1,1,...,1)=0`

    :ivar dim: Number of dimensions
    :ivar xlow: Lower bound constraints
    :ivar xup: Upper bound constraints
    :ivar info: Problem information:
    :ivar min: Global optimum
    :ivar integer: Integer variables
    :ivar continuous: Continuous variables:
    :ivar constraints: Whether there are non-bound constraints
    """
    def __init__(self, dim=10):
        self.xlow = -10.24 * np.ones(dim)
        self.xup = 10.24 * np.ones(dim)
        self.dim = dim
        self.info = str(dim)+"-dimensional Whitley function \n" +\
                             "Global optimum: f(1,1,...,1) = 0"
        self.min = 0
        self.integer = []
        self.continuous = np.arange(0, dim)
        self.constraints = False
        validate(self)

    def objfunction(self, x):
        """
        Evaluate the Whitley function  at x

        :param x: Data point
        :return: Value at x
        """
        if len(x) != self.dim:
            raise ValueError('Dimension mismatch')
        total = 0
        for i in range(len(x)):
            for j in range(len(x)):
                temp = 100*((x[i]**2)-x[j]) + (1-x[j])**2
                total += (float(temp**2)/4000.0) - np.cos(temp) + 1
        return total


class SchafferF7:
    """
    SchafferF7 function

    .. math::
        f(x_1,\\ldots,x_n) = \\left[\\frac{1}{n-1}\\sqrt{s_i} \
        \\cdot (\\sin(50.0s_i^{\\frac{1}{5}})+1)\\right]^2

    where

    .. math::
        s_i = \\sqrt{x_i^2 + x_{i+1}^2}

    subject to

    .. math::
        -100 \\leq x_i \\leq 100

    Global optimum: :math:`f(0,0,...,0)=0`

    :ivar dim: Number of dimensions
    :ivar xlow: Lower bound constraints
    :ivar xup: Upper bound constraints
    :ivar info: Problem information:
    :ivar min: Global optimum
    :ivar integer: Integer variables
    :ivar continuous: Continuous variables:
    :ivar constraints: Whether there are non-bound constraints
    """
    def __init__(self, dim=10):
        self.xlow = -100 * np.ones(dim)
        self.xup = 100 * np.ones(dim)
        self.dim = dim
        self.info = str(dim)+"-dimensional SchafferF7 function \n" +\
                             "Global optimum: f(0,0,...,0) = 0"
        self.min = 0
        self.integer = []
        self.continuous = np.arange(0, dim)
        self.constraints = False
        validate(self)

    def objfunction(self, x):
        """
        Evaluate the SchafferF7 function  at x

        :param x: Data point
        :return: Value at x
        """
        if len(x) != self.dim:
            raise ValueError('Dimension mismatch')
        total = 0
        normalizer = 1.0/float(len(x)-1)
        for i in range(len(x)-1):
            si = np.sqrt(x[i]**2 + x[i+1]**2)
            total += (normalizer * np.sqrt(si) * (np.sin(50*si**0.20) + 1))**2
        return total

# ============================== Constraints ==============================


class Keane:
    """
    Keane's "bump" function

    .. math::
        f(x_1,\\ldots,x_n) = -\\left| \\frac{\\sum_{j=1}^n \\cos^4(x_j) - \
        2 \\prod_{j=1}^n \\cos^2(x_j)}{\\sqrt{\\sum_{j=1}^n jx_j^2}} \\right|

    subject to

    .. math::
        -100 \\leq x_i \\leq 100

    .. math::
        0.75 - \\prod_{j=1}^n x_j < 0

    .. math::
        \\sum_{j=1}^n x_j - 7.5n < 0


    Global optimum: -0.835 for large n

    :ivar dim: Number of dimensions
    :ivar xlow: Lower bound constraints
    :ivar xup: Upper bound constraints
    :ivar info: Problem information:
    :ivar min: Global optimum
    :ivar integer: Integer variables
    :ivar continuous: Continuous variables:
    :ivar constraints: Whether there are non-bound constraints
    """
    def __init__(self, dim=10):
        self.xlow = np.zeros(dim)
        self.xup = 5 * np.ones(dim)
        self.dim = dim
        self.min = -0.835
        self.integer = []
        self.continuous = np.arange(0, dim)
        self.info = str(dim)+"-dimensional Keane bump function \n" +\
                             "Global optimum: -0.835 for large n"
        self.constraints = True
        validate(self)

    # Return a list with the constraint function at the given point
    def eval_ineq_constraints(self, x):
        vec = np.zeros((2,))
        vec[0] = 0.75 - np.prod(x)
        vec[1] = sum(x) - 7.5 * self.dim
        return vec

    # Evaluate the objective function for a single data point
    def objfunction(self, x):
        """
        Evaluate the Keane function  at x

        :param x: Data point
        :return: Value at x
        """
        if len(x) != self.dim:
                raise ValueError('Dimension mismatch')
        n = len(x)
        return -abs((sum(np.cos(x)**4)-2 * np.prod(np.cos(x)**2)) /
                    max([1E-10, np.sqrt(np.dot(1+np.arange(n), x**2))]))


class LargestPolygon:
    """
    The Largest Polygon problems is described as follows:

    Find the polygon of maximal area, among polygons with n sides and
    diameter :math:`d \\leq 1` There are 2n variables, the radius :math:`r_i`
    and angle :math:`\\theta_i` for each point, so the number of variables must
    be even. One vertex is fixed at the origin so there are n/2+1 corners in
    the polygon we are trying to fit. There are at least (n/2+1)! local minima

    The global minimum approaches -0.7854 when n gets large
    """
    def __init__(self, dim=10):
        assert dim % 2 == 0, "dim was odd, should be even"
        self.xlow = np.zeros(dim)
        self.xup = np.hstack((np.ones(dim/2), np.pi * np.ones(dim/2)))
        self.dim = dim
        self.min = -0.7854
        self.integer = []
        self.continuous = np.arange(0, dim)
        self.info = str(self.dim)+"-dimensional Largest Polygon \n" +\
                                  "Global optimum: approaches -0.7854\n"
        self.constraints = True
        validate(self)

    def eval_ineq_constraints(self, x):
        vec = np.zeros(((self.dim/2)**2 + self.dim/2-1,))

        for i in range(self.dim/2):
            for j in range(self.dim/2):
                vec[i*self.dim/2+j] = x[i]**2 + x[j]**2 - \
                    2.0 * x[i] * x[j] * np.cos(x[self.dim/2 + i] -
                                               x[self.dim/2 + j]) - 1

        for i in range(self.dim/2-1):
            vec[(self.dim/2)**2+i] = x[self.dim/2 + i] - x[self.dim/2 + i + 1]

        return vec

    def objfunction(self, x):
        """
        Evaluate the LargestPolygon function  at x

        :param x: Data point
        :return: Value at x
        """
        if len(x) != self.dim:
            raise ValueError('Dimension mismatch')
        val = 0
        for i in range(self.dim/2 - 1):
            val -= 0.5 * x[i+1] * x[i] * \
                np.sin(x[self.dim/2 + i + 1] - x[self.dim/2 + i])
        return val


class LinearMI:
    """
    This is a linear mixed integer problem with non-bound constraints

    There are 5 variables, the first 3 are discrete and the last 2
    are continuous.

    Global optimum: :math:`f(1,0,0,0,0) = -1`
    """
    def __init__(self):
        self.xlow = np.zeros(5)
        self.xup = np.array([10, 10, 10, 1, 1])
        self.dim = 5
        self.min = -1
        self.integer = np.arange(0, 3)
        self.continuous = np.arange(3, 5)
        self.info = str(self.dim)+"-dimensional Linear MI \n" +\
                                  "Global optimum: f(1,0,0,0,0) = -1\n" +\
                                  str(len(self.integer)) + " integer variables"
        self.constraints = True
        validate(self)

    def eval_ineq_constraints(self, x):
        vec = np.zeros((3,))
        vec[0] = x[0] + x[2] - 1.6
        vec[1] = 1.333 * x[1] + x[3] - 3
        vec[2] = - x[2] - x[3] + x[4]
        return vec

    def objfunction(self, x):
        """
        Evaluate the LinearMI function  at x

        :param x: Data point
        :return: Value at x
        """
        if len(x) != self.dim:
            raise ValueError('Dimension mismatch')
        return - x[0] + 3 * x[1] + 1.5 * x[2] + 2 * x[3] - 0.5 * x[4]

if __name__ == "__main__":
    print("\n========================= Hartman3 =======================")
    fun = Hartman3()
    print(fun.info)
    print("Hartman3(1,1,1) = " + str(fun.objfunction(np.array([1, 1, 1]))))
    print("Continuous variables: " + str(fun.continuous))
    print("Integer variables: " + str(fun.integer))

    print("\n========================= Rastrigin =======================")
    fun = Rastrigin(dim=3)
    print(fun.info)
    print("Rastrigin(1,1,1) = " + str(fun.objfunction(np.array([1, 1, 1]))))
    print("Continuous variables: " + str(fun.continuous))
    print("Integer variables: " + str(fun.integer))

    print("\n========================= Ackley =======================")
    fun = Ackley(dim=3)
    print(fun.info)
    print("Ackley(1,1,1) = " + str(fun.objfunction(np.array([1, 1, 1]))))

    print("\n========================= Griewank =======================")
    fun = Griewank(dim=3)
    print(fun.info)
    print("Griewank(1,1,1) = " + str(fun.objfunction(np.array([1, 1, 1]))))
    print("Continuous variables: " + str(fun.continuous))
    print("Integer variables: " + str(fun.integer))

    print("\n========================= Rosenbrock =======================")
    fun = Rosenbrock(dim=3)
    print(fun.info)
    print("Rosenbrock(1,1,1) = " + str(fun.objfunction(np.array([1, 1, 1]))))
    print("Continuous variables: " + str(fun.continuous))
    print("Integer variables: " + str(fun.integer))

    print("\n========================= Schwefel =======================")
    fun = Schwefel(dim=3)
    print(fun.info)
    print("Schwefel(1,1,1) = " + str(fun.objfunction(np.array([1, 1, 1]))))
    print("Continuous variables: " + str(fun.continuous))
    print("Integer variables: " + str(fun.integer))

    print("\n========================= Sphere =======================")
    fun = Sphere(dim=3)
    print(fun.info)
    print("Sphere(1,1,1) = " + str(fun.objfunction(np.array([1, 1, 1]))))
    print("Continuous variables: " + str(fun.continuous))
    print("Integer variables: " + str(fun.integer))

    print("\n========================= Exponential =======================")
    fun = Exponential(dim=3)
    print(fun.info)
    print("Exponential(1,1,1) = " + str(fun.objfunction(np.array([1, 1, 1]))))
    print("Continuous variables: " + str(fun.continuous))
    print("Integer variables: " + str(fun.integer))

    print("\n======================= Styblinski-Tang =====================")
    fun = StyblinskiTang(dim=3)
    print(fun.info)
    print("StyblinskiTang(1,1,1) = " +
          str(fun.objfunction(np.array([1, 1, 1]))))
    print("Continuous variables: " + str(fun.continuous))
    print("Integer variables: " + str(fun.integer))

    print("\n========================= Whitley =======================")
    fun = Whitley(dim=3)
    print(fun.info)
    print("Whitley(1,1,1) = " + str(fun.objfunction(np.array([1, 1, 1]))))
    print("Continuous variables: " + str(fun.continuous))
    print("Integer variables: " + str(fun.integer))

    print("\n========================= Quartic =======================")
    fun = Quartic(dim=3)
    print(fun.info)
    print("Quartic(1,1,1) = " + str(fun.objfunction(np.array([1, 1, 1]))))
    print("Continuous variables: " + str(fun.continuous))
    print("Integer variables: " + str(fun.integer))

    print("\n========================= SchafferF7 =======================")
    fun = SchafferF7(dim=3)
    print(fun.info)
    print("SchafferF7(1,1,1) = " + str(fun.objfunction(np.array([1, 1, 1]))))
    print("Continuous variables: " + str(fun.continuous))
    print("Integer variables: " + str(fun.integer))

    print("\n========================= Liner MI =======================")
    fun = LinearMI()
    print(fun.info)
    print("Linear_MI(1,1,1,1,1) = " +
          str(fun.objfunction(np.array([1, 1, 1, 1, 1]))))
    print("Continuous variables: " + str(fun.continuous))
    print("Integer variables: " + str(fun.integer))

    print("\n====================== Largest Polygon =====================")
    fun = LargestPolygon(dim=4)
    print(fun.info)
    print("LargestPolygon(1,1,1,1) = " + str(fun.objfunction(np.ones(4))))
    print("Continuous variables: " + str(fun.continuous))
    print("Integer variables: " + str(fun.integer))