#!/usr/bin/env python

import json
import logging
import os
import sys
import time
import datetime

import numpy


def get_json(filepath, log):
    """
    Reads a JSON file, returns None on ValueError
    and if not a file.
    """
    parsed_json = None

    # See if it is a file and not a directory or something else
    if not os.path.isfile(file_path):
        log.warning("%s is not a file! Skipping", file_path)
        return parsed_json

    try:
        with open(filepath, "rb") as fp:
            parsed_json = json.loads(fp.read())

    except ValueError as e:
        log.error("Error reading JSON file %s. Error: %s",
                  filepath, e)

    return parsed_json


def setup_logger():
    """"
    Sets up the logger. 
    """
    logformat = "[%(asctime)s %(levelname)s] %(message)s"
    dateformat = "%d-%m-%y %H:%M:%S"
    logger = logging.getLogger("extraction")
    formatter = logging.Formatter(logformat)
    formatter.datefmt = dateformat
    fh = logging.FileHandler("dataextraction.log", mode="a")
    fh.setFormatter(formatter)
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    logger.addHandler(fh)
    logger.addHandler(sh)
    logger.propagate = False


if __name__ == "__main__":

    setup_logger()
    log = logging.getLogger("extraction")

    # Add path to reports here
    DATASET_DIR = "/home/kate/thesis/reports"

    # Location where data will be stored. This should be a directory, not a filename.
    # The filename will be generated using a timestamp. Format: data-timestamp.npy
    NUMPY_DATA_SAVE = "/home/kate/thesis"

    if len(sys.argv) > 1:
        min_calls = int(sys.argv[1])
        log.info("-----> | Using only reports with a minimum of %s calls | <-----", min_calls)
    else:
        min_calls = 1
        log.info("-----> | Using only reports with a minimum of 1 call | <-----")

    ignore_list = []


    success_apis, fail_apis, return_codes = [], [], []
    sample_num = 0

    # Fill the lists with calls
    for sample in os.listdir(DATASET_DIR):

        file_path = os.path.join(DATASET_DIR, sample)

        try:
            # Load JSON file
            log.info("Reading file: %s", file_path)
            parsed_json = get_json(file_path, log)

            if parsed_json is None:
                log.warning("Parsed JSON was None. Skipping %s", file_path)
                continue

            # Check the number of API calls
            total = 0
            for proc in parsed_json["behavior"]["processes"]:

                total += len(proc["calls"])
            if total < min_calls:
                log.warning("Sample %s is less than %s calls. Skipping..",
                            file_path, min_calls)
                ignore_list.append(file_path)
                continue

            # Successfully loaded, increment number
            sample_num += 1
            for n in parsed_json["behavior"]["processes"]:

                for k in n["calls"]:
                    call = k["api"]
                    if k["status"] == 1:
                        if call not in success_apis:
                            success_apis.append(call)

                    elif call not in fail_apis:
                        fail_apis.append(call)

                    if k["return_value"] not in return_codes:
                        return_codes.append(k["return_value"])

        except MemoryError as e:
            log.error("Error! %s", e)
            sys.exit(1)

    log.info("Success APIs: %s", len(success_apis))
    log.info("Fail APIs: %s", len(fail_apis))
    log.info("Return codes: %s", len(return_codes))

    data_length = len(success_apis) + len(fail_apis) + len(return_codes) + 1

    # Create the matrix using the calculated length of all lists
    matrix = numpy.zeros((sample_num, data_length))
    matrix_scores = numpy.zeros((sample_num, 3))

    log.info("Data length: %s", data_length)

    ids = 0

    try:
        for sample in os.listdir(DATASET_DIR):

            file_path = os.path.join(DATASET_DIR, sample)

            if file_path in ignore_list:
                continue

            # Load JSON file again
            log.info("Reading file %s", file_path)
            parsed_json = get_json(file_path, log)

            if parsed_json is None:
                log.warning("Parsed JSON was None. Skipping %s", file_path)
                continue

            log.info("Handling all calls for file %s", file_path)

            for process in parsed_json["behavior"]["processes"]:

                for call in process["calls"]:

                    status = call["status"]
                    api = call["api"]
                    returncode = call["return_value"]

                    if status:
                        # Store successful call in matrix
                        index = success_apis.index(api)
                        matrix[ids][index] += 1
                    else:
                        # Store failed call in matrix
                        offset = len(success_apis)
                        index = offset + fail_apis.index(api)
                        matrix[ids][index] += 1

                    # Store return code in matrix
                    offset = len(success_apis) + len(fail_apis)
                    index = offset + return_codes.index(returncode)
                    matrix[ids][index] += 1
			
			
            if sample.split( "-" )[0] == "benign":
		matrix[ids][data_length-1] = 1
                matrix_scores[ids][2] = 1
	    elif sample.split( "-" )[0] == "dridex":
                matrix[ids][data_length-1] = 2
                matrix_scores[ids][2] = 2
            elif sample.split( "-" )[0] == "locky":
		matrix[ids][data_length-1] = 3
                matrix_scores[ids][2] = 3
            elif sample.split( "-" )[0] == "teslacrypt":
                matrix[ids][data_length-1] = 4
                matrix_scores[ids][2] = 4
            elif sample.split( "-" )[0] == "vawtrak":
                matrix[ids][data_length-1] = 5
                matrix_scores[ids][2] = 5
            elif sample.split( "-" )[0] == "zeus":
                matrix[ids][data_length-1] = 6
                matrix_scores[ids][2] = 6
            elif sample.split( "-" )[0] == "darkcomet":
                matrix[ids][data_length-1] = 7
                matrix_scores[ids][2] = 7
            elif sample.split( "-" )[0] == "cybergate":
                matrix[ids][data_length-1] = 8
                matrix_scores[ids][2] = 8
            elif sample.split( "-" )[0] == "xtreme":
                matrix[ids][data_length-1] = 9
                matrix_scores[ids][2] = 9
            elif sample.split( "-" )[0] == "ctblocker":
                matrix[ids][data_length-1] = 10
                matrix_scores[ids][2] = 10
                
				
            matrix_scores[ids][0] = sample.split(".")[0].split( "-" )[1]
            matrix_scores[ids][1] = parsed_json["info"]["score"]
			

            ids += 1

    finally:
        date_time = time.time()
        dt_stamp = datetime.datetime.fromtimestamp(time.time()).strftime(
            "%d-%m-%Y_%H-%M-%S")
        filename = "data-%s.csv" % dt_stamp
        file_scores = "scores-%s.csv" % dt_stamp
        try:
            path = os.path.join(NUMPY_DATA_SAVE, filename)
            path_scores = os.path.join(NUMPY_DATA_SAVE, file_scores)
            log.info("Storing numpy data in at %s", path)
            numpy.savetxt(path, matrix, delimiter=",")
            numpy.savetxt(path_scores, matrix_scores, delimiter="," )
        except Exception as e:
            path = os.path.join(os.path.dirname(os.path.realpath(__file__)), filename)
            path_scores = os.path.join(os.path.dirname(os.path.realpath(__file__)), file_scores)
            log.error("Error writing numpy data! Trying script directory %s",
                      path)
            numpy.savetxt(path, matrix, delimiter=",")
            numpy.savetxt(path_scores, matrix_scores, delimiter="," )

