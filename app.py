import dash
from dash import html
from dash import dcc
from dash.dependencies import State,Output,Input
from dash import dash_table
import pandas as pd
import plotly.graph_objs as go
from datetime import date


app = dash.Dash(__name__)


# ZMIANA:
# Żeby szybciej się ładowało 

# df = pd.read_csv("crimes.csv")
# df["hour"] = df["Time"].str[0:2]
# df["hour"] = df["hour"].astype("int")
# df["Date"] = pd.to_datetime(df["Date"])
# df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
# df["Date"] = pd.to_datetime(df["Date"])

df = pd.read_csv("crimes.csv", parse_dates=['Date'])
df["hour"] = df.Time.str[0:2].astype("int")
df["Date"] = df.Date.dt.date

df_temp = df.copy()

DayOfWeek = df_temp["DayOfWeek"].unique()
crime_category = df_temp["Category"].unique()

# ZMIANA:
# Żeby PdDistrict nie miał wartości null, nan

# PdDistrict = df["PdDistrict"].unique()

PdDistrict = df_temp.loc[~df_temp.PdDistrict.isna()]["PdDistrict"].unique()


app.layout = html.Div(
    id='container',
    children=[
        
        html.Div(
            id='submit_button_div',
            children=[
                
                html.P(),
            
                html.Button(
                    id = "submit-button",
                    n_clicks = 0,
                    children = "Submit here",
                    style = {
                        "fontSize": 12
                    }
                )
        ]),


        html.Div(
            id='date_range_div',
            children=[
            
                html.H3("Select date range"),
            
                html.P(),
            
                dcc.DatePickerRange(
                    id='my-date-picker-range',
                    min_date_allowed=date(2016, 1, 1),
                    max_date_allowed=date(2016, 12, 31),
                    initial_visible_month=date(2016, 1, 1),
                    start_date = date(2016,1,1),
                    end_date=date(2016, 12, 31),
                    display_format = "YYYY-MM-DD"
            )], 
            style = {
                "float":"left"
            }
        ),


        html.Div(
            id='time_range_div',
            children=[
             
                html.P(),
             
                html.H3("Select time range"),
                
                dcc.RangeSlider(
                    id = "range-slider",
                    min = 0,
                    max = 23,
                    marks = {i : str(i) for i in range(0,24)},
                    value = [0,23]
                )
             ], 
             style = {
                "width": "25%",
                "float":"left"
                }
            ),



        html.Div(
            id='select_day_div',
            children=[
             
                html.P(),
                html.H3("Select day"),
                dcc.Dropdown(
                    id = "Days",
                    options = [{"label":i, "value":i} for i in DayOfWeek],
                    value = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
                    multi = True)
            ],
            style = {
                "width": "25%",
                "float":"left"
                }
            ),


        html.Div(
            id='select_category_div',
            children=[
                
                html.P(),
                html.H3("Select crime category"),
                dcc.Dropdown(
                    id = "crime_category",
                    options = [{"label":i, "value":i} for i in crime_category],
                    value = ["WEAPON LAWS","ASSAULT"],
                    multi = True)
            ],
            style = {
                "width": "25%",
                "float":"left"
                }
            ),

            html.Div([],style = {"clear":"both"}),


        html.Div(
            id='select_district_div',
            children=[
                
                html.P(),
                html.H3("Select district"),
                dcc.Dropdown(
                    id = "districts",
                    options = [{"label":i, "value":i} for i in PdDistrict],
                    value = PdDistrict,
                    multi = True)
                ],
                style = {"width":"25%"}
            ),

             html.P(),

             html.Div(
                id='download_button_div',
                children=[

                    html.Button("Download CSV", 
                        id="btn-csv"),
                    dcc.Download(id="download-dataframe-csv"),

                ]),

            html.P(),
            dcc.Tabs([

                dcc.Tab(
                    label="Dashboard",
                    children=[
                        
                        html.Div([
                            dcc.Graph(
                                id="barplot")],
                            style = {
                                "display": "inline-block", 
                                "width":"70%"
                                }
                            )

                       ]),


                dcc.Tab(
                    label="Table",
                    children=[
                        
                        html.H3("Data"),
                        html.P(),
                        html.Div(
                            id = "table-container"
                            )
                        ])




                ])

    ])

@app.callback(Output("barplot","figure"),
              Input("submit-button","n_clicks"),
              [State("my-date-picker-range","start_date"),
              State("my-date-picker-range","end_date"),
              State("range-slider","value"),
              State("Days","value"),
              State("crime_category","value"),
              State("districts","value")])

def bar_plot(n_clicks, start_date, end_date, value, days, crimes, distr):

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    df_barplot = df.loc[(df["Date"] >= start_date) & (df["Date"] <= end_date)]
    df_barplot = df_barplot.loc[(df_barplot["hour"] >= value[0]) & (df_barplot["hour"] <= value[1])]
    df_barplot = df_barplot.loc[df_barplot["DayOfWeek"].isin(days)]
    df_barplot = df_barplot.loc[df_barplot["Category"].isin(crimes)]
    df_barplot = df_barplot.loc[df_barplot["PdDistrict"].isin(distr)]

    df_barplot = df_barplot.groupby("hour").agg({"Time":"count"}).reset_index()

    data = [go.Bar(
        x=df_barplot["hour"],
        y=df_barplot["Time"],
        text=df_barplot["Time"])]
    
    layout=go.Layout(
        title="Crimes divided into hours",
        xaxis_title="Hours",
        yaxis_title="Number of cases",
        hovermode=False,
        xaxis=dict{
            "dtick": 1
            }
        )

    return {"data": data, "layout": layout}


@app.callback(Output("table-container","children"),
              Input("submit-button","n_clicks"),
              [State("my-date-picker-range","start_date"),
              State("my-date-picker-range","end_date"),
              State("range-slider","value"),
              State("Days","value"),
              State("crime_category","value"),
              State("districts","value")])
def table_filtering(n_clicks,start_date,end_date,value,days, crimes, distr):

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    df_table = df.loc[(df["Date"] >= start_date) & (df["Date"] <= end_date)]
    df_table["Date"] = df_table["Date"].dt.strftime("%Y-%m-%d")
    df_table = df_table.loc[(df_table["hour"] >= value[0]) & (df_table["hour"] <= value[1])]
    df_table = df_table.loc[df_table["DayOfWeek"].isin(days)]
    df_table = df_table.loc[df_table["Category"].isin(crimes)]
    df_table = df_table.loc[df_table["PdDistrict"].isin(distr)]


    table = dash_table.DataTable(id='table',
                        columns=[{"name": i, "id": i} for i in df_table.columns],
                        data=df_table.to_dict('records'), page_size = 25)

    return table

@app.callback(
    Output("download-dataframe-csv", "data"),
    # ZMIANA: 
    # Tutaj literówka w id
    # Input("btn_csv", "n_clicks"),
    Input("btn-csv", "n_clicks"),
    prevent_initial_call=True)
def func(n_clicks):
    return dcc.send_data_frame(df.to_csv, "mydf.csv")


if __name__ == "__main__":
    app.run_server(debug=True)