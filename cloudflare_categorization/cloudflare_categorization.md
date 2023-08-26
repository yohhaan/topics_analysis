# Cloudflare Categorization

In our analysis, we compare the classification of the Topics API for the Web to
the categorization returned by [Cloudflare Domain Intelligence
API](https://developers.cloudflare.com/api/operations/domain-intelligence-get-multiple-domain-details),
available through [Cloudflare Radar](https://radar.cloudflare.com/).

- Prerequisite: classify CrUX with the Topics API (see [experiment
1](../petsymposium-artifact2024.1/experiment1.sh)).
- Prerequisite: access to the API requires the creation of a Cloudflare account
to generate an API token (with permission `Account: Intel - Read`) in order to
query the Domain Intelligence API (rate limited at about 100 monthly requests).
- Rename `set_cloudflare_env.sh.github` to `set_cloudflare_env.sh` and enter
  your `CLOUDFLARE_ACCOUNT_ID` and `CLOUDFLARE_API_TOKEN`.
- Run `./cloudflare_categorization.sh` to categorize domain names with Cloudflare
  API. Some requests to the API are likely to time out, we just rerun them (see
  script for useful commands).
- Then, you need to manually map Google's Topics to Cloudflare's categories as
  explained in the paper. We release our manual mapping in the following file
  `cloudflare_categories_manual_mapping_topics.json`.
- Finally, compare Topics classification to Cloudflare categorization by running
  `./compare_to_cloudflare_sategorization.sh`. Results are output in the
  following files `../output_web/cloudflare/stats_static.txt` for comparison on
  domains from the static mapping and `../output_web/cloudflare/stats_1M.txt`
  for comparison on CrUX.

**Note & Acknowledgment:** We would like to thank Cloudflare for allowing us to
classify the top 1M most visited domains with their Domain Intelligence API by
increasing the API rate limits of our account.