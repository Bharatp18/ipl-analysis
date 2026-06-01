import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

matches = pd.read_csv(r'C:\Users\bhara\ipl-analysis\data\matches.csv')
matches = matches.dropna(subset=['winner'])
matches['year'] = pd.to_datetime(matches['date']).dt.year
matches['toss_won_match'] = (matches['toss_winner'] == matches['winner'])

COLORS = {
    'bg': '#0f0f23',
    'card': '#1a1a3e',
    'accent1': '#667eea',
    'accent2': '#f093fb',
    'accent3': '#4facfe',
    'accent4': '#43e97b',
    'accent5': '#fa709a',
    'subtext': '#a0aec0'
}

app = dash.Dash(__name__)
app.title = "IPL Analytics Dashboard"

app.layout = html.Div([

    html.Div([
        html.H1("IPL Analytics Dashboard",
                style={'margin': '0', 'fontSize': '30px',
                       'color': '#667eea', 'fontWeight': 'bold'}),
        html.P("Explore 13 years of IPL match data",
               style={'margin': '5px 0 0', 'color': COLORS['subtext'], 'fontSize': '14px'}),
    ], style={
        'padding': '24px 32px', 'backgroundColor': COLORS['card'],
        'borderBottom': '1px solid #ffffff11'
    }),

    html.Div([
        html.Label("Filter by Year Range",
                   style={'color': COLORS['subtext'], 'fontSize': '13px',
                          'marginBottom': '10px', 'display': 'block'}),
        dcc.RangeSlider(
            id='year-slider',
            min=int(matches['year'].min()),
            max=int(matches['year'].max()),
            value=[2008, 2022],
            marks={int(y): {
                'label': str(int(y)),
                'style': {'color': COLORS['subtext'], 'fontSize': '11px'}
            } for y in sorted(matches['year'].unique())},
            step=1
        )
    ], style={'padding': '24px 32px', 'backgroundColor': COLORS['bg']}),

    html.Div(id='kpi-cards', style={
        'display': 'flex', 'gap': '16px',
        'padding': '0 32px 24px', 'backgroundColor': COLORS['bg']
    }),

    html.Div([
        html.Div([dcc.Graph(id='wins-chart', config={'displayModeBar': False})],
                 style={'flex': '2', 'backgroundColor': COLORS['card'],
                        'borderRadius': '16px', 'padding': '8px',
                        'border': '1px solid #ffffff11'}),
        html.Div([dcc.Graph(id='toss-chart', config={'displayModeBar': False})],
                 style={'flex': '1', 'backgroundColor': COLORS['card'],
                        'borderRadius': '16px', 'padding': '8px',
                        'border': '1px solid #ffffff11'}),
    ], style={'display': 'flex', 'gap': '16px', 'padding': '0 32px 16px',
              'backgroundColor': COLORS['bg']}),

    html.Div([
        html.Div([dcc.Graph(id='season-chart', config={'displayModeBar': False})],
                 style={'flex': '1', 'backgroundColor': COLORS['card'],
                        'borderRadius': '16px', 'padding': '8px',
                        'border': '1px solid #ffffff11'}),
        html.Div([dcc.Graph(id='toss-impact-chart', config={'displayModeBar': False})],
                 style={'flex': '1', 'backgroundColor': COLORS['card'],
                        'borderRadius': '16px', 'padding': '8px',
                        'border': '1px solid #ffffff11'}),
    ], style={'display': 'flex', 'gap': '16px', 'padding': '0 32px 16px',
              'backgroundColor': COLORS['bg']}),

    html.Div([
        html.Div([dcc.Graph(id='venue-chart', config={'displayModeBar': False})],
                 style={'flex': '1', 'backgroundColor': COLORS['card'],
                        'borderRadius': '16px', 'padding': '8px',
                        'border': '1px solid #ffffff11'}),
        html.Div([dcc.Graph(id='city-chart', config={'displayModeBar': False})],
                 style={'flex': '1', 'backgroundColor': COLORS['card'],
                        'borderRadius': '16px', 'padding': '8px',
                        'border': '1px solid #ffffff11'}),
    ], style={'display': 'flex', 'gap': '16px', 'padding': '0 32px 24px',
              'backgroundColor': COLORS['bg']}),

    html.Div([
        html.P("Built with Python | Dash | Plotly | IPL Dataset 2008-2022",
               style={'color': COLORS['subtext'], 'fontSize': '12px',
                      'textAlign': 'center', 'margin': '0'})
    ], style={'padding': '16px', 'backgroundColor': COLORS['card'],
              'borderTop': '1px solid #ffffff11'})

], style={'backgroundColor': COLORS['bg'], 'minHeight': '100vh',
          'fontFamily': "'Segoe UI', sans-serif"})


def dark_layout(title):
    return dict(
        title=dict(text=title, font=dict(color='white', size=14), x=0.01),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=11),
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='white')),
        xaxis=dict(gridcolor='rgba(255,255,255,0.07)', zerolinecolor='rgba(255,255,255,0.1)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.07)', zerolinecolor='rgba(255,255,255,0.1)'),
    )


@app.callback(
    Output('kpi-cards', 'children'),
    Output('wins-chart', 'figure'),
    Output('toss-chart', 'figure'),
    Output('season-chart', 'figure'),
    Output('venue-chart', 'figure'),
    Output('toss-impact-chart', 'figure'),
    Output('city-chart', 'figure'),
    Input('year-slider', 'value')
)
def update_all(year_range):
    df = matches[
        (matches['year'] >= year_range[0]) &
        (matches['year'] <= year_range[1])
    ].copy()
    
    df['city'] = df['city'].fillna('Unknown')
    df['venue'] = df['venue'].fillna('Unknown')
    df['winner'] = df['winner'].fillna('Unknown')
    
    if len(df) == 0:
        from dash import no_update
        return [no_update] * 7

    total_matches = len(df)
    total_teams = df['winner'].nunique()
    toss_win_pct = round(df['toss_won_match'].mean() * 100, 1)
    top_team = df['winner'].value_counts().index[0]

    def kpi_card(label, value, color):
        return html.Div([
            html.Div(str(value), style={'fontSize': '28px', 'fontWeight': 'bold',
                                        'color': color}),
            html.Div(label, style={'fontSize': '12px', 'color': COLORS['subtext'],
                                   'marginTop': '4px'})
        ], style={
            'flex': '1', 'backgroundColor': COLORS['card'],
            'borderRadius': '16px', 'padding': '20px',
            'border': f'1px solid {color}33',
            'textAlign': 'center', 'color': 'white'
        })

    kpi_cards = [
        kpi_card("Total Matches", total_matches, COLORS['accent1']),
        kpi_card("Most Wins", top_team, COLORS['accent2']),
        kpi_card("Toss Win = Match Win", f"{toss_win_pct}%", COLORS['accent3']),
        kpi_card("Teams in Period", total_teams, COLORS['accent4']),
    ]

    wins = df['winner'].value_counts().reset_index()
    wins.columns = ['Team', 'Wins']
    fig1 = px.bar(wins, x='Team', y='Wins', color='Wins',
                  color_continuous_scale='Purples')
    fig1.update_layout(dark_layout("Total Wins by Team"))
    fig1.update_xaxes(tickangle=-40)
    fig1.update_traces(marker_line_width=0)

    toss = df['toss_decision'].value_counts().reset_index()
    toss.columns = ['Decision', 'Count']
    fig2 = px.pie(toss, names='Decision', values='Count', hole=0.5,
                  color_discrete_sequence=[COLORS['accent1'], COLORS['accent5']])
    fig2.update_layout(dark_layout("Toss Decision: Bat vs Field"))
    fig2.update_traces(textfont_color='white')

    season = df['year'].value_counts().sort_index().reset_index()
    season.columns = ['Year', 'Matches']
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=season['Year'], y=season['Matches'],
        mode='lines+markers',
        line=dict(color=COLORS['accent3'], width=3),
        marker=dict(size=8, color=COLORS['accent3'],
                    line=dict(color='white', width=2)),
        fill='tozeroy',
        fillcolor='rgba(79,172,254,0.1)'
    ))
    fig3.update_layout(dark_layout("Matches Per Season"))

    venue = df['venue'].value_counts().head(8).reset_index()
    venue.columns = ['Venue', 'Matches']
    fig4 = px.bar(venue, x='Matches', y='Venue', orientation='h',
                  color='Matches', color_continuous_scale='Teal')
    fig4.update_layout(dark_layout("Top 8 Venues"))
    fig4.update_traces(marker_line_width=0)

    toss_impact = df['toss_won_match'].value_counts().reset_index()
    toss_impact.columns = ['Won', 'Count']
    toss_impact['Won'] = toss_impact['Won'].map(
        {True: 'Toss winner won', False: 'Toss winner lost'}
    )
    fig5 = px.pie(toss_impact, names='Won', values='Count', hole=0.6,
                  color_discrete_sequence=[COLORS['accent4'], COLORS['accent5']])
    fig5.update_layout(dark_layout("Does Toss Decide the Match?"))
    fig5.update_traces(textfont_color='white')

    city = df['city'].value_counts().head(10).reset_index()
    city.columns = ['City', 'Matches']
    fig6 = px.bar(city, x='City', y='Matches', color='Matches',
                  color_continuous_scale='Magma')
    fig6.update_layout(dark_layout("Top Cities by Matches"))
    fig6.update_xaxes(tickangle=-40)
    fig6.update_traces(marker_line_width=0)

    return kpi_cards, fig1, fig2, fig3, fig4, fig5, fig6


if __name__ == '__main__':
    app.run(debug=True)