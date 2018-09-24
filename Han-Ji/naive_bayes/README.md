# Naive Bayes for Tagging

> Hackmd page for this README https://hackmd.io/s/SkW-NSRZX

Chinese historian tagging platform, like MARKUS, could not return a probability. Tagging platform expected users (historian, or humanities researcher) to use their knowledge to correct the tags manually. However, these platforms do encode some domain knowledge to classify tags (官名、地名、時間名、人名). So, why not encode the pre-defined features into a belief of a term being a tag?

Without putting too much ML techniques on it, we can simply use Bayes rule to encode our domain knowledge and also return a probability of a term being classified as a tag. We will use classifying a time phrase as an example. 

## Tag a time phrase

For example, consider the case to tag a time phrase:

```python
# it is a standard form of a time phrase in classical text
"隆安三年十一月"
```

We can see there are some properties to identify in this phrase: year name 年號 (隆安), number 數字 (三、十一), unit 單位 (年、月). For this phrase, we can calculate the posterior probability of the phase is a time phrase given this phrase

<a href="https://www.codecogs.com/eqnedit.php?latex=P(time&space;\mid&space;phrase)&space;=&space;\frac{P(phrase&space;\mid&space;time)&space;\times&space;P(time)&space;}{&space;P(phrase)}" target="_blank"><img src="https://latex.codecogs.com/gif.latex?P(time&space;\mid&space;phrase)&space;=&space;\frac{P(phrase&space;\mid&space;time)&space;\times&space;P(time)&space;}{&space;P(phrase)}" title="P(time \mid phrase) = \frac{P(phrase \mid time) \times P(time) }{ P(phrase)}" /></a>

### Naive Bayes assumption

By Naive Bayes assumption, the likelehood P(phrase | time) can be expressed a product of individual probability of each feature:

<a href="https://www.codecogs.com/eqnedit.php?latex=$$P(phrase&space;\mid&space;time)&space;=&space;P(features&space;\mid&space;time)&space;=&space;P(feature_1&space;\mid&space;time)&space;\times&space;...&space;\times&space;P(feature_n&space;\mid&space;time)$$" target="_blank"><img src="https://latex.codecogs.com/gif.latex?$$P(phrase&space;\mid&space;time)&space;=&space;P(features&space;\mid&space;time)&space;=&space;P(feature_1&space;\mid&space;time)&space;\times&space;...&space;\times&space;P(feature_n&space;\mid&space;time)$$" title="$$P(phrase \mid time) = P(features \mid time) = P(feature_1 \mid time) \times ... \times P(feature_n \mid time)$$" /></a>

For a time phrase in a classical Chinese text, we could build a feature vector based on our experience:


| is time | year name 年號 | number 數字 | unit 單位 | seasons 季節 | years 干支 | last name 姓氏 | irrelevant chars 不相干的字 | 
| ----    | ---  | --- | --- | --- | --- | --- |  ----     |
| +       | 0.8  | 0.6 | 0.7 | 0.6 | 0.8 | 0.2 | 0.45      |
| -       | 0.2  | 0.4 | 0.3 | 0.4 | 0.2 | 0.8 | 0.55      |

the probabilities are given by the model in my brain. We can justify this model by collection large enough of time phrases in the future usage.

The normalization factor is following

<a href="https://www.codecogs.com/eqnedit.php?latex=P(phrase)&space;=&space;P(time)&space;\prod{&space;P(feature_n&space;\mid&space;time)}&space;&plus;&space;P(\sim&space;time)&space;\prod{&space;P(feature_n&space;\mid&space;\sim&space;time)}" target="_blank"><img src="https://latex.codecogs.com/gif.latex?P(phrase)&space;=&space;P(time)&space;\prod{&space;P(feature_n&space;\mid&space;time)}&space;&plus;&space;P(\sim&space;time)&space;\prod{&space;P(feature_n&space;\mid&space;\sim&space;time)}" title="P(phrase) = P(time) \prod{ P(feature_n \mid time)} + P(\sim time) \prod{ P(feature_n \mid \sim time)}" /></a>

Therefore, Bayes rule give you the posterior:

<a href="https://www.codecogs.com/eqnedit.php?latex=P(time&space;\mid&space;phrase)&space;=&space;\frac{P(time)&space;\prod{&space;P(feature_n&space;\mid&space;time)}}{P(time)&space;\prod{&space;P(feature_n&space;\mid&space;time)}&space;&plus;&space;P(\sim&space;time)&space;\prod{&space;P(feature_n&space;\mid&space;\sim&space;time)}}" target="_blank"><img src="https://latex.codecogs.com/gif.latex?P(time&space;\mid&space;phrase)&space;=&space;\frac{P(time)&space;\prod{&space;P(feature_n&space;\mid&space;time)}}{P(time)&space;\prod{&space;P(feature_n&space;\mid&space;time)}&space;&plus;&space;P(\sim&space;time)&space;\prod{&space;P(feature_n&space;\mid&space;\sim&space;time)}}" title="P(time \mid phrase) = \frac{P(time) \prod{ P(feature_n \mid time)}}{P(time) \prod{ P(feature_n \mid time)} + P(\sim time) \prod{ P(feature_n \mid \sim time)}}" /></a>

## Examples:

```python
from naive_bayes_time import calc_time_posterior

# a standard time phrase in classical texts
calc_time_posterior("隆安三年十一月") 
# 0.8873239436619719

# a time phrase with a impossible year name
calc_time_posterior("張無忌帝一億年二十三月子丑") 
# 0.4697469397630935

# not a time phrase
calc_time_posterior("司馬大人是個人物，並不只是司馬大人是個人物") 
# 0.002414582912800456
```

So, we are 89% certain that `"隆安三年十一月"` is a time phrase, 0.2% certain `"司馬大人是個人物，並不只是司馬大人是個人物"` is a time phrase, and 47% certain `"張無忌帝一億年二十三月子丑"` is a time phrase. In practice, Navie Bayes allow us to pay more attention to `"張無忌帝一億年二十三月子丑"` phrase to further justify whether it is a time phrase or not.

> NOTE: 年號、數字、單位、季節 bags are copied from MARKUS, thanks MARKUS!

## Tag a Place Name (Table)

| is place | 地名 | 方向 | 城鎮 | 單位 | 數字 |  年號   | 經驗字 |
| ----    | ---  | --- | --- | --- | --- | ---      | --- |
| +       | 0.8  | 0.75 | 0.7 | 0.2 | 0.2 | 0.3     | 0.4 |
| -       | 0.2  | 0.25 | 0.3 | 0.8 | 0.8 | 0.7     | 0.6 |

## Naive Class for Single Phrase

```python
from Naive import NaiveBayes

names = ['年號', '數字', '單位', '季節', '干支'] # name of features
iterables = [['清寧', '大業', '太平', '中興', ...], '是元正𨳝一二三四五六七八九十廿卅', '年載月日初中末閏', '春夏秋冬', ['乙卯', '壬辰', '乙亥', '己亥', '戊午', '丙午', '丙寅', '癸酉', '庚辰', '乙丑', '癸亥', '己卯', '己巳', '丁卯', '辛亥', '丙辰', '己未', '戊申', '壬子', '癸丑', '丙子', '戊寅', '辛卯', '辛未', '丁未', '丁亥', '庚子', '壬寅', '庚寅', '甲申', '辛丑', '乙酉', '己酉', '乙未', '甲辰', '戊子', '丁酉', '甲戌', '丙申', '庚戌', '己丑', '丁巳', '癸卯', '癸巳', '甲午', '庚申', '癸未', '乙巳', '壬午', '壬戌', '庚午', '甲子', '辛酉', '辛巳', '丁丑', '丙戌', '戊戌', '甲寅', '戊辰', '壬申']] # all possible examples of features
likelihoods = [0.8, 0.6, 0.7, 0.6, 0.8] # Assign by hand
naive = NaiveBayes(names, iterables, likelihoods, prior=0.3)
```

or

```python
from Naive import NaiveBayes

naive = NaiveBayes(filename="definition_time.json", prior=0.3)
```

- calc the prob of a phrase being a time phrase

```python
# a standard time phrase in classical texts
naive.calc_posterior('興寧三年')
# 0.8571428571428572
```

- Still working on: fit a bunch of training data to get the likelihood and iterables.

## Resources

- [Story about Thomas Bayes](https://www.the-tls.co.uk/articles/public/thomas-bayes-science-crisis/)
- [Naive Bayes Formulations on Wiki](https://en.wikipedia.org/wiki/Naive_Bayes_classifier#Constructing_a_classifier_from_the_probability_model)
- [How to Write a Spelling Corrector](https://norvig.com/spell-correct.html)