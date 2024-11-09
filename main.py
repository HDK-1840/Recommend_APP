import streamlit as st
import pymysql
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from io import BytesIO
from PIL import Image
import pandas as pd


# 数据库连接函数
def get_db_connection():
    return pymysql.connect(
        host="rm-2ze8ji3n1cri7wa6sqo.mysql.rds.aliyuncs.com",
        port=3306,
        user="HDK1840",
        password="Hdk184018401840",
        database="app_use",
        cursorclass=pymysql.cursors.DictCursor
    )


# 创建results表函数
def create_results_table_if_not_exists():
    connection = get_db_connection()
    cursor = connection.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS results (
        id INT AUTO_INCREMENT PRIMARY KEY,
        gender VARCHAR(10),
        age INT,
        region VARCHAR(50),
        vehicle_types TEXT,
        power_types TEXT,
        budget_min INT,
        budget_max INT,
        odo_range INT,
        charge_time FLOAT,
        space_score INT,
        battery_score INT,
        exterior_score INT,
        interior_score INT,
        driving_score INT,
        intelligence_score INT,
        cost_performance_score INT,
        q1 INT,
        q2 INT,
        q3 INT,
        q4 INT,
        q5 INT,
        q6 INT,
        q7 INT,
        q8 INT,
        q9 INT,
        q10 INT,
        q11 INT,
        q12 INT,
        q13 INT
    )
    """
    cursor.execute(create_table_query)
    connection.commit()
    connection.close()


# 初始化session_state
if 'submitted' not in st.session_state:
    st.session_state['submitted'] = False
if 'recommendations' not in st.session_state:
    st.session_state['recommendations'] = None
if 'feedback_submitted' not in st.session_state:
    st.session_state['feedback_submitted'] = False

# 设置标题和问卷内容
st.markdown("<h1 style='text-align: center; font-weight: bold; font-size: 24px; color: #3498db;'>"
            "新能源汽车推荐系统体验"
            "</h1>", unsafe_allow_html=True)
st.markdown("###### 本团队开发了一款新能源汽车推荐系统，欢迎有购车需求的朋友前来体验，并提供宝贵的评价和建议！")
st.markdown("此推荐系统旨在通过问卷的方式主动获取消费者对新能源汽车的需求特征，根据需求特征为消费者推荐尽可能满足其需求的车型。")

# **使用说明部分**
with st.expander("使用说明", expanded=True):
    st.markdown("""
    ##### 请按照以下步骤完成您的用车需求提交及反馈：
    
    1. **填写下方的用车需求表单**。
    2. 填写完成后，点击 **“提交您的用车需求”** 按钮。
    3. **稍等几秒钟**，下滑页面查看系统推荐的结果。
    4. 根据您的使用体验，**填写推荐结果下方的体验评价问卷**。
    5. 点击 **“提交反馈”** 完成整个流程。
    """)

# **需求获取部分**
with st.expander("需求获取", expanded=True):
    st.markdown("###### 请回答以下问题，描述您对车型要求的基本信息")

    # 您的性别 (选择题)
    gender = st.selectbox("您的性别", ["请选择", "男", "女"])

    # 您的年龄 (填空题)
    age = st.number_input("您的年龄", min_value=1, max_value=100, step=1)

    # 您所生活的地区
    provinces = ["请选择", "北京市", "上海市", "天津市", "重庆市", "河北省", "山西省",
                 "辽宁省", "吉林省", "黑龙江省", "江苏省", "浙江省", "安徽省", "福建省",
                 "江西省", "山东省", "河南省", "湖北省", "湖南省", "广东省", "海南省",
                 "四川省", "贵州省", "云南省", "陕西省", "甘肃省", "青海省", "内蒙古自治区",
                 "广西壮族自治区", "西藏自治区", "宁夏回族自治区", "新疆维吾尔自治区",
                 "香港特别行政区", "澳门特别行政区", "台湾省"]
    region = st.selectbox("您所生活的地区", provinces)

    # 您偏好的车型级别 (多选题)
    vehicle_types = {
        "大型车": "5座，高端商务",
        "中大型车": "5座，高端商务",
        "中型车": "5座，家庭、商务通勤",
        "小型车": "4-5座，城市代步",
        "微型车": "2-4座，城市代步",
        "紧凑型车": "5座，家庭或个人代步",
        "大型SUV": "7-8座，越野、商务接待",
        "中大型SUV": "7座，家庭或商务用车",
        "中型SUV": "5-7座，家用及长途旅行",
        "小型SUV": "5座，城市通勤、轻度越野",
        "紧凑型SUV": "5座，城市通勤及家庭用",
        "中大型MPV": "7-9座，商务接待",
        "中型MPV": "6-7座，商务或家庭代步",
        "紧凑型MPV": "5-7座，家庭或个人代步",
        "跑车": "2座，运动驾驶",
        "微面": "5-7座，短途物流、小型运输",
        "微卡": "2-3座，小型货物运输",
        "轻客": "9-15座，载客或小型物流",
        "皮卡": "2-5座，货物运输及多用途"
    }

    vehicle_options = [f"{vehicle_type} ({description})" for vehicle_type, description in vehicle_types.items()]
    selected_vehicle_types = st.multiselect("您偏好的车型级别(可多选)", vehicle_options)

    # 您对新能源汽车的动力类型更倾向于 (多选题)
    power_types = {
        "纯电动": "仅用电池驱动",
        "增程式": "电驱为主，内燃机发电增程",
        "插电式混合动力": "短途电驱长途油驱"
    }
    power_options = [f"{power_type} ({description})" for power_type, description in power_types.items()]
    selected_power_types = st.multiselect("您对新能源汽车的动力类型更倾向于(可多选)", power_options)

    # 您的购车预算范围 (数值范围选择题)
    st.session_state['budget_min'], st.session_state['budget_max'] = st.slider(
        "您的购车预算范围 (单位：万元)", min_value=2, max_value=140, value=(2, 140), step=1
    )
    budget_min = st.session_state['budget_min']
    budget_max = st.session_state['budget_max']

    # 您期望的新能源汽车续航里程 (数值范围选择题)
    ODO_range = st.number_input("您可接受的新能源汽车续航里程最低为 (单位：公里)(请输入40到1000之间的数字)",
                                min_value=40, max_value=1000, value=40, step=10)

    # 您可接受的充满电的时间 (单个数字选择题)
    charge_time = st.number_input("您可接受的充满电的用时最长为 (单位：小时)(请输入0.2到15之间的数字)",
                                  min_value=0.2, max_value=15.0, value=15.0, step=0.1)

    # 车型特征重要程度评分部分
    st.markdown("<h6 style='text-align: left;'>请回答以下问题，描述车型各个特征的表现对您的重要程度。</h6>",
                unsafe_allow_html=True)
    st.markdown("<p style='font-size: 14px; text-align: left;'>"
                "请注意，您只能选择0到10的整数。"
                "给出的分数越接近0，代表该特征表现对您越不重要；给出的分数越接近10，代表该特征表现对您越重要。"
                "并且为了凸显出车型的各个特征表现在您心中的重要程度的不同，以下七个问题您需要共计给出50分。</p>",
                unsafe_allow_html=True)

    # 初始化每个特征的选择分数
    importance_values = {}
    for label in ["空间表现", "电池续航表现", "外观设计", "内饰设计", "驾驶质感", "智能系统", "性价比"]:
        importance_values[label] = st.radio(
            f"{label} (0-10分)",
            list(range(11)),  # 0-10的选项
            index=0,
            horizontal=True  # 设置选项为水平排列
        )

    # 计算总分数
    total_score = sum(importance_values.values())
    st.markdown(f"##### 当前给出的分数总和：{total_score} 分")

    # 提示总分是否符合要求
    if total_score != 50:
        st.error("分数总和必须等于50分，请调整打分。")

    all_answered = (
            gender != "请选择" and
            region != "请选择" and
            selected_vehicle_types and
            selected_power_types and
            total_score == 50
    )

    # 提交需求按钮
    if st.button("提交您的用车需求", disabled=not all_answered):
        st.success("请稍等几秒，下划查看推荐结果并根据推荐结果及您的使用感受完成下面的试用反馈~")

        selected_vehicle_types = [item.split(" ")[0] for item in selected_vehicle_types]
        selected_power_types = [item.split(" ")[0] for item in selected_power_types]
        demand_vector = np.array(list(importance_values.values()))

        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM digital_twins_model_table")
        all_models = cursor.fetchall()
        db.close()

        df = pd.DataFrame(all_models)


        def filter_and_get_top(df, filter_col, min_val=None, max_val=None):
            if min_val is not None and max_val is not None:
                df = df[(df[filter_col] >= min_val) & (df[filter_col] <= max_val)]
            elif max_val is not None:
                df = df[df[filter_col] <= max_val]
            return df if len(df) >= 10 else None


        def filter_and_get_top_1(df, filter_col, max_val=None):
            if max_val is not None:
                df = df[df[filter_col] <= max_val]
            return df if len(df) >= 10 else None


        def filter_and_get_top_2(df, filter_col, min_val=None):
            if min_val is not None:
                df = df[df[filter_col] >= min_val]
            return df if len(df) >= 10 else None


        filtered_df = df.copy()
        previous_df = filtered_df

        temp_df = filter_and_get_top(filtered_df, "corresponding_guide_price_num", budget_min, budget_max)
        if temp_df is not None and len(temp_df) >= 10:
            previous_df = temp_df
            filtered_df = temp_df

        temp_df = filter_and_get_top_2(filtered_df, "ODO_num", min_val=ODO_range)
        if temp_df is not None and len(temp_df) >= 10:
            previous_df = temp_df
            filtered_df = temp_df

        temp_df = filtered_df[filtered_df["vehicle_model_level"].isin(selected_vehicle_types)]
        if not temp_df.empty and len(temp_df) >= 10:
            previous_df = temp_df
            filtered_df = temp_df

        temp_df = filtered_df[filtered_df["corresponding_type"].isin(selected_power_types)]
        if not temp_df.empty and len(temp_df) >= 10:
            previous_df = temp_df
            filtered_df = temp_df

        temp_df = filter_and_get_top_1(filtered_df, "fastest_charging_time", max_val=charge_time)
        if temp_df is not None and len(temp_df) >= 10:
            previous_df = temp_df
            filtered_df = temp_df

        filtered_df = previous_df

        model_vectors = filtered_df[["Space_sentiment", "Battery_life_sentiment", "Exterior_sentiment",
                                     "Interior_sentiment", "Driving_experience_sentiment",
                                     "Intelligence_sentiment", "Cost_performance_sentiment"]].to_numpy()
        similarities = cosine_similarity([demand_vector], model_vectors)[0]
        filtered_df["similarity"] = similarities

        # 存储推荐结果到session_state
        st.session_state.recommendations = filtered_df.nlargest(10, "similarity").to_dict("records")
        st.session_state.submitted = True

# 结果和反馈问卷展示
if st.session_state.submitted:
    with st.expander("推荐结果", expanded=True):
        st.markdown("如果以下推荐结果中没有完全符合您所设条件的车型，代表车型库中不存在完全符合您所设条件的车型，"
                    "您可适当调整以上需求设置并再次提交需求查看推荐结果。")
        st.markdown("口碑情感值用于衡量该车型在某一特征上的网络评价正向程度。"
                    "数值越接近1，表示评论越积极正面；数值越接近0，表示评论越消极负面。")
        for row in st.session_state.recommendations:
            st.write(
                f"**推荐车型**: {row['brand_name']} {row['vehicle_model_name']} {row['detail_vehicle_model_name']}")
            st.write(f"**车型级别**: {row['vehicle_model_level']}")
            st.write(f"**动力类型**: {row['corresponding_type']}")
            st.write(f"**参考价格**: {row['corresponding_guide_price']}")
            st.write(f"**续航里程**: {row['ODO']}")
            st.write(f"**充电时间**: {row['charging_time']}")
            st.write(f"**空间表现口碑情感值**: {row['Space_sentiment']:.3f}")
            st.write(f"**电池续航表现口碑情感值**: {row['Battery_life_sentiment']:.3f}")
            st.write(f"**外观设计口碑情感值**: {row['Exterior_sentiment']:.3f}")
            st.write(f"**内饰设计口碑情感值**: {row['Interior_sentiment']:.3f}")
            st.write(f"**驾驶质感口碑情感值**: {row['Driving_experience_sentiment']:.3f}")
            st.write(f"**智能系统口碑情感值**: {row['Intelligence_sentiment']:.3f}")
            st.write(f"**性价比口碑情感值**: {row['Cost_performance_sentiment']:.3f}")
            image_data = row["pictures"]
            image = Image.open(BytesIO(image_data))
            st.image(image,
                     caption=f"{row['brand_name']} {row['vehicle_model_name']} {row['detail_vehicle_model_name']}",
                     use_column_width=True)

    with st.expander("推荐系统体验评价问卷", expanded=True):
        st.markdown("请您根据以下问题评价该推荐系统的体验。")
        st.markdown("以下题目，您给出的数字越接近10代表您越同意题目观点；您给出的数字越接近0代表您越不同意题目观点。")

        with st.form("feedback_form"):
            tam_questions = {
                "我觉得这个推荐系统能够提高我选择合适新能源汽车的效率。": 10,
                "使用这个推荐系统可以让我的购车决策更明智。": 10,
                "这个推荐系统对我来说是一个有价值的工具。": 10,
                "推荐系统帮助我节省了时间，使我更快速地找到心仪的车型。": 10,
                "总体来说，我认为这个推荐系统在购车决策中非常有帮助。": 10,
                "我觉得这个推荐系统非常易于使用。": 10,
                "在使用推荐系统的过程中，我几乎不需要学习新的知识或技巧。": 10,
                "我认为在推荐系统中查看推荐结果非常简单。": 10,
                "我觉得操作这个推荐系统不需要耗费太多精力。": 10,
                "总体来说，我觉得推荐系统的操作是轻松愉快的。": 10,
                "我很可能会将这个新能源汽车推荐系统推荐给朋友或家人。": 10,
                "相较于之前我使用过的汽车推荐系统，我更愿意使用本次试用的系统。": 10,
                "在我得到的10个推荐车型中，我对其中的几个车型感兴趣？": 10
            }

            responses = {}
            for question in tam_questions.keys():
                responses[question] = st.radio(
                    question,
                    list(range(11)),  # 0-10 的选项
                    index=10,
                    horizontal=True  # 设置选项为水平排列
                )

            submitted = st.form_submit_button("提交反馈")

            # 反馈提交处理
            if submitted:
                st.success("感谢您的参与！")
                st.session_state.feedback_submitted = True  # 使用session_state保持反馈提交状态

                # 检查并创建results表
                create_results_table_if_not_exists()

                # 存储反馈信息
                with get_db_connection() as connection:
                    cursor = connection.cursor()
                    insert_query = """
                        INSERT INTO results (gender, age, region, vehicle_types, power_types, budget_min, budget_max, 
                                             odo_range, charge_time, space_score, battery_score, exterior_score, 
                                             interior_score, driving_score, intelligence_score, cost_performance_score, 
                                             q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                                %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_query, (
                        gender, age, region, ', '.join(selected_vehicle_types), ', '.join(selected_power_types),
                        budget_min, budget_max, ODO_range, charge_time, importance_values["空间表现"],
                        importance_values["电池续航表现"], importance_values["外观设计"], importance_values["内饰设计"],
                        importance_values["驾驶质感"], importance_values["智能系统"], importance_values["性价比"],
                        responses["我觉得这个推荐系统能够提高我选择合适新能源汽车的效率。"],
                        responses["使用这个推荐系统可以让我的购车决策更明智。"],
                        responses["这个推荐系统对我来说是一个有价值的工具。"],
                        responses["推荐系统帮助我节省了时间，使我更快速地找到心仪的车型。"],
                        responses["总体来说，我认为这个推荐系统在购车决策中非常有帮助。"],
                        responses["我觉得这个推荐系统非常易于使用。"],
                        responses["在使用推荐系统的过程中，我几乎不需要学习新的知识或技巧。"],
                        responses["我认为在推荐系统中查看推荐结果非常简单。"],
                        responses["我觉得操作这个推荐系统不需要耗费太多精力。"],
                        responses["总体来说，我觉得推荐系统的操作是轻松愉快的。"],
                        responses["我很可能会将这个新能源汽车推荐系统推荐给朋友或家人。"],
                        responses["相较于之前我使用过的汽车推荐系统，我更愿意使用本次试用的系统。"],
                        responses["在我得到的10个推荐车型中，我对其中的几个车型感兴趣？"]
                    ))
                    connection.commit()
