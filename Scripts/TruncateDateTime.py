# Name: TruncateDateTime.py
# Purpose: Will take a selected datetime field and will truncate it to chosen values for each of the chosen sub dates.
# Author: David Wasserman
# Last Modified: 7/4/2016
# Copyright: David Wasserman
# Python Version:   2.7-3.1
# ArcGIS Version: 10.4 (Pro)
# --------------------------------
# Copyright 2016 David J. Wasserman
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# --------------------------------
# Import Modules
import os, arcpy, datetime
import numpy as np
import pandas as pd

# Define Inputs
FeatureClass = arcpy.GetParameterAsText(0)
InputField = arcpy.GetParameterAsText(1)
NewTextFieldName = arcpy.GetParameterAsText(2)
SetYear = arcpy.GetParameter(3)
SetMonth = arcpy.GetParameter(4)
SetDay = arcpy.GetParameter(5)
SetHour = arcpy.GetParameter(6)
SetMinute = arcpy.GetParameter(7)
SetSecond = arcpy.GetParameter(8)


# Function Definitions
def funcReport(function=None, reportBool=False):
    """This decorator function is designed to be used as a wrapper with other functions to enable basic try and except
     reporting (if function fails it will report the name of the function that failed and its arguments. If a report
      boolean is true the function will report inputs and outputs of a function.-David Wasserman"""

    def funcReport_Decorator(function):
        def funcWrapper(*args, **kwargs):
            try:
                funcResult = function(*args, **kwargs)
                if reportBool:
                    print("Function:{0}".format(str(function.__name__)))
                    print("     Input(s):{0}".format(str(args)))
                    print("     Ouput(s):{0}".format(str(funcResult)))
                return funcResult
            except Exception as e:
                print(
                    "{0} - function failed -|- Function arguments were:{1}.".format(str(function.__name__), str(args)))
                print(e.args[0])

        return funcWrapper

    if not function:  # User passed in a bool argument
        def waiting_for_function(function):
            return funcReport_Decorator(function)

        return waiting_for_function
    else:
        return funcReport_Decorator(function)


def functionTime(function=None, reportTime=True):
    """ If a report time boolean is true, it will print the datetime before and after function run. Includes
    import with a rare namespace.-David Wasserman"""

    def funcReport_Decorator(function):
        def funcWrapper(*args, **kwargs):
            if reportTime:
                try:
                    # from datetime import datetime as functionDateTime_nsx978 #Optional, but removed
                    print("{0} Function Start:{1}".format(str(function.__name__), str(datetime.datetime.now())))
                except:
                    pass
            funcResult = function(*args, **kwargs)
            if reportTime:
                try:
                    print("{0} Function End:{1}".format(str(function.__name__), str(datetime.datetime.now())))
                except:
                    pass
            return funcResult

        return funcWrapper

    if not function:  # User passed in a bool argument
        def waiting_for_function(function):
            return funcReport_Decorator(function)

        return waiting_for_function
    else:
        return funcReport_Decorator(function)


def arcToolReport(function=None, arcToolMessageBool=False, arcProgressorBool=False):
    """This decorator function is designed to be used as a wrapper with other GIS functions to enable basic try and except
     reporting (if function fails it will report the name of the function that failed and its arguments. If a report
      boolean is true the function will report inputs and outputs of a function.-David Wasserman"""

    def arcToolReport_Decorator(function):
        def funcWrapper(*args, **kwargs):
            try:
                funcResult = function(*args, **kwargs)
                if arcToolMessageBool:
                    arcpy.AddMessage("Function:{0}".format(str(function.__name__)))
                    arcpy.AddMessage("     Input(s):{0}".format(str(args)))
                    arcpy.AddMessage("     Ouput(s):{0}".format(str(funcResult)))
                if arcProgressorBool:
                    arcpy.SetProgressorLabel("Function:{0}".format(str(function.__name__)))
                    arcpy.SetProgressorLabel("     Input(s):{0}".format(str(args)))
                    arcpy.SetProgressorLabel("     Ouput(s):{0}".format(str(funcResult)))
                return funcResult
            except Exception as e:
                arcpy.AddMessage(
                        "{0} - function failed -|- Function arguments were:{1}.".format(str(function.__name__),
                                                                                        str(args)))
                print(
                    "{0} - function failed -|- Function arguments were:{1}.".format(str(function.__name__), str(args)))
                print(e.args[0])

        return funcWrapper

    if not function:  # User passed in a bool argument
        def waiting_for_function(function):
            return arcToolReport_Decorator(function)

        return waiting_for_function
    else:
        return arcToolReport_Decorator(function)


def arcPrint(string, progressor_Bool=False):
    try:
        if progressor_Bool:
            arcpy.SetProgressorLabel(string)
            arcpy.AddMessage(string)
            print(string)
        else:
            arcpy.AddMessage(string)
            print(string)
    except arcpy.ExecuteError:
        arcpy.GetMessages(2)
        pass
    except:
        arcpy.AddMessage("Could not create message, bad arguments.")
        pass


@arcToolReport()
def FieldExist(featureclass, fieldname):
    """ArcFunction
     Check if a field in a feature class field exists and return true it does, false if not.- David Wasserman"""
    fieldList = arcpy.ListFields(featureclass, fieldname)
    fieldCount = len(fieldList)
    if (fieldCount >= 1):  # If there is one or more of this field return true
        return True
    else:
        return False


@arcToolReport
def AddNewField(in_table, field_name, field_type, field_precision="#", field_scale="#", field_length="#",
                field_alias="#", field_is_nullable="#", field_is_required="#", field_domain="#"):
    """ArcFunction
    Add a new field if it currently does not exist. Add field alone is slower than checking first.- David Wasserman"""
    if FieldExist(in_table, field_name):
        print(field_name + " Exists")
        arcpy.AddMessage(field_name + " Exists")
    else:
        print("Adding " + field_name)
        arcpy.AddMessage("Adding " + field_name)
        arcpy.AddField_management(in_table, field_name, field_type, field_precision, field_scale,
                                  field_length,
                                  field_alias,
                                  field_is_nullable, field_is_required, field_domain)


@arcToolReport
def CreateUniqueFieldName(field_name, in_table):
    """This function will be used to create a unique field name for an ArcGIS field by adding a number to the end.
    If the file has field character limitations, the new field name will not be validated.- DJW."""
    counter = 1
    new_field_name = field_name
    arcPrint(new_field_name)
    while FieldExist(in_table, new_field_name) and counter <= 1000:
        print(field_name + " Exists, creating new name with counter {0}".format(counter))
        new_field_name = "{0}_{1}".format(str(field_name), str(counter))
        counter += 1
    return new_field_name


@arcToolReport
def ArcGISTabletoDataFrame(in_fc, input_Fields):
    """Function will convert an arcgis table into a pandas dataframe with an object ID index, and the selected
    input fields."""
    OIDFieldName = arcpy.Describe(in_fc).OIDFieldName
    final_Fields = [OIDFieldName] + input_Fields
    arcPrint("Converting feature class table to numpy array.", True)
    npArray = arcpy.da.TableToNumPyArray(in_fc, final_Fields)
    objectIDIndex = npArray[OIDFieldName]
    arcPrint("Converting feature class numpy array into pandas dataframe.", True)
    fcDataFrame = pd.DataFrame(npArray, index=objectIDIndex, columns=input_Fields)
    return fcDataFrame

@arcToolReport
def IfValueTargetReturnAlt(value, alternative, target=None):
    """If value is none/falsy (depending on parameters), return alternative."""
    if value is not target or value != target:
        return value
    else:
        return alternative

@arcToolReport
def assign_new_datetime(datetime_obj, year, month, day, hour, minute, second, original_dt_target=-1):
    """Will assign a new date time within an apply function based on the type of object present. Starts with asking
    for forgiveness rather than permission to get original object properties, then uses isinstance to the appropriate
    datetime object to return."""
    try:
        new_year=IfValueTargetReturnAlt(year, datetime_obj.year, original_dt_target)
        new_month=IfValueTargetReturnAlt(month, datetime_obj.month, original_dt_target)
        new_day=IfValueTargetReturnAlt(day, datetime_obj.day, original_dt_target)
    except:
        pass
    try:
        new_hour=IfValueTargetReturnAlt(hour, datetime_obj.hour, original_dt_target)
        new_minute=IfValueTargetReturnAlt(minute, datetime_obj.minute, original_dt_target)
        new_second=IfValueTargetReturnAlt(second, datetime_obj.second, original_dt_target)
    except:
        pass
    if isinstance(datetime_obj,datetime.datetime):
        return datetime.datetime(year=new_year, month=new_month, day=new_day, hour=new_hour, minute=new_minute, second=new_second)
    elif isinstance(datetime_obj,datetime.date):
        return datetime.date(year=new_year, month=new_month, day=new_day)
    else:
        return datetime.time(hour=new_hour, minute=new_minute, second=new_second)


@functionTime(reportTime=False)
def truncate_date_time(in_fc, input_field, new_field_name, set_year=None, set_month=None, set_day=None, set_hour=None,
                       set_minute=None, set_second=None):
    """ This function will take in an feature class, and use pandas/numpy to truncate a date time so that the
     passed date-time attributes are set to a target."""
    try:
        # arcPrint(pd.__version__) Does not have dt lib.
        arcpy.env.overwriteOutput = True
        workspace = os.path.dirname(in_fc)
        col_new_field = arcpy.ValidateFieldName(CreateUniqueFieldName(new_field_name, in_fc), workspace)
        AddNewField(in_fc, col_new_field, "DATE")
        OIDFieldName = arcpy.Describe(in_fc).OIDFieldName
        arcPrint("Creating Pandas Dataframe from input table.")
        fcDataFrame = ArcGISTabletoDataFrame(in_fc, [input_field, col_new_field])
        JoinField = arcpy.ValidateFieldName("DFIndexJoin", workspace)
        fcDataFrame[JoinField] = fcDataFrame.index
        try:
            arcPrint("Creating new date-time column based on field {0}.".format(str(input_field)), True)
            fcDataFrame[col_new_field]=fcDataFrame[input_field].apply(
                lambda dt: assign_new_datetime(dt,set_year,set_month,set_day,set_hour,set_minute,set_second)).astype(datetime.datetime)
            del fcDataFrame[input_field]
        except Exception as e:
            del fcDataFrame[input_field]
            arcPrint(
                    "Could not process datetime field. "
                    "Check that datetime is a year appropriate to your python version and that "
                    "the time format string is appropriate.")
            arcPrint(e.args[0])
            pass

        arcPrint("Exporting new time field dataframe to structured numpy array.", True)
        finalStandardArray = fcDataFrame.to_records()
        arcPrint("Joining new time string field to feature class.", True)
        arcpy.da.ExtendTable(in_fc, OIDFieldName, finalStandardArray, JoinField, append_only=False)
        arcPrint("Delete temporary intermediates.")
        del fcDataFrame, finalStandardArray
        arcPrint("Script Completed Successfully.", True)

    except arcpy.ExecuteError:
        arcPrint(arcpy.GetMessages(2))
    except Exception as e:
        arcPrint(e.args[0])

        # End do_analysis function


# This test allows the script to be used from the operating
# system command prompt (stand-alone), in a Python IDE,
# as a geoprocessing script tool, or as a module imported in
# another script
if __name__ == '__main__':
    truncate_date_time(FeatureClass, InputField, NewTextFieldName, SetYear, SetMonth, SetDay, SetHour, SetMinute,
                          SetSecond)