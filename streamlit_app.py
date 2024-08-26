import streamlit as st
import pandas as pd
import math
import numpy as np
from pathlib import Path
#import plotly.express as px
#import plotly.graph_objects as go

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='HAITI indicators',
    # This is an emoji shortcode. Could be a URL too.
    page_icon=':earth_americas:',
    layout="wide"
)

t1,t3, t2 = st.columns((0.05,0.05,1)) 

t1.image('data/haiti.jpeg', width = 80)
t2.title("Haiti - Some Historical Indicators")
t2.markdown(" **tel:** 36055983  **| email:** mailto:vitalralph@hotmail.com")
t2.markdown(" source: https://data.worldbank.org/country/haiti ")



tab1, tab2, tab3 = st.tabs(["Economy", "Health & Education", "Demograpgy"])

# -----------------------------------------------------------------------------
# Declare some useful functions.

def header_bg(table_type):
    if table_type > 0 :
        return "tablebackground"
    elif table_type < 0:
        return "viewbackground"
    else:
        return "mvbackground"

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def human_format(num):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    # add more suffixes if you need them
    return ('%.2f%s' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])).replace('.00', '')

def remote_css(url):
    st.markdown(f'<link href="{url}" rel="stylesheet">',
                unsafe_allow_html=True)

remote_css(
    "https://cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.4.1/semantic.min.css")


local_css("style.css")
cb_view_details = st.sidebar.checkbox('View Details')


@st.cache_data
def get_gdp_data():
    """Grab GDP data from a CSV file.

    This uses caching to avoid having to read the file every time. If we were
    reading from an HTTP endpoint instead of a file, it's a good idea to set
    a maximum age to the cache with the TTL argument: @st.cache_data(ttl='1d')
    """

    # Instead of a CSV on disk, you could read from an HTTP endpoint here too.
    DATA_FILENAME = Path(__file__).parent/'data/haiti_ind_wb.csv'
    raw_gdp_df = pd.read_csv(DATA_FILENAME, header=2)
   

    MIN_YEAR = 1970
    MAX_YEAR = 2022

    # The data above has columns like:
    # - Country Name
    # - Country Code
    # - [Stuff I don't care about]
    # - GDP for 1960
    # - GDP for 1961
    # - GDP for 1962
    # - ...
    # - GDP for 2022
    #
    # ...but I want this instead:
    # - Country Name
    # - Country Code
    # - Year
    # - GDP
    #
    # So let's pivot all those year-columns into two: Year and GDP
    gdp_df = raw_gdp_df.melt(
         ['Country Code','Indicator Code','Indicator Name'],
         [str(x) for x in range(MIN_YEAR, MAX_YEAR + 1)],
         'year',
         'Value',
     )


    # Convert years from string to integers

    return gdp_df

test_df = get_gdp_data()



test_df.to_csv('test.csv')

min_value = int(test_df['year'].min())
max_value = int(test_df['year'].max())

year_select = st.sidebar.slider(
    'Which years are you interested in?',
    min_value=min_value,
    max_value=max_value,
    value=min_value)

year_ante = year_select - 1

indicators = {"economy":["NY.GDP.PCAP.CN",
                         "NY.GDP.MKTP.CD",
                         "NY.GDP.DEFL.KD.ZG", 
                         "TX.VAL.MRCH.R3.ZS",
                          "TX.VAL.MRCH.HI.ZS", 
                          "TM.VAL.MRCH.R4.ZS" ,
                          "TM.VAL.MRCH.OR.ZS",
                          "FP.CPI.TOTL",
                         "FM.LBL.BMNY.CN",
                          "FM.AST.DOMS.CN",
                          "FD.AST.PRVT.GD.ZS",
                 ],

              "health":["SH.DYN.NMRT",
                "SH.DYN.MORT.MA",
                "SP.DYN.LE00.MA.IN",
                "SP.DYN.IMRT.IN",
                "SP.DYN.CDRT.IN",
                "SP.ADO.TFRT",
                "SH.DTH.MORT",
                "SE.SEC.CUAT.PO.ZS",
                "SE.SEC.CUAT.LO.MA.ZS",
                "SE.PRM.ENRR",
                ],
              "demography":["SP.URB.TOTL",
                "SP.RUR.TOTL",
                "SP.POP.DPND",
                "SP.POP.7579.MA.5Y",
                "SP.POP.65UP.TO.ZS",
                "SP.POP.65UP.FE.ZS",
                "SP.POP.6064.MA.5Y",
                "SP.POP.5054.MA.5Y",
                "SP.POP.4044.MA.5Y",
                "SP.POP.3034.MA.5Y",
                "SP.POP.2024.MA.5Y",
                "SP.POP.1564.MA.ZS",
                "SP.POP.1519.MA.5Y",
                "SP.POP.0509.MA.5Y",
                "SP.POP.0014.MA.ZS",
                "SP.POP.0004.MA.5Y",
                ],

                }


filtered_df = test_df[
    (test_df['Indicator Code'].isin(indicators['economy']))   
]


def get_val_delta(label, test_df, test_df_ante):
    filter_df = test_df[(test_df['Indicator Code'] == label)]
    filter_df_antre = test_df_ante[(test_df_ante['Indicator Code'] == label)]
    val =  round(filter_df['Value'].to_numpy()[0], 2)
    val_ante = round(filter_df['Value'].to_numpy()[0], 2) if len(filter_df_antre) > 0 else 0
    delta_ = (val - val_ante) / val_ante if val_ante != 0 else -99 
    return val, delta_



f_df = test_df[
    (test_df['Indicator Code'].isin(indicators['economy']))   
    & (test_df['year']==str(year_select))
]

a_df = test_df[
    (test_df['Indicator Code'].isin(indicators['economy']))   
    & (test_df['year']==str(year_ante))
]

df_merge_col = pd.merge(f_df, a_df, on='Indicator Code', how='outer')

print(df_merge_col.head())
df_merge_col['delta'] = df_merge_col[['Value_x', 'Value_y']].apply(lambda x : (x.Value_x - x.Value_y) / x.Value_y , axis=1 )

print(df_merge_col.head())
table_scorecard = """<br><br><br><div id="mydiv" class="ui centered cards">"""
for index, row in df_merge_col.iterrows():
    table_scorecard += """
<div class="card"">   
    <div class=" content """+ header_bg(row['delta']) + """">
            <div class=" header smallheader">"""+row['Indicator Name_x']+"""</div>
    </div>
    <div class="content">
        <div class="description"><br>
            <div class="column kpi number">"""+ human_format((row['Value_x'])) +"""<br>
                <p class="kpi text">Indicateur</p>
            </div>
            <div class="column kpi number">""" + str(row['year_x'])+"""<br>
                <p class="kpi text">"""+ str('Année')+"""</p>
            </div>
            <div class="column kpi number">"""+"{0:}".format(human_format(row['delta']))+"""<br>
                <p class="kpi text">Variation</b>
            </div>
        </div>
    </div>
</div>"""

with tab1:
    st.markdown(table_scorecard, unsafe_allow_html=True)

h_df = test_df[
    (test_df['Indicator Code'].isin(indicators['health']))   
    & (test_df['year']==str(year_select))
]

ha_df = test_df[
    (test_df['Indicator Code'].isin(indicators['health']))   
    & (test_df['year']==str(year_ante))
]

df_merge_col_h = pd.merge(h_df, ha_df, on='Indicator Code', how='outer')
df_merge_col_h['delta'] = df_merge_col_h[['Value_x', 'Value_y']].apply(lambda x : (x.Value_x - x.Value_y) / x.Value_y , axis=1 )


table_scorecard_h = """<br><br><br><div id="mydiv" class="ui centered cards">"""
for index, row in df_merge_col_h.iterrows():
    table_scorecard_h += """
<div class="card"">   
    <div class=" content """+ header_bg(row['delta']) + """">
            <div class=" header smallheader">"""+ str(row['Indicator Name_x'])+"""</div>
    </div>
    <div class="content">
        <div class="description"><br>
            <div class="column kpi number">"""+ str(human_format((row['Value_x']))) +"""<br>
                <p class="kpi text">Indicateur</p>
            </div>
            <div class="column kpi number">""" + str(row['year_x'])+"""<br>
                <p class="kpi text">"""+ str('Année')+"""</p>
            </div>
            <div class="column kpi number">"""+"{0:}".format(human_format(row['delta']))+"""<br>
                <p class="kpi text">Variation</b>
            </div>
        </div>
    </div>
</div>"""

with tab2:
    st.markdown(table_scorecard_h, unsafe_allow_html=True)


d_df = test_df[
    (test_df['Indicator Code'].isin(indicators['demography']))   
    & (test_df['year']==str(year_select))
]

da_df = test_df[
    (test_df['Indicator Code'].isin(indicators['demography']))   
    & (test_df['year']==str(year_ante))
]

df_merge_col_d = pd.merge(d_df, da_df, on='Indicator Code', how='outer')


df_merge_col_d['delta'] = df_merge_col_d[['Value_x', 'Value_y']].apply(lambda x : (x.Value_x - x.Value_y) / x.Value_y , axis=1 )


table_scorecard_d = """<br><br><br><div id="mydiv" class="ui centered cards">"""
for index, row in df_merge_col_d.iterrows():
    table_scorecard_d += """
<div class="card"">   
    <div class=" content """+ header_bg(row['delta']) + """">
            <div class=" header smallheader">"""+row['Indicator Name_x']+"""</div>
    </div>
    <div class="content">
        <div class="description"><br>
            <div class="column kpi number">"""+ human_format((row['Value_x'])) +"""<br>
                <p class="kpi text">Indicateur</p>
            </div>
            <div class="column kpi number">""" + str(row['year_x'])+"""<br>
                <p class="kpi text">"""+ str('Année')+"""</p>
            </div>
            <div class="column kpi number">"""+"{0:}".format(human_format(row['delta']))+"""<br>
                <p class="kpi text">Variation</b>
            </div>
        </div>
    </div>
</div>"""

with tab3:
    st.markdown(table_scorecard_d, unsafe_allow_html=True)
