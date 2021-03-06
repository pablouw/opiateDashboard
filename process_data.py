import itertools
import pandas as pd
import numpy as np
import pathlib
import sqlalchemy
import sys


def calculate_parameters(data):
    data['rrt'] = data['RT'] / data['is_RT']
    data['ion_ratio'] = data['peak_area'] / data['confirming_ion_area']
    data[['rrt', 'ion_ratio']] = data[['rrt', 'ion_ratio']].apply(pd.to_numeric)
    data = data.replace({'rrt': 0}, np.nan)
    return data

def read_sql_results(db):
    if db == 'sqlite':
        engine = sqlalchemy.create_engine('sqlite:////Path/to/file/opiates.db')
    elif db == 'postgresql':
        engine = sqlalchemy.create_engine('postgresql://username:password@localhost/opiates')
    else:
        print('No appropriate db selected. Program will exit.')
        sys.exit()
    conn = engine.connect()
    df = pd.read_sql_query("""
    SELECT *
    FROM  "results"
    """, conn)
    
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
    df = df[df['sample_type'].notna()]
    df = calculate_parameters(df)
    # build IS-Compound dict
    sub_df = df.drop_duplicates(subset=['compound_id'], keep='first')
    intstd_dict = dict(zip(sub_df['compound'], sub_df.int_std))
    return df, intstd_dict

   
def read_data_csv(file):
    opiate_df = pd.read_csv(file)
    opiate_df['Date'] = pd.to_datetime(opiate_df['Date'], format='%Y-%m-%d')
    opiate_df = opiate_df[opiate_df['sample_type'].notna()]
    opiate_df = calculate_parameters(opiate_df)
    # build IS-Compound dict
    sub_df = opiate_df.drop_duplicates(subset=['compound_id'], keep='first')
    intstd_dict = dict(zip(sub_df['compound'], sub_df.int_std))
    return opiate_df, intstd_dict


def create_qa_dict(frame):
    columns = ['compound_code', 'qa_id', 'amr_low', 'amr_high', 'signoise', 'int_std_peak_area',
               'spike_low', 'spike_high', 'straight_metab_check', 'is_spike_recovery', 'delta']
    frame = frame.drop(columns, axis=1, errors='ignore')
    test = frame.groupby('qa_compound').apply(lambda x: x.set_index('qa_compound').to_dict(orient='index'))
    qadict = dict()
    for i in test:
        for k, v in i.items():
            qadict[k] = v
    return qadict


def read_qa(qa_file, diction):
    qa_df = pd.read_csv(qa_file)
    cols = ['ion_ratio_avg', 'ion_ratio_cv', 'rel_reten_low', 'rel_reten_high', 'rel_reten',
            'amr_low', 'amr_high', 'signoise_stda']
    qa_df['rel_reten'] = (qa_df['rel_reten_high'] + qa_df['rel_reten_low']) / 2
    qa_df[cols] = qa_df[cols].apply(pd.to_numeric)
    qa_df ['delta'] = qa_df['ion_ratio_avg'] * qa_df['ion_ratio_cv']
    qa_df['ion_ratio_low'] = qa_df['ion_ratio_avg'] - qa_df['delta']
    qa_df['ion_ratio_high'] = qa_df['ion_ratio_avg'] + qa_df['delta']
    qa_dict = create_qa_dict(qa_df)

    qa_cop = qa_df.copy()
    qa_cop['int_std'] = qa_cop['qa_compound'].map(diction)
    qa_intstd_dict = dict(zip(qa_cop.int_std, qa_cop.int_std_peak_area))
    del qa_cop
    return qa_dict, qa_intstd_dict


def create_sample_type_list(sample_type_list):
    combos = list()
    for L in range(1, len(sample_type_list)):
        for subset in itertools.combinations(sample_type_list, L):
            combos.append(subset)
    for c in combos:
        if len(c) == 1:
            continue
        else:
            item = str(c[0]) + "|" + str(c[1])
            sample_type_list.append(item)
    sample_type_list.append('All')
    return sample_type_list


actual_dir = pathlib.Path().absolute()
df, compound_dict = read_data_csv(f'{actual_dir}/dashboard_files/sample_data.csv')
qa_compound_dict, int_std_dict = read_qa(f'{actual_dir}/dashboard_files/qa.csv',
                                         compound_dict)
available_samples = create_sample_type_list(df['sample_type'].unique().tolist())
