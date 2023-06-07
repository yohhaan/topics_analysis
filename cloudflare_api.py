import os
import pandas as pd
import re
import requests
import sys

CLOUDFLARE_ACCOUNT_ID = str(os.environ.get("CLOUDFLARE_ACCOUNT_ID"))
CLOUDFLARE_API_TOKEN = str(os.environ.get("CLOUDFLARE_API_TOKEN"))

bulk_url = (
    "https://api.cloudflare.com/client/v4/accounts/"
    + CLOUDFLARE_ACCOUNT_ID
    + "/intel/domain/bulk"
)
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + CLOUDFLARE_API_TOKEN,
}

if __name__ == "__main__":
    if sys.argv[1] == "cloudflare_csv_header":
        print("domain\tcloudflare_id")
    if sys.argv[1] == "crux_top":
        """
        Generate domain list of top domains according to CrUX
        """
        top = int(sys.argv[2])
        # CrUX
        crux = pd.read_csv("sandbox_dependencies/topics/crux.csv", sep=",")
        crux = crux.head(top)
        # Regex to remove http(s)://
        crux["origin"] = crux.origin.apply(lambda x: re.sub("https?:\/\/", "", x))
        crux.origin.to_csv(
            "output/cloudflare/crux_top" + str(top) + ".domains",
            index=False,
            header=False,
        )

    if sys.argv[1] == "api_request":
        """
        Call Cloudflare API to classify bulk domains
        """
        domains = sys.argv[2:]
        first_domain = True
        for domain in domains:
            if first_domain:
                bulk_url += "?domain=" + domain
                first_domain = False
            else:
                bulk_url += "&domain=" + domain
        response = requests.request("GET", bulk_url, headers=headers)

        if response.status_code == 200:
            # parse json response
            json_cloudflare = response.json()
            for result in json_cloudflare["result"]:
                # No category returned by Cloudflare
                if "content_categories" not in result:
                    print("{}\t-10".format(result["domain"]) + "\n", end="")
                else:
                    content_categories = result["content_categories"]
                    for c in content_categories:
                        print("{}\t{}".format(result["domain"], c["id"]) + "\n", end="")
            exit(0)
        else:
            # print(response.status_code)
            for domain in domains:
                print("{}\terror".format(domain) + "\n", end="")
            exit(1)
