# Navie Bayes for Tagging

Having uncertainty is better than a point estimate. Assuming informative prior is better than giving a flat prior. As a (potential?) Bayesian, I believe "tagging," this standard pre-processing technique used in historian domain, could be expressed in a Bayesian way. 

Chinese historian tagging platform, like MARKUS, could not return a probability. Tagging platform expected users (historian, or humanities researcher) to use their knowledge to correct the tags manually. However, these platforms do encode some domain knowledge to classify tags (官名、地名、時間名、人名) in a heuristics way. So, why not encode this classification knowledge in a Bayesian way?

Without putting too much ML techniques on it, we can use Bayes rule to encode our domain knowledge and also return a probabilistic result. 

## Tag a time phrase
For example, consider the case to tag a time phrase:

```python
"隆安三年十一月"
```

We can see there are some properties to identify in this phrase: 年號 (隆安), 數字 (三、十一), 單位 (年、月). For this phrase, we can calculate the posterior probability of the phase being a time phrase given this phrase

$$
P(time \mid phrase) = \frac{ P(phrase \mid time) \times P(time) }{ P(phrase) }
$$

### Naive Bayes assumption

By Naive Bayes assumption, the likelehood $P(phrase \mid time)$ could be expressed a product of individual probability of each feature:

$$
P(phrase \mid time) = P(features \mid time) = P(feature_1 \mid time) \times ... \times P(feature_n \mid time) 
$$

For a time phrase in a Chinese historian text, we could build a feature vector based on our experience:


| is time | 年號 | 數字 | 單位 | 季節 | 干支 | 姓氏 | 不相干的字 | 
| ----    | ---  | --- | --- | --- | --- | --- |  ----     |
| +       | 0.8  | 0.6 | 0.7 | 0.6 | 0.8 | 0.2 | 0.45      |
| -       | 0.2  | 0.4 | 0.3 | 0.4 | 0.2 | 0.8 | 0.55      |

the probs are given by the model in my brain 😆. We could justify this model by collection large enough of time phrases.

The normalization factor is following

$$
P(phrase) = P(time) \prod{ P(feature_n \mid time)} + P(\sim time) \prod{ P(feature_n \mid \sim time)}
$$

Therefore, Bayes rule give you the posterior:
$$
P(time \mid phrase) = \frac{ P(time) \prod{ P(feature_n \mid time)} }{ P(time) \prod{ P(feature_n \mid time)} + P(\sim time) \prod{ P(feature_n \mid \sim time)} }
$$

> NOTE: 年號、數字、單位、季節 bags are copied from MARKUS, thanks MARKUS! 

## Examples:
```python
from naive_bayes_time import calc_time_posterior

calc_time_posterior("隆安三年十一月") 
# 0.8873239436619719

calc_time_posterior("張無忌帝一億年二十三月子丑") 
# 0.4697469397630935

calc_time_posterior("司馬大人是個人物，並不只是司馬大人是個人物") 
# 0.002414582912800456
```

So, we are 89% certain that `"隆安三年十一月"` is a time phrase, 0.2% certain `"司馬大人是個人物，並不只是司馬大人是個人物"` is a time phrase, and 47% certain `"張無忌帝一億年二十三月子丑"` is a time phrase. In practice, Navie Bayes allow us to pay more attention on `"張無忌帝一億年二十三月子丑"` pharse to further justify whether it is a time phrase or not. 