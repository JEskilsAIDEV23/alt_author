import pandas as pd
import requests
import json

def libris(author_url):
    URL = f"http://libris.kb.se/xsearch?query={author_url}&format=json&n=50"
    df = pd.read_json(URL)
    df = df['xsearch']
    df = df['list']
    df = pd.json_normalize(df)
    df_out = df.loc[(df.type=='book')&(df.language=='swe')]
    df_libris = df_out.to_dict()
    return df_libris

def OL_1(author_url):
    url_OL1 = 'https://openlibrary.org/search/authors.json?q='+f'{author_url}'
    response = requests.get(url_OL1)
    url_OLD1 = response.json()
    url_OLD1 = url_OLD1['docs']
    df_OL = pd.json_normalize(url_OLD1)
    df_OL_out = df_OL.loc[0]
    df_OL_out
    OL = df_OL_out['key']
    top_work = df_OL['top_work']
    df_OL1_Dict = df_OL_out.to_dict()
    return OL, top_work, df_OL1_Dict

def OL_2(OL):
    url_OL2 = f'https://openlibrary.org/authors/{OL}.json'
    response = requests.get(url_OL2)
    url_OLD2 = response.json()
    df_OL2 = pd.json_normalize(url_OLD2)
    try:
        bio_OL = df_OL2.loc[0]['bio.value']
    except:
        bio_OL = 'No Bio Exist'
    viaf = df_OL2.loc[0]['remote_ids.viaf']
    isni = df_OL2.loc[0]['remote_ids.isni']
    return bio_OL, isni, viaf

def OL_3(OL):
    url_OL3 = f'https://openlibrary.org/authors/{OL}/works.json'
    response = requests.get(url_OL3)
    url_OLD3 = response.json()
    df_OL3 = pd.json_normalize(url_OLD3, record_path =['entries'])
    df_OL3['works'] = list(df_OL3.index)
    df_OL3['main_auth'] = list(df_OL3.index)
    df_OL3['auth'] = list(df_OL3.index)

    def replace_key(x):
        work = df_OL3.loc[x]['key'].replace('/works/','')
        return work

    def check_auth(x):
        main = df_OL3['authors'][x][0]['author']['key']
        return main

    def replace_auth_key(x):
        auth = df_OL3.loc[x]['main_auth'].replace('/authors/','')
        return auth

    df_OL3['works'] = df_OL3["works"].apply(lambda x=df_OL3.index: replace_key(x))
    df_OL3['main_auth'] = df_OL3["main_auth"].apply(lambda x=df_OL3.index: check_auth(x))
    df_OL3['auth'] = df_OL3["auth"].apply(lambda x=df_OL3.index: replace_auth_key(x))
    df_OL3_out = df_OL3[["works","auth","title","description","subjects","first_sentence.value"]]
    df_OL3_Dict = df_OL3_out.to_dict()
    return df_OL3_out

def OL4_Get(x):
    #url_OL4 = f"https://openlibrary.org/works/{x}.json"
    url_OL4 = f"https://openlibrary.org/works/{x}/editions.json"
    response = requests.get(url_OL4)
    url_OLD4 = response.json()
    df_OLD4 = pd.json_normalize(url_OLD4, record_path =['entries'])
    df_OLD4['book_id'] = df_OLD4['key'].str.replace('/books/', '')
    return df_OLD4

def OL4_isbn(df_OL3_out):
    isbn_dict = {}
    for i in df_OL3_out.index:
        try:
            df_OLD4 = OL4_Get(df_OL3_out.loc[i]['works'])
            isbn_dict[df_OL3_out.loc[i]['works']] = {}
            isbn_dict[df_OL3_out.loc[i]['works']]['book_id'] = df_OLD4['book_id'][0]
            isbn_dict[df_OL3_out.loc[i]['works']]['title'] = df_OLD4['title'][0]
            isbn_dict[df_OL3_out.loc[i]['works']]['isbn_10'] = 'none'
            isbn_dict[df_OL3_out.loc[i]['works']]['isbn_13'] = 'none'
            if isinstance(df_OLD4["book_id"], list):
                isbn_dict[df_OL3_out.loc[i]['works']]['book_id'] = df_OLD4['book_id'][0]
            else:
                isbn_dict[df_OL3_out.loc[i]['works']]['book_id'] = df_OLD4['book_id'][0]
            if 'isbn_10' in df_OLD4:
                if isinstance(df_OLD4["isbn_10"], list):
                    isbn_dict[df_OL3_out.loc[i]['works']]['isbn_10'] = df_OLD4['isbn_10'][0]
                else:
                    isbn_dict[df_OL3_out.loc[i]['works']]['isbn_10'] = df_OLD4['isbn_10'][0]
            if 'isbn_13' in df_OLD4:
                if isinstance(df_OLD4["isbn_13"], list):
                    isbn_dict[df_OL3_out.loc[i]['works']]['isbn_13'] = df_OLD4['isbn_13'][0]
                else:
                    isbn_dict[df_OL3_out.loc[i]['works']]['isbn_13'] = df_OLD4['isbn_13'][0]
        except:
            print('multiple editions of same book exists')
    return isbn_dict

author_url ='Astrid+Lindgren'
libris(author_url)
OL, top_work, df_OL1_Dict = OL_1(author_url)
OL_2(OL)
df_OL3_out = OL_3(OL)
OL4_isbn(df_OL3_out)

