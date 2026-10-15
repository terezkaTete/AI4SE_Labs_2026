# Task 4 analysis

Model: claude-haiku-5-5, questions answered by every prompt: 155

## 1. Overview

| Prompt | Correct | Accuracy | Mean time (s) | Mean output tokens | Tokens per correct answer |
|---|---|---|---|---|---|
| Chain of Thought | 131/155 | 84.5% | 4.20 | 805 | 3,513 |
| Few-Shot | 138/155 | 89.0% | 2.08 | 246 | 2,265 |
| ICIO | 134/155 | 86.5% | 2.39 | 315 | 2,467 |

## 2. Is the difference in accuracy significant?

Cochran's Q test (all three prompts at once): Q = 5.69, p = 0.058

| Pair | Only first correct | Only second correct | p (McNemar) | p (Holm-corrected) |
|---|---|---|---|---|
| Chain of Thought vs Few-Shot | 1 | 8 | 0.039 | 0.117 |
| Chain of Thought vs ICIO | 2 | 5 | 0.453 | 0.688 |
| Few-Shot vs ICIO | 7 | 3 | 0.344 | 0.688 |

## 3. Is the difference in time and tokens significant?

| Pair | Median time difference (s) | p (time) | Median output token difference | p (tokens) |
|---|---|---|---|---|
| Chain of Thought vs Few-Shot | +2.04 | < 0.001 | +574 | < 0.001 |
| Chain of Thought vs ICIO | +1.85 | < 0.001 | +493 | < 0.001 |
| Few-Shot vs ICIO | -0.26 | < 0.001 | -54 | < 0.001 |

Wilcoxon signed-rank test on the paired values per question, Holm-corrected.

| Pair | Difference in tokens per correct answer | 95 % bootstrap interval | Significant |
|---|---|---|---|
| Chain of Thought vs Few-Shot | +1,248 | +1,100 to +1,428 | yes |
| Chain of Thought vs ICIO | +1,047 | +920 to +1,198 | yes |
| Few-Shot vs ICIO | -201 | -326 to -92 | yes |

## 4. Accuracy by question type

| Question type | Questions | Chain of Thought | Few-Shot | ICIO |
|---|---|---|---|---|
| city | 5 | 5/5 | 5/5 | 5/5 |
| city + rating | 45 | 43/45 | 42/45 | 44/45 |
| street | 45 | 38/45 | 40/45 | 39/45 |
| region | 39 | 26/39 | 32/39 | 26/39 |
| best | 15 | 14/15 | 14/15 | 15/15 |
| restaurant by name | 5 | 5/5 | 5/5 | 5/5 |
| off-topic | 1 | 0/1 | 0/1 | 0/1 |
| with distracting text | 44 | 37/44 | 39/44 | 37/44 |
| without distracting text | 111 | 94/111 | 99/111 | 97/111 |

## 5. How many prompts got each question wrong

| Wrong in | Questions |
|---|---|
| 0 prompt(s) | 128 |
| 1 prompt(s) | 6 |
| 2 prompt(s) | 7 |
| 3 prompt(s) | 14 |

Questions that every prompt got wrong:

- [street] give me a restaurant on avenue near the alameda in belmont with a rating above 2.3 (below average or better)?
- [street] where can i eat some vietnamese food on shellmound st # 12 in emeryville with a rating above 1.7 (poorly rated or better)?
- [street] give me a restaurant on san pablo ave # a in pinole for deli food with a rating above 2 (below average or better), though I am also choosing between noodles and
- [street] My unrelated culinary dilemma involves choosing between cinnamon toast, vegetable pie, and a bowl of rice for a pretend celebration, while a very serious commit
- [street] A very long menu debate has occupied my afternoon: should a picnic feature warm noodles, cold muffins, or an elaborate tower of crackers, and would any of them 
- [off-topic] What is the lifes greates illusion?
- [region] give me some restaurants in the unknown ?
- [region] where can i find a restaurant in the monterey ?
- [region] what are some places in the monterey for bar food with a rating above 1.7 (poorly rated or better)?
- [region] give me a dinner restaurant in the bay area with a rating above 2 (below average or better)?
- [region] where are some restaurants for vietnamese/louisiana food in the bay area with a rating above 2 (below average or better)?
- [region] Thinking about snacks, I wonder whether a muffin or a burrito is easier to fold, where can i eat some swiss food in the monterey with a rating above 2 (below av
- [region] where can i eat some ice cream food in the monterey with a rating above 1.7 (poorly rated or better)?
- [city + rating] I have been comparing the merits of lentil soup, roasted pears, and tiny pancakes for a fictional train journey, and still cannot decide which snack would best 

## 6. What kind of mistakes

| Kind of mistake | Chain of Thought | Few-Shot | ICIO |
|---|---|---|---|
| returned nothing | 16 | 8 | 13 |
| should return nothing | 1 | 1 | 0 |
| too many rows | 3 | 4 | 4 |
| too few rows | 1 | 1 | 1 |
| partly overlapping rows | 0 | 1 | 1 |
| completely different rows | 3 | 2 | 2 |

Some example mistakes:

- **Chain of Thought**, should return nothing: *What is the best delivery in rio del mar ?*  
  `SELECT L.HOUSE_NUMBER, R.NAME FROM RESTAURANT R JOIN LOCATION L ON R.ID = L.RESTAURANT_ID WHERE L.CITY_NAME = 'rio del mar' AND R.RATING = (SELECT MAX(R2.RATING) FROM RESTAURANT R2 JOIN LOCATION L2 ON R2.ID = L2.RESTAURA`
- **Chain of Thought**, returned nothing: *give me a restaurant on avenue near the alameda in belmont with a rating above 2.3 (below average or better)?*  
  `SELECT L.HOUSE_NUMBER, R.NAME FROM RESTAURANT R JOIN LOCATION L ON R.ID = L.RESTAURANT_ID WHERE L.CITY_NAME = 'belmont' AND L.STREET_NAME = 'alameda' AND R.RATING > 2.3;`
- **Chain of Thought**, returned nothing: *give me a restaurant on w evelyn ave ste 108 in sunnyvale with a rating above 2 (below average or better)?*  
  `SELECT L.HOUSE_NUMBER, R.NAME FROM RESTAURANT R JOIN LOCATION L ON R.ID = L.RESTAURANT_ID WHERE L.STREET_NAME = 'w evelyn ave' AND L.CITY_NAME = 'sunnyvale' AND R.RATING > 2;`
- **Chain of Thought**, returned nothing: *where can i eat some vietnamese food on shellmound st # 12 in emeryville with a rating above 1.7 (poorly rated or better*  
  `SELECT L.HOUSE_NUMBER, R.NAME FROM RESTAURANT R JOIN LOCATION L ON R.ID = L.RESTAURANT_ID WHERE L.CITY_NAME = 'emeryville' AND L.STREET_NAME = 'shellmound st' AND L.HOUSE_NUMBER = 12 AND R.FOOD_TYPE = 'vietnamese' AND R.`
- **Chain of Thought**, returned nothing: *give me a restaurant on san pablo ave # a in pinole for deli food with a rating above 2 (below average or better), thoug*  
  `SELECT L.HOUSE_NUMBER, R.NAME FROM RESTAURANT R JOIN LOCATION L ON R.ID = L.RESTAURANT_ID WHERE L.STREET_NAME = 'san pablo ave' AND L.CITY_NAME = 'pinole' AND R.FOOD_TYPE = 'deli' AND R.RATING > 2;`
- **Chain of Thought**, completely different rows: *give me a restaurant on contra costa blvd ste a in pleasant hill for pizza food with a rating above 2 (below average or *  
  `SELECT L.HOUSE_NUMBER, R.NAME FROM RESTAURANT R JOIN LOCATION L ON R.ID = L.RESTAURANT_ID WHERE L.STREET_NAME = 'contra costa blvd' AND L.CITY_NAME = 'pleasant hill' AND R.FOOD_TYPE = 'pizza' AND R.RATING > 2;`

