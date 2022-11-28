import dash
from dash import html
from dash import dcc
from dash.dependencies import State,Output,Input
from dash import dash_table
import pandas as pd
import plotly.graph_objs as go
from datetime import date


app = dash.Dash(__name__, assets_folder='assets')

df = pd.read_csv("crimes.csv", parse_dates=['Date'])
df["hour"] = df.Time.str[0:2].astype("int")
df["Date"] = pd.to_datetime(df.Date.dt.date)

df_temp = df.copy()

DayOfWeek = df_temp["DayOfWeek"].unique()
crime_category = df_temp["Category"].unique()
PdDistrict = df_temp.loc[~df_temp.PdDistrict.isna()]["PdDistrict"].unique()

app.layout = html.Div(
    id='container',
    children=[

        html.Div(
            id='filters',
            children=[

                html.Div(
                    id='header',
                    children=[
                        html.H3('San Francisco Crimes')
                    ]
                ),
                
                html.Div(
                id='buttons',
                    children=[

                        html.Button("Download CSV", 
                            id="btn-csv"
                        ),
                        dcc.Download(
                            id="download-dataframe-csv"
                        ),

                        html.Br(),
                        html.Br(),

                        html.Button(
                            id = "submit-button",
                            n_clicks = 0,
                            children = "Submit here",
                            style = {
                                "fontSize": 14
                            }
                        )
                    ]
                ),

                html.Div(
                    id='date_range_div',
                    className='filter',
                    children=[
                    
                        html.H4("Select date range"),
                        
                        dcc.DatePickerRange(
                            id='my-date-picker-range',
                            min_date_allowed=date(2016, 1, 1),
                            max_date_allowed=date(2016, 12, 31),
                            initial_visible_month=date(2016, 1, 1),
                            start_date = date(2016,1,1),
                            end_date=date(2016, 12, 31),
                            display_format = "YYYY-MM-DD"
                        )
                    ]
                ),


                html.Div(
                    id='time_range_div',
                    className='filter',
                    children=[
                    
                        html.H4("Select time range"),
                        
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
                    id='select_day_div',
                    className='filter',
                    children=[                 
                        html.H4("Select day"),
                        dcc.Dropdown(
                            id = "Days",
                            options = [{"label":i, "value":i} for i in DayOfWeek],
                            value = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
                            multi = True)
                    ]
                ),


                html.Div(
                    id='select_category_div',
                    className='filter',
                    children=[
                        html.H4("Select crime category"),
                        dcc.Dropdown(
                            id = "crime_category",
                            options = [{"label":i, "value":i} for i in crime_category],
                            value = ["WEAPON LAWS","ASSAULT"],
                            multi = True)
                    ]
                ),

                html.Div(
                    id='select_district_div',
                    className='filter',
                    children=[
                        html.H4("Select district"),
                        dcc.Dropdown(
                            id = "districts",
                            options = [{"label":i, "value":i} for i in PdDistrict],
                            value = PdDistrict,
                            multi = True)
                        ]
                    ),

        ]),

        html.Div(
            id='content',

            children=[

            dcc.Tabs(
                id="tab_or_graph",
                value="dashboard",
                children=[
                    dcc.Tab(label="Dashboard", value="dashboard"),
                    dcc.Tab(label="Table", value="table"),
                ]),

            html.Br(),
            html.Div(id="tabs-container", children=[])
    
        ]),

        html.Div([],style = {"clear":"both"})
    ])

def generuj_wykres_tabele(df_fun, value):

    if value == 'dashboard':

        df_group = (df_fun
            .groupby("hour")
            .agg({
                "Time": "count"})
            .reset_index()
        )
                    
        data = [go.Bar(
            x=df_group["hour"],
            y=df_group["Time"],
            text=df_group["Time"])]
        
        layout=go.Layout(
            title="Crimes divided into hours",
            xaxis_title="Hours",
            yaxis_title="Number of cases",
            hovermode=False,
            xaxis={
                "dtick": 1
                }
            )

        return dcc.Graph(
            figure={
                "data": data, 
                "layout": layout
                }
            )

    else:
        return dash_table.DataTable(
            id='table',
            columns=[{"name": i, "id": i} for i in df_fun.columns],
            data=df_fun.to_dict('records'), 
            page_size = 25)


@app.callback(Output("tabs-container","children"),
              Input("submit-button","n_clicks"),
              Input('tab_or_graph','value'),
              State("my-date-picker-range","start_date"),
              State("my-date-picker-range","end_date"),
              State("range-slider","value"),
              State("Days","value"),
              State("crime_category","value"),
              State("districts","value")
)
def aktualizacja_danych(
    n_clicks,
    tab_or_graph, 
    start_date, 
    end_date, 
    value, 
    days, 
    crimes, 
    distr):

    if dash.callback_context.triggered_id == 'submit-button':

        global df_temp

        df_temp = df.loc[(df["Date"] >= start_date) & (df["Date"] <= end_date)].copy() 
        df_temp = df_temp.loc[(df_temp["hour"] >= value[0]) & (df_temp["hour"] <= value[1])]
        df_temp = df_temp.loc[df_temp["DayOfWeek"].isin(days)]
        df_temp = df_temp.loc[df_temp["Category"].isin(crimes)]
        df_temp = df_temp.loc[df_temp["PdDistrict"].isin(distr)]

    return generuj_wykres_tabele(
        df_fun=df_temp, 
        value=tab_or_graph
    )

@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn-csv", "n_clicks"),
    prevent_initial_call=True
)
def func(n_clicks):
    return dcc.send_data_frame(df_temp.to_csv, "mydf.csv")


if __name__ == "__main__":
    app.run_server(debug=True)