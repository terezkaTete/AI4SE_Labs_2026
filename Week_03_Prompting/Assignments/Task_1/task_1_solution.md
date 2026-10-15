# Task 1: Prompting frameworks

All frameworks were taken from https://frompting.com/frameworks. The prompts are in `prompts.json`. Each prompt has a `{question}` placeholder that is replaced with a question from the dataset in Task 2.

## How I chose the frameworks

Most frameworks on the site are templates for writing, like marketing copy, presentations or user stories. Many of the AI ones (RACE, CRISP, CO-STAR, RTF...) are quite similar to each other. They give the model a role, some context and an output format, and the differences are mostly in the section names. If I compared three of those, I would expect almost the same results and there wouldn't be much to analyse in Task 4. So I picked three frameworks that each help the model in a different way:

- Few-Shot shows the model examples,
- ICIO gives it a precise specification of the input and output,
- Chain of Thought makes it reason step by step before answering.

The task is to turn a question into an SQL query, and the evaluation script runs that query and compares the rows with the expected answer. So what matters is whether the model follows the conventions of the dataset. I checked these by running queries on the database. The result must be the house number and the restaurant name, the city is taken from the LOCATION table, regions are found through GEOGRAPHIC, and "rating above 2" has to be written as `> 2` (with `>=` the alameda question returned 125 rows instead of 62). Many questions also contain sentences that have nothing to do with restaurants.

All three prompts contain the same schema and the same four examples. Each framework then states the rules in its own way. I made sure none of the example questions are in the dataset.

## Few-Shot

Source: https://frompting.com/frameworks/few-shot

The prompt follows the four parts from the site. There is a task line, then the allowed output (one query with two columns over the three tables), then the examples, and finally tie-break rules for cases where it isn't clear what to do, e.g. whether a place is a city or a region, or what "best" means.

I chose it because the conventions of this dataset are easiest to show rather than explain. The model can copy the join and the selected columns straight from the examples. It is also the shortest prompt and the model only returns the query, so it should be the fastest.

I expect it to do well on questions that look like the examples. On question types the examples don't cover, it could make mistakes, because there are only a few rules.

## ICIO

Source: https://frompting.com/frameworks/icio

ICIO stands for Instruction, Context, Input and Output. The instruction is to translate the question into one query. The context describes the database, the rules, and the fact that the output is checked automatically. The input is the question, put between markers, with a note that everything inside is data and not instructions. The output part says what the query must look like and shows the four examples as samples.

The site recommends ICIO for transforming data into a fixed format that a program will read, which describes this task well. The markers around the question are useful here because many questions contain unrelated sentences, and the model should not treat them as part of the request.

I expect ICIO to be the most reliable at following the rules and returning clean output that can be executed. It should be better than Few-Shot on the questions with noise in them.

## Chain of Thought

Source: https://frompting.com/frameworks/cot

The prompt asks the model to go through named steps before writing the query: find the actual request, decide if the place is a city, region or street, get the food type and rating condition, write down assumptions, and check the query (right columns, `>` instead of `>=`). The examples show the same reasoning in a short form. The answer has to end with a line `SQL: <query>`, and in Task 2 only the text after it is used.

I wanted one prompt where the model reasons before answering, because the hard part of the task is understanding the question correctly (city or region, "above" or "at least", what is noise). The site actually says CoT is not ideal for outputs that are parsed and for models that already reason on their own. I think it's interesting to test that, and the final `SQL:` line solves the parsing.

I expect CoT to make fewer mistakes on the harder questions, e.g. regions and "best". But it will be much slower because the answers are longer, and sometimes the final line might be missing or formatted wrong. If the model used in Task 2 already reasons internally, the improvement may be small.

## Expectations

I expect ICIO and CoT to be more accurate than Few-Shot, with CoT being clearly the slowest. Since all prompts have the same examples, the differences in accuracy may be small. The difference in time should be large. I will check both in Task 4.