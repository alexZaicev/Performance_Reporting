# -*- coding: utf-8 -*-
"""
Created on Thu May  7 10:47:21 2020

@author: ID107354
"""

from fpdf import FPDF
import glob
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from pylab import title, savefig # figure, xlabel, ylabel, xticks, bar, legend, axis
import plotly.graph_objects as go
import unicodedata
import os
import pandas as pd
import math

from Measure import Measure
from Measure_data import Measure_data


# PDF format in mm. Equivalent to 11.69 * 16.53 inches
# Unit used in the code is mm (e.g. in cell()) 
pdf = FPDF('L', 'mm', (297, 420)) 
pdf.set_doc_option("core_fonts_encoding", "windows-1252")
pdf.set_auto_page_break(auto=False)

# matplotlib setting for good font quality on plots (non-fuzzy) 
plt.rcParams['figure.dpi'] = 210

# tentative to add other fonts (to display special characters). not working - abandonned
# pdf.add_font('calibril', '', "C:\Windows\Fonts\calibril.ttf", uni=False)
# TODO try HTML for DOT https://pyfpdf.readthedocs.io/en/latest/reference/write_html/index.html


# TODO change the TEST FILES with the real latest templates
# TODO if got more than one year data, when getting .measure.ATTRIBUTE elements, sort first and get head?
# TODO set a parameter that can easily be changed to display only last x months or x quarters or x years
# on the pdf report. do it per type of frequency (3 parameters?)

def main():
    
    dict_measure = {}
    
    # TEST FILES, not in the real PM OneDrive
    df_measure, df_measure_data = read_template("C:/Users/id107354/Documents/DSC Insight/1 - Quick Win Projects/Performance Management/PDF Generation/Test Files")    

    # get header names
    # print(df_measure.columns.values)
    
    # transform the loaded dataframes into objects and create dictionary dict_measure
    for idx, line in df_measure.iterrows():
        # print(line["Measure Title"])
        measure = Measure(line)
        # print(measure.measure_title)df_measure_data
        measure_data_df = df_measure_data[["Measure Id"] == measure.measure_id]
        # adds a YearMonth column to the dataframe format YYYYYYMM (like 20192001), which
        # is required for sorting bars in the main graph, used as an x_axis 
        measure_data_df.loc[:, "YearMonth"] = measure_data_df.loc[:, "Fiscal Year"].str.replace("-", "").str.cat(measure_data_df.loc[:, "Month"].str[1:3])
        measure_data_df.loc[:, "YearQuarter"] = measure_data_df.loc[:, "Fiscal Year"].str.replace("-", "").str.cat(measure_data_df.loc[:, "Quarter"].str[1:2])
        measure_data_df.loc[:, "Year"] = measure_data_df.loc[:, "Fiscal Year"].str.replace("-", "")

        # sort measure_data_df by Fiscal Year and Month before passing it to measure_data - most recent one on the top
        measure_data = Measure_data(measure_data_df.sort_values(by=["Fiscal Year", "Month"], ascending=False), measure)
        dict_measure[measure.measure_id] = measure_data
    
    # print(dict_measure["3_14"].data["YearMonth"])

    # measure(s) we don't want on the final report
    excluded_measures = ["3_03"]
    
    # measures_test = ["3_07"] # ["3_12", "3_10", "3_03", "3_14"]
    # "3_01", "3_04" are annually
    # "3_09", "3_14", "3_15" are Quarterly
    # "3_02", "3_06", "3_07", "3_08", "3_10", "3_11", "3_12", "3_13", "3_16" are Monthly
    
    lines = 2
    graphsperline = 3
    graph_width = 135
    graph_height = 118
    coords = (10, 30)
    graphs = 0

    for k in dict_measure.keys():
    # for i in range(len(measures_test)):
        
        # ignore measures we don't want
        if k in excluded_measures:
            print("Measure ", str(k), " ignored")
            continue

        graphs+=1
        if coords == (10, 30):
            pdf.add_page()
        
        # parameters: measure_id, x_left, y_top at the top left of the visual (origin)
        create_visual(dict_measure[k], coords[0], coords[1]) 
        print("Measure ", str(k), " processed")
        # create_visual(dict_measure[measures_test[i]], coords[0], coords[1]) 


        if graphs % graphsperline == 0:
            coords = (10, coords[1] + graph_height)
        else:
            coords = (coords[0] + graph_width, coords[1])
        if graphs % (graphsperline * lines) == 0:
            create_grid()
            coords = (10, 30)
        
 
    create_grid()
    export_pdf()
    


# loads data from templates
def read_template(parent_dir):
    parent_dir = parent_dir + "/*/*template.xlsx"
    df_measure = pd.DataFrame()
    df_measure_data = pd.DataFrame()
    for file in glob.iglob(parent_dir):
        print("Reading file ", str(file))
        file = file.replace("\\", "/")
        dict_template = pd.read_excel(file, sheet_name=["CurrentYearData", "CurrentYearMeasures"])
        df_measure = df_measure.append(dict_template["CurrentYearMeasures"])
        df_measure_data = df_measure_data.append(dict_template["CurrentYearData"])
    return df_measure, df_measure_data


# returns the latest month values and indexes (non blank and numerical) for the given frequency and attribute
def get_latest_values_per_given_frequency(frequency, frequency_numerical, m, attribute_name):
    latest_values = []
    latest_indexes = []
    for freq_num in frequency_numerical:
        df_one_freq = pd.DataFrame(m.data[m.data[frequency]==str(freq_num)], columns=[attribute_name])
        df_one_freq = pd.to_numeric(df_one_freq[attribute_name], errors="coerce").dropna()
        if df_one_freq.empty:
            latest_values.append(None)
        else:
            latest_values.append(df_one_freq.head(1).values[0])
            latest_indexes.append(df_one_freq.head(1).index.values[0])

    return latest_values, latest_indexes



# create and add the barchart to the pdf
def create_barchart(m):
    freq = m.measure.frequency
    
    fig, ax = plt.subplots()
    
    # handles percentages
    # TODO add contains() instead of ==
    if str(m.measure.data_format).upper() == "PERCENTAGE":
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    
    graph_title = m.measure.measure_title + " (ex " + m.measure.measure_ref_no + ")"
    title_size = 12
    # handles big size of text for the title
    # TODO create a function that divides the length by something and round it up to set it dynamically?
    if len(graph_title) > 100:
        title_size = 9
    # handle potential unwanted carriage returns
    title(graph_title.replace('\r', '').replace('\n', ''), fontsize=title_size, wrap = True)
    
    if freq.upper() in ["M", "MONTHLY", "MONTH"]:
        x_frequency = "YearMonth"
        x_numerical = list(map(int, m.data[x_frequency].values))
        x_ticklabels = m.data["Month"].str[6:9]
        y_target = list(map(float, pd.to_numeric(m.data["Target"], errors="coerce")))
    elif freq.upper() in ["Q", "QUARTERLY", "QUARTER"]:
        x_frequency = "YearQuarter"
        x_numerical = list(map(int, m.data[x_frequency].drop_duplicates().values))
        x_ticklabels = m.data["Quarter"].drop_duplicates()
        # gets the latest month value which is numeric not blank per quarter
        y_target = get_latest_values_per_given_frequency(x_frequency, x_numerical, m, "Target")[0]
    elif freq.upper() in ["A", "ANNUALLY", "ANNUAL", "YEARLY", "YEAR", "BI A", "BI ANNUAL", "BI ANNUALLY"]:
        x_frequency = "Year"
        x_numerical = list(map(int, m.data[x_frequency].drop_duplicates().values))
        x_ticklabels = m.data["Fiscal Year"].drop_duplicates()
        # gets the latest month value which is numeric not blank per year
        y_target = get_latest_values_per_given_frequency(x_frequency, x_numerical, m, "Target")[0]
    else:
        print("Frequency '" + freq + "' of measure " + str(m.measure.measure_id) + " not recognised. By default we assume it is monthly.")
        x_frequency = "YearMonth"
        x_numerical = list(map(int, m.data[x_frequency].values))
        x_ticklabels = m.data["Month"].str[6:9]
        y_target = list(map(float, pd.to_numeric(m.data["Target"], errors="coerce")))

    # print(x_numerical)
    # print(x_ticklabels)
    # print(pd.DataFrame(m.data, columns=["Target", "Result", "Quarter", "YearMonth", "YearQuarter", "Year"]))
        
    # Target line
    # TODO handle when there's one month target data on itself (e.g. March for 3_06): draw a line?
    # for now if there's only one month target data it does not show, it needs 2 points at least
    ax.plot(x_numerical, y_target, "k--", color = 'darkblue', zorder = 4)
    
    # Baseline line
    # TODO use .head(1) when several years of data and after sorting
    baseline = pd.to_numeric(m.measure.baseline, errors="coerce")
    # print("baseline " + str(baseline))
    ax.plot(x_numerical, [baseline] * len(x_numerical), color = 'brown', zorder = 4)
    
    # add a grid
    ax.grid(color = 'grey', which = 'major', axis = 'y', linestyle = '-', linewidth = 0.5, zorder = 0)
    
    # get the indexes related to the latest results
    result_indexes = get_latest_values_per_given_frequency(x_frequency, x_numerical, m, "Result")[1]
    # creates a dataframe from those indexes 
    df_latest_results = pd.DataFrame(m.data, index=result_indexes, columns=["Result", x_frequency, "Performance"])

    # Conditional formatting 'masks' and lists: one mask per colour (e.g is_perf_BLUE) and
    # two lists per colour (e.g. result_BLUE and month_BLUE)
    
    # True/False 'masks'
    # if no value is given in performance, "na=False" manages it
    is_perf_BLUE = df_latest_results["Performance"].str.upper().str.contains("BLUE", na=False)
    is_perf_GREEN = df_latest_results["Performance"].str.upper().str.contains("GREEN", na=False)
    is_perf_AMBER = df_latest_results["Performance"].str.upper().str.contains("AMBER", na=False)
    is_perf_RED = df_latest_results["Performance"].str.upper().str.contains("RED", na=False)
    is_perf_GREY = df_latest_results["Performance"].str.upper().str.contains("TREND", na=False)
    # handles if a performance other than BRAG is given (e.g. "Discontinued", or empty)
    is_perf_Not_BRAG = ~(is_perf_BLUE | is_perf_GREEN | is_perf_AMBER | is_perf_RED | is_perf_GREY)

    # print(is_perf_RED)
    # print(is_perf_Not_BRAG)

    # Based on the masks, retrieves the x and y values that are later given to display the bars 
    # Error handling: pd.to_numeric selects numeric values only and sets to nan if not numeric
    result_BLUE = list(map(float, pd.to_numeric(df_latest_results[is_perf_BLUE]["Result"], errors="coerce")))
    month_BLUE = list(map(float, df_latest_results[is_perf_BLUE][x_frequency].values))
    result_GREEN = list(map(float, pd.to_numeric(df_latest_results[is_perf_GREEN]["Result"], errors="coerce")))
    month_GREEN = list(map(float, df_latest_results[is_perf_GREEN][x_frequency].values))
    result_AMBER = list(map(float, pd.to_numeric(df_latest_results[is_perf_AMBER]["Result"], errors="coerce")))
    month_AMBER = list(map(float, df_latest_results[is_perf_AMBER][x_frequency].values))
    result_RED = list(map(float, pd.to_numeric(df_latest_results[is_perf_RED]["Result"], errors="coerce")))
    month_RED = list(map(float, df_latest_results[is_perf_RED][x_frequency].values))
    result_GREY = list(map(float, pd.to_numeric(df_latest_results[is_perf_GREY]["Result"].values)))
    month_GREY = list(map(float, df_latest_results[is_perf_GREY][x_frequency].values))
    result_Not_BRAG_GREY = list(map(float, pd.to_numeric(df_latest_results[is_perf_Not_BRAG]["Result"], errors="coerce")))
    month_Not_BRAG_GREY = list(map(float, df_latest_results[is_perf_Not_BRAG][x_frequency].values))
    
    # print(result_RED)
    # print(month_RED)
    
    # deal with bar width when there's just one value (typically annual measures)
    if len(x_numerical)==1 & ~(df_latest_results.empty):
        # print(int(df_latest_results[x_frequency].values[0]))
        ax.set_xlim(int(df_latest_results[x_frequency].values[0]) - 1, int(df_latest_results[x_frequency].values[0]) + 1)
       
    bar_width = 0.6
    
    # display the bars
    ax.bar(month_BLUE, result_BLUE, width=bar_width, color="blue", zorder=3)
    ax.bar(month_GREEN, result_GREEN, width=bar_width, color="#1DA237", zorder=3)
    ax.bar(month_AMBER, result_AMBER, width=bar_width, color="#FFBF00", zorder=3)
    ax.bar(month_RED, result_RED, width=bar_width, color="red", zorder=3)
    ax.bar(month_GREY, result_GREY, width=bar_width, color="grey", zorder=3)
    ax.bar(month_Not_BRAG_GREY, result_Not_BRAG_GREY, width=bar_width, color="grey", zorder=3)
    
    # set labels
    ax.set_xticks(x_numerical);
    ax.set_xticklabels(x_ticklabels, rotation = "horizontal");

    # save a unique image per measure id
    plot_path = "./image/" + str(m.measure.measure_id) + "_barchart.png"
    savefig(plot_path)
    # add the image to the pdf
    pdf.image(plot_path, x = None, y = None, w = 94, h = 0, type = '', link = '')
    
    
# create and add dial to the pdf
def create_dial(m):
    quartile_projection = pd.to_numeric(m.data["Quartile Projection"], errors="coerce").dropna()

    if quartile_projection.empty == False:
        quartile_projection = quartile_projection.head(1).values[0]
        pdf.set_font('arial', 'B', 8)
        pdf.cell(35, 6, 'Quartile Projection', 0, 2, 'C')
        pdf.set_font('arial', '', 7)
        pdf.cell(35, 3, 'Current actual against', 0, 2, 'C')
        pdf.cell(35, 3, 'national data available', 0, 2, 'C')
        fig = go.Figure(go.Indicator(
            mode = "gauge",
            value = 0,
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {
                'axis': {'range': [0, 100], 'visible': False},
                'bar': {'color': "darkblue"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 25], 'color': '#007BED'},
                    {'range': [25, 50], 'color': '#00AF33'},
                    {'range': [50, 75], 'color': '#FFBF00'},
                    {'range': [75, 100], 'color': '#FF0D00'}],
                'threshold': {
                    'line': {'color': "black", 'width': 10},
                    'thickness': 1,
                    'value': quartile_projection}}))
        
        # save a unique dial image per measure
        dial_path = "./image/" + str(m.measure.measure_id) + "_dial.png"
        fig.write_image(dial_path)
        
        # add the dial to the pdf
        pdf.image(dial_path, x = None, y = None, w = 35, h = 0, type = '', link = '')


# TODO handle the new DOT symbols (not in Test files but in actual files). watchout for the ~(dot in ["p", "q", "r", "s", "u"])
def add_dot_image(pref_dot, x, y):
    # print(pref_dot)
    if pref_dot == "p":
        pdf.image("./image/DOT/DOT_up-filled.PNG", x = x, y = y, w = 3, h = 0, type = '', link = '')        
    elif pref_dot == "q":
        pdf.image("./image/DOT/DOT_down-filled.PNG", x = x, y = y, w = 3, h = 0, type = '', link = '')
    elif pref_dot == "r":
        pdf.image("./image/DOT/DOT_up-empty.PNG", x = x, y = y, w = 3, h = 0, type = '', link = '')
    elif pref_dot == "s":
        pdf.image("./image/DOT/DOT_down-empty.PNG", x = x, y = y, w = 3, h = 0, type = '', link = '')
    elif pref_dot == "u":
        pdf.image("./image/DOT/DOT_right-filled.PNG", x = x, y = y, w = 3, h = 0, type = '', link = '')
    else:
        print("No direction of travel given or invalid value:" + str(pref_dot))

        
# deals with percentage and turns nan into N/A
# note that we are passing "" as data_format input parameter when we know the value is a string (e.g. Quartile)
# TODO handle encoding error for all fields displayed on pdf
def format_value(value, data_format):
    # print("value before formatting: ", str(value), ". data format: ", str(data_format))
    max_length = 14
    if str(value) == "nan":
        value = "N/A"
    # testing when a value is numeric or not
    if math.isnan(pd.to_numeric(value, errors="coerce")):
        # cuts the string if it's too long. Only keeps first max_length-3 characters
        if len(value)>max_length:
            print(str(value) + "too long. len=" + str(len(value)))
            value = str(value)[0:max_length-3] + ".."
        # print("value after formatting: ", str(value), ". data format: ", str(data_format))
        return value
    elif str(data_format).upper() == "PERCENTAGE":
        value = pd.to_numeric(value, errors="coerce")
        value = "{0:.2%}".format(value)
    # print("value after formatting: ", str(value), ". data format: ", str(data_format))
    return value


# create and add the visual (barchart, commentary, benchmark, current position, dial)
def create_visual(m, x_origin, y_origin):
    
    # initialisations
    pdf.set_xy(x_origin, y_origin)
    data_format = m.measure.data_format
    freq = m.measure.frequency
    
    # create and add the barchart to the pdf
    create_barchart(m)
    
    # Commentary (adding an empty row before it)
    # TODO display the month for which the commentary has been retrieved on the pdf?
    pdf.set_font('arial', '', 5.5)
    pdf.cell(0, 1, " ", 0, 2, 'C')
    commentary_step0 = m.data["Report Commentary"].dropna()
    commentary_step1 = str(commentary_step0.head(1).values[0]).replace("’", "'").replace("“", "\"").replace("”", "\"")
    commentary_step2 = unicodedata.normalize('NFKC', commentary_step1).encode('cp1252', 'replace').decode("utf-8", 'ignore')
    # TODO Limit the numbers of characters to be printed (or make the font smaller if so), otherwise it can overwrite and 
    # screw things up on elements below it, cf. test22.pdf
    pdf.multi_cell(93, 2.5, commentary_step2, 0, 'J')
    
    
    # Benchmark table
    pdf.set_xy(x_origin + 95, y_origin + 5)
    benchmark = m.data["Benchmark Result"].dropna()
    if benchmark.empty:
        national_average = "No benchmark"
        bham_at_benchmark = ""
        quartile = ""
        benchmark_year = ""
        benchmark_group = ""
    else:
        # get the index of the latest benchmark result (Nat. Ave.) we use to get the re-
        # lated benchmark info (Bham quartile position and year of benchmark data)
        index_benchmark = benchmark.head(1).index.values[0]
        national_average = format_value(m.data["Benchmark Result"][index_benchmark], data_format)
        bham_at_benchmark = format_value(m.data["Birmingham result at time of Benchmark"][index_benchmark], data_format)
        quartile = format_value(m.data["Birmingham Quartile position"][index_benchmark], "")
        benchmark_year = "benchmark " + str(format_value(m.data["Year of benchmark data"][index_benchmark], ""))
        benchmark_group = format_value(m.data["Benchmark Group for reporting purposes"][index_benchmark], "")

    pdf.set_font('arial', 'B', 8)
    pdf.cell(35, 6, 'Benchmark', 1, 2, 'C')

    pdf.set_font('arial', '', 7)
    pdf.cell(20, 6, '%s' % "Pref. DofT", border = 'L', ln = 0, align = 'C')
    
    # saving coordinates for inserting DOT image later on
    x_pref_DOT = pdf.get_x() + 6
    y_pref_DOT = pdf.get_y() + 1
    pdf.cell(15, 6, '%s' % " ", border = 'R', ln = 2, align = 'C')
    pdf.cell(-20)
    
    pdf.cell(20, 6, '%s' % "Nat. Ave.", border = 'L', ln = 0, align = 'C')
    pdf.cell(15, 6, '%s' % str(national_average), border = 'R', ln = 2, align = 'C')
    pdf.cell(-20)
    
    pdf.cell(20, 6, '%s' % "Bham", border = 'L', ln = 0, align = 'C')
    pdf.cell(15, 6, '%s' % str(bham_at_benchmark), border = 'R', ln = 2, align = 'C')
    pdf.cell(-20)
    
    pdf.cell(20, 6, '%s' % "Quartile", border = 'L', ln = 0, align = 'C')
    pdf.set_fill_color(r = 255, g = 255, b = 255)
    if "4TH" in quartile.upper():
        pdf.set_fill_color(r = 255, g = 0, b = 0)
    elif "3RD" in quartile.upper():
        pdf.set_fill_color(r = 255, g = 153, b = 51)
    elif "2ND" in quartile.upper():
        pdf.set_fill_color(r = 0, g = 255, b = 0)
    elif "1ST" in quartile.upper():
        pdf.set_fill_color(r = 0, g = 128, b = 255)
    # if quartile position is N/A, python reads it as nan, but we don't want to display nan
    elif quartile=="nan":
        quartile="N/A"
    # else:
    #    print("No quartile position or invalid value")

    pdf.cell(15, 6, '%s' % str(quartile), border = 'R', ln = 2, align = 'C', fill=True)
    pdf.cell(-20)
    
    # benchmark year and group        
    pdf.set_font('arial', '', 6)
    pdf.cell(35, 5, '%s' % str(benchmark_year + " " + benchmark_group), ln = 2, border = 'LRB', align = 'C')

    # empty row between benchmark and current position
    pdf.cell(35, 5, " ", ln = 2, align = 'C')
    
    # Current Position table
    # TODO print the month for which we get the current position values somewhere?
    current_position = m.data["Result"].dropna()
    if (current_position.empty):
        dot = ""
        result = ""
        target = ""
    else: 
        # get the index of the latest result we use to get the related current
        # position info (dot, result, target)
        index_current_position = current_position.head(1).index.values[0]
        result = format_value(m.data["Result"][index_current_position], data_format)
        target = format_value(m.data["Target"][index_current_position], data_format)
        
        # handle looking for different DOT columns depending on the frequency
        # TODO add the "ANNUAL" and "QUARTERLY" and other cases (like in create_barchart() function)
        dot = format_value(m.data["DOT from previous month"][index_current_position], "")
        if (str(freq).upper() == "A") | (str(freq).upper() == "BI A"):
            dot = format_value(m.data["DOT from same period last year"][index_current_position], "")
        elif str(freq).upper() == "Q":
            dot = format_value(m.data["DOT from previous quarter"][index_current_position], "")      
    
    pdf.set_font('arial', 'B', 8)
    pdf.cell(35, 6, 'Current Position', 1, 2, 'C')
    pdf.set_font('arial', '', 7)
    
    pdf.cell(20, 6, '%s' % "DofT", border = 'L', ln = 0, align = 'C')
    # save coordinates for inserting DOT image later on
    x_DOT = pdf.get_x() + 6
    y_DOT = pdf.get_y() + 1
    # handle when DOT is a text other than the classic characters
    text_dot = " "
    if ~(dot in ["p", "q", "r", "s", "u"]):
        text_dot = dot
    pdf.cell(15, 6, '%s' % text_dot, border = 'R', ln = 2, align = 'C')
    pdf.cell(-20)
    
    # highlight Actual in yellow when data is provisional
    pdf.set_fill_color(r = 255, g = 255, b = 0)
    fill_bool = str(m.data["Status (Provisional / Confirmed)"][index_current_position]).upper() == "PROVISIONAL"
    pdf.cell(20, 6, '%s' % "Actual", border = 'L', ln = 0, align = 'C')
    pdf.cell(15, 6, '%s' % str(result), border = 'R', ln = 2, align = 'C', fill = fill_bool)
    pdf.cell(-20)
    
    pdf.cell(20, 6, '%s' % "Target", border = 'L', ln = 0, align = 'C')
    pdf.cell(15, 6, '%s' % str(target), border = 'R', ln = 2, align = 'C')
    pdf.cell(-20)
    
    pdf.cell(20, 6, '%s' % "Baseline", border = 'LB', ln = 0, align = 'C')
    baseline = format_value(m.measure.baseline, data_format)
    pdf.cell(15, 6, '%s' % str(baseline), border = 'RB', ln = 2, align = 'C')
    pdf.cell(-20)
    
    # empty row between Current Position table and Quartile projection
    pdf.cell(35, 3, " ", ln = 2, align = 'C')
    
    # Dial for Quartile Projection
    # TODO add the month somewhere for which the quartile projection is for?
    create_dial(m)
    
    # Adding the direction of travel images (cannot do it earlier because would create an empty row)
    # preferred direction of travel in Benchmark table
    pref_dot = m.measure.pref_dot
    add_dot_image(pref_dot, x_pref_DOT, y_pref_DOT)
    
    # direction of travel in Current Position table
    add_dot_image(dot, x_DOT, y_DOT)

# The Grid
def create_grid():
    pdf.set_xy(10, 30)
    pdf.set_font('arial', 'B', 8)
    pdf.cell(135, 118, '', 1, 0, '')
    pdf.cell(135, 118, '', 1, 0, '')
    pdf.cell(135, 118, '', 1, 2, '')
    pdf.cell(-270)
    pdf.cell(135, 118, '', 1, 0, '')
    pdf.cell(135, 118, '', 1, 0, '')
    pdf.cell(135, 118, '', 1, 2, '')


# Output
def export_pdf():
    output_name = 'test47.pdf'
    pdf.output(output_name, 'F')
    os.startfile(output_name)


if __name__=="__main__":
    main()
