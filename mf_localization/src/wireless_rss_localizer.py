#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2021  IBM Corporation
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import json
import argparse
import copy
import numpy as np
import matplotlib.pyplot as plt

from sklearn.neighbors import KNeighborsRegressor, NearestNeighbors

import rospy
import tf2_ros
import tf_conversions
from std_msgs.msg import String

from wireless_utils import *

class SimpleRSSLocalizer:

    def __init__(self, n_neighbors=1, max_rssi_threshold=-100, min_beacons=3, rssi_offset=0.0):
        self._n_neighbors = n_neighbors
        self._max_rssi_threshold = max_rssi_threshold
        self._min_beacons = min_beacons
        self._rssi_offset = rssi_offset

    def fit(self, samples):
        self._samples = samples

        # enumerate unique transmitter IDs
        idset = set()
        for s in samples:
            data = s["data"]
            beacons = data["beacons"]
            for b in beacons:
                tid = b["id"].lower()
                idset.add(tid)

        self._keys = np.array(list(idset))

        # convert samples data to numpy array
        keys = self._keys
        X = np.zeros((len(samples), 4))
        Y = -100 * np.ones((len(samples),len(keys)))

        for i,s in enumerate(samples):
            info = s["information"]
            if "floor" in info:
                floor = info["floor"]
            else:
                floor = 0.0

            X[i] = np.array([info["x"], info["y"], info["z"], floor])

            data = s["data"]
            beacons = data["beacons"]

            for b in beacons:
                key = b["id"].lower()
                rssi = float(b["rssi"])
                if -100 < rssi < -1:
                    indices = np.where(keys==key)
                    Y[i, indices ] = rssi

        self._X = X
        self._Y = Y

    def predict(self, beacons):

        # create an RSS vector
        keys = self._keys
        y = -100 * np.ones((1,len(keys)))

        max_rssi = -100
        c_match = 0
        indices_active = []
        for b in beacons:
            key = b["id"].lower()
            rssi = float(b["rssi"])
            if -100 < rssi < -1: # check if raw rssi is in the range
                rssi = rssi - self._rssi_offset # apply rssi offset
                indices = np.where(keys==key)
                if 0 < len(indices[0]):
                    y[0, indices] = rssi
                    c_match += 1
                    max_rssi = np.max([max_rssi, rssi])
                    indices_active.append(indices[0][0])

        # return if the input does not match the stored data
        if c_match == 0:
            return None # undetermined

        # unreliable
        if c_match < self._min_beacons:
            return None
        elif max_rssi <= self._max_rssi_threshold:
            return None

        # create a knn regressor by using visible transmitter IDs
        indices_active = np.array(indices_active)
        knnr = KNeighborsRegressor(n_neighbors=self._n_neighbors)
        Y_active = self._Y[:, indices_active]
        knnr.fit(Y_active,self._X)
        x = knnr.predict(y[:, indices_active])

        return x

    def find_closest(self, x):
        knnr = KNeighborsRegressor(n_neighbors=self._n_neighbors)
        X = self._X

        nn = NearestNeighbors(n_neighbors=1)
        nn.fit(self._X)
        ret = nn.kneighbors(x, return_distance=False)

        return self._X[ret][0]

def main(samples_file, queries_file):
    with open(samples_file) as f:
        samples = json.load(f)

    beacons_samples = extract_samples(samples, key="iBeacon")
    wifi_samples = extract_samples(samples, key="WiFi")

    print("#beacons="+str(len(beacons_samples)))
    print("#wifi="+str(len(wifi_samples)))

    wifi_localizer = SimpleRSSLocalizer(n_neighbors=3)
    wifi_localizer.fit(wifi_samples)

    ble_localizer = SimpleRSSLocalizer(n_neighbors=3)
    ble_localizer.fit(beacons_samples)

    if queries_file is not None:
        with open(queries_file) as f:
            q_samples = json.load(f)

        X_w = []
        X_b = []
        Y_w = []
        Y_b = []
        ble_errors = []
        wifi_errors = []
        for q in q_samples:
            q_info = q["information"]
            loc_gt = np.array([q_info["x"], q_info["y"], q_info["z"], 0.0])

            q_beacons = q["data"]["beacons"]

            res = wifi_localizer.predict(q_beacons)
            if res is not None:
                loc_est = res[0]
                X_w.append(list(loc_gt))
                Y_w.append(list(loc_est))
                wifi_error = np.linalg.norm( loc_gt - loc_est)
                wifi_errors.append(wifi_error)

            res = ble_localizer.predict(q_beacons)
            if res is not None:
                loc_est = res[0]
                X_b.append(list(loc_gt))
                Y_b.append(list(loc_est))
                ble_error = np.linalg.norm( loc_gt - loc_est)
                ble_errors.append(ble_error)

        X_w = np.array(X_w)
        Y_w = np.array(Y_w)
        X_b = np.array(X_b)
        Y_b = np.array(Y_b)

        print("mean(wifi_errors)="+str( np.mean(wifi_errors) ))
        print("mean(ble_errors)="+str( np.mean(ble_errors) ))
        plt.hist(ble_errors, bins=500, normed=True, cumulative=True, histtype="step", label="BLE")
        plt.hist(wifi_errors, bins=500, normed=True, cumulative=True, histtype="step", label="wifi")
        plt.ylim([0,1])
        plt.legend()
        plt.show()

        plt.scatter(X_b[:,0], X_b[:,1], label="BLE_gt", color="k")
        plt.scatter(Y_b[:,0], Y_b[:,1], label="BLE", color="b")
        plt.gca().set_aspect('equal')
        plt.legend()
        plt.show()

        plt.scatter(X_w[:,0], X_w[:,1], label="WiFi_gt", color="k")
        plt.scatter(Y_w[:,0], Y_w[:,1], label="WiFi_est", color="b")
        plt.gca().set_aspect('equal')
        plt.legend()
        plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s","--samples", required=True)
    parser.add_argument("-q","--queries", default=None)
    args = parser.parse_args()

    samples_file = args.samples
    queries_file = args.queries

    main(samples_file, queries_file)
