import base64
import zipfile
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.chart import PieChart, Reference, Series
import pandas as pd
import streamlit as st
import pandas as pd
import pandas as pd
from io import BytesIO
import streamlit as st
from shutil import copyfile
import os
import pandas as pd
from openpyxl.styles import Alignment
from openpyxl.styles.borders import Border, Side
import requests
import time
from bs4 import BeautifulSoup
from datetime import date
import requests
import random
import json
from hashlib import md5
import numpy as np
from PIL import Image
import xlsxwriter
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)


def intro():
    import streamlit as st
    st.write("# 欢迎使用SMDG线上服务 👋")
    st.sidebar.success("请选择极致服务")
    st.markdown(
        """
        SMDG Logistics SRL 是一家位于比利时列日，专注于中欧货运服务的跨境物流公司 
                   
        **👈 从左边下拉框，请选择您需要的服务** 去体验SMDG极致的智能化服务
        ### 想要了解更多?
        - 欧盟海关码查询网站  [Tarbel](https://eservices.minfin.fgov.be/extTariffBrowser/browseNomen.xhtml?suffix=80&country=&lang=EN&page=1&date=20220727)
        - 欧盟进出口数据查询网站 [Import - Export Statistics](https://trade.ec.europa.eu/access-to-markets/en/statistics)
        - VAT有效性查询 [VIES VAT Validation](https://ec.europa.eu/taxation_customs/vies/)
        - EORI有效性查询 [Eori Validation](https://ec.europa.eu/taxation_customs/dds2/eos/eori_validation.jsp)
        ### SMDG 尾程派送优质服务
        - 零担    派送 : 涵盖 包括德国、法国、西班牙在内的主要西欧国家的零担派送业务
        - DHL   Paket : 价格低廉，时效快 (一周5天包车派送)
        - UPS     德国 ：覆盖全欧的UPS 快递派送业务
        - 比利时DPD直送 ：CDG7 / DTM2 亚马逊快递直送业务
        - AMM -  WRO5 : 集装箱直送业务
        ### 联系我们
        - 邮箱 : info@smdg.eu
        - 地址 : Rue Louis Bleriot 5A 4460 Bierset Belgiumt
        """)


def custom_invoice():
    import streamlit as st
    import time
    import numpy as np
    st.markdown(f"# 智能生成{list(page_names_to_funcs.keys())[1]}")
    st.write(
        """ 在这里您可以通过上传清关资料线上生成相关的CI和PL """)
    st.subheader("第一步骤 ：上传发票抬头信息")
    invoice_tete = st.file_uploader("", type=(["xlsx", "xls"]))
    if invoice_tete is None:
        pass
    else:
        st.write("已上传发票抬头信息 : ", invoice_tete.name)
        datasender = pd.read_excel(invoice_tete)
        hide_table_row_index = """
                    <style>
                    thead tr th:first-child {display:none}
                    tbody th {display:none}
                    </style>
                    """
        st.markdown(hide_table_row_index, unsafe_allow_html=True)
        st.write(" Please find All sender information ")
        st.table(datasender[["发件人代码", "发件人英文"]])
        col1, col2 = st.columns([2, 9.5])
        with col1:
            option = st.number_input("Choose the sender:", min_value=0, max_value=len(datasender), key=int)
        with col2:
            if option <= 0 or option >= len(datasender) + 1:
                pass
            else:
                choose_sender = datasender["发件人英文"].loc[datasender["发件人代码"] == int(option)].tolist()[0]
                Nameofsender = choose_sender
                sender_adresse_complete = datasender["完整地址"].loc[datasender["发件人代码"] == int(option)].tolist()[0]
                Sendercountrycode = datasender["国家代码"].loc[datasender["发件人代码"] == int(option)].tolist()[0]
                Streetsender = datasender["地址"].loc[datasender["发件人代码"] == int(option)].tolist()[0]
                Citysender = datasender["城市"].loc[datasender["发件人代码"] == int(option)].tolist()[0]
                Senderzipcode = str(datasender["邮编"].loc[datasender["发件人代码"] == int(option)].tolist()[0]).split(".")[0]
                st.write("")
                st.write("You have choosen :", choose_sender)
                st.write("Adresse complet is : ", sender_adresse_complete)
        st.write("")
        st.subheader("第二步骤：上传清关发票数据，可批量上传")
        custom_invoice_datas = st.file_uploader("", type=(["xlsx", "xls"]),
                                                accept_multiple_files=True)
        if custom_invoice_datas is None:
            pass
        else:
            p = 0
            for custom_invoice_data in custom_invoice_datas:
                p = p + 1
                st.write("")
                st.write(" ##### :point_right:    处理第", str(p), "份清关材料 : ", custom_invoice_data.name)
                st.write(" - 请输入 提单总重, 包裹总数, 境内运费, 国际运费 (*为必填)")
                col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
                with col1:
                    lta_officel_weight_kg = st.number_input("*请输入提单毛重 : ", min_value=0, max_value=1000000, key=int)
                with col2:
                    lta_officel_carton = st.number_input("*请输入提单包裹数量 : ", min_value=0, max_value=1000000, key=int)
                with col3:
                    transport_fee_interne = st.number_input("*请输入欧洲境内运费 :", min_value=0, max_value=1000000, key=int)
                with col4:
                    transport_fee_externe = st.number_input("请输入国际运费: ", min_value=0, max_value=1000000, key=int)

                datainvoice = pd.read_excel(custom_invoice_data)
                datainvoice = datainvoice.dropna(subset=["货箱编号"])
                # 已有产品申报单价
                datainvoice['产品申报单价'] = datainvoice['产品申报单价'].apply(lambda x: float(x))
                datainvoice['产品申报数量'] = datainvoice['产品申报数量'].apply(lambda x: int(x))
                datainvoice['货箱重量(KG)'] = datainvoice['货箱重量(KG)'].apply(lambda x: float(x))
                datainvoice['跟踪号'] = datainvoice['跟踪号'].apply(lambda x: str(x).split(".")[0])
                datainvoice['产品海关编码'] = datainvoice['产品海关编码'].apply(lambda x: str(x)[:10])
                datainvoice['产品海关编码'] = datainvoice['产品海关编码'].apply(lambda x: int(x))
                datainvoice['申报总价'] = datainvoice['产品申报单价'] * datainvoice['产品申报数量']
                datainvoice['毛重比例'] = datainvoice['货箱重量(KG)'] / datainvoice['货箱重量(KG)'].sum()
                datainvoice['包裹净重'] = datainvoice['货箱重量(KG)'] - len(set(datainvoice['货箱编号'].tolist())) * 1 * \
                                      datainvoice['毛重比例']
                datainvoice['产品净重'] = ((datainvoice['包裹净重'] / datainvoice['产品申报数量']) - 0.005).round(2)
                datainvoice['包裹净重'] = round(datainvoice['产品净重'] * datainvoice['产品申报数量'], 2)
                datainvoice['箱数'] = datainvoice['货箱编号']  # 先等于运单号，然后在调整
                datainvoice['每公斤价值'] = round(datainvoice['申报总价'] / datainvoice['货箱重量(KG)'], 2)  # 先等于运单号，然后在调整
                datainvoice['产品英文品名'] = datainvoice['产品英文品名']
                datainvoice['产品中文品名'] = datainvoice['产品中文品名']
                datainvoice = datainvoice.sort_values("货箱编号")
                datainvoice = datainvoice.fillna("")
                vats = list(set(datainvoice["VAT号"].tolist()))
                vats.sort()
                ltas = list(set(datainvoice["提单号"].tolist()))
                if len(ltas) == 1:
                    lta = ltas[0]
                else:
                    lta = str(ltas)
                kg_brut_total = datainvoice['货箱重量(KG)'].sum()
                carton_total = len(set(datainvoice['货箱编号'].tolist()))
                option = st.selectbox(
                    '根据不同的业务，请选择对应的清关行：',
                    ('SMDG Logistics SRL', 'Alando', 'Cacesa', 'Flying', 'ECLL'))
                if st.button('生成清关材料👈'):
                    if lta_officel_weight_kg == kg_brut_total:
                        st.write(':+1:重量相符')
                    else:
                        st.write(':triumph:重量不符合', "   --- 输入重量：", str(lta_officel_weight_kg), "   KG    ,  ", "发票重量：",
                                 str(kg_brut_total), "   KG")
                    if lta_officel_carton == carton_total:
                        st.write(':+1:包裹数量相符')
                    else:
                        st.write(':triumph:包裹数量不符合', "   --- 输入包裹数量：", str(lta_officel_carton), "   Cartons    ,  ",
                                 "发票包裹数量：", str(carton_total), "   Cartons")
                    st.write("")
                    if transport_fee_interne == 0:
                        transport_fee_interne = 1300
                    if transport_fee_externe == 0:
                        transport_fee_externe = ""

                    col1, col2, col3 = st.columns([1, 5, 5])
                    with col1:
                        pass
                    with col2:
                        st.write("- ###### 提单号码    : ", lta)
                        st.write("- ###### 清关材料数量 : ", str(len(vats)), " Docs")
                    with col3:
                        st.write("- ###### 包裹总数       : ", str(carton_total), " Cartons")
                        st.write("- ###### 包裹总重       : ", str(kg_brut_total), " KG")

                    # 开始生成清关材料：
                    st.write("")
                    st.write('##### 您已选择', option, " 作为清关服务商")
                    if option == "SMDG Logistics SRL":
                        st.write(" - 感谢您的信任，SMDG 正在筹备清关资质，预计2023年年初可以开始独立自主的清关业务")
                        st.write(" - 进一步消息请联系 邮箱 ： info@smdg.eu")
                        st.write(" - :pray:请重新选择清关行. 为带来不便, 深感抱歉")

                    elif option == "Cacesa":
                        st.write(" - 清关材料完善中...")
                        st.write(" - :pray:为带来不便, 深感抱歉")


                    elif option == "Flying":
                        st.write(" - 清关材料完善中...")
                        st.write(" - :pray:为带来不便, 深感抱歉")

                    elif option == "ECLL":
                        st.write(" - 清关材料完善中...")
                        st.write(" - :pray:为带来不便, 深感抱歉")

                    elif option == "Alando":
                        st.write(" - ###### 开始生成清关材料")
                        # 生成alando材料模板
                        dic_lta = []
                        a = 0
                        for vat in vats:
                            a = a + 1
                            datainvoice_vat = datainvoice.loc[datainvoice['VAT号'] == vat]
                            # 获取交货条款;交货城市;清关方式;收件人国家
                            incoterme = list(set(datainvoice_vat["交货条款"].tolist()))[0]
                            incoterme_city = list(set(datainvoice_vat["交货城市"].tolist()))[0]
                            delivery_country = list(set(datainvoice_vat["收件人国家"].tolist()))[0]
                            code_regime = list(set(datainvoice_vat["清关方式"].tolist()))[0]
                            qty_carton = len(set(datainvoice_vat["货箱编号"].tolist()))
                            exporter_chi = "---"
                            exporter_eng = Nameofsender
                            ref_number = lta + " - " + str(a)
                            invoice_number = "HBL - " + lta + " - " + str(a)
                            importer = datainvoice_vat["收件人"].tolist()[0]
                            EORI = datainvoice_vat["EORI"].tolist()[0]
                            adresse = datainvoice_vat["地址"].tolist()[0]
                            code_postal = str(datainvoice_vat["邮编"].tolist()[0]).split(".")[0]
                            city = datainvoice_vat["城市"].tolist()[0]
                            county_2_chiffre = datainvoice_vat["国家代码"].tolist()[0]
                            county_complet = datainvoice_vat["国家全称"].tolist()[0]
                            adresse_importer_complet = adresse + " ," + str(code_postal) + " ," + city + " ," + str(
                                county_complet)

                            # 建立分单文件夹

                            wb = Workbook()
                            ws = wb.active
                            ws['A1'] = 42
                            ws.append([1, 2, 3])
                            ws['A2'] = 56
                            wb.save("sample.xlsx")

                            def get_binary_file_downloader_html(bin_file, file_label='File'):
                                with open(file_path, 'rb') as f:
                                    data = f.read()
                                bin_str = base64.b64encode(data).decode()
                                href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">点击下载 {file_label}</a>'
                                return href

                            file_path = 'sample.xlsx'
                            file_label = '测试文件'
                            st.markdown(get_binary_file_downloader_html(file_path, file_label),
                                        unsafe_allow_html=True)

                            zip_file = zipfile.ZipFile(r'file_name.zip', 'w')
                            zip_file.write('sample.xlsx')
                            title = 'file_name'
                            with open("file_name.zip", "rb") as f:
                                bytes_read = f.read()
                                b64 = base64.b64encode(bytes_read).decode()
                                href = f'<a href="data:file/zip;base64,{b64}" download=\'{title}.zip\'>\
                                        Click to download\
                                    </a>'
                            st.markdown(href, unsafe_allow_html=True)

def mapping_demo():
    import streamlit as st
    import pandas as pd
    import pydeck as pdk

    from urllib.error import URLError

    st.markdown("生成" & f"# {list(page_names_to_funcs.keys())[2]}")
    st.write(
        """ 在这里您可以通过上传清关资料线上生成相关的CI和PL """
    )

    @st.cache
    def from_data_file(filename):
        url = (
                "http://raw.githubusercontent.com/streamlit/"
                "example-data/master/hello/v1/%s" % filename
        )
        return pd.read_json(url)

    try:
        ALL_LAYERS = {
            "Bike Rentals": pdk.Layer(
                "HexagonLayer",
                data=from_data_file("bike_rental_stats.json"),
                get_position=["lon", "lat"],
                radius=200,
                elevation_scale=4,
                elevation_range=[0, 1000],
                extruded=True,
            ),
            "Bart Stop Exits": pdk.Layer(
                "ScatterplotLayer",
                data=from_data_file("bart_stop_stats.json"),
                get_position=["lon", "lat"],
                get_color=[200, 30, 0, 160],
                get_radius="[exits]",
                radius_scale=0.05,
            ),
            "Bart Stop Names": pdk.Layer(
                "TextLayer",
                data=from_data_file("bart_stop_stats.json"),
                get_position=["lon", "lat"],
                get_text="name",
                get_color=[0, 0, 0, 200],
                get_size=15,
                get_alignment_baseline="'bottom'",
            ),
            "Outbound Flow": pdk.Layer(
                "ArcLayer",
                data=from_data_file("bart_path_stats.json"),
                get_source_position=["lon", "lat"],
                get_target_position=["lon2", "lat2"],
                get_source_color=[200, 30, 0, 160],
                get_target_color=[200, 30, 0, 160],
                auto_highlight=True,
                width_scale=0.0001,
                get_width="outbound",
                width_min_pixels=3,
                width_max_pixels=30,
            ),
        }
        st.sidebar.markdown("### Map Layers")
        selected_layers = [
            layer
            for layer_name, layer in ALL_LAYERS.items()
            if st.sidebar.checkbox(layer_name, True)
        ]
        if selected_layers:
            st.pydeck_chart(
                pdk.Deck(
                    map_style="mapbox://styles/mapbox/light-v9",
                    initial_view_state={
                        "latitude": 37.76,
                        "longitude": -122.4,
                        "zoom": 11,
                        "pitch": 50,
                    },
                    layers=selected_layers,
                )
            )
        else:
            st.error("Please choose at least one layer above.")
    except URLError as e:
        st.error(
            """
            **This demo requires internet access.**
            Connection error: %s
        """
            % e.reason
        )


def data_frame_demo():
    import streamlit as st
    import pandas as pd
    import altair as alt

    from urllib.error import URLError

    st.markdown(f"# {list(page_names_to_funcs.keys())[3]}")
    st.write(
        """
        This demo shows how to use `st.write` to visualize Pandas DataFrames.
(Data courtesy of the [UN Data Explorer](http://data.un.org/Explorer.aspx).)
"""
    )

    @st.cache
    def get_UN_data():
        AWS_BUCKET_URL = "http://streamlit-demo-data.s3-us-west-2.amazonaws.com"
        df = pd.read_csv(AWS_BUCKET_URL + "/agri.csv.gz")
        return df.set_index("Region")

    try:
        df = get_UN_data()
        countries = st.multiselect(
            "Choose countries", list(df.index), ["China", "United States of America"]
        )
        if not countries:
            st.error("Please select at least one country.")
        else:
            data = df.loc[countries]
            data /= 1000000.0
            st.write("### Gross Agricultural Production ($B)", data.sort_index())

            data = data.T.reset_index()
            data = pd.melt(data, id_vars=["index"]).rename(
                columns={"index": "year", "value": "Gross Agricultural Product ($B)"}
            )
            chart = (
                alt.Chart(data)
                    .mark_area(opacity=0.3)
                    .encode(
                    x="year:T",
                    y=alt.Y("Gross Agricultural Product ($B):Q", stack=None),
                    color="Region:N",
                )
            )
            st.altair_chart(chart, use_container_width=True)
    except URLError as e:
        st.error(
            """
            **This demo requires internet access.**
            Connection error: %s
        """
            % e.reason
        )


page_names_to_funcs = {
    "公司介绍": intro,
    "清关资料": custom_invoice,
    "海关码": mapping_demo,
    "空运提货": data_frame_demo
}

demo_name = st.sidebar.selectbox("请选择服务", page_names_to_funcs.keys())
page_names_to_funcs[demo_name]()
