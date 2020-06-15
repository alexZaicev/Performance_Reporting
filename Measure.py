# -*- coding: utf-8 -*-
"""
Created on Mon May 11 10:51:32 2020

@author: ID107354
"""

class Measure:
    
    def __init__(self, df_measure):
        self.fiscal_year = df_measure["Fiscal Year"]
        self.measure_id = df_measure["Measure Id"]
        self.measure_ref_no = df_measure["Measure Ref No"]
        self.outcome = df_measure["Outcome"]
        self.priority = df_measure["Priority"]
        self.measure_title = df_measure["Measure Title"]
        self.measure_description = df_measure["Measure Description"]
        self.additional_kpi_information = df_measure["Additional KPI Information "]
        self.new_existing = df_measure["New / Existing"]
        self.pref_dot = df_measure["Preferred direction of travel"]
        self.aim = df_measure["Aim"]
        self.frequency = df_measure["Frequency\nMonthly\nQuarterly\n1/2 Yearly\nAnnual  "]
        self.data_format = df_measure["Data Format"]
        self.data_presented = df_measure["Data presented"]
        self.baseline = df_measure["Baseline "]
        self.tolerance = df_measure["Tolerances"]
        self.directorate = df_measure["Directorate"]
        self.cabinet_member_portfolio = df_measure["Cabinet Member Portfolio"]
        self.corporate_director = df_measure["Corporate Director"]
        self.responsible_officer = df_measure["Responsible Officer"]
        self.measure_owner = df_measure["Measure \nOwner"]
        self.data_source = df_measure["Data Source"]
        self.expected_availability = df_measure["Expected date/ month availability"]
        self.final_dqaf_received = df_measure["Final DQAF received"]
        self.outcome_no = df_measure["Outcome No"]
        self.outcome_priority_no = df_measure["Outcome Priority No"]
        self.theme = df_measure["Theme"]
        self.theme_priority_no = df_measure["Theme Priority No"]
