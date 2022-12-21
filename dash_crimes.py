import dash
from dash import html
from dash import dcc
from dash.dependencies import State,Output,Input
from dash import dash_table
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from datetime import date
import folium
from folium.plugins import MarkerCluster


app = dash.Dash(__name__)

df = pd.read_csv("crimes.csv", parse_dates = ["Date"])


df["hour"] = df["Time"].str[0:2].astype("int")
df["Date"] = pd.to_datetime(df["Date"].dt.date)

df_temp = df.copy()

df_temp = df_temp.loc[(df_temp["hour"] >= 0) & (df_temp["hour"] <= 23)]
df_temp = df_temp.loc[df_temp["DayOfWeek"].isin(["Wednesday","Sunday"])]
df_temp = df_temp.loc[df_temp["Category"].isin(["WEAPON LAWS"])]

DayOfWeek = df["DayOfWeek"].unique()
crime_category = df["Category"].unique()
PdDistrict = df.loc[~df["PdDistrict"].isna()]["PdDistrict"].unique()


app.layout = html.Div([


            html.Div([
                        html.P(),
                        html.Button(id = "submit-button",
                                    n_clicks = 0,
                                    children = "Apply settings",
                                    style = {"fontSize" : 24}),

                        html.Br(),
                        html.Br(),

                        html.Button(id = "submit-button2",
                                    n_clicks = 0,
                                    children = "Update Dashboard",
                                    style = {"fontSize" : 24})]),


             html.Div([
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

                        )

             ], style = {"float":"left"}),


             html.Div([
             html.P(),
             html.P(),
             html.H3("Select time range"),
                dcc.RangeSlider(id = "range-slider",
                                min = 0,
                                max = 23,
                                marks = {i : str(i) for i in range(0,24)},
                                value = [0,23])

             ], style = {"width" : "25%", "float":"left"}),



             html.Div([
             html.P(),
             html.P(),
             html.H3("Select day"),
                dcc.Dropdown(id = "Days",
                             options = [{"label":i, "value":i} for i in DayOfWeek],
                             value = ["Wednesday","Sunday"],
                             multi = True)
             ],style = {"width":"25%", "float":"left"}),


             html.Div([
             html.P(),
             html.P(),
             html.H3("Select crime category"),
                dcc.Dropdown(id = "crime_category",
                             options = [{"label":i, "value":i} for i in crime_category],
                             value = ["WEAPON LAWS"],
                             multi = True)
             ],style = {"width":"25%","float":"left"}),

            html.Div([],style = {"clear":"both"}),


             html.Div([
             html.P(),
             html.P(),
             html.H3("Select district"),
                dcc.Dropdown(id = "districts",
                               options = [{"label":i, "value":i} for i in PdDistrict],
                               value = PdDistrict,
                               multi = True)
             ],style = {"width":"25%"}),

             html.P(),
             html.P(),

             html.Label("Total number of crimes"),
             html.Div(id = "crimes_number"),
             html.Br(),
             html.Label("Number of violations per each crime"),
             html.Div(id = "crimes_share"),
             html.Br(),
             html.Label("The most popular violations"),
             html.Div(id = "table-short", style = {"width":"15%"}),
             html.Br(),



             html.Div([

                html.Button("Download CSV", id = "btn-csv"),
                dcc.Download(id = "download-dataframe-csv"),

             ]),

             html.Br(),

             html.Div([

                html.Button("Download XLSX", id = "btn-xlsx"),
                dcc.Download(id = "download-dataframe-xlsx"),

                          ]),

             html.P(),
                       dcc.Tabs([

                       dcc.Tab(label = "Dashboard",

                               children = [

                               html.Br(),
                               html.Br(),
                               html.Br(),

                               html.Div([dcc.Graph(id = "barplot")],
                                    style = {"width":"50%", "float":"left"}),

                               html.Div([html.Iframe(id = "map", srcDoc = None, width = "100%",height = "400")], style = {"float":"left","width":"50%"})

                               ]),


                       dcc.Tab(label = "Table",
                               children = [

                        html.H3("Data"),

                        html.P(),

                        html.Div(id = "table-container")

                               ])
                       ]),

            html.Div(id="hidden-div", style={"display":"none"})

])

@app.callback(Output("barplot","figure"),
              Input("submit-button2","n_clicks")
#              [State("my-date-picker-range","start_date"),
#              State("my-date-picker-range","end_date"),
#              State("range-slider","value"),
#              State("Days","value"),
#              State("crime_category","value"),
#              State("districts","value")]

              )

def bar_plot(n_clicks):
#n_clicks,start_date,end_date,value,days,crimes, distr


#    df_barplot = df.loc[(df["Date"] >= start_date) & (df["Date"] <= end_date)]
#    df_barplot = df_barplot.loc[(df_barplot["hour"] >= value[0]) & (df_barplot["hour"] <= value[1])]
#    df_barplot = df_barplot.loc[df_barplot["DayOfWeek"].isin(days)]
#    df_barplot = df_barplot.loc[df_barplot["Category"].isin(crimes)]
#    df_barplot = df_barplot.loc[df_barplot["PdDistrict"].isin(distr)]

    df_barplot = df_temp.groupby("hour").agg({"Time":"count"}).reset_index()

    data = [go.Bar(x = df_barplot["hour"], y = df_barplot["Time"], text = df_barplot["Time"])]
    layout = go.Layout(title = "Crimes divided into hours",
                       xaxis_title = "Hours",
                       yaxis_title = "Number of cases",
                       hovermode = False,
                      # hoverlabel=dict(
                      #                    bgcolor="white",
                      #                    font_size=16,
                      #                      font_family="Rockwell"),
                      xaxis = dict(dtick = 1))


    fig = {"data" : data, "layout" : layout}

    return fig


@app.callback(Output("table-container","children"),
              Input("submit-button2","n_clicks")
#              [State("my-date-picker-range","start_date"),
#              State("my-date-picker-range","end_date"),
#              State("range-slider","value"),
#              State("Days","value"),
#              State("crime_category","value"),
#              State("districts","value")]
)
def table_filtering(n_clicks):
# start_date,end_date,value,days, crimes, distr
#
#    df_table = df.loc[(df["Date"] >= start_date) & (df["Date"] <= end_date)]
#    df_table["Date"] = df_table["Date"].dt.strftime("%Y-%m-%d")
#    df_table = df_table.loc[(df_table["hour"] >= value[0]) & (df_table["hour"] <= value[1])]
#    df_table = df_table.loc[df_table["DayOfWeek"].isin(days)]
#    df_table = df_table.loc[df_table["Category"].isin(crimes)]
#    df_table = df_table.loc[df_table["PdDistrict"].isin(distr)]


    table = dash_table.DataTable(id='table',
                        columns=[{"name": i, "id": i} for i in df_temp.columns],
                        data=df_temp.to_dict('records'), page_size = 25)

    return table

@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn-csv", "n_clicks"),
    prevent_initial_call=True)
def func(n_clicks):
    return dcc.send_data_frame(df_temp.to_csv, "DATA_" + date.today().strftime("%Y-%m-%d") + ".csv",index = False)


@app.callback(
    Output("download-dataframe-xlsx", "data"),
    Input("btn-xlsx", "n_clicks"),
    prevent_initial_call=True)
def func(n_clicks):
    return dcc.send_data_frame(df_temp.to_excel, "DATA_" + date.today().strftime("%Y-%m-%d") + ".xlsx",index = False)



@app.callback(Output("crimes_number","children"),
              Input("submit-button2","n_clicks"))

def crimes_number(n_clicks):
    result = len(df_temp)
    return result


@app.callback(Output("crimes_share","children"),
              Input("submit-button2","n_clicks"))

def crimes_number(n_clicks):

    a = len(df_temp)
    b = len(df_temp.drop_duplicates(subset = ["IncidntNum"]))
    result = a/b
    result = np.round(result,3)
    return result


@app.callback(Output("table-short","children"),
              Input("submit-button2","n_clicks"))

def table_most_popular_crimes(n_clicks):

    df_short = df_temp.groupby("Descript").agg({"IncidntNum":"count"}, as_index = False)\
                                          .sort_values(by = "IncidntNum", ascending = False)\
                                          .head(5)
    df_short.columns = ["N"]
    df_short.reset_index(inplace = True)


    df_final = dash_table.DataTable(id='df_dinal',
                        columns=[{"name": i, "id": i} for i in df_short.columns],
                        data=df_short.to_dict('records'), page_size = 5)

    return df_final


@app.callback(Output("map","SrcDoc"),
              Input("submit-button2","n_clicks"))

def map(n_clicks):

    df_map = df_temp.copy()


    mean_x = np.mean(df_map["X"])
    mean_y = np.mean(df_map["Y"])

    m = folium.Map(location = [mean_y, mean_x])
    marker_cluster = MarkerCluster().add_to(m)

    for index, row in df_map.iterrows():

        folium.CircleMarker([row["Y"], row["X"]], popup = row["Descript"], fill = True).add_to(marker_cluster)

    m.save("map.html")

    return open("map.html","r").read()



@app.callback(Output("hidden-div","children"),
              Input("submit-button","n_clicks"),
              [State("my-date-picker-range","start_date"),
               State("my-date-picker-range","end_date"),
               State("range-slider","value"),
               State("Days","value"),
               State("crime_category","value"),
               State("districts","value")])

def aktualizacja_danych(n_clicks,start_date,end_date,value,days, crimes, distr):

#    if dash.callback_context.triggered_id == "submit-button":

    global df_temp

    df_temp = df.loc[(df["Date"] >= start_date) & (df["Date"] <= end_date)].copy()
    df_temp = df_temp.loc[(df_temp["hour"] >= value[0]) & (df_temp["hour"] <= value[1])]
    df_temp = df_temp.loc[df_temp["DayOfWeek"].isin(days)]
    df_temp = df_temp.loc[df_temp["Category"].isin(crimes)]
    df_temp = df_temp.loc[df_temp["PdDistrict"].isin(distr)]

    print("Data updated")

if __name__ == "__main__":
    app.run_server()
