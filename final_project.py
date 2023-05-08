# Declan Butler
# CS230
# Data:US shootings
# URL:

# Description:This is a Python script that analyzes data about mass shootings
# in the United States. The script loads the data from a CSV file and performs
# some data cleaning to prepare it for visualization. The cleaned data is then
# used to create several interactive charts using the Plotly library, including
# a 3D scatter plot of the shooting locations and a box plot of shooter ages by year.
# The script also allows users to filter the data by year and state, and provides a
# pivot table that shows the total number of victims by state and year.
# Any of the moves you make with the slider or states selections impact all of the
# maps and charts below it.
# Overall, it's a pretty cool project that demonstrates how Python can be used for
# data analysis and visualization.


import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.subplots as sp
import plotly.graph_objects as go
import re

def load_data(file):
    data = pd.read_csv(file)
    data['total_victims'] = pd.to_numeric(data['total_victims'], errors='coerce')
    data['longitude'] = pd.to_numeric(data['longitude'], errors='coerce')
    data['state'] = data['location'].apply(lambda x: x.split(', ')[-1])
    data['date'] = pd.to_datetime(data['date'])
    data['year'] = data['date'].dt.year
    data['age_of_shooter'] = pd.to_numeric(data['age_of_shooter'], errors='coerce')
    data['fatalities'] = pd.to_numeric(data['fatalities'], errors='coerce')
    data['injured'] = pd.to_numeric(data['injured'], errors='coerce')
    data = data.dropna(subset=['fatalities', 'injured'])
    return data
def sort_data(data, columns, ascending_order=True):
    return data.sort_values(by=columns, ascending=ascending_order)
def extract_first_letter_of_first_name(summary):
    match = re.search(r'\b([A-Z])[a-z]*', summary)
    if match:
        return match.group(1)
    else:
        return None

def create_3d_scatter_plot(data):
    data = data.copy()
    data['total_victims'].fillna(0, inplace=True)
    data['latitude'] = pd.to_numeric(data['latitude'], errors='coerce')
    data.dropna(subset=['latitude'], inplace=True)
    fig = px.scatter_mapbox(data, lat='latitude', lon='longitude', color='total_victims', size='total_victims',
                            color_continuous_scale='Viridis', hover_name='location', hover_data=['fatalities', 'injured'],
                            zoom=3, mapbox_style='carto-positron', title='Mass Shootings Locations and Victims')
    return fig

def create_box_plot(data):
    fig = px.box(data, x='year', y='age_of_shooter', title='Distribution of Shooter Ages by Year',
                 labels={'age_of_shooter': 'Shooter Age', 'year': 'Year'},
                 hover_data=['year', 'age_of_shooter'])
    fig.update_traces(hovertemplate="Year: %{x}<br>Age: %{y}")
    return fig

def create_filtered_victims_by_state_pie_chart(data, selected_states, selected_data_type='total_victims'):
    filtered_data = data.copy()
    filtered_data = filtered_data[filtered_data['state'].isin(selected_states)]
    total_victims = filtered_data[selected_data_type].sum()
    state_data = filtered_data.groupby(['state'])['total_victims'].sum().reset_index(name='total_victims')
    state_data['percent'] = state_data['total_victims'] / total_victims * 100
    fig = go.Figure(data=[go.Pie(labels=state_data['state'], values=state_data['percent'])])
    fig.update_layout(title_text=f'Total {selected_data_type.capitalize()} Victims by State\n(Percentage of Selected States Total)')
    return fig

def extract_first_letter_and_age(summary, age):
    first_letter = extract_first_letter_of_first_name(summary)
    age = int(age) if not pd.isna(age) else None
    return first_letter, age

def create_first_letter_and_age_distribution_bar_chart(data):
    #I found the first letter of first name to be a really fun thing to look at and now
    #I know who to stay away from.
    data['first_letter_and_age'] = data.apply(lambda x: extract_first_letter_and_age(x['summary'], x['age_of_shooter']),
                                              axis=1)
    first_letter_and_age_df = pd.DataFrame(data['first_letter_and_age'].tolist(), columns=['first_letter', 'age'])
    first_letter_counts = first_letter_and_age_df['first_letter'].value_counts().reset_index().rename(
        columns={'index': 'first_letter', 'first_letter': 'count'})
    age_counts = first_letter_and_age_df['age'].dropna().value_counts().reset_index().rename(
        columns={'index': 'age', 'age': 'count'})
    fig = sp.make_subplots(rows=1, cols=2, subplot_titles=['First Letter of First Name', 'Age of Shooter'])
    first_letter_fig = px.bar(first_letter_counts, x='first_letter', y='count')
    for trace in first_letter_fig.data:
        fig.add_trace(trace, row=1, col=1)
    age_fig = px.bar(age_counts, x='age', y='count')
    for trace in age_fig.data:
        fig.add_trace(trace, row=1, col=2)
    fig.update_layout(title='Frequency of First Letter of Shooter\'s First Name and Age Distribution',
                      legend_title_text='First Letters and Ages')
    return fig
def style():
    st.markdown("""
        <style>
            .css-1aumxhk {
                font-family: Arial, sans-serif;
                background-color: #F5F5F5;
                color: #2C2C2C;
            }
            h1 {
                font-size: 48px;
                font-weight: bold;
            }
            h2 {
                font-size: 36px;
                font-weight: bold;
            }
        </style>
    """, unsafe_allow_html=True)

def main():
    style()
    st.sidebar.title("Navigation")
    section = st.sidebar.radio("Go to", ["Introduction", "Data Visualization", "Advanced Filtering"])
    data = load_data('/Users/declanbutler/Desktop/PycharmProjects/pythonProject/tester/mass_shootings.csv')
    if section == "Introduction":
        st.title("Introduction")
        st.markdown("Sup guys. Declan here. Please use my cool widgets on the next page")
    elif section == "Advanced Filtering":
        st.title("Advanced Filtering")
        st.markdown("Select multiple conditions for filtering the data.")
        min_fatalities = st.sidebar.number_input("Minimum Fatalities", min_value=0, value=0)
        min_injured = st.sidebar.number_input("Minimum Injured", min_value=0, value=0)
        filter_condition = st.sidebar.radio("Filter Condition", ['AND', 'OR'])
        if filter_condition == "AND":
            filtered_data = data[(data['fatalities'] >= min_fatalities) & (data['injured'] >= min_injured)]
        else:
            filtered_data = data[(data['fatalities'] >= min_fatalities) | (data['injured'] >= min_injured)]
        pivot_table = pd.pivot_table(filtered_data, index='state', columns='year', values='total_victims',
                                     aggfunc='sum', fill_value=0)
        st.write("Pivot Table: Total Victims by State and Year")
        st.write(pivot_table)
    elif section == "Data Visualization":
        selected_year_range = st.slider('Select year range:', min_value=1982, max_value=2023, value=(2018, 2023))
        selected_states = st.multiselect('Select states:', data['state'].unique())
        filtered_data = data[(data['year'] >= selected_year_range[0]) & (data['year'] <= selected_year_range[1])]
        if selected_states:
            filtered_data = filtered_data[filtered_data['state'].isin(selected_states)]

        st.title("Mass Shooting Data Visualization")
        fig1 = create_3d_scatter_plot(filtered_data)
        fig1.update_layout(title_text='Mass Shootings Locations and Victims')
        st.plotly_chart(fig1, use_container_width=True)
        fig2 = create_filtered_victims_by_state_pie_chart(filtered_data, selected_states=selected_states,
                                                          selected_data_type='total_victims')
        fig2.update_layout(title_text='Total Victims by State (Percentage of Selected States Total)')
        st.plotly_chart(fig2, use_container_width=True)
        fig3 = create_box_plot(filtered_data)
        fig3.update_layout(title_text='Distribution of Shooter Ages by Year')
        st.plotly_chart(fig3, use_container_width=True)
        fig4 = create_first_letter_and_age_distribution_bar_chart(filtered_data)
        fig4.update_layout(title_text='Frequency of First Letter of Shooter\'s First Name and Age Distribution',
                           legend_title_text='First Letters and Ages')
        st.plotly_chart(fig4, use_container_width=True)
if __name__ == "__main__":
    main()
