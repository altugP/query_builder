import pandas as pd
import numpy as np
import os


# region Setup -----------------------------------------------------------------
num_cols_before: int = 2
num_cols_per_db: int = 4
keywords_file: str = 'keywords'  # script checks for .csv and .xlsx file endings
output_file: str = 'queries.md'
# endregion --------------------------------------------------------------------


# region Functions -------------------------------------------------------------
def get_num_dbs(df: pd.DataFrame) -> int:
  '''Returns the number of databases in the given dataframe'''
  return (len(df.columns) - num_cols_before) // num_cols_per_db


def get_db_name(df: pd.DataFrame) -> str:
  '''Returns the name of the first database in the dataframe as string'''
  return df.columns[num_cols_before].split('Include in ')[-1]


def get_indices(df: pd.DataFrame) -> np.ndarray:
  '''Returns a list of indices for all db specific columns of the dataframe'''
  num_db: int = get_num_dbs(df)
  indices: list = []
  for db in range(num_db):
    i: int = num_cols_before + num_cols_per_db * db  # start index (inclusive)
    j: int = i + num_cols_per_db  # end index (exclusive)
    indices.append((i, j))
  return np.array(indices)


def get_db_slice(df: pd.DataFrame, i: int, j: int) -> pd.DataFrame:
  '''Returns a datagrame containing the concept, the keyword, and the three
     columns for a database identified by the indices i and j'''
  return pd.concat([df.iloc[:, 0:num_cols_before],
                    df.iloc[:, i:j]], axis=1)


def create_query(words: list, encapsulate_pairs: bool,
                 include_ids: list = None, join: str = 'OR') -> str:
  '''Returns a query string using the provided keywords by joining them using
     the provided join term'''
  filtered_words = [word for word, flag in zip(words, include_ids) if flag]
  if not encapsulate_pairs:
    return '(' + f' {join} '.join(filtered_words) + ')'
  n = len(filtered_words)
  if n <= 0:
    return ''
  result: str = filtered_words[0]
  if n == 1:
    return '(' + result + ')'
  for word in filtered_words[1:]:
    result = f'({result} {join} {word})'
  return result


def build_output(queries_by_db: list) -> None:
  '''Creates an .md file detailing all (sub-) queries for each database'''
  content = f'''# Literature Review Search Queries

This file was generated using Python. It shows the different search terms as (sub-) queries for each search concept for every database.
'''
  for db in queries_by_db:
    content += f'''
## {db['db_name']}

`{db['full_query']}`

### {db['db_name']} - Sub-Queries by Research Concept

| Core Concept | Query String |
| :----------- | :----------- |
'''
    for concept, sub_query in db['sub_queries'].items():
      content += f'''| {concept} | `{sub_query}` |
'''
  with open(output_file, 'w') as file:
    file.write(content)
# endregion --------------------------------------------------------------------


# region Main ------------------------------------------------------------------
# read input file and create dataframe
try:
  data: pd.DataFrame = pd.read_csv(f'{keywords_file}.csv').fillna('')
except FileNotFoundError:
  if os.path.exists(f'{keywords_file}.xlsx'):
    data: pd.DataFrame = pd.read_excel(f'{keywords_file}.xlsx')
  else:
    print('No keywords file found')
    exit(1)

# list for resulting queries
queries_by_db: list = [[] for _ in range(get_num_dbs(data))]

# iterate over all databases
idx: np.ndarray = get_indices(data)
for db in range(len(idx)):
  # select relevant columns for the current database
  db_df: pd.DataFrame = get_db_slice(data, idx[db, 0], idx[db, 1])
  # group all entries by concept
  grouped_data = db_df.groupby('Concept')
  # create sub-searches by concept
  db_data: dict = {'sub_queries': {}}
  for concept, df in grouped_data:
    db_data['db_name'] = get_db_name(df)
    appended_words = (df.iloc[:, num_cols_before + 1]
                      + df['Keyword']
                      + df.iloc[:, num_cols_before + 2]).to_list()
    db_data['sub_queries'][concept] = create_query(appended_words,
                                                   df.iloc[:, -1].all(),
                                                   df.iloc[:, num_cols_before]
                                                   .to_list(),
                                                   join='OR')
  query: str = create_query(list(db_data['sub_queries'].values()),
                            False, df.iloc[:, num_cols_before].to_list(),
                            join='AND')
  db_data['full_query'] = query
  queries_by_db[db] = db_data
build_output(queries_by_db)
print('Output file created')
exit(0)
# endregion --------------------------------------------------------------------
