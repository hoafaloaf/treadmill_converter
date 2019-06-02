#!/usr/bin/env python

import argparse
import os
import sys

import xmltodict


def scale_value(value, scale_factor, as_int=False):
    return str((int if as_int else float)(float(value) * scale_factor))


def treadmill_converter(**args):
    input_file = args.get("input_file")
    if not input_file:
        raise IOError("No input file specified!")
    input_file = os.path.abspath(input_file)

    distance = args.get("distance")
    if distance is None:
        raise IOError("No final distance specified!")

    output_file = args.get("output_file")
    if not output_file:
        output_base, output_ext = os.path.splitext(input_file)
        output_file = "{}_updated{}".format(output_base, output_ext)

    print("Input file:  {}".format(input_file))
    print("Output file: {}".format(output_file))

    doc = None
    with open(input_file, "r") as ff:
        doc = xmltodict.parse(ff)

    activity = doc["TrainingCenterDatabase"]["Activities"]["Activity"]
    track_points = list()

    # Assuming track_points are in the correct order.
    for lap in activity["Lap"]:
        track_points.extend(lap["Track"]["Trackpoint"])

    final_distance = float(track_points[-1]["DistanceMeters"])
    scale_factor = distance / final_distance

    print("Treadmill Distance: {}".format(distance))
    print("Final Distance:     {}".format(final_distance))
    print("Scale Factor:       {}".format(scale_factor))

    for lap in activity["Lap"]:
        lap["Calories"] = scale_value(lap["Calories"], scale_factor, True)
        lap["DistanceMeters"] = scale_value(lap["DistanceMeters"],
                                            scale_factor)
        lap["Extensions"]["ns3:LX"]["ns3:AvgSpeed"] = scale_value(
            lap["Extensions"]["ns3:LX"]["ns3:AvgSpeed"], scale_factor)
        lap["MaximumSpeed"] = scale_value(lap["MaximumSpeed"], scale_factor)

    for track_point in track_points:
        track_point["DistanceMeters"] = scale_value(
            track_point["DistanceMeters"], scale_factor)
        track_point["Extensions"]["ns3:TPX"]["ns3:Speed"] = scale_value(
            track_point["Extensions"]["ns3:TPX"]["ns3:Speed"], scale_factor)

    # Write the updated file.
    print("\nWriting output: {}".format(output_file))

    with open(output_file, "w") as ff:
        ff.write(xmltodict.unparse(doc, pretty=True).encode("utf-8"))

    return None


def parse_args():
    parser = argparse.ArgumentParser(
        description=("Update treadmill tcx files to reflect their proper "
                     "length."))
    parser.add_argument(
        "-i",
        "--input_file",
        dest="input_file",
        help="The .tcx file you'd like to update.",
        type=str)
    parser.add_argument(
        "-o",
        "--output_file",
        dest="output_file",
        help="The .tcx file to which you'd like to write your updated data.",
        type=str)
    parser.add_argument(
        "-d",
        "--distance",
        dest="distance",
        help="The total distance (in meters) as reported by the treadmill",
        type=float)

    args = parser.parse_args()
    return vars(args)


if __name__ == "__main__":
    sys.exit(treadmill_converter(**parse_args()))
