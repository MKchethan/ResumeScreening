from flask import Flask, render_template, send_from_directory, request
import json
import re
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'static/'

model = SentenceTransformer('bert-base-nli-mean-tokens')


@app.route('/post_form', methods=['POST'])
def process_form():
    data = json.loads(request.data)

    keys = ['JD_YOE', 'JD_Skillset', 'JD_Desig']
    JD_dict = {x: data[x] for x in keys}

    keys = ['candi_YOE', 'candi_Skillset', 'candi_Desig']
    candi_dict = {x: data[x] for x in keys}

    candi_df = pd.DataFrame([candi_dict])
    JD_df = pd.DataFrame([JD_dict])

    df = pd.DataFrame(columns=["Years of Experience", "Skillset", "Designation"])
    JD_df.columns = ['Years of Experience', 'Skillset', 'Designation']
    candi_df.columns = ['Years of Experience', 'Skillset', 'Designation']
    df = pd.concat([df, JD_df, candi_df], axis=0)
    df.reset_index(inplace=True, drop=True)

    a_list = []
    for j in range((df.shape[0])):
        cur_row = []
        for k in range(df.shape[1]):
            cur_row.append(df.iat[j, k])
        a_list.append(cur_row)

    jd = a_list[0]
    res = a_list[1]

    jd_ = [' '.join(jd)]
    res_ = [' '.join(res)]
    print(jd_)
    print(res_)

    jd_enc = model.encode(jd_)
    res_enc = model.encode(res_)
    cos_sim = cosine_similarity(jd_enc, res_enc).tolist()[0]
    cos_sim = (cos_sim[0]) * 100
    cos_sim = '{:.1f}'.format(cos_sim)
    cos_sim = float(cos_sim)
    print(cos_sim)
    status = []
    # percent = int(input("Enter the threshold: "))
    if cos_sim >= 70:
        sta = "Selected"
        status.append(sta)

    elif cos_sim > 50 and cos_sim < 70:
        sta = "Hold"
        status.append(sta)
    else:
        sta = "Rejected"
        status.append(sta)

    remarks = []
    if status[0] == "Selected":
        rem_ = "JD is matched with Candidate's skills set"
        remarks.append(rem_)
    elif status[0] == "Hold":
        rem_ = "JD is partially matched with Candidate's skills set"
        remarks.append(rem_)
    else:
        rem_ = "JD is not matched with Candidate's skills set"
        remarks.append(rem_)

    name = data.get("candi_Name")
    jd_num = data.get("JD_Number")

    dict_ = {"Name": name, "JD_Number": jd_num, "Percentage%": cos_sim, "Status": status[0], "Remarks": remarks[0]}
    print(dict_)
    return (dict_)


if __name__ == '__main__':
    app.run(debug=True)

