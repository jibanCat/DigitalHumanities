import numpy as np
import pandas as pd
from hanziconv import HanziConv
import re

# Prior and Likelihood
place_prior = 0.3
likelihood = {"地名": 0.80,
              "方向": 0.75,
              "城鎮": 0.7, 
              "姓氏": 0.2, 
              "單位": 0.2,
              "數字": 0.2,
              "年號": 0.3, 
              "官名": 0.2,
              "經驗字": 0.4, 
              "不相干的字": 0.45}

# loading our own bag-of-words for place name
lsperson_excel = pd.ExcelFile("../SongShu/SongshuDH/lsperson - 法鼓山劉宋相關人名地名.xlsx")
df_place1 = pd.read_excel(lsperson_excel, "place")
place_excel = pd.ExcelFile("../SongShu/SongshuDH/劉宋地名與官名 2017-11-14.xlsx")
df_place2 = pd.read_excel(place_excel, "Places")
df_bureaucracy = pd.read_excel(place_excel, "Offices")
place_set = set(df_place2.Name.values.tolist() + df_place1.placeName.values.tolist())

# cleaning place names
place_set = set([p for p in place_set if len(re.findall(r"[a-zA-Z.\-]", p)) == 0])

# loading emperical bag-of-words
direction_bag = "至于於向破奔鎮入征"
place_unit = "鄉市縣鎮郡城州"
unit = "年載月日初中末閏"
number    = "是元正𨳝一二三四五六七八九十廿卅" # MARKUS 大概是用這行判斷數字
year_name = {"建國","元統","元貞","大德","天曆","天順","延祐","泰定","皇慶","至元","至大","至正","至治","至順","致和","永興","太清","永樂","元璽","光壽","建熙","壽光","延初","皇始","乾德","光天","廣大","通正","佐初","光初","元徽","大明","孝建","昇明","景和","景平","泰豫","保定","大成","大象","天和","宣政","建德","武成","乾興","元祐","元符","元豐","咸平","嘉祐","大中祥符","大觀","天聖","宣和","寶元","崇寧","康定","建中靖國","慶曆","政和","明道","景德","景祐","治平","淳化","熙寧","皇祐","端拱","紹聖","至和","至道","重和","雍熙","靖康","康應","康曆","應安","曆應","永德","觀應","承光","承和","承平","承玄","玄始","神璽","義和","乾佑","天會","天福","建福","德興","神曆","大延","天安","天興","天賜","太平真君","太延","太昌","始光","孝昌","延和","延昌","承明","普泰","景明","正光","正平","武泰","泰常","熙平","登國","皇興","神䴥","神瑞","神龜","興光","興安","乾明","大寧","天統","德昌","武平","河清","皇建","隆化","乾貞","天祚","武義","順義","頒義","交泰","保大","升元","昇元","乾道","咸淳","嘉定","嘉泰","嘉熙","寶慶","寶祐","建炎","德祐","慶元","景定","景炎","淳熙","淳祐","祥興","端平","紹定","紹熙","開慶","開禧","隆興","庚寅","弘光","永曆","紹武","隆武","興國","中大同","中大通","大同","大寶","大通","天成","天正","天監","天鑑","承聖","普通","紹泰","弘昌","乾亨","乾和","大有","應乾","白龍","太上","燕王","延興","永明","永泰","隆昌","保貞","太平興國","寶大","寶太","寶正","寶貞","廣初","建隆","正明","開寶","上元","中和","乾元","乾寧","乾封","乾甯","乾符","儀鳳","先天","光化","光啟","光宅","光慶","咸亨","咸通","唐元","唐安","唐興","唐隆","嗣聖","垂拱","大中","大和","大曆","大順","天寶","天復","天祐","太極","寶應","寶曆","寶歷","廣德","廣明","建中","弘道","文德","文明","明慶","景福","景雲","景龍","會昌","正觀","武德","永崇","永徽","永淳","永貞","永隆","神龍","總章","興元","調露","貞元","貞觀","載初","長慶","開元","開成","開耀","顯慶","麟德","龍朔","龍紀","嘉靖","天啟","宣德","崇禎","建文","弘治","成化","景泰","正統","泰昌","洪武","洪熙","萬曆","隆慶","建陽","乾隆","光緒","同治","咸豐","嘉慶","宣統","崇德","康熙","道光","雍正","順治","天眷","天輔","崇慶","承安","收國","明昌","正大","正豐","正隆","泰和","皇統","至寧","興定","貞祐","開興","光武","隆熙","乾統","保寧","咸雍","壽昌","壽隆","大平","大康","天慶","天祿","天贊","天顯","應曆","會同","泰安","清寧","神冊","統和","重熙","開泰","嘉禾","天冊","天璽","天紀","太元","太平","寶鼎","建衡","永安","神鳳","赤烏","鳳凰","黃武","廣順","顯德","同光","應順","淸泰","清泰","長興","開運","乾化","貞明","開平","鳳曆","龍德","承康","龍飛","乾祐","光始","建始","燕元","長樂","弘始","洪始","白雀","皇初","廣政","明德","泰寧","天命","天聰","政開","水德萬歲","聖冊","虎泰","嘉寧","宣平","晏平","漢興","玉恒","玉衡","仁平","大昌","開國","鴻濟","地皇","天鳳","始建國","咸熙","太和","景元","景初","正元","正始","青龍","黃初","升平","咸和","咸安","咸康","大亨","太寧","太興","寧康","崇和","崇安","昇平","永昌","義熙","興寧","隆和","隆安","中平","元初","元和","元嘉","元興","光和","光熹","初平","和平","延光","延平","延康","延熹","建初","建和","建安","建寧","建康","建武中元","昭寧","本初","永元","永初","永和","永嘉","永壽","永寧","永平","永康","永建","永憙","永漢","永熹","漢安","熹平","章和","興平","陽嘉","元象","天平","武定","興和","永始","久視","大足","天冊萬歲","天授","如意","延載","神功","聖曆","萬歲登封","萬歲通天","證聖","長壽","長安","民國","元熙","光興","嘉平","建元","永鳳","河瑞","漢昌","麟嘉","定鼎","建光","神鼎","勝光","承陽","昌武","真興","鳳翔","龍升","中統","延熙","建興","景耀","炎興","章武","乾定","人慶","元德","光定","大慶","天佑垂聖","天佑民安","天儀治平","天安禮定","天授禮法延祚","天盛","天賜禮盛國慶","奲都","寶義","延嗣甯國","應天","拱化","正德","福聖承道","雍寧","顯道","光熙","咸寧","大安","太安","太康","太熙","永熙","泰始","大定","天保","廣運","嘉興","五鳳","元光","元壽","元始","元封","元平","元康","元延","元朔","元狩","元鳳","元鼎","初元","初始","地節","天漢","太初","太初元將","太始","始元","始建","居攝","建昭","征和","本始","永光","河平","甘露","神爵","竟寧","綏和","陽朔","鴻嘉","黃龍","中興","建平","建明","建武","昌平","更始","燕興","建宏","建弘","建義","永宏","永弘","永洪","咸清","天禧","崇福","康國","延慶","紹興","大統","天德","通文","龍啟","光大","天嘉","天康","太建","永定","禎明","至德","仁壽","大業","義寧","開皇","延壽","光德"}
emperical_chars = "彼令生北哀帝王國士歸夫已以之大為"
bureaucracy_set = set(df_bureaucracy.Name.values.tolist())

# exclude the rare family names
family_name = pd.read_excel("Chinese_Family_Name（1k）.xlsx")
family_set = {HanziConv.toTraditional(n) for n,ref in zip(family_name.Nb, family_name.RealFre) if ref > 30}

# construct a dict for iterations
iterables  = {"地名": place_set,
              "方向": direction_bag,
              "城鎮": place_unit, 
              "姓氏": family_set, 
              "單位": unit, 
              "數字": number,
              "年號": year_name, 
              "官名": bureaucracy_set,
              "經驗字": emperical_chars, }


def update_feature_vector(phrase, feature_vector, feature_list, feature_name):
    """update the feature vector based on the list of features and a given phrase and 
    a given feature name"""
    for x in feature_list:
        if x in phrase:
            feature_vector[feature_name] += len(x)
            
    return feature_vector


def calc_posterior(feature_vector, likelihood, prior):
    """Calc the posterior using bayes theorem. 
    The assumption here is the naive bayes, so the prob of features 
    are independent. The joint prob of likelihood is a prod of individual
    feature prob."""
    positive_likelihood = prior * np.prod([
        likelihood[key]**hits for key, hits in feature_vector.items()
    ])
    negative_likelihood = (1 - prior) * np.prod([
        (1 - likelihood[key])**hits for key, hits in feature_vector.items()
    ])

    # Bayes theorem
    posterior = positive_likelihood / (positive_likelihood + negative_likelihood)
    return posterior

def update_place_feature_vector(place_phrase, feature_vector, iterables, ):
    """
    Update the place feature vector based on a given place phrase and a dict of 
    time phrase feature iterables. The definiation of feature_vector refer to `calc_place_posterior`.
    """
    irrelevant_phrase = place_phrase

    for key, iterable in iterables.items():
        update_feature_vector(
            place_phrase, feature_vector, iterable, key
        )

        # measure the length irrelevant phrase
        for x in iterable:
            if x in irrelevant_phrase:
                irrelevant_phrase = irrelevant_phrase.replace(x, "")

    feature_vector['不相干的字'] = len(irrelevant_phrase)
    return feature_vector

def calc_place_posterior(phrase, iterables=iterables, likelihood=likelihood, place_prior=place_prior):
    """Calc the posterior of a place phrase based on a given feature iterables and 
    a pre-defined likelehood model and a time words frequency prior.
    Current feature for time: 
        { "地名", "方向","城鎮", "姓氏", "單位", "年號", "數字", "經驗字", "不相干的字", "官名" }
    """
    feature_vector = {
        "地名": 0,
        "方向": 0,
        "城鎮": 0,
        "姓氏": 0,
        "單位": 0,
        "年號": 0,
        "數字": 0,
        "官名": 0,
        "經驗字":0,
        "不相干的字": 0}
    
    feature_vector = update_place_feature_vector(
        phrase, feature_vector, iterables
    )
    return calc_posterior(feature_vector, likelihood, place_prior)