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


app = dash.Dash(__name__, assets_folder='assets')

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


app.layout = html.Div(
    id='container',
    children=[

            html.Div(
                id="nav-bar",
                children=[
                
                    html.Div(
                        id='header',
                        children=[
                            'San Francisco crimes'
                        ]
                    ),
                    
                    html.Button(
                        id = "submit-button",
                        className='button',
                        n_clicks = 0,
                        children = "Apply settings",
                        ),

                    html.Br(),

                    html.Button(
                        id = "submit-button2",
                        className='button',
                        n_clicks = 0,
                        children = "Update Dashboard",
                        ),

                    html.Div(
                        children=[
                            html.P("Select date range"),
                            dcc.DatePickerRange(
                                id='my-date-picker-range',
                                min_date_allowed=date(2016, 1, 1),
                                max_date_allowed=date(2016, 12, 31),
                                initial_visible_month=date(2016, 1, 1),
                                start_date = date(2016,1,1),
                                end_date=date(2016, 12, 31),
                                display_format = "YYYY-MM-DD",
                                style = {
                                    'line-height': '10px'
                                }
                            )

                        ]
                    ),

                    html.Div(
                        children=[
                            html.P("Select time range"),
                            dcc.RangeSlider(
                                id = "range-slider",
                                min = 0,
                                max = 23,
                                marks = {i : str(i) for i in range(0,24)},
                                value = [0,23]
                            )

                        ]  
                    ),

                    html.Div(
                        children=[
                            html.P("Select day"),
                            dcc.Dropdown(
                                id = "Days",
                                options = [{"label":i, "value":i} for i in DayOfWeek],
                                value = ["Wednesday","Sunday"],
                                multi = True)
                        ]
                    ),


                    html.Div(
                        children=[
                            html.P("Select crime category"),
                            dcc.Dropdown(
                                id = "crime_category",
                                options = [{"label":i, "value":i} for i in crime_category],
                                value = ["WEAPON LAWS"],
                                multi = True)
                        ]
                    ),

                    html.Div(
                        children=[
                            html.P("Select district"),
                            dcc.Dropdown(
                                id = "districts",
                                options = [{"label":i, "value":i} for i in PdDistrict],
                                value = PdDistrict,
                                multi = True)
                        ]
                    ),
                    
                    html.Div(
                        children=[
                            html.Button("Download CSV",
                                id = "btn-csv",
                                className='button'
                            ),
                            dcc.Download(
                                id = "download-dataframe-csv"
                                ),
                        ]
                    ),

                    html.Div(
                        children=[
                            html.Button(
                                "Download XLSX", 
                                id = "btn-xlsx", 
                                className='button'
                            ),
                            dcc.Download(id = "download-dataframe-xlsx"),
                        ]
                    )
                ]
            ),

            html.Div(
                id='content',
                children=[

                    dcc.Tabs(
                        children=[
                            dcc.Tab(
                                label = "Dashboard",
                                children = [
                                    
                                    html.Div(
                                        id='bar-container',
                                        children=[dcc.Graph(id = "barplot")]
                                    ),

                                    html.Div(
                                        id='map-container',
                                        children=[
                                            html.Iframe(
                                                id = "map", 
                                                srcDoc = None, 
                                                width = "100%",
                                                height = "500")
                                        ]
                                    ),

                                    html.Div(
                                        id='stat-container',
                                        children=[
                                            html.Div(
                                            id='crimes-number_cont',
                                            children=[
                                                html.Label("Total number of crimes"),
                                                html.Div(id = "crimes_number")
                                            ]),

                                            html.Div(
                                                id='crimes_share-cont',
                                                children=[
                                                    html.Label("Number of violations per each crime"),
                                                    html.Div(id = "crimes_share")
                                                ]),

                                            html.Div(
                                                id='popular-violations',
                                                children=[                    
                                                    html.Label("The most popular violations"),
                                                    html.Div(
                                                        id = "table-short"
                                                    )
                                                ])
                                            ]

                                        )
                                    ]
                               ),


                            dcc.Tab(
                                label = "Table",
                                children = [
                                    html.Div(
                                        id = "table-container"
                                    )
                                    
                               ])
                       ]
                    )


                ]
            ),

            html.Div(id='hidden-div')
])

@app.callback(Output("barplot","figure"),
              Input("submit-button2","n_clicks"))
def bar_plot(n_clicks):

    df_barplot = df_temp.groupby("hour").agg({"Time":"count"}).reset_index()

    data = [go.Bar(x = df_barplot["hour"], y = df_barplot["Time"], text = df_barplot["Time"])]
    layout = go.Layout(
        title = "Crimes divided into hours",
        xaxis_title = "Hours",
        yaxis_title = "Number of cases",
        hovermode = False,
        xaxis = dict(dtick = 1)
    )


    fig = {"data" : data, "layout" : layout}

    return fig


@app.callback(Output("table-container","children"),
              Input("submit-button2","n_clicks"))
def table_filtering(n_clicks):

    table = dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in df_temp.columns],
        data=df_temp.to_dict('records'), 
        page_size = 25,
        style_cell={
            'textAlign': 'center',
            'font_size': '12px',
            'font_family': 'Verdana, Geneva, Tahoma, sans-serif'
        },
        style_header={
            'backgroundColor': 'rgb(210, 210, 210)',
            'color': 'black',
            #'fontWeight': 'bold',
            'font_size': '12',
            'font_family': 'Verdana, Geneva, Tahoma, sans-serif'
        },
        style_table={
            'overflowX': 'scroll'
        },
        style_data={
            'color': 'black',
            'backgroundColor': 'white'
        }
        )

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

    df_final = dash_table.DataTable(
                        id='df_dinal',
                        columns=[{"name": i, "id": i} for i in df_short.columns],
                        data=df_short.to_dict('records'), 
                        page_size = 5,
                        style_cell={
                            'textAlign': 'center',
                            'font_size': '12px',
                             'font_family': 'Verdana, Geneva, Tahoma, sans-serif'
                        },
                        style_header={
                            'backgroundColor': 'rgb(210, 210, 210)',
                            'color': 'black',
                            #'fontWeight': 'bold',
                            'font_size': '12px',
                            'font_family': 'Verdana, Geneva, Tahoma, sans-serif'
                        },
                        style_table={
                            'overflowX': 'scroll'
                        },
                        style_data={
                            'color': 'black',
                            'backgroundColor': 'white'
                        }
                        )

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

        folium.CircleMarker(
            [row["Y"], 
            row["X"]], 
            popup = row["Descript"], 
            fill = True).add_to(marker_cluster)

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

    global df_temp

    df_temp = df.loc[(df["Date"] >= start_date) & (df["Date"] <= end_date)].copy()
    df_temp = df_temp.loc[(df_temp["hour"] >= value[0]) & (df_temp["hour"] <= value[1])]
    df_temp = df_temp.loc[df_temp["DayOfWeek"].isin(days)]
    df_temp = df_temp.loc[df_temp["Category"].isin(crimes)]
    df_temp = df_temp.loc[df_temp["PdDistrict"].isin(distr)]

    print("Data updated")

if __name__ == "__main__":
    app.run_server(debug=True)
