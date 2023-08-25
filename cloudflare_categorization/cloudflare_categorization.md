# Cloudflare Categorization

In our analysis, we compare the classification of the Topics API for the Web to
the categorization returned by [Cloudflare Domain Intelligence
API](https://developers.cloudflare.com/api/operations/domain-intelligence-get-multiple-domain-details),
available through [Cloudflare Radar](https://radar.cloudflare.com/).

Access to the API requires the creation of a Cloudflare account to generate an
API token (with permission `Account: Intel - Read`) in order to query the Domain
Intelligence API (rate limited at about 100 monthly requests).
- Rename `set_cloudflare_env.sh.github` to `set_cloudflare_env.sh` and enter
  your `CLOUDFLARE_ACCOUNT_ID` and `CLOUDFLARE_API_TOKEN`.
- Run `cloudflare_categorization.sh` to categorize domain names with Cloudflare
  API. Some requests to the API are likely to time out, we just rerun them (see
  script for useful commands).
- Refer to the `analysis.py` code to compare Topics classification to
  Cloudflare categorization. This requires beforehand to manually map Google's
  Topics to Cloudflare's categories as explained in the paper. We release our
  manual mapping in the following file
  `cloudflare_categories_manual_mapping_topics.json`.

**Note & Acknowledgment:** We would like to thank Cloudflare for allowing us to
classify the top 1M most visited domains with their Domain Intelligence API by
increasing the API rate limits of our account.