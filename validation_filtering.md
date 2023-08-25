# Validation Filtering

To verify that we filter the same way the output of the ML model than what
Google does in Google Chrome Beta, execute the following steps:

- Run `./validation_filtering.sh`, this will extract 1000 words from Wordnet and
  classify them with Topics.
- File `output/validation/validation.domains` contains the 1000 words randomly
  sampled, copy-paste this list in the input box of the Topics model shipped
  with Google Chrome Beta:
  - Install Google Chrome Beta.
  - Enable Topics features API.
  - Visit `chrome://topics-internals` to run inference.
- Run the classification in Google Chrome Beta and select the output: copy and
  paste the table that is `\tab` separated in file
  `output/validation/validation.beta`.
- In the analysis code (`analysis.py`), uncomment the code calling the function
  `validation_parameters()` to validate parameters, it returns correct and
  incorrect domain names sets. Incorrect sets should be empty, but in practice
  there are floating point issues and so sometimes a negligible amount of
  domains will get filtered differently. Checking the filtering strategy
  manually shows that the few differences are coming from floating point
  comparison issues between our implementation and Google's. These are
  negligible at the scale of our analysis.

Notes:
- The version of the model and taxonomy used in the analysis must match the ones
  in Google Chrome Beta for this validation to make sense.
- Otherwise, this means that the model and taxonomy have been updated in
  between, and then you either need to use an older version of Google Chrome
  Beta or modify the analysis to use the latest version of the Topics API.