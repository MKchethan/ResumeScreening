from flask import Flask, render_template, send_from_directory, request
import json
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'


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

    print(a_list)

    jd = a_list[0]
    res = a_list[1]

    jd_ = [' '.join(jd)]
    res_ = [' '.join(res)]

    X_list = word_tokenize(jd_[0])
    Y_list = word_tokenize(res_[0])
    print(X_list)
    print(Y_list)
    # sw contains the list of stopwords
    sw = stopwords.words('english')
    l1 = []
    l2 = []

    # remove stop words from the string
    X_set = {w for w in X_list if not w in sw}
    Y_set = {w for w in Y_list if not w in sw}

    # form a set containing keywords of both strings
    rvector = X_set.union(Y_set)
    for w in rvector:
        if w in X_set:
            l1.append(1)  # create a vector
        else:
            l1.append(0)
        if w in Y_set:
            l2.append(1)
        else:
            l2.append(0)
    c = 0
    print("r", rvector)
    # cosine formula
    for i in range(len(rvector)):
        c += l1[i] * l2[i]
    cos_sim = c / float((sum(l1) * sum(l2)) ** 0.5)

    cos_sim = (cos_sim) * 100
    cos_sim = '{:.1f}'.format(cos_sim)
    cos_sim = float(cos_sim)
    status = []

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
    return (dict_)


if __name__ == '__main__':
    app.run(debug=True)

