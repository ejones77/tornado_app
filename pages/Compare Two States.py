import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from scipy import stats
import numpy as np

st.title('Compare Two States')
st.write("""
Pick any two states, see if they're different. 
""")

@st.cache_data
def load_data():
    df = pd.read_csv('us_tornado_dataset_1950_2021.csv')
    df['date'] = pd.to_datetime(df['date'])
    return df
tornado = load_data()

states = tornado['st'].sort_values().unique()
default_state1 = 'TX'
default_state2 = 'OK'

state1 = st.sidebar.selectbox('State 1', options=states, index=np.where(states == default_state1)[0][0].item())
state2 = st.sidebar.selectbox('State 2', options=states, index=np.where(states == default_state2)[0][0].item())

## COMPARE AVG TORNADOS/YR

#check distributions first
st.write(f"We're going to use a t test to compare the average yearly tornados between {state1} and {state2}, but first we need to confirm \
         that the distribution of average tornados resembles a normal distribution. If the histogram below doesn't resemble a bell curve, \
         the results may be unreliable -- this is bound to be less reliable when comparing two states with lower tornado frequency.")


state1_counts = tornado[tornado['st'] == state1].groupby('yr').size()
state2_counts = tornado[tornado['st'] == state2].groupby('yr').size()

trace1 = go.Histogram(
    x=state1_counts,
    opacity=0.75,
    name=state1,
    autobinx=True,
    marker=dict(color='blue')
)

trace2 = go.Histogram(
    x=state2_counts,
    opacity=0.75,
    name=state2,
    autobinx=True,
    marker=dict(color='red')
)

data = [trace1, trace2]

layout = go.Layout(
    title='Histogram of Tornado Counts Per Year',
    xaxis=dict(title='Count'),
    yaxis=dict(title='Frequency'),
    bargap=0.2,
    bargroupgap=0.1
)

fig = go.Figure(data=data, layout=layout)
st.plotly_chart(fig, use_container_width=True)



t_stat, p_value = stats.ttest_ind(tornado[tornado['st'] == state1].groupby('yr').size(), tornado[tornado['st'] == state2].groupby('yr').size())

mean_counts = tornado.groupby(['st', 'yr']).size().groupby('st').mean()
mean_count1, mean_count2 = round(mean_counts[state1], 2), round(mean_counts[state2], 2)
st.write(f'Mean number of tornadoes per year in {state1}: {mean_count1}')
st.write(f'Mean number of tornadoes per year in {state2}: {mean_count2}')


if p_value < 0.05:
    st.write(f"The p-value is less than 0.05, so we reject the null hypothesis that the means of the number of tornadoes per year in {state1} and {state2} are equal. \
             This suggests that there is a significant difference in the number of tornadoes per year between these two states.")
    if mean_count1 > mean_count2:
        st.write(f"{state1} has a higher average number of tornadoes per year ({mean_count1}) than {state2} ({mean_count2}).")
    else:
        st.write(f"{state2} has a higher average number of tornadoes per year ({mean_count2}) than {state1} ({mean_count1}).")
else:
    st.write(f"The p-value is greater than 0.05, so we fail to reject the null hypothesis that the means of the number of tornadoes per year in {state1} and {state2} are equal. \
             This suggests that there is not a significant difference in the number of tornadoes per year between these two states.")



## BEFORE / AFTER 2000
st.write("Now let's look at each state before and after 2000 -- within each state, we want to know whether there's a significant difference in tornado occurrence before and after 2000.")

counts = tornado.groupby(['st', 'yr']).size()

state1_counts_before_2000 = round(counts[state1][counts[state1].index < 2000], 2)
state1_counts_since_2000 = round(counts[state1][counts[state1].index >= 2000], 2)

state2_counts_before_2000 = round(counts[state2][counts[state2].index < 2000], 2)
state2_counts_since_2000 = round(counts[state2][counts[state2].index >= 2000], 2)


t_stat1, p_value1 = stats.ttest_ind(state1_counts_before_2000, state1_counts_since_2000)
t_stat2, p_value2 = stats.ttest_ind(state2_counts_before_2000, state2_counts_since_2000)

fig = make_subplots(rows=1, cols=2, subplot_titles=(state1, state2))
fig.add_trace(go.Scatter(x=state1_counts_before_2000.index, y=state1_counts_before_2000.values, mode='lines', name='Before 2000'), row=1, col=1)
fig.add_trace(go.Scatter(x=state1_counts_since_2000.index, y=state1_counts_since_2000.values, mode='lines', name='Since 2000'), row=1, col=1)
fig.add_trace(go.Scatter(x=state2_counts_before_2000.index, y=state2_counts_before_2000.values, mode='lines', name='Before 2000'), row=1, col=2)
fig.add_trace(go.Scatter(x=state2_counts_since_2000.index, y=state2_counts_since_2000.values, mode='lines', name='Since 2000'), row=1, col=2)
fig.update_layout(title='Yearly Tornado Counts by State and Year',
                  yaxis_title='Count',
                  xaxis_title='Year')

st.plotly_chart(fig, use_container_width=True)

# For state 1
if p_value1 < 0.05:
    st.write(f"For {state1}, the p-value is less than 0.05, so we reject the null hypothesis that the means of the number of tornadoes per year before and since 2000 are equal. \
             This suggests that there is a significant difference in the number of tornadoes per year before and since 2000.")
    if state1_counts_before_2000.mean() > state1_counts_since_2000.mean():
        st.write(f"{state1} has a higher average number of tornadoes per year before 2000 ({state1_counts_before_2000.mean()}) than since 2000 ({state1_counts_since_2000.mean()}).")
    else:
        st.write(f"{state1} has a higher average number of tornadoes per year since 2000 ({state1_counts_since_2000.mean()}) than before 2000 ({state1_counts_before_2000.mean()}).")
else:
    st.write(f"For {state1}, the p-value is greater than 0.05, so we fail to reject the null hypothesis that the means of the number of tornadoes per year before and since 2000 are equal. \
             This suggests that there is not a significant difference in the number of tornadoes per year before and since 2000 in {state1}.")

# For state 2
if p_value2 < 0.05:
    st.write(f"For {state2}, the p-value is less than 0.05, so we reject the null hypothesis that the means of the number of tornadoes per year before and since 2000 are equal. \
             This suggests that there is a significant difference in the number of tornadoes per year before and since 2000.")
    if state2_counts_before_2000.mean() > state2_counts_since_2000.mean():
        st.write(f"{state2} has a higher average number of tornadoes per year before 2000 ({state2_counts_before_2000.mean()}) than since 2000 ({state2_counts_since_2000.mean()}).")
    else:
        st.write(f"{state2} has a higher average number of tornadoes per year since 2000 ({state2_counts_since_2000.mean()}) than before 2000 ({state2_counts_before_2000.mean()}).")
else:
    st.write(f"For {state2}, the p-value is greater than 0.05, so we fail to reject the null hypothesis that the means of the number of tornadoes per year before and since 2000 are equal. \
             This suggests that there is not a significant difference in the number of tornadoes per year before and since 2000 in {state2}.")