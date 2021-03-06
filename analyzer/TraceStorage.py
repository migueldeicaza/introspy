#!/usr/bin/env python
import os
import sqlite3
import json
from TracedCall import TracedCall, TracedCallJSONEncoder

class TraceStorage:
    """ Object representation of an introspy database """

    def __init__(self, db):
        self.calls = []
        conn = None

        try:
            conn = sqlite3.connect(db)
            conndb = conn.cursor()
            conndb.execute("SELECT * FROM tracedCalls")
            rowid = 1
            for row in conndb:
                self.calls.append(TracedCall(rowid, row[0], row[1], row[2]))
                rowid += 1
        except sqlite3.Error as e:
            print "Fatal error: %s" % e
            raise
        finally:
            if conn:
                conn.close()

    def get_traced_calls(self, group=None, subgroup=None):
        if group == None:
            return self.calls
        return self.filter_traced_calls(group, subgroup)

    def filter_traced_calls(self, group, subgroup):
        filt_calls = []
        for call in self.calls:
            if call.group.lower() == group.lower():
                    filt_calls.append(call)
        if subgroup == None:
            return filt_calls
        filtered_calls = []
        for call in filt_calls:
            if call.subgroup.lower() == subgroup.lower():
                filtered_calls.append(call)
        return filtered_calls

    def write_to_JS_file(self, fileDir, fileName='tracedCalls.js'):
        # Convert the list of traced calls to a JS var declaration
        tracedCalls_dict = {}
        tracedCalls_dict['calls'] =  self.calls
        try:
            tracedCalls_json = json.dumps(tracedCalls_dict, cls=TracedCallJSONEncoder)
        except TypeError as e:
            print e
            raise
        JS_data = 'var tracedCalls = ' + tracedCalls_json + ';'

        # Write the result to a file
        JS_filePath = os.path.join(fileDir, fileName)
        JS_file = open(JS_filePath, 'w')
        JS_file.write(JS_data)
