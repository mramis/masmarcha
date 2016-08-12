#!usr/bin/env python
# coding: utf-8

'''This module was create for manipulate the domain of joint-angles-data 
and compare more than only-one text imput file.
'''

# Copyright (C) 2016  Mariano Ramis
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from __future__ import division

import numpy as np

def linear(X, A0, A1):
    '''Define f_linear(x) = y, from y - y1 = m(x - x1) were
            m = y1 - y0 / x1 - x0
    Args:
        x: the x value to interpolate in the linear function f(x) = y;
        Pi: each one is 2-tuple with the (xi, yi) coordinate
            of two consecutive points in the plane.
    Returns:
        "numpy array (x, f(x) = y)" interpolated value.
    '''
    X0, Y0 = A0.T
    X1, Y1 = A1.T
    Y = (Y1 - Y0)/(X1 - X0)*(X - X0) + Y0
    return np.hstack((X, Y)).reshape(2, 2).T


def linear_interpolation_range(A0, A1, steps):
    '''Interpola los datos que faltan en una cantidad finita de puntos dentro
    de un intervalo
    
    '''
    X0, X1 = A0.T[0], A1.T[0]
    DX = (X1 - X0)/(steps + 1)
    points = (X0 + X*DX for X in range(1, steps + 1))
    for p in points:
        yield linear(p, A0, A1)












def linearInterpolationInDomainData(Pi, Pj, domain):
    '''Performs an linear interpolate between 2-tuples and an domain matrix::
        domain = np.array([x0, x1, x2, ..., xn])
    print X0,Y0, X1,Y1
    print X0,Y0, X1,Y1
        # if xi = Pi[0] = (xi, yi)[0] is in domain and
        # if xj = Pj[0] = (xj, yj)[0] is in domain, then
        result = np.array(linear(Pi, Pj, interval))
        # were interval it's a np.array([xi, xi+1, ..., xj-1, xj])
        # from domian x-points, and result:
        result = np.domain([xi   , yi  ],
                           [xi+1 , yi+1], # yi+1 an interpolated value
                           [...  , ... ], # this same
                           [xj-1 , yj-1]) # and this same

    Args:
        Pi: numpy array([xi, yi])
        Pj: numpy array([xj, yj])
        domain: it's a numpy array that's contains a range of x-points
            were x0 = domain[0] >= xi and xn = domain[-1] <= xj.
    Result:
        Numpy array that contains linear-interpolated values who shape
            (n, 2), were n depends that number of x that are in domain
            between xi and xj.
        
    '''
    xi, xj = Pi[0], Pj[0]
    # define a matrix that contains the interval of x who are between
    # [xi, xj] in domain matrix.
    x_array_interval = domain.clip(xi, xj)
    x_interest_interval = np.unique(x_array_interval)
    # now we make an linear interpolation over the x of interest
    # domain less the last one, who is reserved for the next process.
    result_array = []# of linear interpolate process
    for x in x_interest_interval[:-1]:
        result_array.append(linear(x, Pi, Pj))
    return(np.array(result_array))

def interpolateArray(array_to_interpolate, domain):
    '''Perform linearInterpolationInDomainData function over an array(
        array_to_interpolate), taking Pi = array_to_interpolate[i] and
        Pj = array_to_interpolate[i+1] for i = 1, 2, ..., n; n = row numbers
        of array_to_interpolate
    Args:
        array_to_interpolate: arrays of 2-tuple joints-points.
        domain: it's the same arrays who pass to linearInterpolationOf_
        PointsInDomain.
    Returns:
        An numpy array who has the row number that domain, and the
        (xi, yi=interpolated_value).
    '''
    result_array = np.ndarray((1, 2))# of each linear interpolate process
    P0 = array_to_interpolate[0]
    for P1 in array_to_interpolate[1:]:
        interpolated = linearInterpolationInDomainData(P0, P1, domain)
        result_array = np.vstack((result_array, interpolated))
        P0 = P1
    result_array = np.vstack((result_array, P1))
    # the first element is removed because it's a random element iniciated
    # when result_array
    return(result_array[1:].T)

def extendArraysDomain(*arrays):
    '''Take a group of 1-D arrays (the joint-angles arrays) and extend the
        domain (time units) for each one.
    Args:
        1-D m-arrays of the "same-joint" angles::
            hip_1 = np.array([h11, h12, h13, ..., h1r]);
            hip_2 = np.array([h21, h22, h23, ..., h2r, h2r+1, ..., h2n]);
            ..... = ....................................................;
            hip_m = np.array([hm1, hm2, hm3, ..., hmr-2, hmr-1])
            Each one of the m-arrays it's a test of hip joint, that we want
            compare, but they have diferents length of domain. So we take
            the n-length domain value and extend(fix) to the rest.
    Returns:
        Fixed_arrays: 1-D array, with m 2-D np.array(["X-fixed-domain",
            array_input])
        Domain_array: 1-D array with the common x-potins of domain for each
            one array from imput(Args).

    '''
    # Make an array of interger points (time units) for each input arrays
    # and take the "n index" of max length of this arrays. 
    array_of_domains = np.array([np.arange(array.size) for array in arrays])
    size_of_arrays_domains = [(X.size - 1) for X in array_of_domains]
    n_max_length = max(size_of_arrays_domains)

    # the returns arrays:
    Fixed_arrays = np.ndarray((len(arrays),), dtype=object)
    common_domain = np.array(())
    
    for index, length_array in enumerate(size_of_arrays_domains):
        # this scalar variable works for extend de domain of each
        # array of input to the n_max length array of domain input.
        scalar = n_max_length / float(length_array)
        fixed = array_of_domains[index] * scalar
        
        # bulid the array of (fixed_time, angle=each_array_input) and the
        # common x values of the domain of all arrays input.
        time_theta_array_ouput = np.stack((fixed, arrays[index]))
        common_domain = np.append(common_domain, fixed)
        Fixed_arrays[index] = time_theta_array_ouput.T
        Domain_array = np.unique(common_domain)
    return Fixed_arrays, Domain_array


